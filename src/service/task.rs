use super::{error_log_and_write, service_template, write_ok};
use crate::tcb::{TCB, TaskId};
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use serde_json::json;
use std::collections::HashMap;
use std::io::Write;
use std::sync::Mutex;

lazy_static! {
    pub static ref running_tasks: Mutex<HashMap<TaskId, TCB>> = Mutex::new(HashMap::new());
    static ref next_task_id: Mutex<TaskId> = Mutex::new(1);
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Create {
        name: String,
        parent_id: TaskId,
    },
    Remove {
        id: TaskId,
    },
    Modify {
        id: TaskId,
        #[command(subcommand)]
        attribute: Attribute,
    },
    Getall,
    Get {
        id: TaskId,
    },
}

#[derive(Subcommand)]
enum Attribute {
    Name { value: String },
    Progress { value: f64 },
    CurrentWork { value: String },
}

pub fn task_service() {
    service_template(
        "task".to_string(),
        String::from("127.0.0.1:0"),
        |_stream, _reader, writer, _buf, args| {
            let mut tasks = running_tasks.lock().unwrap();
            match ServiceCommand::try_parse_from({
                let mut t = vec!["task".to_string()];
                t.extend(args);
                t
            }) {
                Ok(ServiceCommand { sub_command }) => match sub_command {
                    SubCommand::Create { name, parent_id } => {
                        let mut task_id = next_task_id.lock().unwrap();
                        tasks.insert(
                            *task_id,
                            TCB {
                                id: *task_id,
                                name,
                                parent: parent_id,
                                ..TCB::default()
                            },
                        );
                        if let Some(t) = tasks.get_mut(&parent_id) {
                            t.children.push(*task_id);
                        }
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
                    }
                    SubCommand::Get { id } => {
                        if let Some(tcb) = tasks.get(&id) {
                            writer
                                .write_all(tcb.to_json().to_string().as_bytes())
                                .unwrap();
                            writer.flush().unwrap();
                        } else {
                            error_log_and_write(writer, format!("Task {id} does not exists"));
                        }
                    }
                    SubCommand::Getall => {
                        let mut data = json!({});
                        for (key, value) in tasks.iter() {
                            data[key.to_string()] = value.to_json();
                        }
                        writer.write_all(data.to_string().as_bytes()).unwrap();
                        writer.flush().unwrap();
                    }
                    SubCommand::Remove { id } => {
                        if let Some(tcb) = tasks.remove(&id) {
                            if let Some(parent) = tasks.get_mut(&tcb.parent) {
                                if let Some(index) =
                                    parent.children.iter().position(|x| *x == tcb.id)
                                {
                                    parent.children.remove(index);
                                }
                            }
                        } else {
                            error_log_and_write(writer, format!("Task {id} does not exists"));
                            return;
                        }
                        write_ok(writer);
                    }
                    SubCommand::Modify {
                        id,
                        attribute: sub_command,
                    } => {
                        if let Some(tcb) = tasks.get_mut(&id) {
                            match sub_command {
                                Attribute::Name { value } => tcb.name = value,
                                Attribute::Progress { value } => tcb.progress = value,
                                Attribute::CurrentWork { value } => tcb.current_work = value,
                            }
                        } else {
                            error_log_and_write(writer, format!("Task {id} does not exists"));
                            return;
                        }
                        write_ok(writer);
                    }
                },
                Err(e) => error_log_and_write(writer, e.to_string()),
            };
        },
        |_stream| {},
    );
}
