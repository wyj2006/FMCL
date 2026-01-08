import base64
import json
import os
import threading
from typing import Any, Literal, TypedDict, Union

from result import Err, Ok, Result

from fmcllib.address import get_service_connection
from fmcllib.filesystem import fileinfo
from fmcllib.wrapper import safe_function, singleton

SETTING_DEFAULT_PATH = fileinfo("/settings.json").unwrap()["native_paths"][0]
client = get_service_connection("setting")
lock = threading.Lock()


class SettingAttrDict(TypedDict):
    """defaultsettings.json里每一项的格式"""

    display_name: str
    translation_context: str
    description: str
    scope: list[Literal["global", "game"]]


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

    def __init__(self, native_path=SETTING_DEFAULT_PATH):
        # 使用native_path让调用方处理可能存在的二义性
        self.native_path = native_path
        # 所有的设置都有一个共同的根, root_key就是这个设置相对于根的路径
        self.root_key = native_path.replace(".", "").replace("\\", "/")

        if os.path.exists(native_path):
            for key, val in json.load(open(native_path, encoding="utf-8")).items():
                self.add_or_update(key, val)
        self.add_or_update("", native_path, True)  # 更改root的值

    @safe_function(lock)
    def add_or_update(self, key: str, value, is_default=False) -> Result[None, str]:
        client.sendall(
            " ".join(
                [
                    f'add-or-update{"-default" if is_default else ""}',
                    f'"{Setting.key_join(self.root_key, key)}"',
                    f"{base64.b64encode(json.dumps(value).encode()).decode()}\0",
                ]
            ).encode()
        )
        result = json.loads(client.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(None)

    @safe_function(lock)
    def add_or_update_attr(self, key: str, attr_name: str, value) -> Result[None, str]:
        client.sendall(
            " ".join(
                [
                    f"add-or-update-attr",
                    f'"{Setting.key_join(self.root_key, key)}"',
                    attr_name,
                    f"{base64.b64encode(json.dumps(value).encode()).decode()}\0",
                ]
            ).encode()
        )
        result = json.loads(client.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(None)

    @safe_function(lock)
    def _get(self, key: str) -> Result[SettingDict, str]:
        client.sendall(f'get "{Setting.key_join(self.root_key, key)}"\0'.encode())
        result = json.loads(client.recv(1024 * 1024))

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

    @safe_function(lock)
    def children(self, key: str) -> Result[list[str], str]:
        client.sendall(
            f'list-children "{Setting.key_join(self.root_key, key)}"\0'.encode()
        )
        result = json.loads(client.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(result["names"])

    @safe_function(lock)
    def generate_json(self, key: str = "") -> Result[Union[dict, object], str]:
        client.sendall(
            f'generate-json "{Setting.key_join(self.root_key, key)}"\0'.encode()
        )
        result = json.loads(client.recv(1024 * 1024))

        if "error_msg" in result:
            return Err(result["error_msg"])
        return Ok(result)
