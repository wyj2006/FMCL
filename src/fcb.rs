use std::{fs, path::Path};

#[derive(Debug)]
pub struct FCB {
    pub name: String,
    pub path: String,
    pub native_paths: Vec<String>,
    pub children: Vec<FCB>,
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

    pub fn load(&mut self, name: &str) -> Result<(), String> {
        if let Some(_) = self.find(name) {
            return Ok(());
        }

        let mut paths = vec![];

        for native_path in &self.native_paths {
            for result_entry in match fs::read_dir(native_path) {
                Ok(t) => t,
                Err(_) => continue,
            } {
                let entry = match result_entry {
                    Ok(t) => t,
                    Err(_) => continue,
                };
                if entry.file_name() == name {
                    paths.push(entry.path().to_str().unwrap().to_string());
                }
            }
        }

        if paths.len() > 0 {
            match self.find(name) {
                Some(child) => {
                    for path in paths {
                        if !child.native_paths.contains(&path) {
                            child.native_paths.push(path);
                        }
                    }
                    return Ok(());
                }
                None => {
                    self.children.push(FCB {
                        name: String::from(name),
                        path: Path::new(&self.path)
                            .join(name)
                            .to_str()
                            .unwrap()
                            .to_string(),
                        native_paths: paths,
                        children: vec![],
                    });
                    return Ok(());
                }
            }
        } else {
            return Err(format!(
                "{} not found",
                Path::new(&self.path).join(name).to_str().unwrap()
            ));
        }
    }

    pub fn create(&mut self, fcb: FCB) -> Result<(), String> {
        if let Some(_) = self.find(&fcb.name) {
            return Err(format!("{} already exists", fcb.name));
        }
        self.children.push(fcb);
        Ok(())
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
