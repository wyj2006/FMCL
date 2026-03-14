import json
import logging
import re
import sys
import traceback
import webbrowser
from importlib.metadata import version
from typing import Optional, TypedDict

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QLayout, QWidget
from qfluentwidgets import FluentIcon, PushButton, SettingCard
from result import is_ok
from ui_about import Ui_About

from fmcllib import VERSION
from fmcllib.filesystem import fileinfo
from fmcllib.function import IconDict, get_icon

tr = QCoreApplication.translate


class NameDict(TypedDict):
    value: str
    translation_context: str


class ActionDict(TypedDict):
    type: str
    value: str


class Operator(TypedDict):
    name: NameDict
    action: ActionDict


class AboutItemDict(TypedDict):
    name: str
    description: NameDict
    icon: Optional[IconDict]
    operators: list[Operator]


class AboutDict(TypedDict):
    launcher: list[AboutItemDict]
    thanks: list[AboutItemDict]
    dependences: list[AboutItemDict]


class AboutItem(SettingCard):
    def __init__(self, about: AboutItemDict, parent=None):
        super().__init__(
            QIcon(
                (get_icon(about["icon"]) if about["icon"] != None else QIcon())
                .pixmap(32, 32)
                .scaled(32, 32)
            ),
            about["name"],
            get_name(about["description"]),
            parent,
        )
        if about["icon"] == None:
            self.iconLabel.hide()
        else:
            self.setIconSize(32, 32)

        for operator in about["operators"]:
            button = PushButton()
            button.setText(get_name(operator["name"]))
            match operator["action"]["type"]:
                case "open_browser":
                    button.clicked.connect(
                        lambda _, url=operator["action"]["value"]: webbrowser.open(url)
                    )
                case "about_qt":
                    button.clicked.connect(QApplication.aboutQt)
            self.hBoxLayout.addWidget(button)


class About(QWidget, Ui_About):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.INFO.icon())

        if not is_ok(result := fileinfo("/about.json")):
            return
        for native_path in result.ok_value["native_paths"]:
            about_dict: AboutDict = json.load(open(native_path, encoding="utf-8"))
            for kind, abouts in about_dict.items():
                layout: QLayout = getattr(self, f"{kind}_layout")
                for about in abouts:
                    about_item = AboutItem(about)
                    layout.addWidget(about_item)


def get_name(name_dict: NameDict):
    value = name_dict["value"]
    for i in re.finditer(r"\$\{(.*?)_VERSION\}", name_dict["value"]):
        try:
            match i.group(1):
                case "FMCL":
                    value = value.replace(i.group(0), VERSION)
                case "Python":
                    value = value.replace(i.group(0), sys.version)
                case module_name:
                    value = value.replace(i.group(0), version(module_name))
        except:
            logging.error(f"无法替换'{i.group(0)}': \n{traceback.format_exc()}")
    return tr(name_dict["translation_context"], value)
