use super::address::{register_address, unregister_address};
use super::{check_conntection, error_log_and_write, service_template};
use lazy_static::lazy_static;
use serde_json::{self, json};
use std::collections::HashMap;
use std::io::Write;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
use std::sync::Mutex;

lazy_static! {
    static ref registered_mirror: Mutex<HashMap<String, (String, String)>> =
        Mutex::new(HashMap::new());
}

pub fn register_mirror(name: &String, kind: &String, port: &String) {
    registered_mirror
        .lock()
        .unwrap()
        .insert(name.clone(), (kind.clone(), port.clone()));
    register_address(
        &format!("mirror{name}{kind}{port}"),
        &"127.0.0.1".to_string(),
        &port,
    );
}

pub fn unregister_mirror(name: &String) {
    if let Some((kind, port)) = registered_mirror.lock().unwrap().remove(name) {
        unregister_address(&format!("mirror{name}{kind}{port}"));
    }
}

///移除已经失去连接的mirror
pub fn remove_mirror_disconnected() {
    let mut disconnected = Vec::new();
    for (name, (_kind, port)) in registered_mirror.lock().unwrap().iter() {
        if !check_conntection(&SocketAddr::V4(SocketAddrV4::new(
            Ipv4Addr::new(127, 0, 0, 1),
            port.parse().unwrap(),
        ))) {
            disconnected.push(name.clone());
        }
    }
    for name in disconnected {
        unregister_mirror(&name);
    }
}

pub fn mirror_service() {
    service_template(
        "mirror".to_string(),
        String::from("127.0.0.1:0"),
        |stream| format!("{}(mirror)", stream.peer_addr().unwrap()),
        |_stream, _reader, writer, _buf, args| {
            if args.len() >= 4 && args[0] == "register" {
                register_mirror(&args[1], &args[2], &args[3]);
            } else if args.len() >= 2 && args[0] == "unregister" {
                unregister_mirror(&args[1]);
            } else if args.len() >= 1 && args[0] == "getall" {
                let mut data = json!({});
                for (key, value) in registered_mirror.lock().unwrap().iter() {
                    data[key] = json!({
                        "kind":value.0,
                        "port":value.1
                    });
                }
                writer.write_all(data.to_string().as_bytes()).unwrap();
                writer.flush().unwrap();
            } else if args.len() >= 2 && args[0] == "get" {
                let registered = registered_mirror.lock().unwrap();
                let name = &args[1];
                if registered.contains_key(name) {
                    writer
                        .write_all(
                            json!({
                                "kind":registered[name].0,
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
            remove_mirror_disconnected();
        },
    );
}
