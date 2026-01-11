use serde::Serialize;

pub type TaskId = usize;

///Task Control Block
#[derive(Debug, Default, Serialize)]
pub struct TCB {
    pub id: TaskId,
    pub name: String,
    pub progress: f64,
    pub current_work: String,
    pub parent: TaskId,
    pub children: Vec<TaskId>, //只是为了显示清晰, 对功能没有实际影响
}
