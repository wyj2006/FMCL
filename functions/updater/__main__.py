import argparse
import sys
import threading

import __main__
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from qfluentwidgets import FluentIcon
from result import Err, Ok
from updater import Updater

import resources as _
from fmcllib import show_qerrormessage
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.utils import LatestInfo, check_update
from fmcllib.window import Window

translate = QCoreApplication.translate

parser = argparse.ArgumentParser()
parser.add_argument(
    "--quiet",
    help=translate("Updater", "如果已是最新版本或正在检查更新, 则不弹出提示窗口"),
    action="store_true",
)

args = parser.parse_args()
quiet = args.quiet

app = Application(sys.argv)
app.setWindowIcon(FluentIcon.UPDATE.icon())

info: LatestInfo
check_error = None


def check_latest() -> LatestInfo:
    global check_error
    match check_update():
        case Ok(t):
            setattr(__main__, "info", t)
        case Err(e):
            check_error = e


dialog = None
if not quiet:
    dialog = QProgressDialog()
    dialog.setWindowTitle(translate("Updater", "更新"))
    dialog.setLabelText(translate("Updater", "正在检查更新"))
    dialog.setRange(0, 2**31 - 1)
    dialog.setValue(0)
    dialog.setWindowModality(Qt.WindowModality.WindowModal)
    dialog.canceled.connect(exit)

threading.Thread(target=check_latest, daemon=True).start()

while not hasattr(__main__, "info") and check_error == None:
    if dialog != None:
        dialog.setValue(dialog.value() + 1)

if dialog != None:
    dialog.setValue(dialog.maximum())

if check_error != None:
    if not quiet:
        show_qerrormessage(translate("Updater", "检查更新失败"), str(check_error))
    exit(1)

if info == None:
    if not quiet:
        QMessageBox.information(
            None, translate("Updater", "更新"), translate("Updater", "已是最新版")
        )
    exit(0)

updater = Updater(info)
updater.installEventFilter(
    WindowSource(
        updater,
        on_detach=lambda w: Window(w).show(),
    )
)

window = Window(updater)
window.show()

sys.exit(app.exec())
