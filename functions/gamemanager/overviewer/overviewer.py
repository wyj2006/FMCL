import os
import subprocess
import time
import traceback

from PyQt6.QtWidgets import QApplication, QInputDialog, QTableWidgetItem, QWidget
from qfluentwidgets import FluentIcon, PushButton, SettingCard

from fmcllib import show_qerrormessage
from fmcllib.function import Function
from fmcllib.game import Instance

from .icon_selector import IconSelector
from .ui_overviewer import Ui_Overviewer


class InfoViewer(SettingCard):
    def __init__(self, instance: Instance, parent=None):
        super().__init__(instance.icon, instance.name, "", parent)
        self.setIconSize(32, 32)
        self.hBoxLayout.setContentsMargins(16, 0, 16, 0)

        self.instance = instance

        self.rename_button = PushButton(self.tr("重命名"))
        self.rename_button.clicked.connect(self.rename)
        self.hBoxLayout.addWidget(self.rename_button)

        self.icon_button = PushButton(self.tr("更改图标"))
        self.icon_button.clicked.connect(self.changeIcon)
        self.hBoxLayout.addWidget(self.icon_button)

        tr_version = {
            "original": self.tr("原版"),
            "fabric": self.tr("Fabric"),
            "forge": self.tr("Forge"),
        }
        self.setContent(
            ", ".join(
                [
                    f"{tr_version[key]}: {val}"
                    for key, val in self.instance.version.items()
                    if val
                ]
            )
        )

    def changeIcon(self):
        selector = IconSelector(self.instance.icon_path, self)
        if selector.exec():
            self.instance.icon_path = selector.icon_path

    def rename(self):
        name, ok = QInputDialog.getText(
            self, self.tr("输入"), self.tr("新名称"), text=self.instance.name
        )
        if not ok:
            return
        try:
            new_instance = self.instance.rename(name)
        except:
            show_qerrormessage(self.tr("无法重命名"), traceback.format_exc(), self)
            return
        Function.quick_run(
            "/functions/gamemanager", "--instance-path", new_instance.path
        )
        QApplication.quit()


class Overviewer(QWidget, Ui_Overviewer):
    def __init__(self, instance: Instance):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.LAYOUT.icon())

        self.instance = instance
        self.info_viewer = InfoViewer(self.instance)
        self.verticalLayout.insertWidget(0, self.info_viewer)

        self.browser.setTitle(self.tr("浏览"))
        for name, path in (
            (self.tr("游戏文件夹"), self.instance.path),
            (self.tr("设置文件"), self.instance.setting_path),
            (self.tr("游戏时长记录文件"), self.instance.time_record_path),
            (
                (self.tr("模组文件夹"), self.instance.mods_path)
                if self.instance.support_mod and os.path.exists(self.instance.mods_path)
                else ("", "")
            ),
        ):
            if not name:
                continue
            open_button = PushButton(self.tr("打开"))
            open_button.clicked.connect(
                lambda _, path=path: subprocess.run(
                    ["start", "explorer", f"/select,{path}"], shell=True
                )
            )
            self.browser.addGroup(
                FluentIcon.FOLDER.icon(),
                name,
                path,
                open_button,
            )

        records = instance.time_records
        self.time_record_view.setRowCount(len(records))

        total_time = 0
        for i, v in enumerate(records):
            item = QTableWidgetItem()
            item.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v["start"])))
            self.time_record_view.setItem(i, 0, item)

            item = QTableWidgetItem()
            item.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v["end"])))
            self.time_record_view.setItem(i, 1, item)

            item = QTableWidgetItem()
            total_time += v["end"] - v["start"]
            item.setText(
                self.tr("{day}天{hour}小时{minute}分{second}秒").format(
                    **self.splitTime(int(v["end"] - v["start"]))
                )
            )
            self.time_record_view.setItem(i, 2, item)

        self.time_record_view.resizeColumnsToContents()

        total_time = int(total_time)
        self.time_summary.setText(
            self.tr(
                "一共运行了{count}次, 总时长: {day}天{hour}小时{minute}分{second}秒"
            ).format(count=i + 1, **self.splitTime(total_time))
        )

    def splitTime(self, time: float | int) -> dict:
        return dict(
            day=time // (24 * 60 * 60),
            hour=time % (24 * 60 * 60) // 3600,
            minute=time % 3600 // 60,
            second=time % 3600 % 60,
        )
