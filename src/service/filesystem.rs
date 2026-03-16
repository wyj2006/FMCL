use super::service_template;
use crate::common::WORK_DIR;
use crate::error::Error;
use crate::fcb::{FCB, VPath};
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::{info, warn};
use serde_json::{self, json};
use std::collections::BTreeSet;
use std::fs;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
use std::path::PathBuf;
use std::sync::Mutex;
use std::vec;

//所有的路径都是绝对路径
lazy_static! {
    pub static ref fcb_root: Mutex<FCB> = Mutex::new(FCB {
        name: String::from("root"),
        path: VPath::from("/"),
        native_paths: BTreeSet::from([PathBuf::from(WORK_DIR.to_string())]),
        children: vec![],
        mount_paths: BTreeSet::new(),
    });
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Fileinfo {
        path: String,
        #[arg(long)]
        create: bool,
    },
    Listdir {
        path: String,
    },
    MountNative {
        path: String,
        native_path: String,
    },
    UnmountNative {
        path: String,
        native_path: String,
    },
    Makedirs {
        path: String,
    },
    Mount {
        path: String,
        mount_path: String,
    },
    Unmount {
        path: String,
        mount_path: String,
    },
}

pub fn load_child(root: &mut FCB, fcb: &mut FCB, name: &str) -> Result<(), Error> {
    if let Some(_) = fcb.find(name) {
        return Ok(());
    }

    let mut paths = BTreeSet::new();

    for native_path in &collect_native_paths(root, fcb)? {
        for result_entry in match fs::read_dir(native_path) {
            Ok(t) => t,
            Err(_) => continue,
        } {
            let entry = match result_entry {
                Ok(t) => t,
                Err(_) => continue,
            };
            if entry.file_name() == name {
                paths.insert(entry.path());
            }
        }
    }

    let child_path = fcb.path.join(name);

    if paths.len() > 0 {
        match fcb.find(name) {
            Some(child) => {
                child.native_paths.extend(paths);
                Ok(())
            }
            None => {
                fcb.children.push(FCB {
                    name: String::from(name),
                    path: child_path,
                    native_paths: paths,
                    children: vec![],
                    mount_paths: BTreeSet::new(),
                });
                Ok(())
            }
        }
    } else {
        Err(Error::FileNotFound(child_path.to_string()))
    }
}

pub fn get_fcb<'a, 'b>(root: &'a mut FCB, path: &'b str) -> Result<&'a mut FCB, Error> {
    //所有的FCB都引用于fcb_root, 而fcb_root本身就是带锁的
    let mut cur = unsafe { &mut *(root as *mut FCB) };
    'outer: for name in &VPath::from(path).0 {
        if name == "" {
            continue;
        }
        match load_child(root, cur, name) {
            Ok(_) => {
                cur = cur.find(name).unwrap();
            }
            Err(e) => {
                for mount_path in &cur.mount_paths {
                    match get_fcb(
                        unsafe { &mut *(root as *mut FCB) },
                        &mount_path.join(name).to_string(),
                    ) {
                        Ok(t) => {
                            cur = t;
                            continue 'outer;
                        }
                        Err(_) => continue,
                    }
                }
                return Err(e);
            }
        }
    }
    Ok(cur)
}

pub fn get_or_create_fcb<'a, 'b>(root: &'a mut FCB, path: &'b str) -> Result<&'a mut FCB, Error> {
    //所有的FCB都引用于fcb_root, 而fcb_root本身就是带锁的
    let mut cur: &mut FCB = unsafe { &mut *(root as *mut FCB) };
    'outer: for name in &VPath::from(path).0 {
        if name == "" {
            continue;
        }
        if let Err(_) = load_child(root, cur, name) {
            for mount_path in &cur.mount_paths {
                match get_or_create_fcb(
                    unsafe { &mut *(root as *mut FCB) },
                    &mount_path.join(name).to_string(),
                ) {
                    Ok(t) => {
                        cur = t;
                        continue 'outer;
                    }
                    Err(_) => continue,
                }
            }
            cur.create(FCB {
                name: name.to_string(),
                path: cur.path.join(name),
                native_paths: {
                    let mut native_paths = BTreeSet::new();
                    for native_path in &cur.native_paths {
                        native_paths.insert(native_path.join(name));
                    }
                    native_paths
                },
                children: vec![],
                mount_paths: BTreeSet::new(),
            })?;
        }
        cur = cur.find(name).unwrap();
    }
    Ok(cur)
}

