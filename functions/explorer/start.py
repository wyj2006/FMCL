import logging
import traceback

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QListView, QListWidgetItem, QWidget
from qfluentwidgets import FluentIcon, ListWidget, NavigationItemPosition
from ui_start import Ui_Start

from fmcllib import show_qerrormessage
from fmcllib.filesystem import fileinfo, listdir
from fmcllib.function import Function


class FunctionList(ListWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("function_list")
        self.setResizeMode(QListView.ResizeMode.Adjust)

        # item.toolTip到Function的映射
        self.item_function: dict[str, Function] = {}

        for name in listdir("/start").unwrap_or([]):
            try:
                for native_path in fileinfo(f"/start/{name}").unwrap()["native_paths"]:
                    function = Function(native_path)
                    item = QListWidgetItem(function.icon, function.display_name)
                    item.setToolTip(f"{name}({native_path})")
                    self.addItem(item)
                    self.item_function[item.toolTip()] = function
            except:
                logging.error(f"无法显示功能{name}:{traceback.format_exc()}")

        self.itemClicked.connect(self.on_function_list_itemClicked)

    @pyqtSlot(QListWidgetItem)
    def on_function_list_itemClicked(self, item: QListWidgetItem):
        function = self.item_function[item.toolTip()]
        try:
            function.run().unwrap()
        except:
            show_qerrormessage(
                self.tr("运行{path}出错").format(path=function.path),
                traceback.format_exc(),
                self,
            )


class Start(QWidget, Ui_Start):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.function_list = FunctionList()

        self.navigation_interface.addItem(
            "function_list",
            FluentIcon.APPLICATION,
            self.tr("功能列表"),
            lambda: self.stackWidget.setCurrentWidget(self.function_list),
            tooltip=self.tr("功能列表"),
        )

        self.navigation_interface.addItem(
            "power",
            FluentIcon.POWER_BUTTON,
            self.tr("电源"),
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
            tooltip=self.tr("电源"),
        )

        self.stackWidget.addWidget(self.function_list)
        self.navigation_interface.setCurrentItem("function_list")

    def collapsePanel(self):
        self.navigation_interface.panel.collapse()
