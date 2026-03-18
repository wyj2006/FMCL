import os
import threading
import traceback
import webbrowser

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon
from result import Err
from ui_updater import Ui_Updater

from fmcllib import show_qerrormessage
from fmcllib.filesystem import fileinfo
from fmcllib.task import Task, download
from fmcllib.utils import LatestInfo, apply_update


class Updater(QWidget, Ui_Updater):
    errorOccurred = pyqtSignal(str)

    def __init__(self, latest: LatestInfo):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f'{self.tr("更新")}: {latest["tag_name"]}')
        self.setWindowIcon(FluentIcon.UPDATE.icon())
        self.latest = latest

        self.stackedWidget.setCurrentIndex(1)
        self.content.setText(latest["body"])

        self.errorOccurred.connect(
            lambda msg: show_qerrormessage(self.tr("无法更新"), msg, self)
        )

    @pyqtSlot(bool)
    def on_download_button_clicked(self, _):
        webbrowser.open(self.latest["assets"][0]["browser_download_url"])

    @pyqtSlot(bool)
    def on_update_button_clicked(self, _):
        self.update_button.setEnabled(False)
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        try:
            with Task(self.tr("更新")) as task_id:
                path = os.path.join(
                    fileinfo("/").unwrap()["native_paths"][0],
                    self.latest["assets"][0]["name"],
                )
                download(self.latest["assets"][0]["url"], path, task_id)
                match apply_update(path):
                    case Err(e):
                        self.errorOccurred.emit(e)
        except:
            self.errorOccurred.emit(traceback.format_exc())
        self.update_button.setEnabled(True)
