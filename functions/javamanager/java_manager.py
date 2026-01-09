import json
import os
import traceback

import qtawesome as qta
from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import QApplication, QFileDialog, QSizePolicy, QSpacerItem, QWidget
from qfluentwidgets import FluentIcon, SettingCard, TransparentToolButton
from ui_java_manager import Ui_JavaManager

from fmcllib import show_qerrormessage
from fmcllib.java import JavaInfo, auto_find_java, get_java_info
from fmcllib.window import Window


class JavaViewer(SettingCard):
    def __init__(self, java_info: JavaInfo, parent=None):
        super().__init__(
            qta.icon("fa6b.java"),
            java_info["version"],
            java_info["path"],
            parent,
        )
        self.setIconSize(32, 32)
        self.java_info = java_info

        self.copy_path = TransparentToolButton()
        self.copy_path.setIcon(FluentIcon.COPY.icon())
        self.copy_path.setToolTip(self.tr("复制路径"))
        self.copy_path.clicked.connect(self.copyPath)
        self.hBoxLayout.addWidget(self.copy_path)

    def copyPath(self):
        QApplication.clipboard().setText(self.java_info["path"])
        self.copy_path.setIcon(FluentIcon.ACCEPT.icon())
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(
            lambda: self.copy_path.setIcon(FluentIcon.COPY.icon())
        )
        self.timer.start(3000)


class JavaManager(QWidget, Ui_JavaManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("fa6b.java"))
        self.java_infos = {}

        self.refresh_button = TransparentToolButton()
        self.refresh_button.setIcon(FluentIcon.SYNC.icon())
        self.refresh_button.setToolTip(self.tr("刷新"))
        self.refresh_button.clicked.connect(self.refresh)

        self.add_button = TransparentToolButton()
        self.add_button.setIcon(FluentIcon.ADD.icon())
        self.add_button.setToolTip(self.tr("添加"))
        self.add_button.clicked.connect(self.addJava)

        self.refresh()

    def refresh(self):
        self.load()

        while self.java_layout.count() > 0:
            item = self.java_layout.takeAt(0)
            if item.widget() != None:
                item.widget().deleteLater()

        for java_info in auto_find_java():
            self.java_infos[java_info["path"]] = java_info

        for java_info in self.java_infos.values():
            viewer = JavaViewer(java_info)
            self.java_layout.addWidget(viewer)

        self.java_layout.addSpacerItem(
            QSpacerItem(
                0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
        )

    def load(self):
        if os.path.exists("java_info.json"):
            self.java_infos |= json.load(open("java_info.json", encoding="utf-8"))

    def save(self):
        json.dump(
            self.java_infos,
            open("java_info.json", mode="w", encoding="utf-8"),
            indent=4,
        )

    def addJava(self):
        java_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("选择Java"), filter="Java (java.exe)"
        )
        if not java_path:
            return
        try:
            java_info = get_java_info(java_path)
            self.java_infos[java_info["path"]] = java_info
            self.save()
            self.refresh()
        except:
            show_qerrormessage(self.tr("无法添加Java"), traceback.format_exc(), self)

    def event(self, a0: QEvent):
        match a0.type():
            case QEvent.Type.Show:
                window = self.window()
                if not isinstance(window, Window):
                    return super().event(a0)
                self.refresh_button.setFixedHeight(window.titleBar.height())
                self.refresh_button.setFixedWidth(window.titleBar.closeBtn.width())
                window.titleBar.hBoxLayout.insertWidget(
                    1, self.refresh_button, 0, Qt.AlignmentFlag.AlignRight
                )

                self.add_button.setFixedSize(self.refresh_button.size())
                window.titleBar.hBoxLayout.insertWidget(
                    1, self.add_button, 0, Qt.AlignmentFlag.AlignRight
                )
        return super().event(a0)
