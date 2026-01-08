import base64
import json
import logging
import os
import threading
import traceback
from typing import Literal, TypedDict

import qtawesome as qta
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIcon
from result import Err, Ok, Result

from fmcllib import show_qerrormessage
from fmcllib.address import get_service_connection
from fmcllib.filesystem import fileinfo, listdir
from fmcllib.wrapper import safe_function, singleton

tr = QCoreApplication.translate
client = get_service_connection("function")
lock = threading.Lock()


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
    type: str
    display_name: str
    translation_context: str
    icon: FunctionInfoIcon
    command: FunctionInfoCommand


@singleton
class Function:
    @staticmethod
    def getall_names():
        return listdir("/functions")

    @staticmethod
    @safe_function(lock)
    def getall_running() -> Result[dict, str]:
        client.sendall("getall-running\0".encode())
        result = json.loads(client.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(result)

    @staticmethod
    def quick_run(path: str, *args, index=0):
        """
        运行path对应的功能,
        index指示使用path所代表的native_paths的索引(Function传入的是本地路径)
        """
        try:
            Function(fileinfo(path).unwrap()["native_paths"][index]).run(*args)
        except:
            show_qerrormessage(f"无法运行功能'{path}'", traceback.format_exc())

    def __init__(self, native_path: str):
        # 使用native_path让调用方处理可能存在的二义性
        self.native_path = native_path
        self.name = os.path.basename(native_path)

        self.function_info: FunctionInfo = {
            "type": "unknown",
            "display_name": self.name,
            "translation_context": "",
            "icon": {"type": "default"},
        } | json.load(
            open(os.path.join(native_path, "function.json"), encoding="utf-8")
        )

    @safe_function(lock)
    def run(self, *args) -> Result[None, str]:
        args = list(args)

        client.sendall(
            " ".join(
                [
                    "run",
                    f'"{os.path.abspath(self.native_path).replace("\\","/")}"',
                    base64.b64encode(json.dumps(args).encode()).decode() + "\0",
                ]
            ).encode()
        )
        result = json.loads(client.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(None)

    @property
    def type(self):
        return self.function_info["type"]

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
            case "QtAwesome":
                return qta.icon(self.function_info["icon"]["value"])
        logging.error(f"无法识别的function icon: {self.function_info['icon']}")
        return QCoreApplication.instance().windowIcon()
