use std::{fs, path::Path};

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

        let mut opt_path: Option<String> = None;

        for native_path in &self.native_paths {
            for result_entry in match fs::read_dir(native_path) {
                Ok(t) => t,
                Err(e) => return Err(e.to_string()),
            } {
                let entry = match result_entry {
                    Ok(t) => t,
                    Err(e) => return Err(e.to_string()),
                };
                if entry.file_name() == name {
                    opt_path = Some(String::from(entry.path().to_str().unwrap()));
                    break;
                }
            }
        }

        match opt_path {
            Some(path) => match self.find(name) {
                Some(child) => {
                    child.native_paths.push(path);
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
                        native_paths: vec![path],
                        children: vec![],
                    });
                    return Ok(());
                }
            },
            None => {
                return Err(format!("{}/{name} not found", self.path));
            }
        }
    }

    pub fn create(&mut self, fcb: FCB) -> Result<(), String> {
        if let Some(_) = self.find(&fcb.name) {
            return Err(format!("{} already exists", fcb.name));
        }
        self.children.push(fcb);
        Ok(())
    }
}
