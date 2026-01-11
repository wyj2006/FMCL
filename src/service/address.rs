use crate::error::Error;

use super::{check_conntection, service_template};
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::info;
use serde_json::{self, json};
use std::collections::HashMap;
use std::env;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4, ToSocketAddrs};
use std::sync::Mutex;

lazy_static! {
    static ref registered_address: Mutex<HashMap<String, SocketAddr>> = Mutex::new(HashMap::new());
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Register { name: String, address: String },
    Unregister { name: String },
    Getall,
    Get { name: String },
}

pub fn register_address(name: &String, address: SocketAddr) {
    registered_address
        .lock()
        .unwrap()
        .insert(name.clone(), address);
}

pub fn unregister_address(name: &String) {
    registered_address.lock().unwrap().remove(name);
}

///移除已经失去连接的address
pub fn remove_address_disconnected() {
    //用try_lock减少对正常服务的影响
    if let Ok(mut t) = registered_address.try_lock() {
        t.retain(|name, address| {
            //自己肯定没有失去连接
            if name == "address" {
                true
            } else {
                check_conntection(address)
            }
        });
    }
}

pub fn address_service() {
    service_template(
        "address".to_string(),
        SocketAddr::V4(SocketAddrV4::new(
            Ipv4Addr::new(127, 0, 0, 1),
            env::var("FMCL_ADDRESS_SERVER_PORT")
                .unwrap_or("1024".to_string())
                .parse()
                .unwrap(),
        )),
        |_stream, _reader, _writer, _buf, args| match ServiceCommand::try_parse_from({
            let mut t = vec!["address".to_string()];
            t.extend(args);
            t
        })? {
            ServiceCommand { sub_command } => match sub_command {
                SubCommand::Register { name, address } => {
                    info!("Register '{address}' as '{name}'");
                    register_address(
                        &name,
                        address
                            .to_socket_addrs()?
                            .next()
                            .ok_or(Error::InvalidAddress(address))?,
                    );
                    Ok(Some(json!({})))
                }
                SubCommand::Unregister { name } => {
                    unregister_address(&name);
                    Ok(Some(json!({})))
                }
                SubCommand::Get { name } => {
                    let registered = registered_address.lock().unwrap();
                    if registered.contains_key(&name) {
                        Ok(Some(json!({
                            "name":name,
                            "address":registered[&name],
                        })))
                    } else {
                        Err(Error::AddressNotExists(name))
                    }
                }
                SubCommand::Getall => {
                    let registered = registered_address.lock().unwrap();
                    let mut data = json!({});
                    for (key, value) in registered.iter() {
                        data[key] = json!({
                            "name":key,
                            "address":value,
                        });
                    }
                    Ok(Some(data))
                }
            },
        },
        |_stream| {
            remove_address_disconnected();
        },
    );
}
