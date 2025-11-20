use super::{error_log_and_write, service_template, write_ok};
use crate::tcb::{TCB, TaskId};
use lazy_static::lazy_static;
use serde_json::json;
use std::collections::HashMap;
use std::io::Write;
use std::sync::Mutex;

lazy_static! {
    pub static ref running_tasks: Mutex<HashMap<TaskId, TCB>> = Mutex::new(HashMap::new());
    static ref next_task_id: Mutex<TaskId> = Mutex::new(1);
}

pub fn task_service() {
    service_template(
        "task".to_string(),
        String::from("127.0.0.1:0"),
        |_stream, _reader, writer, _buf, args| {
            let mut tasks = running_tasks.lock().unwrap();
            if args.len() >= 3 && args[0] == "create" {
                let mut task_id = next_task_id.lock().unwrap();
                let parent_id;
                //非负数
                match args[2].parse::<TaskId>() {
                    Ok(t) => {
                        parent_id = t;
                    }
                    Err(e) => {
                        error_log_and_write(writer, e.to_string());
                        return;
                    }
                }
                tasks.insert(
                    *task_id,
                    TCB {
                        id: *task_id,
                        name: args[1].clone(),
                        parent: parent_id,
                        ..TCB::default()
                    },
                );
                writer
                    .write_all(
                        json! ({
                            "id":*task_id
                        })
                        .to_string()
                        .as_bytes(),
                    )
                    .unwrap();
                writer.flush().unwrap();
                *task_id += 1;
            } else if args.len() >= 2 && args[0] == "remove" {
                let id = match args[1].parse::<TaskId>() {
                    Ok(t) => t,
                    Err(e) => {
                        error_log_and_write(writer, e.to_string());
                        return;
                    }
                };
                if let Some(tcb) = tasks.remove(&id) {
                    if let Some(parent) = tasks.get_mut(&tcb.parent) {
                        parent.children.remove(tcb.id);
                    }
                } else {
                    error_log_and_write(writer, format!("Task {id} does not exists"));
                    return;
                }
                write_ok(writer);
            } else if args.len() >= 4 && args[0] == "modify" {
                let id = match args[1].parse::<TaskId>() {
                    Ok(t) => t,
                    Err(e) => {
                        error_log_and_write(writer, e.to_string());
                        return;
                    }
                };
                if let Some(tcb) = tasks.get_mut(&id) {
                    match args[2].as_str() {
                        "name" => tcb.name = args[3].clone(),
                        "progress" => {
                            tcb.progress = match args[3].parse() {
                                Ok(t) => t,
                                Err(e) => {
                                    error_log_and_write(writer, e.to_string());
                                    return;
                                }
                            }
                        }
                        "current_work" => tcb.current_work = args[3].clone(),
                        _ => {
                            error_log_and_write(writer, format!("Unknown attribute {}", args[2]));
                            return;
                        }
                    }
                } else {
                    error_log_and_write(writer, format!("Task {id} does not exists"));
                    return;
                }
                write_ok(writer);
            } else if args.len() >= 1 && args[0] == "getall" {
                let mut data = json!({});
                for (key, value) in tasks.iter() {
                    data[key.to_string()] = value.to_json();
                }
                writer.write_all(data.to_string().as_bytes()).unwrap();
                writer.flush().unwrap();
            } else if args.len() >= 2 && args[0] == "get" {
                let id = match args[1].parse::<TaskId>() {
                    Ok(t) => t,
                    Err(e) => {
                        error_log_and_write(writer, e.to_string());
                        return;
                    }
                };
                if let Some(tcb) = tasks.get(&id) {
                    writer
                        .write_all(tcb.to_json().to_string().as_bytes())
                        .unwrap();
                    writer.flush().unwrap();
                } else {
                    error_log_and_write(writer, format!("Task {id} does not exists"));
                }
            }
        },
        |_stream| {},
    );
}
