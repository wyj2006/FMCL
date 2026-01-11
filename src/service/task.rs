use super::service_template;
use crate::error::Error;
use crate::tcb::{TCB, TaskId};
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::info;
use serde_json::json;
use std::collections::HashMap;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
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
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| {
            let mut tasks = running_tasks.lock().unwrap();
            match ServiceCommand::try_parse_from({
                let mut t = vec!["task".to_string()];
                t.extend(args);
                t
            })? {
                ServiceCommand { sub_command } => match sub_command {
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
                        info!("Create task {task_id}");
                        *task_id += 1;
                        Ok(Some(json! ({
                            "id":*task_id-1
                        })))
                    }
                    SubCommand::Get { id } => {
                        if let Some(tcb) = tasks.get(&id) {
                            Ok(Some(json!(tcb)))
                        } else {
                            Err(Error::TaskNotExists(id))
                        }
                    }
                    SubCommand::Getall => {
                        let mut data = json!({});
                        for (key, value) in tasks.iter() {
                            data[key.to_string()] = json!(value);
                        }
                        Ok(Some(data))
                    }
                    SubCommand::Remove { id } => {
                        if let Some(tcb) = tasks.remove(&id) {
                            info!("Remove task {id}");
                            if let Some(parent) = tasks.get_mut(&tcb.parent) {
                                if let Some(index) =
                                    parent.children.iter().position(|x| *x == tcb.id)
                                {
                                    parent.children.remove(index);
                                }
                            }
                            Ok(Some(json!({})))
                        } else {
                            Err(Error::TaskNotExists(id))
                        }
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
                            Ok(Some(json!({})))
                        } else {
                            Err(Error::TaskNotExists(id))
                        }
                    }
                },
            }
        },
        |_stream| {},
    );
}
