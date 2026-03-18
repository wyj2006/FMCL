import argparse
import subprocess
import traceback

from psutil import NoSuchProcess, Process
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QErrorMessage, QProgressDialog

parser = argparse.ArgumentParser()
parser.add_argument("pid", type=int)
parser.add_argument("path")

args = parser.parse_args()
pid: int = args.pid
path = args.path

app = QApplication([])

dialog = QProgressDialog()
dialog.setWindowTitle("重启")
dialog.setLabelText("等待原进程结束")
dialog.setRange(0, 2**31 - 1)
dialog.setValue(0)
dialog.setWindowModality(Qt.WindowModality.WindowModal)
dialog.canceled.connect(exit)

try:
    process = Process(pid)
    while process.is_running():
        dialog.setValue(dialog.value() + 1)
except NoSuchProcess:
    pass
except:
    w = QErrorMessage()
    w.resize(500, 309)
    w.setWindowTitle("无法保证原进程结束")
    w.showMessage(traceback.format_exc())
    w.exec()
    exit(1)

dialog.setValue(dialog.maximum())

try:
    # TODO 跨平台(包括其它地方)
    subprocess.run(["start", path], shell=True)
except:
    w = QErrorMessage()
    w.resize(500, 309)
    w.setWindowTitle("无法运行")
    w.showMessage(traceback.format_exc())
    w.exec()
