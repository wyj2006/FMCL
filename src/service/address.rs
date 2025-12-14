use super::{check_conntection, error_log_and_write, service_template, write_ok};
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use serde_json::{self, json};
use std::collections::HashMap;
use std::env;
use std::io::Write;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
use std::sync::Mutex;

lazy_static! {
    static ref registered_address: Mutex<HashMap<String, (String, String)>> =
        Mutex::new(HashMap::new());
}

pub fn register_address(name: &String, ip: &String, port: &String) {
    registered_address
        .lock()
        .unwrap()
        .insert(name.clone(), (ip.clone(), port.clone()));
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Register {
        name: String,
        ip: String,
        port: String,
    },
    Unregister {
        name: String,
    },
    Getall,
    Get {
        name: String,
    },
}

pub fn unregister_address(name: &String) {
    registered_address.lock().unwrap().remove(name);
}

///移除已经失去连接的address
pub fn remove_address_disconnected() {
    //用try_lock减少对正常服务的影响
    if let Ok(mut t) = registered_address.try_lock() {
        let mut disconnected = Vec::new();
        for (name, (_kind, port)) in t.iter() {
            //自己肯定没有失去连接
            if name == "address" {
                continue;
            }
            if !check_conntection(&SocketAddr::V4(SocketAddrV4::new(
                Ipv4Addr::new(127, 0, 0, 1),
                port.parse().unwrap(),
            ))) {
                disconnected.push(name.clone());
            }
        }
        for name in disconnected {
            t.remove(&name); //unregister_address(&name);
        }
    }
}

pub fn address_service() {
    service_template(
        "address".to_string(),
        String::from(format!(
            "127.0.0.1:{}",
            env::var("FMCL_ADDRESS_SERVER_PORT").unwrap_or("1024".to_string())
        )),
        |_stream, _reader, writer, _buf, args| {
            match ServiceCommand::try_parse_from({
                let mut t = vec!["address".to_string()];
                t.extend(args);
                t
            }) {
                Ok(ServiceCommand { sub_command }) => match sub_command {
                    SubCommand::Register { name, ip, port } => {
                        register_address(&name, &ip, &port);
                        write_ok(writer);
                    }
                    SubCommand::Unregister { name } => {
                        unregister_address(&name);
                        write_ok(writer);
                    }
                    SubCommand::Get { name } => {
                        let registered = registered_address.lock().unwrap();
                        if registered.contains_key(&name) {
                            writer
                                .write_all(
                                    json!({
                                        "name":name,
                                        "ip":registered[&name].0,
                                        "port":registered[&name].1
                                    })
                                    .to_string()
                                    .as_bytes(),
                                )
                                .unwrap();
                            writer.flush().unwrap();
                        } else {
                            error_log_and_write(writer, format!("{name} does not exists"));
                        }
                    }
                    SubCommand::Getall => {
                        let registered = registered_address.lock().unwrap();
                        let mut data = json!({});
                        for (key, value) in registered.iter() {
                            data[key] = json!({
                                "name":key,
                                "ip":value.0,
                                "port":value.1
                            });
                        }
                        writer.write_all(data.to_string().as_bytes()).unwrap();
                        writer.flush().unwrap();
                    }
                },
                Err(e) => error_log_and_write(writer, e.to_string()),
            };
        },
        |_stream| {
            remove_address_disconnected();
        },
    );
}
