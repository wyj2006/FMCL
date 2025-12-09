use super::{error_log_and_write, service_template, write_ok};
use crate::common::WORK_DIR;
use crate::fcb::FCB;
use lazy_static::lazy_static;
use log::warn;
use serde_json::{self, json};
use std::fs;
use std::io::Write;
use std::path::Path;
use std::sync::Mutex;
use std::vec;

lazy_static! {
    pub static ref fcb_root: Mutex<FCB> = Mutex::new(FCB {
        name: String::from("root"),
        path: String::from(""),
        native_paths: vec![WORK_DIR.to_string()],
        children: vec![],
    });
}

pub fn get_fcb<'a, 'b>(parent: &'a mut FCB, path: &'b String) -> Result<&'a mut FCB, String> {
    let mut cur = parent;
    let path = path.replace("\\", "/");
    for name in path.split("/") {
        if name == "" {
            continue;
        }
        match cur.load(name) {
            Ok(_) => {
                cur = cur.find(name).unwrap();
            }
            Err(e) => {
                return Err(e);
            }
        }
    }
    Ok(cur)
}

pub fn get_or_create_fcb<'a, 'b>(
    parent: &'a mut FCB,
    path: &'b String,
) -> Result<&'a mut FCB, String> {
    let mut cur = parent;
    let path = path.replace("\\", "/");
    for name in path.split("/") {
        if name == "" {
            continue;
        }
        if let Err(_) = cur.load(name) {
            if let Err(e) = cur.create(FCB {
                name: name.to_string(),
                path: format!("{}/{name}", cur.path),
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
            }) {
                return Err(e.to_string());
            }
        }
        cur = cur.find(name).unwrap();
    }
    Ok(cur)
}

pub fn listdir(parent: &mut FCB, path: &String) -> Result<Vec<String>, String> {
    match get_fcb(parent, path) {
        Ok(t) => {
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
                        Err(e) => {
                            return Err(e.to_string());
                        }
                    };
                    names.push(entry.file_name().to_str().unwrap().to_string());
                }
            }
            //虚拟的子项
            for child in &t.children {
                let name = child.name.clone();
                if !names.contains(&name) {
                    names.push(name);
                }
            }
            Ok(names)
        }
        Err(e) => Err(e),
    }
}

pub fn mount_native(parent: &mut FCB, path: &String, native_path: &String) -> Result<(), String> {
    match get_or_create_fcb(parent, path) {
        Ok(t) => {
            if !t.native_paths.contains(native_path) {
                t.native_paths.push(native_path.clone());
            }
            Ok(())
        }
        Err(e) => Err(e),
    }
}

pub fn unmount_native(parent: &mut FCB, path: &String, native_path: &String) -> Result<(), String> {
    match get_or_create_fcb(parent, path) {
        Ok(t) => {
            if let Some(index) = t.native_paths.iter().position(|x| x == native_path) {
                t.native_paths.remove(index);
            }
            Ok(())
        }
        Err(e) => Err(e),
    }
}

pub fn makedirs(parent: &mut FCB, path: &String) -> Result<(), String> {
    match get_or_create_fcb(parent, path) {
        Ok(t) => {
            if t.native_paths.len() > 1 {
                warn!(
                    "More than one native path. Choose the first one: {}",
                    t.native_paths[0]
                );
            }
            let native_path = &t.native_paths[0];
            if let Err(e) = fs::create_dir_all(native_path) {
                return Err(e.to_string());
            }
        }
        Err(e) => return Err(e),
    }
    Ok(())
}

pub fn filesystem_service() {
    service_template(
        "filesystem".to_string(),
        String::from("127.0.0.1:0"),
        |_stream, _reader, writer, _buf, args| {
            let parent = &mut fcb_root.lock().unwrap();
            if args.len() >= 2 && args[0] == "fileinfo" {
                let path = &args[1];
                match get_fcb(parent, path) {
                    Ok(t) => {
                        writer
                            .write_all(
                                json!({
                                    "name":t.name,
                                    "path":t.path,
                                    "native_paths":t.native_paths
                                })
                                .to_string()
                                .as_bytes(),
                            )
                            .unwrap();
                        writer.flush().unwrap();
                    }
                    Err(e) => {
                        error_log_and_write(writer, e);
                    }
                };
            } else if args.len() >= 2 && args[0] == "listdir" {
                let path = &args[1];
                match listdir(parent, path) {
                    Ok(t) => {
                        writer
                            .write_all(
                                json!( {
                                    "names":t
                                })
                                .to_string()
                                .as_bytes(),
                            )
                            .unwrap();
                        writer.flush().unwrap();
                    }
                    Err(e) => {
                        error_log_and_write(writer, e);
                    }
                }
            } else if args.len() >= 3 && args[0] == "mount_native" {
                let path = &args[1];
                let native_path = &args[2];
                match mount_native(parent, path, native_path) {
                    Ok(_) => {
                        write_ok(writer);
                    }
                    Err(e) => {
                        error_log_and_write(writer, e);
                    }
                }
            } else if args.len() >= 3 && args[0] == "unmount_native" {
                let path = &args[1];
                let native_path = &args[2];
                match unmount_native(parent, path, native_path) {
                    Ok(_) => {
                        write_ok(writer);
                    }
                    Err(e) => {
                        error_log_and_write(writer, e);
                    }
                }
            } else if args.len() >= 2 && args[0] == "makedirs" {
                match makedirs(parent, &args[1]) {
                    Ok(_) => {
                        write_ok(writer);
                    }
                    Err(e) => {
                        error_log_and_write(writer, e);
                    }
                }
            }
        },
        |_stream| {},
    );
}
