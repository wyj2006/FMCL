import argparse
import os
import subprocess
import time
import traceback

from PyQt6.QtWidgets import QApplication, QErrorMessage

parser = argparse.ArgumentParser()
parser.add_argument("old_version_path", help="旧版本路径")
parser.add_argument("new_version_path", help="新版本路径")

args = parser.parse_args()
old_version_path = args.old_version_path
new_version_path = args.new_version_path

app = QApplication([])
try:
    subprocess.run(
        [new_version_path],
        creationflags=subprocess.DETACHED_PROCESS,
        start_new_session=True,
    )
except:
    w = QErrorMessage()
    w.resize(500, 309)
    w.setWindowTitle("无法更新")
    w.showMessage(traceback.format_exc())
    w.exec()
    exit(1)

for i in range(16):
    try:
        # 原进程可能尚未结束
        os.remove(old_version_path)
        break
    except:
        time.sleep(0.1)
