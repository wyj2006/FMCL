use anyhow::{Result, anyhow};
use serde_json::{Map, Value};

use crate::{
    message::{SettingMessage, SettingMsgKind},
    service::notify::broadcast,
};

#[derive(Debug, Default)]
pub struct SettingItem {
    pub name: String,
    pub value: Value,
    pub key: String,
    pub children: Vec<SettingItem>,
    pub default_value: Value,
    pub attribute: Map<String, Value>,
}

impl SettingItem {
    pub fn key_join(args: &[&str]) -> String {
        return args
            .iter()
            .map(|x| {
                let x = x.strip_prefix(".").unwrap_or(x);
                x.strip_suffix(".").unwrap_or(x)
            })
            .filter(|x| x != &"")
            .collect::<Vec<_>>()
            .join(".");
    }

    pub fn find(&mut self, name: &str) -> Option<&mut SettingItem> {
        for child in self.children.iter_mut() {
            if child.name == name {
                return Some(child);
            }
        }
        None
    }

    pub fn create(&mut self, settingitem: SettingItem) -> Result<()> {
        if let Some(_) = self.find(&settingitem.name) {
            Err(anyhow!("'{}' already exists", settingitem.name))
        } else {
            broadcast(&SettingMessage {
                key: settingitem.key.clone(),
                kind: SettingMsgKind::Created,
            });
            self.children.push(settingitem);
            Ok(())
        }
    }
}
