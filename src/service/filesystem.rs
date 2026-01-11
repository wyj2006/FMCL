use super::service_template;
use crate::common::WORK_DIR;
use crate::error::Error;
use crate::fcb::FCB;
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::{info, warn};
use serde_json::{self, json};
use std::collections::HashMap;
use std::fs;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
use std::path::Path;
use std::sync::{Mutex, RwLock};
use std::vec;

//所有的路径都是绝对路径
lazy_static! {
    pub static ref fcb_root: Mutex<FCB> = Mutex::new(FCB {
        name: String::from("root"),
        path: String::from(""),
        native_paths: vec![WORK_DIR.to_string()],
        children: vec![],
    });
    pub static ref mount_table: RwLock<HashMap<String, Vec<String>>> = RwLock::new(HashMap::new());
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
        target_path: String,
        source_path: String,
    },
    Unmount {
        target_path: String,
        source_path: String,
    },
}

pub fn get_fcb<'a, 'b>(root: &'a mut FCB, path: &'b String) -> Result<&'a mut FCB, Error> {
    //所有的FCB都引用于fcb_root, 而fcb_root本身就是带锁的
    let mut cur = unsafe { &mut *(root as *mut FCB) };
    let path = path.replace("\\", "/");
    'outer: for name in path.split("/") {
        if name == "" {
            continue;
        }
        match cur.load(name) {
            Ok(_) => {
                cur = cur.find(name).unwrap();
            }
            Err(e) => {
                if let Some(source_paths) = mount_table.read().unwrap().get(&cur.path) {
                    for source_path in source_paths {
                        match get_fcb(
                            unsafe { &mut *(root as *mut FCB) },
                            &Path::new(source_path)
                                .join(name)
                                .to_str()
                                .unwrap()
                                .to_string(),
                        ) {
                            Ok(t) => {
                                cur = t;
                                continue 'outer;
                            }
                            Err(_) => continue,
                        }
                    }
                }
                return Err(e);
            }
        }
    }
    Ok(cur)
}

pub fn get_or_create_fcb<'a, 'b>(
    root: &'a mut FCB,
    path: &'b String,
) -> Result<&'a mut FCB, Error> {
    //所有的FCB都引用于fcb_root, 而fcb_root本身就是带锁的
    let mut cur: &mut FCB = unsafe { &mut *(root as *mut FCB) };
    let path = path.replace("\\", "/");
    'outer: for name in path.split("/") {
        if name == "" {
            continue;
        }
        if let Err(_) = cur.load(name) {
            if let Some(source_paths) = mount_table.read().unwrap().get(&cur.path) {
                for source_path in source_paths {
                    match get_or_create_fcb(
                        unsafe { &mut *(root as *mut FCB) },
                        &Path::new(source_path)
                            .join(name)
                            .to_str()
                            .unwrap()
                            .to_string(),
                    ) {
                        Ok(t) => {
                            cur = t;
                            continue 'outer;
                        }
                        Err(_) => continue,
                    }
                }
            }
            cur.create(FCB {
                name: name.to_string(),
                path: Path::new(&cur.path)
                    .join(name)
                    .to_str()
                    .unwrap()
                    .to_string(),
                native_paths: {
                    let mut native_paths = Vec::new();
                    for native_path in &cur.native_paths {
                        native_paths.push(
                            Path::new(&native_path)
                                .join(name)
                                .to_str()
                                .unwrap()
                                .to_string(),
                        );
                    }
                    native_paths
                },
                children: Vec::new(),
            })?;
        }
        cur = cur.find(name).unwrap();
    }
    Ok(cur)
}

pub fn listdir(root: &mut FCB, path: &String) -> Result<Vec<String>, Error> {
    let t = get_fcb(root, path)?;
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
    if let Some(source_paths) = mount_table.read().unwrap().get(&t.path) {
        for source_path in source_paths {
            for name in match listdir(root, source_path) {
                Ok(t) => t,
                Err(_) => continue,
            } {
                if !names.contains(&name) {
                    names.push(name);
                }
            }
        }
    }
    Ok(names)
}

