use super::{error_log_and_write, service_template, write_ok};
use crate::setting_item::SettingItem;
use base64::prelude::*;
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::error;
use serde_json::{self, Map, Value, json};
use std::collections::VecDeque;
use std::default::Default;
use std::fs;
use std::io::Write;
use std::path::Path;
use std::sync::Mutex;

lazy_static! {
    pub static ref setting_root: Mutex<SettingItem> = Mutex::new(SettingItem {
        name: "root".to_string(),
        ..Default::default()
    });
}

#[derive(Parser)]
struct ServiceCommand {
    #[command(subcommand)]
    sub_command: SubCommand,
}

#[derive(Subcommand)]
enum SubCommand {
    Get {
        key: String,
    },
    ListChildren {
        key: String,
    },
    AddOrUpdate {
        key: String,
        value: String,
    },
    AddOrUpdateDefault {
        key: String,
        value: String,
    },
    AddOrUpdateAttr {
        key: String,
        attr_name: String,
        value: String,
    },
    GenerateJson {
        key: String,
    },
}

pub fn get_settingitem<'a, 'b>(
    parent: &'a mut SettingItem,
    key: &'b String,
) -> Result<&'a mut SettingItem, String> {
    let mut cur = parent;
    for name in key.split(".") {
        if name == "" {
            continue;
        }
        match cur.find(name) {
            Some(t) => cur = t,
            None => return Err(format!("{name} in {key} doesn't exist")),
        }
    }
    Ok(cur)
}

pub fn get_or_create_settingitem<'a, 'b>(
    parent: &'a mut SettingItem,
    key: &'b String,
) -> Result<&'a mut SettingItem, String> {
    let mut cur = parent;
    for name in key.split(".") {
        if name == "" {
            continue;
        }
        if let None = cur.find(name) {
            if let Err(e) = cur.create(SettingItem {
                name: name.to_string(),
                ..Default::default()
            }) {
                return Err(e);
            }
        }
        cur = cur.find(name).unwrap();
    }
    Ok(cur)
}

pub fn list_children(parent: &mut SettingItem, key: &String) -> Result<Vec<String>, String> {
    match get_settingitem(parent, key) {
        Ok(t) => {
            let mut names: Vec<String> = vec![];
            //实际的子项
            for child in &t.children {
                names.push(child.name.clone());
            }
            Ok(names)
        }
        Err(e) => Err(e),
    }
}

pub fn add_or_update_default_setting(
    parent: &mut SettingItem,
    key: &String,
    value: &Value,
) -> Result<(), String> {
    match get_or_create_settingitem(parent, key) {
        Ok(t) => {
            if t.value == t.default_value {
                //此时的值和默认值相同, 认为该设置项并没有更改
                //所以同步这两个值
                t.value = value.clone();
                t.default_value = value.clone();
            } else {
                t.default_value = value.clone();
            }
            Ok(())
        }
        Err(e) => Err(e),
    }
}

pub fn add_or_update_setting(
    parent: &mut SettingItem,
    key: &String,
    value: &Value,
) -> Result<(), String> {
    match get_or_create_settingitem(parent, key) {
        Ok(t) => {
            t.value = value.clone();
            Ok(())
        }
        Err(e) => Err(e),
    }
}

pub fn add_or_update_attr(
    parent: &mut SettingItem,
    key: &String,
    attr_name: &String,
    attr: &Value,
) -> Result<(), String> {
    match get_or_create_settingitem(parent, key) {
        Ok(t) => {
            let v = t.attribute.get_mut(key);
            match (v, attr) {
                //对于字典和数组进行合并, 其它的进行覆盖
                (Some(Value::Object(x)), Value::Object(y)) => {
                    x.extend(y.clone().into_iter());
                }
                (Some(Value::Array(x)), Value::Array(y)) => {
                    x.extend(y.clone().into_iter());
                }
                _ => {
                    t.attribute.insert(attr_name.clone(), attr.clone());
                }
            }
            Ok(())
        }
        Err(e) => Err(e),
    }
}

///获得相对parent的路径为key的子孙节点(grandchild)的子节点组成的json value
pub fn generate_setting_json(parent: &mut SettingItem, key: &String) -> Result<Value, String> {
    let mut result = Map::new();
    let key_prefix = key; //grandchild相对于parent的路径

    let mut queue = VecDeque::new(); //队列里的key都是相对于grandchild的
    for name in list_children(parent, key)? {
        queue.push_back(name);
    }

    while let Some(key) = queue.pop_front() {
        let to_parent_key = SettingItem::key_join(&vec![&key_prefix, &key]); //相对于parent的路径
        let setting_item = get_settingitem(parent, &to_parent_key)?;

        if setting_item.default_value != setting_item.value && setting_item.value != Value::Null {
            result.insert(key.clone(), setting_item.value.clone());
        }

        for name in list_children(parent, &to_parent_key)? {
            queue.push_back(SettingItem::key_join(&vec![&key, &name]));
        }
    }

    Ok(Value::Object(result))
}

