use crate::error::Error;

use super::service_template;
use base64::prelude::*;
use clap::Parser;
use log::{debug, error, info, warn};
use serde_json::json;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
use std::thread::{self, Builder};

#[derive(Parser)]
struct ServiceCommand {
    level: String,
    thread_name: String,
    message: String,
}

pub fn logging(level: String, thread_name: String, message: String) {
    Builder::new()
        .name(thread_name)
        .spawn(move || match level.as_str() {
            "debug" => debug!("{}", message),
            "info" => info!("{}", message),
            "warning" => warn!("{}", message),
            "error" => error!("{}", message),
            "critical" => error!("{}", message),
            _ => {}
        })
        .unwrap();
}

pub fn logging_service() {
    service_template(
        "logging".to_string(),
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| match ServiceCommand::try_parse_from({
            let mut t = vec!["logging".to_string()];
            t.extend(args);
            t
        })? {
            command => match BASE64_STANDARD.decode(command.message) {
                Ok(message) => {
                    logging(
                        command.level,
                        format!(
                            "{}=>{}",
                            thread::current().name().unwrap(),
                            command.thread_name
                        ),
                        String::from_utf8_lossy(&message).to_string(),
                    );
                    Ok(Some(json!({})))
                }
                Err(e) => Err(Error::from(e)),
            },
        },
        |_stream| {},
    )
}
