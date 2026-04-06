use anyhow::Result;
use serde::Serialize;
use serde_json::to_string;

pub trait NotifyMessage {
    fn to_data(&self) -> Result<String>;
}

impl<T> NotifyMessage for T
where
    T: Serialize,
{
    fn to_data(&self) -> Result<String> {
        Ok(to_string(self)?)
    }
}

#[derive(Serialize)]
pub struct SettingMessage {
    pub key: String,
    pub kind: SettingMsgKind,
}

#[derive(Serialize)]
pub enum SettingMsgKind {
    ValueChanged,
    AttrChanged,
    DefaultValueChanged,
    Created,
}