pub fn save_settings() {
    let root: &mut SettingItem = &mut setting_root.lock().unwrap();
    for child in root.children.iter_mut() {
        let json_value = generate_setting_json(child, &String::new()).unwrap();
        let save_path = match &child.value {
            Value::String(x) => x,
            _ => {
                error!("No save path specified for {}", child.name);
                continue;
            }
        };
        if let Some(parent_path) = Path::new(save_path).parent() {
            if let Err(e) = fs::create_dir_all(parent_path) {
                error!("Cannot create parent dirs for '{save_path}': {e}");
                continue;
            }
        }
        if let Err(e) = fs::write(
            save_path,
            serde_json::to_string_pretty(&json_value).unwrap_or(json_value.to_string()),
        ) {
            error!("Cannot save settings to '{save_path}': {e}");
            continue;
        }
    }
}

pub fn setting_service() {
    service_template(
        "setting".to_string(),
        String::from("127.0.0.1:0"),
        |_stream, _reader, writer, _buf, args| {
            let parent: &mut SettingItem = &mut setting_root.lock().unwrap();
            match ServiceCommand::try_parse_from({
                let mut t = vec!["setting".to_string()];
                t.extend(args);
                t
            }) {
                Ok(ServiceCommand { sub_command }) => match sub_command {
                    SubCommand::Get { key } => match get_settingitem(parent, &key) {
                        Ok(t) => {
                            writer
                                .write_all(
                                    json!({
                                        "name":t.name,
                                        "value":t.value,
                                        "default_value":t.default_value,
                                        "attribute":Value::Object(t.attribute.clone())
                                    })
                                    .to_string()
                                    .as_bytes(),
                                )
                                .unwrap();
                            writer.flush().unwrap();
                        }
                        Err(e) => {
                            error_log_and_write(writer, e);
                        }
                    },
                    SubCommand::ListChildren { key } => match list_children(parent, &key) {
                        Ok(t) => {
                            writer
                                .write_all(
                                    json!({
                                        "names":t
                                    })
                                    .to_string()
                                    .as_bytes(),
                                )
                                .unwrap();
                            writer.flush().unwrap();
                        }
                        Err(e) => {
                            error_log_and_write(writer, e);
                        }
                    },
                    SubCommand::AddOrUpdateDefault { key, value } => {
                        let json_str = match BASE64_STANDARD.decode(value) {
                            Ok(t) => t,
                            Err(e) => {
                                error_log_and_write(writer, e.to_string());
                                return;
                            }
                        };
                        let value: Value =
                            match serde_json::from_str(&String::from_utf8_lossy(&json_str)) {
                                Ok(t) => t,
                                Err(e) => {
                                    error_log_and_write(writer, e.to_string());
                                    return;
                                }
                            };
                        if let Err(e) = add_or_update_default_setting(parent, &key, &value) {
                            error_log_and_write(writer, e);
                        } else {
                            write_ok(writer);
                        }
                    }
                    SubCommand::AddOrUpdate { key, value } => {
                        let json_str = match BASE64_STANDARD.decode(value) {
                            Ok(t) => t,
                            Err(e) => {
                                error_log_and_write(writer, e.to_string());
                                return;
                            }
                        };
                        let value: Value =
                            match serde_json::from_str(&String::from_utf8_lossy(&json_str)) {
                                Ok(t) => t,
                                Err(e) => {
                                    error_log_and_write(writer, e.to_string());
                                    return;
                                }
                            };
                        if let Err(e) = add_or_update_setting(parent, &key, &value) {
                            error_log_and_write(writer, e);
                        } else {
                            write_ok(writer);
                        }
                    }
                    SubCommand::AddOrUpdateAttr {
                        key,
                        attr_name,
                        value,
                    } => {
                        let json_str = match BASE64_STANDARD.decode(value) {
                            Ok(t) => t,
                            Err(e) => {
                                error_log_and_write(writer, e.to_string());
                                return;
                            }
                        };
                        let value: Value =
                            match serde_json::from_str(&String::from_utf8_lossy(&json_str)) {
                                Ok(t) => t,
                                Err(e) => {
                                    error_log_and_write(writer, e.to_string());
                                    return;
                                }
                            };
                        if let Err(e) = add_or_update_attr(parent, &key, &attr_name, &value) {
                            error_log_and_write(writer, e);
                        } else {
                            write_ok(writer);
                        }
                    }
                    SubCommand::GenerateJson { key } => match generate_setting_json(parent, &key) {
                        Ok(t) => {
                            writer.write_all(t.to_string().as_bytes()).unwrap();
                            writer.flush().unwrap();
                        }
                        Err(e) => {
                            error_log_and_write(writer, e);
                        }
                    },
                },
                Err(e) => error_log_and_write(writer, e.to_string()),
            };
        },
        |_stream| {},
    );
}
