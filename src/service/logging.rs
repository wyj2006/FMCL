use super::service_template;
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
        |_stream, _reader, _writer, buf, args| {
            if args.len() >= 2 {
                let prefix_length = args[0].len() + args[1].len() + 1;
                logging(
                    args[0].clone(),
                    args[1].clone(),
                    buf[prefix_length + 1..].to_string(),
                );
            }
        },
        |_stream| {},
    )
}
