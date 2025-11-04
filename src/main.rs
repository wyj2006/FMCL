mod common;
mod fcb;
mod service;
mod setting_item;

use crate::common::WORK_DIR;
use crate::service::function::kill_all_functions;
use anstyle::{AnsiColor, Color, Effects, RgbColor, Style};
use chrono::Local;
use log::{Level, error, info};
use serde_json::json;
use service::address::remove_address_disconnected;
use service::filesystem::{fcb_root, get_fcb};
use service::function::{remove_stopped_functions, run_function, running_functions};
use service::setting::save_settings;
use service::{
    address_service, filesystem_service, function_service, logging_service, setting_service,
};
use std::collections::hash_map::DefaultHasher;
use std::fs::OpenOptions;
use std::hash::{Hash, Hasher};
use std::panic;
use std::process;
use std::thread;
use std::time::Duration;

pub fn default_level_style(level: Level) -> Style {
    match level {
        Level::Trace => AnsiColor::Cyan.on_default(),
        Level::Debug => AnsiColor::Blue.on_default(),
        Level::Info => AnsiColor::Green.on_default(),
        Level::Warn => AnsiColor::Yellow.on_default(),
        Level::Error => AnsiColor::Red.on_default().effects(Effects::BOLD),
    }
}

fn main() {
    ctrlc::set_handler(move || {
        info!("User interrupted");
        //没有正在运行的功能会自动退出
        kill_all_functions();
    })
    .unwrap_or_else(|e| error!("Error setting Ctrl-C handler: {e}"));

    panic::set_hook(Box::new(|panic_info| {
        error!("{panic_info}");
        kill_all_functions();
        process::exit(1);
    }));

    fern::Dispatch::new()
        .chain(
            fern::Dispatch::new()
                .level(log::LevelFilter::Debug)
                .chain(std::io::stdout())
                .format(|out, message, record| {
                    let level_style = default_level_style(record.level());

                    let threadname = thread::current().name().unwrap_or("???").to_string();
                    let mut hasher = DefaultHasher::new();
                    threadname.hash(&mut hasher);
                    let hashval = hasher.finish() % (0xffffff - 0xb4b4b4) + 0xb4b4b4; //转换成浅色的rgb
                    let threadname_style = Style::new().fg_color(Some(Color::Rgb(RgbColor(
                        ((hashval >> 16) & 0xff) as u8,
                        ((hashval >> 8) & 0xff) as u8,
                        (hashval & 0xff) as u8,
                    ))));

                    out.finish(format_args!(
                        "[{}] [{level_style}{}{level_style:#}][{threadname_style}{}{threadname_style:#}]: {}",
                        Local::now().format("%Y-%m-%d %H:%M:%S"),
                        record.level(),
                        threadname,
                        message
                    ))
                }),
        )
        .chain(
            fern::Dispatch::new()
                .level(log::LevelFilter::Info)
                .chain(
                    OpenOptions::new()
                        .write(true)
                        .create(true)
                        .truncate(true)
                        .open(WORK_DIR.to_string() + "/latest.log")
                        .unwrap(),
                )
                .format(|out, message, record| {
                    out.finish(format_args!(
                        "[{}] [{}][{}]: {}",
                        Local::now().format("%Y-%m-%d %H:%M:%S"),
                        record.level(),
                        thread::current().name().unwrap_or("???").to_string(),
                        message
                    ))
                }),
        )
        .apply()
        .unwrap_or_else(|e| error!("Error setup logger: {e}"));

    thread::Builder::new()
        .name("file system".to_string())
        .spawn(filesystem_service)
        .unwrap();

    thread::Builder::new()
        .name("function".to_string())
        .spawn(function_service)
        .unwrap();

    thread::Builder::new()
        .name("logging".to_string())
        .spawn(logging_service)
        .unwrap();

    thread::Builder::new()
        .name("setting".to_string())
        .spawn(setting_service)
        .unwrap();

    thread::Builder::new()
        .name("address".to_string())
        .spawn(address_service)
        .unwrap();

    {
        match get_fcb(
            &mut fcb_root.lock().unwrap(),
            &("/functions/init".to_string()),
        ) {
            Ok(t) => {
                if let Err(e) = run_function(
                    json!({
                        "template":"python",
                        "cwd":t.native_paths[0],
                    })
                    .as_object()
                    .unwrap(),
                ) {
                    error!("Connot run init: {e}");
                }
            }
            Err(e) => {
                error!("Cannot run init: {e}");
            }
        };
    }

    loop {
        thread::sleep(Duration::from_secs(1));
        remove_address_disconnected(); //定期检测或者在断开与服务的连接时检查
        remove_stopped_functions();
        let mut could_quit = false;
        if let Ok(mutex) = running_functions.try_lock() {
            could_quit = mutex.len() == 0;
        }
        if could_quit {
            break;
        }
    }
    save_settings();
}
