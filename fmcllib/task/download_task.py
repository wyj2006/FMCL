import os

import requests
from result import Err, Ok, Result, is_err

from .common import create_task, modify_task, remove_task


def download(url: str, path: str) -> Result[None, str]:
    if is_err(task_id := create_task("Download")):
        return Err(task_id.err_value)
    task_id = task_id.ok_value
    modify_task(task_id, "current_work", f"Download '{url}' to '{path}'")
    modify_task(task_id, "progress", 0)

    r = requests.get(url, stream=True)
    file_size = int(r.headers.get("Content-Length"))
    cur_size = 0

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode="wb") as file:
        for chunk in r.iter_content(chunk_size=1024):
            file.write(chunk)
            cur_size += len(chunk)
            modify_task(task_id, "progress", cur_size / file_size)

    remove_task(task_id)
    Ok(None)
