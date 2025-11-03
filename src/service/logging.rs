use super::{error_log_and_write, service_template};
use base64::prelude::*;
use log::{debug, error, info, warn};
use std::thread::Builder;

pub fn logging(level: String, thread_name: String, message: String) {
    Builder::new()
        .name(thread_name)
        .spawn(move || match level.as_str() {
            "debug" => debug!("{}", message),
            "info" => info!("{}", message),
            "warn" => warn!("{}", message),
            "error" => error!("{}", message),
            "critical" => error!("{}", message),
            _ => {}
        })
        .unwrap();
}

pub fn logging_service() {
    service_template(
        "logging".to_string(),
        String::from("127.0.0.1:0"),
        |stream| format!("{}(logging)", stream.peer_addr().unwrap()),
        |_stream, _reader, writer, _buf, args| {
            if args.len() >= 2 {
                let message = match BASE64_STANDARD.decode(args[2].clone()) {
                    Ok(t) => t,
                    Err(e) => {
                        error_log_and_write(writer, e.to_string());
                        return;
                    }
                };
                logging(
                    args[0].clone(),
                    args[1].clone(),
                    String::from_utf8_lossy(&message).to_string(),
                );
            }
        },
        |_stream| {},
    )
}
