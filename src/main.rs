mod common;
mod fcb;
mod service;
mod setting_item;
mod tcb;

use crate::common::WORK_DIR;
use crate::service::filesystem::get_or_create_fcb;
use crate::service::function::kill_all_functions;
use crate::setting_item::SettingItem;
use anstyle::{AnsiColor, Color, Effects, RgbColor, Style};
use chrono::Local;
use hotwatch::{EventKind, Hotwatch};
use log::{Level, error, info};
use serde_json::{Value, json};
use service::address::remove_address_disconnected;
use service::filesystem::{fcb_root, get_fcb};
use service::function::{remove_stopped_functions, run_function, running_functions};
use service::setting::save_settings;
use service::setting::{get_settingitem, setting_root};
use service::{
    address_service, filesystem_service, function_service, logging_service, setting_service,
    task_service,
};
use std::collections::hash_map::DefaultHasher;
use std::fs::{self, OpenOptions};
use std::hash::{Hash, Hasher};
use std::path::Path;
use std::process;
use std::thread;
use std::time::Duration;
use std::{panic, path};

pub fn default_level_style(level: Level) -> Style {
    match level {
        Level::Trace => AnsiColor::Cyan.on_default(),
        Level::Debug => AnsiColor::Blue.on_default(),
        Level::Info => AnsiColor::Green.on_default(),
        Level::Warn => AnsiColor::Yellow.on_default(),
        Level::Error => AnsiColor::Red.on_default().effects(Effects::BOLD),
    }
}

///根据/settings.json里的内容更新/.minecraft的本地路径
fn update_minecraft_mount() {
    match get_or_create_fcb(&mut fcb_root.lock().unwrap(), &("/.minecraft".to_string())) {
        Ok(t) => {
            let game_dirs = match get_settingitem(
                &mut setting_root.lock().unwrap(),
                &SettingItem::key_join(&vec![
                    &("/settings_json".to_string()),
                    &("game.dirs".to_string()),
                ]),
            ) {
                Ok(t) => {
                    if t.value.is_array() {
                        t.value.as_array().unwrap().clone()
                    } else {
                        vec![json!(".minecraft")]
                    }
                }
                Err(_) => vec![json!(".minecraft")],
            };
            let cur_dir_index: usize = match get_settingitem(
                &mut setting_root.lock().unwrap(),
                &SettingItem::key_join(&vec![
                    &("/settings_json".to_string()),
                    &("game.cur_dir_index".to_string()),
                ]),
            ) {
                Ok(t) => t.value.as_u64().unwrap_or(0) as usize,
                Err(_) => 0,
            };
            let game_dir = if let Some(t) = game_dirs.get(cur_dir_index) {
                if t.is_string() {
                    t.as_str().unwrap()
                } else {
                    ".minecraft"
                }
            } else {
                ".minecraft"
            };
            t.native_paths = vec![
                path::absolute(game_dir)
                    .unwrap()
                    .to_str()
                    .unwrap()
                    .to_string(),
            ];
        }
        Err(e) => {
            error!("Cannot update /.minecraft: {e}");
        }
    }
}

///更新所有游戏下的function.json
pub fn update_game_function() {
    let game_dirs = match get_settingitem(
        &mut setting_root.lock().unwrap(),
        &SettingItem::key_join(&vec![
            &("/settings_json".to_string()),
            &("game.dirs".to_string()),
        ]),
    ) {
        Ok(t) => {
            if t.value.is_array() {
                t.value.as_array().unwrap().clone()
            } else {
                vec![json!(".minecraft")]
            }
        }
        Err(_) => vec![json!(".minecraft")],
    };
    for game_dir in game_dirs {
        let Value::String(game_dir) = game_dir else {
            continue;
        };
        let versions_path = Path::new(&game_dir).join("versions");
        for game_path in match fs::read_dir(&versions_path) {
            Ok(t) => t,
            Err(e) => {
                error!("{e}");
                continue;
            }
        } {
            let Ok(game_path) = game_path else {
                continue;
            };
            let function_path = game_path.path().join("function.json");
            let game_path = match path::absolute(game_path.path()) {
                Ok(t) => t,
                Err(e) => {
                    error!("{e}");
                    continue;
                }
            };
            if let Err(e) = fs::write(
                function_path,
                json!({
                    "type":"game",
                    "display_name":game_path.file_name().unwrap().to_str().unwrap(),//TODO 根据游戏设置设置
                    "translation_context":"Game",
                    "icon":{
                        "type":"QIcon",
                        "value":":/image/grass@2x.png" //TODO 根据游戏设置设置
                    },
                    "command":{
                        "template":"function",
                        "program":"/functions/gamemonitor",
                        "args":["--game-path",game_path]
                    }
                })
                .to_string(),
            ) {
                error!("{e}");
            }
        }
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

    thread::Builder::new()
        .name("task".to_string())
        .spawn(task_service)
        .unwrap();

    match get_fcb(
        &mut fcb_root.lock().unwrap(),
        &("/functions/init".to_string()),
    ) {
        Ok(t) => {
            if let Err(e) = run_function(&t.native_paths[0], vec![]) {
                error!("Connot run init: {e}");
            }
        }
        Err(e) => {
            error!("Cannot run init: {e}");
        }
    };

    let _watcher = match Hotwatch::new() {
        Ok(mut t) => {
            if let Err(e) = t.watch(
                match get_fcb(
                    &mut fcb_root.lock().unwrap(),
                    &("/settings.json".to_string()),
                ) {
                    Ok(t) => t.native_paths[0].clone(),
                    Err(_) => Path::new(&WORK_DIR.to_string())
                        .join("settings.json")
                        .to_str()
                        .unwrap()
                        .to_string(),
                },
                |event| {
                    let EventKind::Modify(_) = event.kind else {
                        return;
                    };
                    //在/settings.json更改后更新/.minecraft对应的本地路径
                    update_minecraft_mount();
                    update_game_function();
                },
            ) {
                error!("Cannot watch /settings.json: {e}");
            }
            //防止watcher被drop
            Some(t)
        }
        Err(e) => {
            error!("Fail to create a watcher: {e}");
            None
        }
    };
    update_minecraft_mount();
    update_game_function();

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
