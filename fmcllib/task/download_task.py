import logging
import os
import time
import traceback
from random import uniform

import requests

from .common import ATTR_CURRENT_WORK, ATTR_PROGRESS, Task, modify_task


def download(url: str, path: str, parent_task_id=0, retry_times=16):
    # 即使任务创建失败也正常下载
    with Task("下载", parent_task_id) as task_id:
        for i in range(retry_times):
            try:
                modify_task(task_id, ATTR_CURRENT_WORK, f"下载 '{url}' 到 '{path}'")
                modify_task(task_id, ATTR_PROGRESS, 0)

                r = requests.get(url, stream=True, timeout=5)
                file_size = int(r.headers.get("Content-Length", 1))
                cur_size = 0

                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, mode="wb") as file:
                    for chunk in r.iter_content(chunk_size=1024):
                        file.write(chunk)
                        cur_size += len(chunk)
                        modify_task(task_id, ATTR_PROGRESS, cur_size / file_size)
                break
            except:
                if i == retry_times - 1:
                    raise
                logging.error(f"需要重新下载'{url}': \n{traceback.format_exc()}")
                modify_task(task_id, ATTR_CURRENT_WORK, f"等待重新下载")
                time.sleep(uniform(1, 2**i) / 1000)
