use serde_json::{Value, json};

pub type TaskId = usize;

///Task Control Block
#[derive(Debug, Default)]
pub struct TCB {
    pub id: TaskId,
    pub name: String,
    pub progress: f64,
    pub current_work: String,
    pub parent: TaskId,
    pub children: Vec<TaskId>, //只是为了显示清晰, 对功能没有实际影响
}

impl TCB {
    pub fn to_json(&self) -> Value {
        json!({
            "id":self.id,
            "name":self.name,
            "progress":self.progress,
            "current_work":self.current_work,
            "parent":self.parent,
            "children":self.children
        })
    }
}
