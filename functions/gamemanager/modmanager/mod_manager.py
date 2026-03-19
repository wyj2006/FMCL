import os
import subprocess
import sys
import traceback
import webbrowser

import qtawesome as qta
from PyQt6.QtCore import QEvent, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QListWidgetItem,
    QMessageBox,
    QWidget,
)
from qfluentwidgets import FluentIcon, SettingCard, TransparentToolButton

from fmcllib import show_qerrormessage
from fmcllib.game import Instance, Mod

from .ui_mod_info import Ui_ModInfo
from .ui_mod_manager import Ui_ModManager


class ModInfo(QDialog, Ui_ModInfo):
    def __init__(self, mod: Mod, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(mod.name)
        self.mod = mod

        self.icon_label.setPixmap(mod.icon.scaled(64, 64))
        self.name_label.setText(mod.name)
        self.description_label.setText(mod.description)
        self.version_label.setText(mod.version)
        self.path_label.setText(mod.path)

        for author in mod.authors:
            label = QLabel()
            label.setText(author)
            self.author_layout.addWidget(label)

        if not self.mod.url:
            self.url_button.hide()

        self.adjustSize()

    @pyqtSlot(bool)
    def on_ok_button_clicked(self, _):
        self.done(0)

    @pyqtSlot(bool)
    def on_url_button_clicked(self, _):
        webbrowser.open(self.mod.url)


class ModViewer(SettingCard):
    def __init__(self, mod: Mod):
        super().__init__(QIcon(mod.icon.scaled(32, 32)), mod.name, mod.description)
        self.setIconSize(32, 32)
        self.mod = mod
        self.setEnabled(not mod.is_disabled)

        self.open_folder_button = TransparentToolButton(FluentIcon.FOLDER.icon())
        self.open_folder_button.clicked.connect(self.open_folder)
        self.hBoxLayout.addWidget(self.open_folder_button)

        self.info_button = TransparentToolButton(FluentIcon.INFO.icon())
        self.info_button.clicked.connect(self.show_info)
        self.hBoxLayout.addWidget(self.info_button)

    def open_folder(self):
        try:
            if sys.platform.startswith("win"):
                subprocess.run(
                    ["start", "explorer", f"/select,{self.mod.path}"], shell=True
                )
            else:
                # TODO 跨平台(以及其它地方)
                raise Exception(self.tr("暂不支持该系统"))
        except:
            show_qerrormessage(self.tr("无法打开文件所在位置"), traceback.format_exc())

    def show_info(self):
        ModInfo(self.mod, self).exec()

    def enable(self):
        self.mod.enable()
        self.setEnabled(True)

    def disable(self):
        self.mod.disable()
        self.setEnabled(False)

    def delete(self):
        self.mod.delete()


class ModManager(QWidget, Ui_ModManager):
    def __init__(self, instance: Instance):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("mdi.puzzle-outline"))
        self.instance = instance

        if self.instance.support_mod:
            self.stackedWidget.setCurrentIndex(1)
            self.first_refreshed = False
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.first_refreshed = True

        self.search_input.searchSignal.connect(self.refresh)
        self.search_input.clearSignal.connect(self.refresh)
        self.search_input.editingFinished.connect(self.refresh)

        self.refresh_button.clicked.connect(self.refresh)

    def refresh(self):
        if not self.instance.support_mod:
            return
        self.mod_list.clear()
        mods_path = self.instance.mods_path
        if not os.path.exists(mods_path):
            return

        keyword = self.search_input.text()
        for name in os.listdir(mods_path):
            path = os.path.join(mods_path, name)
            if not Mod.is_mod(path):
                continue
            mod = Mod(path)
            if keyword not in mod.name or keyword not in os.path.basename(mod.path):
                continue
            viewer = ModViewer(mod)
            item = QListWidgetItem()
            item.setSizeHint(viewer.size())

            self.mod_list.addItem(item)
            self.mod_list.setItemWidget(item, viewer)

            self.update_statistics()
            QApplication.instance().processEvents()

    def event(self, a0):
        match a0.type():
            case QEvent.Type.Show if not self.first_refreshed:
                self.first_refreshed = True
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.refresh)
                self.timer.setSingleShot(True)
                self.timer.start()
        return super().event(a0)

    @pyqtSlot(bool)
    def on_enable_button_clicked(self, _):
        for item in self.mod_list.selectedItems():
            viewer: ModViewer = self.mod_list.itemWidget(item)
            viewer.enable()

    @pyqtSlot(bool)
    def on_disable_button_clicked(self, _):
        for item in self.mod_list.selectedItems():
            viewer: ModViewer = self.mod_list.itemWidget(item)
            viewer.disable()

    @pyqtSlot(bool)
    def on_del_button_clicked(self, _):
        if (
            QMessageBox.question(self, self.tr("删除"), self.tr("确认删除?"))
            != QMessageBox.StandardButton.Yes
        ):
            return
        for item in self.mod_list.selectedItems():
            viewer: ModViewer = self.mod_list.itemWidget(item)
            viewer.delete()
            self.mod_list.takeItem(self.mod_list.row(item))
        self.update_statistics()

    @pyqtSlot()
    def on_mod_list_itemSelectionChanged(self):
        self.update_statistics()

    def update_statistics(self):
        total = self.mod_list.count()
        selected = len(self.mod_list.selectedItems())
        if selected == 0:
            self.statistics.setText(f"{total}")
        else:
            self.statistics.setText(f"{selected}/{total}")
