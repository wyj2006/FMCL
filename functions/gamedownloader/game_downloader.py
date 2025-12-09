import threading

from original_selector import OriginalSelector
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import FluentIcon
from ui_game_downloader import Ui_GameDownloader

from fmcllib.game import download_install_original, download_original


class GameDownloader(QWidget, Ui_GameDownloader):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.DOWNLOAD.icon())

        self.original_selector = None

    @pyqtSlot(bool)
    def on_select_original_toggled(self, checked: bool):
        if checked:
            if self.original_selector == None:
                self.original_selector = OriginalSelector()
                self.original_selector.versionSelected.connect(
                    lambda version: self.select_original.setText(
                        self.tr("原版") + f":{version}"
                    )
                )
                self.original_selector.versionSelected.connect(self.autoSetInstanceName)
            self.pivot.addItem(
                "original",
                self.tr("原版"),
                lambda: self.selector_stack.setCurrentWidget(self.original_selector),
            )
            self.selector_stack.addWidget(self.original_selector)
            self.selector_stack.setCurrentWidget(self.original_selector)
        else:
            self.select_original.setText(self.tr("原版"))
            self.selector_stack.removeWidget(self.original_selector)
            self.pivot.removeWidget("original")
            self.autoSetInstanceName()

    @pyqtSlot(int)
    def on_selector_stack_currentChanged(self, _):
        if self.selector_stack.currentWidget() == None:
            return
        self.pivot.setCurrentItem(
            {self.original_selector: "original"}[self.selector_stack.currentWidget()]
        )

    @property
    def auto_instance_name(self):
        a = []
        if self.selector_stack.indexOf(self.original_selector) != -1:
            a.append(self.original_selector.select_version_info["id"])
        return "-".join(a)

    def autoSetInstanceName(self):
        if self.auto_set_instance_name.isChecked():
            self.instance_name.setText(self.auto_instance_name)

    @pyqtSlot(bool)
    def on_download_button_clicked(self, _):
        if self.selector_stack.indexOf(self.original_selector) != -1:
            name = self.instance_name.text()
            path = QFileDialog.getExistingDirectory(self)
            url = self.original_selector.select_version_info["url"]
            threading.Thread(
                target=download_original, args=(name, path, url), daemon=True
            ).start()

    @pyqtSlot(bool)
    def on_download_install_button_clicked(self, _):
        if self.selector_stack.indexOf(self.original_selector) != -1:
            name = self.instance_name.text()
            url = self.original_selector.select_version_info["url"]
            threading.Thread(
                target=download_install_original, args=(name, url), daemon=True
            ).start()
