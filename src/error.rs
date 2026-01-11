use crate::tcb::TaskId;
use base64::DecodeError;
use std::{fmt::Display, io};

#[derive(Debug)]
pub enum Error {
    SettingItemExists(String),
    FileNotFound(String),
    FileExists(String),
    // name
    AddressNotExists(String),
    // address
    InvalidAddress(String),
    // template, key
    TemplateKeyMissing(String, String),
    InvalidArgs(String),
    InvalidExtArgs(String),
    ProgramNotFound,
    // key, file path
    InvalidKey(String, String),
    InvalidFile(String),
    //name, key
    SettingNotExists(String, String),
    TaskNotExists(TaskId),
    ClapError(clap::error::Error),
    IOError(io::Error),
    JsonError(serde_json::Error),
    B64DecodeError(DecodeError),
}

impl Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Error::AddressNotExists(address) => format!("Address '{address}' does not exist"),
                Error::InvalidAddress(address) => format!("Invalid address: {address}"),
                Error::FileExists(path) => format!("'{path}' already exists"),
                Error::FileNotFound(path) => format!("'{path}' not found"),
                Error::InvalidArgs(args) => format!("Invalid args: {args}"),
                Error::InvalidExtArgs(args) => format!("Invalid external args: {args}"),
                Error::InvalidFile(path) => format!("Invalid '{path}'"),
                Error::InvalidKey(key, path) => format!("Invalid '{key}' in '{path}'"),
                Error::ProgramNotFound => format!("Program not found"),
                Error::SettingItemExists(name) => format!("'{name}' already exists"),
                Error::SettingNotExists(name, key) => format!("'{name}' in '{key}' does not exist"),
                Error::TaskNotExists(id) => format!("{id} does not exist"),
                Error::TemplateKeyMissing(template, key) =>
                    format!("Missing '{key}' for template '{template}'"),
                Error::ClapError(e) => e.to_string(),
                Error::IOError(e) => e.to_string(),
                Error::JsonError(e) => e.to_string(),
                Error::B64DecodeError(e) => e.to_string(),
            }
        )
    }
}

macro_rules! wrap_impl {
    ($from:ty, $to:expr) => {
        impl From<$from> for Error {
            fn from(value: $from) -> Self {
                $to(value)
            }
        }
    };
}

wrap_impl!(clap::error::Error, Error::ClapError);
wrap_impl!(io::Error, Error::IOError);
wrap_impl!(serde_json::Error, Error::JsonError);
wrap_impl!(DecodeError, Error::B64DecodeError);
