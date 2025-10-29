use serde_json::{Map, Value};

#[derive(Debug)]
pub struct SettingItem {
    pub name: String,
    pub value: Value,
    pub children: Vec<SettingItem>,
    pub default_value: Value,
    pub attribute: Map<String, Value>,
}

impl Default for SettingItem {
    fn default() -> Self {
        SettingItem {
            name: String::new(),
            value: Value::Null,
            children: Vec::new(),
            default_value: Value::Null,
            attribute: Map::new(),
        }
    }
}

impl SettingItem {
    pub fn key_join(args: &Vec<&String>) -> String {
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

    pub fn create(&mut self, settingitem: SettingItem) -> Result<(), String> {
        if let Some(_) = self.find(&settingitem.name) {
            return Err(format!("{} already exists", settingitem.name));
        }
        self.children.push(settingitem);
        Ok(())
    }
}
