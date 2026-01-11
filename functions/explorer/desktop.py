import logging
import traceback
from fnmatch import fnmatch
from typing import TypedDict

from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import QAbstractItemView, QListView, QListWidgetItem
from qfluentwidgets import FluentIcon, ListWidget, RoundMenu
from result import is_err

from fmcllib import show_qerrormessage
from fmcllib.filesystem import fileinfo, listdir
from fmcllib.function import Function
from fmcllib.setting import Setting


class FunctionContextMenuAction(TypedDict):
    type: str
    program: str
    args: list[str]


class Desktop(ListWidget):
    def __init__(self):
        super().__init__()
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setIconSize(QSize(32, 32))
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setWordWrap(True)
        self.setFlow(QListView.Flow.TopToBottom)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # item.toolTip到Function的映射
        self.item_function: dict[str, Function] = {}

        self.itemDoubleClicked.connect(
            lambda item: self.run(self.item_function[item.toolTip()])
        )

        self.refresh()

    def refresh(self):
        self.clear()
        self.item_function = {}

        for name in listdir("/desktop").unwrap_or([]):
            try:
                for native_path in fileinfo(f"/desktop/{name}").unwrap()[
                    "native_paths"
                ]:
                    function = Function(native_path)
                    item = QListWidgetItem()
                    item.setText(function.display_name)
                    item.setToolTip(f"{function.display_name}({native_path})")
                    item.setIcon(function.icon)
                    item.setSizeHint(QSize(80, 80))
                    self.addItem(item)
                    self.item_function[item.toolTip()] = function
            except:
                logging.error(f"无法显示功能'{name}'在桌面上:{traceback.format_exc()}")

    def event(self, a0: QEvent):
        match a0.type():
            case QEvent.Type.Resize:
                self.refresh()
        return super().event(a0)

    def showContextMenu(self):
        menu = RoundMenu()

        item = self.itemAt(self.mapFromGlobal(QCursor.pos()))

        if item == None:
            refresh = QAction(FluentIcon.SYNC.icon(), self.tr("刷新"))
            refresh.triggered.connect(self.refresh)
            menu.addAction(refresh)
        else:
            item_function = self.item_function[item.toolTip()]

            run_action = QAction(FluentIcon.PLAY.icon(), self.tr("运行"))
            run_action.triggered.connect(lambda: self.run(item_function))
            menu.addAction(run_action)

            action: FunctionContextMenuAction
            for action in (
                Setting()
                .get("explorer.desktop.function_context_menu_actions")
                .unwrap_or([])
            ):
                if not fnmatch(item_function.type, action["type"]):
                    continue
                if is_err(result := fileinfo(action["program"])):
                    continue
                function = Function(result.ok_value["native_paths"][0])

                args = []
                for arg in action["args"]:
                    args.append(
                        arg.replace("${function_dir}", item_function.native_path)
                    )

                action = QAction(function.icon, function.display_name)
                action.triggered.connect(
                    lambda _, f=function, args=args: self.run(f, *args)
                )
                menu.addAction(action)

        menu.exec(QCursor.pos())

    def run(self, function: Function, *args):
        try:
            function.run(*args).unwrap()
        except:
            show_qerrormessage(
                self.tr("运行{path}时出错").format(path=function.native_path),
                traceback.format_exc(),
                self,
            )
