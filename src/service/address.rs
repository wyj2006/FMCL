use super::{check_conntection, error_log_and_write, running_services, service_template};
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

pub fn unregister_address(name: &String) {
    registered_address.lock().unwrap().remove(name);
}

///移除已经失去连接的address
pub fn remove_address_disconnected() {
    let mut disconnected = Vec::new();
    for (name, (_kind, port)) in registered_address.lock().unwrap().iter() {
        //正在运行的服务肯定没有失去连接
        if running_services.lock().unwrap().contains(name) {
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
        unregister_address(&name);
    }
}

pub fn address_service() {
    service_template(
        "address".to_string(),
        String::from(format!(
            "127.0.0.1:{}",
            env::var("FMCL_ADDRESS_SERVER_PORT").unwrap_or("1024".to_string())
        )),
        |stream| format!("{}(address)", stream.peer_addr().unwrap()),
        |_stream, _reader, writer, _buf, args| {
            if args.len() >= 4 && args[0] == "register" {
                register_address(&args[1], &args[2], &args[3]);
            } else if args.len() >= 2 && args[0] == "unregister" {
                unregister_address(&args[1]);
            } else if args.len() >= 1 && args[0] == "getall" {
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
            } else if args.len() >= 2 && args[0] == "get" {
                let registered = registered_address.lock().unwrap();
                let name = &args[1];
                if registered.contains_key(name) {
                    writer
                        .write_all(
                            json!({
                                "name":name,
                                "ip":registered[name].0,
                                "port":registered[name].1
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
        },
        |_stream| {
            remove_address_disconnected();
        },
    );
}
