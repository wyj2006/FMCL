use super::{error_log_and_write, service_template, write_ok};
use crate::common::WORK_DIR;
use base64::prelude::*;
use lazy_static::lazy_static;
use log::{info, warn};
use serde_json::{Map, Value};
use std::collections::HashMap;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

lazy_static! {
    pub static ref running_functions: Mutex<HashMap<String, Child>> = Mutex::new(HashMap::new());
}

pub fn run_function(command: &Map<String, Value>) -> Result<u128, String> {
    let mut program = match command.get("program") {
        Some(Value::String(program)) => Some(program.to_string()),
        Some(_) | None => None,
    };
    let cwd = match command.get("cwd") {
        Some(Value::String(cwd)) => cwd,
        Some(_) | None => &WORK_DIR.to_string(),
    };
    let mut envs = HashMap::new();
    let mut args = match command.get("args") {
        Some(Value::Array(raw_args)) => {
            let mut args: Vec<String> = Vec::new();
            for arg in raw_args {
                if let Value::String(arg) = arg {
                    args.push(arg.clone());
                }
            }
            args
        }
        Some(_) | None => Vec::new(),
    };

    match command.get("template") {
        Some(Value::String(template)) => {
            if template == "python" {
                program = Some("python".to_string());
                envs.insert("PYTHONPATH".to_string(), WORK_DIR.to_string());
                args.insert(0, "__main__.py".to_string());
            } else {
                warn!("Unkown template: {}", template);
            }
        }
        Some(template) => {
            warn!("Unkown template: {}", template);
        }
        None => {}
    }

    let child = Command::new(match program {
        Some(program) => program,
        None => {
            return Err("Cannot find program to run".to_string());
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
        String::from("127.0.0.1:0"),
        |_stream, _reader, writer, _buf, args| {
            if args.len() >= 2 && args[0] == "run" {
                let json_str = match BASE64_STANDARD.decode(args[1].clone()) {
                    Ok(t) => t,
                    Err(e) => {
                        error_log_and_write(writer, e.to_string());
                        return;
                    }
                };
                let json_str = String::from_utf8_lossy(&json_str);
                match match serde_json::from_str(&json_str) {
                    Ok(command) => {
                        if let Value::Object(command) = command {
                            match run_function(&command) {
                                Ok(t) => Ok(t),
                                Err(e) => Err(e),
                            }
                        } else {
                            Err(format!("{} is not a json object", json_str))
                        }
                    }
                    Err(e) => Err(format!("Cannot parse {}: {}", json_str, e)),
                } {
                    Ok(_) => {
                        write_ok(writer);
                        info!("Run {json_str}");
                    }
                    Err(e) => {
                        error_log_and_write(writer, e);
                    }
                }
            }
        },
        |_stream| {
            remove_stopped_functions();
        },
    );
}
