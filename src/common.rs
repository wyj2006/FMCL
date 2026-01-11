use std::env;
use std::path::Path;
use std::sync::LazyLock;

pub static WORK_DIR: LazyLock<String> = LazyLock::new(|| {
    if cfg!(debug_assertions) {
        String::from(
            env::current_exe()
                .unwrap()
                .parent()
                .unwrap()
                .parent()
                .unwrap()
                .parent()
                .unwrap()
                .to_str()
                .unwrap(),
        )
    } else {
        Path::new(env::current_exe().unwrap().to_str().unwrap())
            .parent()
            .unwrap()
            .join("FMCL")
            .to_str()
            .unwrap()
            .to_string()
    }
});

pub fn parse_command(command: &String) -> Vec<String> {
    enum ParseState {
        START,
        WHITESPACE,
        ARG,
        STRING,
        ESCAPE,
    }

    let mut args = Vec::new();
    let mut arg = String::new();
    let mut state = ParseState::START;

    for c in command.chars() {
        match state {
            ParseState::START => {
                if c.is_whitespace() {
                    state = ParseState::WHITESPACE;
                } else if c == '"' {
                    state = ParseState::STRING;
                } else {
                    state = ParseState::ARG;
                    arg.push(c);
                }
            }
            ParseState::WHITESPACE => {
                if !c.is_whitespace() {
                    state = ParseState::START;
                    arg.push(c);
                }
            }
            ParseState::ARG => {
                if c.is_whitespace() {
                    args.push(arg);
                    arg = String::new();
                    state = ParseState::START;
                } else if c == '"' {
                    state = ParseState::STRING;
                } else {
                    arg.push(c);
                }
            }
            ParseState::STRING => {
                if c == '\\' {
                    state = ParseState::ESCAPE;
                } else if c == '"' {
                    state = ParseState::ARG;
                } else {
                    arg.push(c);
                }
            }
            ParseState::ESCAPE => {
                match c {
                    '"' => arg.push('"'),
                    _ => {
                        arg.push('\\');
                        arg.push(c);
                    }
                }
                state = ParseState::STRING;
            }
        }
    }

    if arg.len() != 0 {
        args.push(arg);
    }

    args
}
