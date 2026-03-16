use crate::error::Error;
use std::{
    collections::BTreeSet,
    path::{Path, PathBuf},
};

#[derive(Debug, Hash, PartialEq, Eq, Clone, PartialOrd, Ord)]
pub struct VPath(pub Vec<String>);

impl VPath {
    pub fn join<T>(&self, path: T) -> VPath
    where
        VPath: From<T>,
    {
        let mut buf = self.0.clone();
        buf.extend(VPath::from(path).0);
        VPath(buf)
    }
}

impl ToString for VPath {
    fn to_string(&self) -> String {
        format!("/{}", self.0.join("/"))
    }
}

impl From<&str> for VPath {
    fn from(path: &str) -> VPath {
        let mut buf = vec![];
        for name in path.replace("\\", "/").split("/") {
            if name == "" {
                continue;
            }
            buf.push(name.to_string());
        }
        VPath(buf)
    }
}

impl From<&String> for VPath {
    fn from(value: &String) -> Self {
        VPath::from(value.as_str())
    }
}

#[derive(Debug)]
pub struct FCB {
    pub name: String,
    pub path: VPath,
    pub native_paths: BTreeSet<PathBuf>,
    pub children: Vec<FCB>,
    pub mount_paths: BTreeSet<VPath>,
}

impl FCB {
    pub fn find(&mut self, name: &str) -> Option<&mut FCB> {
        for child in self.children.iter_mut() {
            if child.name == name {
                return Some(child);
            }
        }
        None
    }

    pub fn create(&mut self, fcb: FCB) -> Result<(), Error> {
        if let Some(_) = self.find(&fcb.name) {
            Err(Error::FileExists(fcb.name))
        } else {
            self.children.push(fcb);
            Ok(())
        }
    }

    /// 移除所有native_path存在的child
    /// native_path存在的child可以重新加载, 但native_path不存在的child就不一定了
    pub fn unload_all(&mut self) {
        self.children.retain_mut(|child| {
            child
                .native_paths
                .retain(|native_path| !Path::new(native_path).exists());
            child.native_paths.len() > 0
        });
        //因为child的native_path变了, 所以它也需要unload
        for child in &mut self.children {
            child.unload_all();
        }
    }
}
