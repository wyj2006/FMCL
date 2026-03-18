use super::service_template;
use crate::{
    force_quit,
    service::filesystem::{fcb_root, get_fcb},
};
use clap::{Parser, Subcommand};
use log::info;
use semver::{Version, VersionReq};
use serde::{Deserialize, Serialize};
use serde_json::{json, to_value};
use std::{
    env::{self, consts::EXE_EXTENSION},
    net::{Ipv4Addr, SocketAddr, SocketAddrV4},
    process::Command,
};
use ureq::{Agent, tls::TlsConfig};

#[derive(Deserialize, Serialize)]
pub struct AssetInfo {
    pub url: String,
    pub name: String,
    pub browser_download_url: String,
}

#[derive(Deserialize, Serialize)]
pub struct LatestInfo {
    pub tag_name: String,
    pub assets: Vec<AssetInfo>,
    pub body: String,
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    CheckUpdate,
    ApplyUpdate { new_version_path: String },
}

pub fn utils_service() {
    service_template(
        "utils".to_string(),
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| match ServiceCommand::try_parse_from({
            let mut t = vec!["utils".to_string()];
            t.extend(args);
            t
        })? {
            ServiceCommand { sub_command } => match sub_command {
                SubCommand::CheckUpdate => {
                    let agent: Agent = Agent::config_builder()
                        //TODO 不禁止验证
                        .tls_config(TlsConfig::builder().disable_verification(true).build())
                        .build()
                        .into();
                    let mut response = agent
                        .get("https://api.github.com/repos/wyj2006/FMCL/releases/latest")
                        .call()?;

                    let mut info: LatestInfo = response.body_mut().read_json::<LatestInfo>()?;

                    if VersionReq::parse(&format!("{}", info.tag_name))?
                        .matches(&Version::parse(env!("CARGO_PKG_VERSION"))?)
                    {
                        info.assets.retain(|x| x.name.ends_with(EXE_EXTENSION));
                        Ok(Some(to_value(info)?))
                    } else {
                        Ok(Some(json!(null)))
                    }
                }
                SubCommand::ApplyUpdate { new_version_path } => {
                    info!("Apply update: {new_version_path}");
                    match get_fcb(&mut fcb_root.lock().unwrap(), "/scripts/apply_update.py") {
                        Ok(t) => {
                            Command::new("python")
                                .arg(t.native_paths.first().unwrap().to_str().unwrap())
                                .arg(env::current_exe()?.to_str().unwrap())
                                .arg(new_version_path)
                                .spawn()
                                .unwrap();
                            *force_quit.write().unwrap() = true;
                            Ok(Some(json!({})))
                        }
                        Err(e) => Err(e.into()),
                    }
                }
            },
        },
        |_stream| {},
    );
}