pub fn mount_native(root: &mut FCB, path: &String, native_path: &String) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    if !t.native_paths.contains(native_path) {
        t.native_paths.push(native_path.clone());
    }
    Ok(())
}

pub fn unmount_native(root: &mut FCB, path: &String, native_path: &String) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    if let Some(index) = t.native_paths.iter().position(|x| x == native_path) {
        t.native_paths.remove(index);
        t.unload_all(); //已有的children将要重新加载
    }
    Ok(())
}

pub fn mount(root: &mut FCB, target_path: &String, source_path: &String) -> Result<(), Error> {
    let fcb = get_or_create_fcb(root, target_path)?;
    let mut mt = mount_table.write().unwrap();
    if let Some(t) = mt.get_mut(&fcb.path) {
        t.push(source_path.to_string());
    } else {
        mt.insert(fcb.path.clone(), vec![source_path.to_string()]);
    }
    Ok(())
}

pub fn unmount(root: &mut FCB, target_path: &String, source_path: &String) -> Result<(), Error> {
    let fcb = get_or_create_fcb(root, target_path)?;
    let mut mt = mount_table.write().unwrap();
    if let Some(t) = mt.get_mut(&fcb.path) {
        if let Some(i) = t.iter().position(|x| x == source_path) {
            t.remove(i);
            fcb.unload_all(); //已有的children将要重新加载
        }
    }
    Ok(())
}

pub fn makedirs(root: &mut FCB, path: &String) -> Result<(), Error> {
    let t = get_or_create_fcb(root, path)?;
    if t.native_paths.len() > 1 {
        warn!(
            "More than one native path. Choose the first one: {}",
            t.native_paths[0]
        );
    }
    let native_path = &t.native_paths[0];
    fs::create_dir_all(native_path)?;
    Ok(())
}

pub fn filesystem_service() {
    service_template(
        "filesystem".to_string(),
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| {
            let root = &mut fcb_root.lock().unwrap();
            match ServiceCommand::try_parse_from({
                let mut t = vec!["filesystem".to_string()];
                t.extend(args);
                t
            })? {
                ServiceCommand { sub_command } => match sub_command {
                    SubCommand::Fileinfo { path, create } => {
                        let t = if create {
                            get_or_create_fcb(root, &path)?
                        } else {
                            get_fcb(root, &path)?
                        };
                        Ok(Some(json!({
                            "name":t.name,
                            "path":t.path,
                            "native_paths":t.native_paths
                        })))
                    }
                    SubCommand::Listdir { path } => {
                        let t = listdir(root, &path)?;
                        Ok(Some(json!({
                            "names":t
                        })))
                    }
                    SubCommand::MountNative { path, native_path } => {
                        mount_native(root, &path, &native_path)?;
                        info!("Mount '{native_path}' to '{path}'");
                        Ok(Some(json!({})))
                    }
                    SubCommand::UnmountNative { path, native_path } => {
                        unmount_native(root, &path, &native_path)?;
                        info!("Unmount '{native_path}' to '{path}'");
                        Ok(Some(json!({})))
                    }
                    SubCommand::Makedirs { path } => {
                        makedirs(root, &path)?;
                        Ok(Some(json!({})))
                    }
                    SubCommand::Mount {
                        target_path,
                        source_path,
                    } => {
                        mount(root, &target_path, &source_path)?;
                        info!("Mount '{source_path}' to '{target_path}'");
                        Ok(Some(json!({})))
                    }
                    SubCommand::Unmount {
                        target_path,
                        source_path,
                    } => {
                        unmount(root, &target_path, &source_path)?;
                        info!("Unmount '{source_path}' to '{target_path}'");
                        Ok(Some(json!({})))
                    }
                },
            }
        },
        |_stream| {},
    );
}
