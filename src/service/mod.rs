pub mod address;
pub mod filesystem;
pub mod function;
pub mod logging;
pub mod setting;

pub use address::{address_service, register_address};
pub use filesystem::filesystem_service;
pub use function::function_service;
pub use logging::logging_service;
pub use setting::setting_service;

use crate::common::parse_command;
use log::{error, info};
use serde_json::json;
use std::io::Write;
use std::io::{self, BufRead, BufReader, BufWriter};
use std::marker::{Send, Sync};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::sync::Arc;
use std::thread::Builder;

pub fn error_log_and_write(writer: &mut BufWriter<&TcpStream>, e: String) {
    error!("{e}");
    writer
        .write_all(json!({"error_msg":e}).to_string().as_bytes())
        .unwrap();
    writer.flush().unwrap();
}

pub fn write_ok(writer: &mut BufWriter<&TcpStream>) {
    writer.write_all(json!({}).to_string().as_bytes()).unwrap();
    writer.flush().unwrap();
}

pub fn check_conntection(address: &SocketAddr) -> bool {
    if let Ok(_) = TcpStream::connect(address) {
        true
    } else {
        false
    }
}

pub fn service_template<T, E>(name: String, address: String, handler: T, on_disconnect: E)
where
    T: Fn(&TcpStream, &mut BufReader<&TcpStream>, &mut BufWriter<&TcpStream>, String, Vec<String>)
        + Send
        + Sync
        + 'static,
    E: Fn(&TcpStream) + Send + Sync + 'static,
{
    let listener = TcpListener::bind(&address).unwrap();
    let local_addr = listener.local_addr().unwrap();
    register_address(
        &name,
        &local_addr.ip().to_string(),
        &local_addr.port().to_string(),
    );
    info!("Listening on {}", local_addr);

    let handler = Arc::new(handler);
    let on_disconnect = Arc::new(on_disconnect);

    loop {
        let stream = if let Ok(t) = listener.accept() {
            t.0
        } else {
            continue;
        };

        let handler = Arc::clone(&handler);
        let on_disconnect = Arc::clone(&on_disconnect);

        let connection_id;
        {
            let mut reader = io::BufReader::new(&stream);
            let mut writer = io::BufWriter::new(&stream);

            let mut buf: Vec<u8> = vec![];
            let bytes_read = match reader.read_until(b'\0', &mut buf) {
                Ok(t) => t,
                Err(e) => {
                    error!("{e}");
                    continue;
                }
            };
            let buf = String::from_utf8_lossy(&buf);
            if bytes_read == 0 {
                continue;
            }
            connection_id = String::from(&buf[..buf.len() - 1]); //去除最后的\0
            write_ok(&mut writer);
        }

        Builder::new()
            .name(format!(
                "{}@{}({})",
                connection_id,
                stream.peer_addr().unwrap(),
                name
            ))
            .spawn(move || {
                let mut reader = io::BufReader::new(&stream);
                let mut writer = io::BufWriter::new(&stream);

                info!("Connected");

                loop {
                    let mut buf: Vec<u8> = vec![];
                    let bytes_read = match reader.read_until(b'\0', &mut buf) {
                        Ok(t) => t,
                        Err(e) => {
                            error!("{e}");
                            break;
                        }
                    };

                    let buf = String::from_utf8_lossy(&buf);
                    if bytes_read == 0 {
                        break;
                    }
                    let buf = String::from(&buf[..buf.len() - 1]); //去除最后的\0

                    let args = parse_command(&buf);
                    info!("Read: {buf:?} {args:?}");

                    handler(&stream, &mut reader, &mut writer, buf, args);
                }
                on_disconnect(&stream);
                info!("Disconnected");
            })
            .unwrap();
    }
}
