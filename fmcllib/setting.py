import base64
import json
import os
from typing import Any, TypedDict, Union

from result import Err, Ok, Result

from fmcllib.address import get_address, get_service_connection
from fmcllib.filesystem import readall
from fmcllib.safe_socket import SafeSocket
from fmcllib.singleton import singleton

SETTING_DEFAULT_PATH = "/settings.json"


class SettingAttrDict(TypedDict):
    """defaultsettings.json里每一项的格式"""

    display_name: str
    translation_context: str
    description: str


class DefaultSettingDict(SettingAttrDict):
    """defaultsettings.json里每一项的格式"""

    default_value: Any


class SettingDict(TypedDict):
    """由setting服务返回的格式"""

    name: str
    value: Any
    default_value: Any
    attribute: SettingAttrDict


@singleton
class Setting:
    @staticmethod
    def key_join(*args):
        # 先将args中的元素全部转换成str类型
        # 在去除这些元素两边的'.'
        # 最后去除空字符串
        return ".".join(
            filter(lambda x: x != "", map(lambda x: x.strip("."), map(str, args)))
        )

    def __init__(self, path=SETTING_DEFAULT_PATH):
        self.path = path
        # 所有的设置都有一个共同的根, parent_key就是这个设置相对于根的路径
        self.parent_key = path.replace(".", "_")
        self.socket = get_service_connection("setting")

        readall(
            os.path.join(
                os.path.dirname(path),
                "defaultsettings.json",
            ),
            lambda contents: list(
                (
                    self.add_or_update(key, attr, True)
                    if name == "default_value"
                    else self.add_or_update_attr(key, name, attr)
                )
                for content in contents
                for key, val in json.loads(content).items()
                for name, attr in val.items()
            ),
        )
        readall(
            path,
            lambda contents: list(
                self.add_or_update(key, val)
                for content in contents
                for key, val in json.loads(content).items()
            ),
        )
        self.add_or_update("", path, True)  # 更改root的值

    def add_or_update(self, key: str, value, is_default=False) -> Result[None, str]:
        self.socket.sendall(
            " ".join(
                [
                    f'add_or_update{"_default" if is_default else ""}',
                    f'"{Setting.key_join(self.parent_key, key)}"',
                    f"{base64.b64encode(json.dumps(value).encode()).decode()}\0",
                ]
            ).encode()
        )
        result = json.loads(self.socket.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(None)

    def add_or_update_attr(self, key: str, attr_name: str, value) -> Result[None, str]:
        self.socket.sendall(
            " ".join(
                [
                    f"add_or_update_attr",
                    f'"{Setting.key_join(self.parent_key, key)}"',
                    attr_name,
                    f"{base64.b64encode(json.dumps(value).encode()).decode()}\0",
                ]
            ).encode()
        )
        result = json.loads(self.socket.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(None)

    def _get(self, key: str) -> Result[SettingDict, str]:
        self.socket.sendall(
            f'get "{Setting.key_join(self.parent_key, key)}"\0'.encode()
        )
        result = json.loads(self.socket.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(result)

    def get(self, key: str) -> Result[Any, str]:
        match self._get(key):
            case Ok(result):
                return Ok(result["value"])
            case Err(e):
                return Err(e)

    def get_default(self, key: str) -> Result[Any, str]:
        match self._get(key):
            case Ok(result):
                return Ok(result["default_value"])
            case Err(e):
                return Err(e)

    def get_allattr(self, key: str) -> Result[SettingAttrDict, str]:
        match self._get(key):
            case Ok(result):
                return Ok(result["attribute"])
            case Err(e):
                return Err(e)

    def get_attr(self, key: str, attr_name: str, default=None) -> Result[Any, str]:
        match self._get(key):
            case Ok(result):
                return Ok(result["attribute"].get(attr_name, default))
            case Err(e):
                return Err(e)

    def set_attr(self, key: str, attr_name: str, value):
        return self.add_or_update_attr(key, attr_name, value)

    def set(self, key: str, value):
        return self.add_or_update(key, value)

    def children(self, key: str) -> Result[list[str], str]:
        self.socket.sendall(
            f'list_children "{Setting.key_join(self.parent_key, key)}"\0'.encode()
        )
        result = json.loads(self.socket.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(result["names"])

    def generate_json(self, key: str = "") -> Result[Union[dict, object], str]:
        self.socket.sendall(
            f'generate_json "{Setting.key_join(self.parent_key, key)}"\0'.encode()
        )
        result = json.loads(self.socket.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(result)
