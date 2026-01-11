import logging

import qtawesome as qta
from overviewer import Overviewer
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import NavigationItemPosition
from result import Err, Ok
from ui_game_manager import Ui_GameManager

from fmcllib.filesystem import fileinfo
from fmcllib.function import Function
from fmcllib.game import Instance


class GameManager(QWidget, Ui_GameManager):
    def __init__(self, instance_path: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("mdi6.minecraft"))
        self.setWindowTitle(f"{self.windowTitle()}: {instance_path}")
        self.horizontalLayout.setStretchFactor(self.stack, 1)

        self.instance = Instance(instance_path)

        self.overviewer = Overviewer(self.instance)
        self.navigation_bar.addItem(
            self.overviewer.objectName(),
            self.overviewer.windowIcon(),
            self.overviewer.windowTitle(),
            lambda: self.stack.setCurrentWidget(self.overviewer),
        )
        self.stack.addWidget(self.overviewer)
        self.stack.setCurrentWidget(self.overviewer)

        match fileinfo("/functions/settingeditor"):
            case Ok(t):
                setting_function = Function(t["native_paths"][0])
                self.navigation_bar.addItem(
                    "setting",
                    setting_function.icon,
                    setting_function.display_name,
                    lambda: setting_function.run(
                        "--setting-path", self.instance.setting_path
                    ),
                    selectable=False,
                    position=NavigationItemPosition.BOTTOM,
                )
            case Err(e):
                logging.error(f"无法添加设置标签: {e}")

    @pyqtSlot(int)
    def on_stack_currentChanged(self, _):
        self.navigation_bar.setCurrentItem(self.stack.currentWidget().objectName())
