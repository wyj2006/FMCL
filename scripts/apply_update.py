import argparse
import os
import subprocess
import traceback

from psutil import Process
from PyQt6.QtWidgets import QApplication, QErrorMessage

parser = argparse.ArgumentParser()
parser.add_argument("pid", type=int)
parser.add_argument("old_version_path", help="旧版本路径")
parser.add_argument("new_version_path", help="新版本路径")

args = parser.parse_args()
pid: int = args.pid
old_version_path = args.old_version_path
new_version_path = args.new_version_path

app = QApplication([])
try:
    subprocess.run(["start", new_version_path], shell=True)
except:
    w = QErrorMessage()
    w.resize(500, 309)
    w.setWindowTitle("无法更新")
    w.showMessage(traceback.format_exc())
    w.exec()
    exit(1)

try:
    process = Process(pid)
    # 等待原先进程退出
    while process.is_running():
        pass
    os.remove(old_version_path)
except:
    pass