pub fn listdir(root: &mut FCB, path: &str) -> Result<Vec<String>, Error> {
    let t = get_fcb(unsafe { &mut *(root as *mut FCB) }, path)?;
    let mut names: Vec<String> = vec![];
    //实际的子项
    for native_path in &t.native_paths {
        for result_entry in match fs::read_dir(native_path) {
            Ok(t) => t,
            Err(_) => {
                //有可能这个native_path不是目录
                continue;
            }
        } {
            let entry = match result_entry {
                Ok(t) => t,
                Err(_) => {
                    continue;
                }
            };
            let name = entry.file_name().to_str().unwrap().to_string();
            if !names.contains(&name) {
                names.push(name);
            }
        }
    }
    //虚拟的子项
    for child in &t.children {
        let name = child.name.clone();
        if !names.contains(&name) {
            names.push(name);
        }
    }
    //挂载在上面的子项
    //可以使用 t.mount_paths.clone() 来避免使用unsafe
    for mount_path in &t.mount_paths {
        for name in match listdir(root, &mount_path.to_string()) {
            Ok(t) => t,
            Err(_) => continue,
        } {
            if !names.contains(&name) {
                names.push(name);
            }
        }
    }
    Ok(names)
}

pub fn mount_native(root: &mut FCB, path: &str, native_path: &str) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    t.native_paths.insert(PathBuf::from(native_path));
    Ok(())
}

pub fn unmount_native(root: &mut FCB, path: &str, native_path: &str) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    t.native_paths.remove(&PathBuf::from(native_path));
    t.unload_all(); //已有的children将要重新加载
    Ok(())
}

pub fn mount(root: &mut FCB, path: &str, mount_path: &str) -> Result<(), Error> {
    let t = get_or_create_fcb(unsafe { &mut *(root as *mut FCB) }, &path)?;
    if !collect_mount_paths(root, t)?.contains(&VPath::from(mount_path)) {
        t.mount_paths.insert(VPath::from(mount_path));
    }
    Ok(())
}

pub fn unmount(root: &mut FCB, path: &str, mount_path: &str) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    t.mount_paths.remove(&VPath::from(mount_path));
    t.unload_all();
    Ok(())
}

pub fn makedirs(root: &mut FCB, path: &str) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    if t.native_paths.len() > 1 {
        warn!(
            "More than one native path. Choose the first one: {}",
            t.native_paths.first().unwrap().to_str().unwrap()
        );
    }
    let native_path = t.native_paths.first().unwrap();
    fs::create_dir_all(native_path)?;
    Ok(())
}

pub fn collect_mount_paths(root: &mut FCB, fcb: &FCB) -> Result<BTreeSet<VPath>, Error> {
    let mut paths = fcb.mount_paths.clone();
    for mount_path in &fcb.mount_paths {
        let Ok(t) = get_fcb(unsafe { &mut *(root as *mut FCB) }, &mount_path.to_string()) else {
            continue;
        };
        paths.extend(collect_mount_paths(root, t)?);
    }
    Ok(paths)
}

//获得fcb对应的native_paths, 包括挂载在它上面的
pub fn collect_native_paths(root: &mut FCB, fcb: &FCB) -> Result<BTreeSet<PathBuf>, Error> {
    let mut paths = fcb.native_paths.clone();
    for mount_path in &fcb.mount_paths {
        let Ok(t) = get_fcb(unsafe { &mut *(root as *mut FCB) }, &mount_path.to_string()) else {
            continue;
        };
        paths.extend(collect_native_paths(root, t)?);
    }
    Ok(paths)
}

pub fn filesystem_service() {
    service_template(
        "filesystem".to_string(),
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| {
            let root = &mut *fcb_root.lock().unwrap();
            match ServiceCommand::try_parse_from({
                let mut t = vec!["filesystem".to_string()];
                t.extend(args);
                t
            })? {
                ServiceCommand { sub_command } => match sub_command {
                    SubCommand::Fileinfo { path, create } => {
                        let t = if create {
                            get_or_create_fcb(unsafe { &mut *(root as *mut FCB) }, &path)?
                        } else {
                            get_fcb(unsafe { &mut *(root as *mut FCB) }, &path)?
                        };
                        Ok(Some(json!({
                            "name":t.name,
                            "path":t.path.to_string(),
                            "native_paths":collect_native_paths(root, t)?
                        })))
                    }
                    SubCommand::Listdir { path } => {
                        let t = listdir(root, &path)?;
                        Ok(Some(json!({
                            "names":t
                        })))
                    }
                    SubCommand::MountNative { path, native_path } => {
                        info!("Mount '{native_path}' to '{path}'");
                        mount_native(root, &path, &native_path)?;

                        Ok(Some(json!({})))
                    }
                    SubCommand::UnmountNative { path, native_path } => {
                        info!("Unmount '{native_path}' to '{path}'");
                        unmount_native(root, &path, &native_path)?;

                        Ok(Some(json!({})))
                    }
                    SubCommand::Makedirs { path } => {
                        makedirs(root, &path)?;
                        Ok(Some(json!({})))
                    }
                    SubCommand::Mount {
                        path: target_path,
                        mount_path: source_path,
                    } => {
                        info!("Mount '{source_path}' to '{target_path}'");
                        mount(root, &target_path, &source_path)?;
                        Ok(Some(json!({})))
                    }
                    SubCommand::Unmount {
                        path: target_path,
                        mount_path: source_path,
                    } => {
                        info!("Unmount '{source_path}' to '{target_path}'");
                        unmount(root, &target_path, &source_path)?;

                        Ok(Some(json!({})))
                    }
                },
            }
        },
        |_stream| {},
    );
}
