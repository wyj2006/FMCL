use crate::tcb::TaskId;
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

#[derive(Serialize)]
pub struct TaskMessage {
    pub id: TaskId,
    pub kind: TaskMsgKind,
}

#[derive(Serialize)]
pub enum TaskMsgKind {
    Created,
    Removed,
}

#[derive(Serialize)]
pub struct FunctionMessage {
    pub path: String,
    pub kind: FunctionMsgKind,
}

#[derive(Serialize)]
pub enum FunctionMsgKind {
    Started,
    Stopped,
}

#[derive(Serialize)]
pub struct AddressMessage {
    pub name: String,
    pub kind: AddressMsgKind,
}

#[derive(Serialize)]
pub enum AddressMsgKind {
    Registered,
    Unregistered,
}
