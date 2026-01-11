use super::service_template;
use crate::common::WORK_DIR;
use crate::error::Error;
use crate::service::filesystem::{fcb_root, get_fcb};
use base64::prelude::*;
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::{info, warn};
use serde_json::{Value, json};
use std::collections::HashMap;
use std::fs;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
use std::path::Path;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

lazy_static! {
    pub static ref running_functions: Mutex<HashMap<String, Child>> = Mutex::new(HashMap::new());
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Run { native_path: String, args: String },
    GetallRunning,
}

pub fn run_function(native_path: &String, external_args: Vec<String>) -> Result<u128, Error> {
    let json_path = Path::new(native_path).join("function.json");
    let command = match serde_json::from_str(&fs::read_to_string(
        Path::new(native_path).join("function.json"),
    )?) {
        Ok(t) => {
            if let Value::Object(t) = t {
                if let Some(Value::Object(t)) = t.get("command") {
                    t.clone()
                } else {
                    return Err(Error::InvalidKey(
                        "command".to_string(),
                        json_path.to_str().unwrap().to_string(),
                    ));
                }
            } else {
                return Err(Error::InvalidFile(json_path.to_str().unwrap().to_string()));
            }
        }
        Err(e) => return Err(Error::from(e)),
    };

    let mut program = match command.get("program") {
        Some(Value::String(program)) => Some(program.to_string()),
        _ => None,
    };
    let cwd = match command.get("cwd") {
        Some(Value::String(cwd)) => cwd,
        _ => native_path,
    };
    let mut envs = HashMap::new();
    let mut args = match command.get("args") {
        Some(Value::Array(t)) => {
            let mut args: Vec<String> = Vec::new();
            for arg in t {
                if let Value::String(arg) = arg {
                    args.push(arg.clone());
                }
            }
            args
        }
        _ => Vec::new(),
    };
    args.extend(external_args);

    match command.get("template") {
        Some(Value::String(template)) => match template.as_str() {
            "python" => {
                program = Some("python".to_string());
                envs.insert("PYTHONPATH".to_string(), WORK_DIR.to_string());
                args.insert(0, "__main__.py".to_string());
            }
            "function" => {
                let Some(Value::String(function_path)) = command.get("program") else {
                    return Err(Error::TemplateKeyMissing(
                        "function".to_string(),
                        "program".to_string(),
                    ));
                };
                let args = if let Some(Value::Array(t)) = command.get("args") {
                    let mut args: Vec<String> = Vec::new();
                    for arg in t {
                        if let Value::String(arg) = arg {
                            args.push(arg.clone());
                        }
                    }
                    args
                } else {
                    return Err(Error::InvalidArgs(format!("{:?}", command.get("args"))));
                };
                return run_function(
                    match get_fcb(&mut fcb_root.lock().unwrap(), function_path) {
                        Ok(t) => &t.native_paths[0],
                        Err(e) => return Err(e),
                    },
                    args,
                );
            }
            _ => warn!("Unkown template: {}", template),
        },
        Some(template) => {
            warn!("Unkown template: {}", template);
        }
        None => {}
    }

    let child = Command::new(match program {
        Some(program) => program,
        None => {
            return Err(Error::ProgramNotFound);
        }
    })
    .current_dir(cwd.clone())
    .envs(envs)
    .args(args)
    .spawn()
    .unwrap();
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis();
    running_functions
        .lock()
        .unwrap()
        .insert(timestamp.to_string(), child);
    Ok(timestamp)
}

///移除已经结束的功能
pub fn remove_stopped_functions() {
    //用try_lock减少对正常服务的影响
    if let Ok(mut t) = running_functions.try_lock() {
        let mut stopped_functions = Vec::new();

        for (timestamp, child) in t.iter_mut() {
            match child.try_wait() {
                Ok(Some(_)) | Err(_) => {
                    stopped_functions.push(timestamp.clone());
                }
                _ => {}
            }
        }

        for timestamp in &stopped_functions {
            t.remove(timestamp);
        }
    }
}

pub fn kill_all_functions() {
    for (_, child) in running_functions.lock().unwrap().iter_mut() {
        child.kill().unwrap();
        info!("Kill {}", child.id());
    }
}

pub fn function_service() {
    service_template(
        "function".to_string(),
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| match ServiceCommand::try_parse_from({
            let mut t = vec!["function".to_string()];
            t.extend(args);
            t
        })? {
            ServiceCommand { sub_command } => match sub_command {
                SubCommand::Run { native_path, args } => {
                    let json_str = BASE64_STANDARD.decode(args)?;
                    let json_str = String::from_utf8_lossy(&json_str);
                    let args = match serde_json::from_str(&json_str) {
                        Ok(args) => {
                            if let Value::Array(t) = args {
                                let mut args: Vec<String> = Vec::new();
                                for arg in t {
                                    if let Value::String(arg) = arg {
                                        args.push(arg.clone());
                                    }
                                }
                                args
                            } else {
                                return Err(Error::InvalidExtArgs(json_str.to_string()));
                            }
                        }
                        Err(e) => return Err(Error::from(e)),
                    };
                    match run_function(&native_path, args.clone()) {
                        Ok(_) => {
                            info!("Run '{native_path}' with {args:?}");
                            Ok(Some(json!({})))
                        }
                        Err(e) => Err(e),
                    }
                }
                SubCommand::GetallRunning => {
                    let mut data = json!({});
                    for (timestamp, child) in running_functions.lock().unwrap().iter() {
                        data[timestamp] = json!(child.id());
                    }
                    Ok(Some(data))
                }
            },
        },
        |_stream| {
            remove_stopped_functions();
        },
    );
}
