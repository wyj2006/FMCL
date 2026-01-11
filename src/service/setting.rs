use super::service_template;
use crate::error::Error;
use crate::setting_item::SettingItem;
use base64::prelude::*;
use clap::{Parser, Subcommand};
use lazy_static::lazy_static;
use log::error;
use serde_json::{self, Map, Value, json};
use std::collections::VecDeque;
use std::default::Default;
use std::fs;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
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
) -> Result<&'a mut SettingItem, Error> {
    let mut cur = parent;
    for name in key.split(".") {
        if name == "" {
            continue;
        }
        match cur.find(name) {
            Some(t) => cur = t,
            None => return Err(Error::SettingNotExists(name.to_string(), key.to_string())),
        }
    }
    Ok(cur)
}

pub fn get_or_create_settingitem<'a, 'b>(
    parent: &'a mut SettingItem,
    key: &'b String,
) -> Result<&'a mut SettingItem, Error> {
    let mut cur = parent;
    for name in key.split(".") {
        if name == "" {
            continue;
        }
        if let None = cur.find(name) {
            cur.create(SettingItem {
                name: name.to_string(),
                ..Default::default()
            })?;
        }
        cur = cur.find(name).unwrap();
    }
    Ok(cur)
}

pub fn list_children(parent: &mut SettingItem, key: &String) -> Result<Vec<String>, Error> {
    let t = get_settingitem(parent, key)?;
    let mut names: Vec<String> = vec![];
    //实际的子项
    for child in &t.children {
        names.push(child.name.clone());
    }
    Ok(names)
}

pub fn add_or_update_default_setting(
    parent: &mut SettingItem,
    key: &String,
    value: &Value,
) -> Result<(), Error> {
    let t = get_or_create_settingitem(parent, key)?;
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

pub fn add_or_update_setting(
    parent: &mut SettingItem,
    key: &String,
    value: &Value,
) -> Result<(), Error> {
    get_or_create_settingitem(parent, key)?.value = value.clone();
    Ok(())
}

pub fn add_or_update_attr(
    parent: &mut SettingItem,
    key: &String,
    attr_name: &String,
    attr: &Value,
) -> Result<(), Error> {
    let t = get_or_create_settingitem(parent, key)?;
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

///获得相对parent的路径为key的子孙节点(grandchild)的子节点组成的json value
pub fn generate_setting_json(parent: &mut SettingItem, key: &String) -> Result<Value, Error> {
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
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0)),
        |_stream, _reader, _writer, _buf, args| {
            let parent: &mut SettingItem = &mut setting_root.lock().unwrap();
            match ServiceCommand::try_parse_from({
                let mut t = vec!["setting".to_string()];
                t.extend(args);
                t
            })? {
                ServiceCommand { sub_command } => match sub_command {
                    SubCommand::Get { key } => {
                        let t = get_settingitem(parent, &key)?;
                        Ok(Some(json!({
                            "name":t.name,
                            "value":t.value,
                            "default_value":t.default_value,
                            "attribute":Value::Object(t.attribute.clone())
                        })))
                    }
                    SubCommand::ListChildren { key } => {
                        let t = list_children(parent, &key)?;
                        Ok(Some(json!({
                            "names":t
                        })))
                    }
                    SubCommand::AddOrUpdateDefault { key, value } => {
                        let value: Value = serde_json::from_str(&String::from_utf8_lossy(
                            &BASE64_STANDARD.decode(value)?,
                        ))?;
                        add_or_update_default_setting(parent, &key, &value)?;
                        Ok(Some(json!({})))
                    }
                    SubCommand::AddOrUpdate { key, value } => {
                        let value: Value = serde_json::from_str(&String::from_utf8_lossy(
                            &BASE64_STANDARD.decode(value)?,
                        ))?;
                        add_or_update_setting(parent, &key, &value)?;
                        Ok(Some(json!({})))
                    }
                    SubCommand::AddOrUpdateAttr {
                        key,
                        attr_name,
                        value,
                    } => {
                        let value: Value = serde_json::from_str(&String::from_utf8_lossy(
                            &BASE64_STANDARD.decode(value)?,
                        ))?;
                        add_or_update_attr(parent, &key, &attr_name, &value)?;
                        Ok(Some(json!({})))
                    }
                    SubCommand::GenerateJson { key } => {
                        let t = generate_setting_json(parent, &key)?;
                        Ok(Some(t))
                    }
                },
            }
        },
        |_stream| {},
    );
}
