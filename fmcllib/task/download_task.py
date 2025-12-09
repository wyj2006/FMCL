import logging
import os
import time
import traceback
from random import uniform

import requests

from .common import create_task, modify_task, remove_task


def download(url: str, path: str, parent_task_id=0, retry_times=16):
    for i in range(retry_times):
        try:
            # 即使任务创建失败也正常下载
            task_id = create_task("下载", parent_task_id).unwrap_or(0)
            modify_task(task_id, "current_work", f"下载 '{url}' 到 '{path}'")
            modify_task(task_id, "progress", 0)

            r = requests.get(url, stream=True, timeout=5)
            file_size = int(r.headers.get("Content-Length", 1))
            cur_size = 0

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, mode="wb") as file:
                for chunk in r.iter_content(chunk_size=1024):
                    file.write(chunk)
                    cur_size += len(chunk)
                    modify_task(task_id, "progress", cur_size / file_size)

            remove_task(task_id)
            break
        except:
            logging.error(f"重新下载'{url}': \n{traceback.format_exc()}")
            time.sleep(uniform(1, 2**i))
