use super::service_template;
use crate::message::NotifyMessage;
use anyhow::{Result, anyhow};
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::{debug, error, info};
use serde_json::json;
use std::{
    collections::HashSet,
    net::{Ipv4Addr, SocketAddr, SocketAddrV4, ToSocketAddrs, UdpSocket},
    sync::Mutex,
};

lazy_static! {
    //与 registered_address不同的是, 这里的地址都是用udp协议连接的
    static ref subscribed_names: Mutex<HashSet< SocketAddr>> = Mutex::new(HashSet::new());
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Subscribe { address: String },
}

pub fn broadcast(message: &dyn NotifyMessage) {
    let data = match message.to_data() {
        Ok(t) => t,
        Err(_) => return,
    };
    debug!("Broadcast {data}");
    for address in subscribed_names.lock().unwrap().iter() {
        let Err(e) = (|| -> Result<()> {
            let stream = UdpSocket::bind("0.0.0.0:0")?;
            stream.send_to(data.as_bytes(), address)?;
            Ok(())
        })() else {
            continue;
        };
        error!("Error occurred when broadcasting: {e}");
    }
}

pub fn notify_service() {
    service_template(
        "notify".to_string(),
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| match ServiceCommand::try_parse_from({
            let mut t = vec!["notify".to_string()];
            t.extend(args);
            t
        })? {
            ServiceCommand { sub_command } => match sub_command {
                SubCommand::Subscribe { address } => {
                    info!("Subscribe '{address}'");
                    subscribed_names.lock().unwrap().insert(
                        address
                            .to_socket_addrs()?
                            .next()
                            .ok_or(anyhow!(format!("invalid address: {address}")))?,
                    );
                    Ok(Some(json!({})))
                }
            },
        },
        |_stream| {},
    )
}
