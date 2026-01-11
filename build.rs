use std::process::Command;

fn main() {
    if cfg!(not(debug_assertions)) {
        Command::new("python")
            .arg("scripts/compress.py")
            .spawn()
            .unwrap();
        if cfg!(windows) {
            let mut res = winres::WindowsResource::new();
            res.set_icon("resources/icon/fmcl.ico");
            res.compile().unwrap();
        }
    }
}
