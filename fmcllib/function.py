import base64
import json
import logging
import os
from functools import reduce
from typing import Literal, TypedDict

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIcon
from result import Err, Ok, Result

from fmcllib.address import get_service_connection
from fmcllib.filesystem import fileinfo, listdir, readall
from fmcllib.singleton import singleton

tr = QCoreApplication.translate


class FunctionInfoIcon(TypedDict):
    type: Literal["default", "FluentIcon", "QIcon"]
    value: str


class FunctionInfoCommand(TypedDict):
    template: str
    program: str
    args: list[str]
    cwd: str
    env: dict[str, str]


class FunctionInfo(TypedDict):
    display_name: str
    translation_context: str
    icon: FunctionInfoIcon
    command: FunctionInfoCommand


@singleton
class Function:
    @staticmethod
    def getall_names():
        return listdir("/functions")

    def __init__(self, name):
        self.name = name
        self.fileinfo = fileinfo(f"/functions/{name}").unwrap()
        self.native_paths = self.fileinfo["native_paths"]
        if len(self.native_paths) > 1:
            logging.warning(
                f"发现重名的功能{name}({self.native_paths}), 将默认使用第一个:{self.native_paths[0]}"
            )

        self.function_info: FunctionInfo = {
            "display_name": name,
            "translation_context": "",
            "icon": {"type": "default"},
        }
        readall(
            f"/functions/{name}/function.json",
            lambda contents: reduce(
                lambda x, y: (x.update(json.loads(y)), x)[1],
                contents,
                self.function_info,
            ),
        )
        self.socket = get_service_connection("function")

    def run(self, args: list[str] = None) -> Result[None, str]:
        if args == None:
            args = []
        command = {"cwd": os.path.abspath(self.native_paths[0])}
        command |= self.function_info["command"]

        self.socket.sendall(
            f"run {base64.b64encode(json.dumps(command).encode()).decode()}\0".encode()
        )
        result = json.loads(self.socket.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(None)

    @property
    def display_name(self):
        return tr(
            self.function_info["translation_context"],
            self.function_info["display_name"],
        )

    @property
    def icon(self):
        match self.function_info["icon"]["type"]:
            case "default":
                return QCoreApplication.instance().windowIcon()
            case "FluentIcon":
                return getattr(FluentIcon, self.function_info["icon"]["value"]).icon()
            case "QIcon":
                return QIcon(self.function_info["icon"]["value"])
        logging.error(f"无法识别的function icon: {self.function_info['icon']}")
        return QCoreApplication.instance().windowIcon()
