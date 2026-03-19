import json
import logging
import os
import re
from pathlib import Path
from typing import TypedDict

from PyQt6.QtGui import QIcon

from fmcllib.setting import Setting

from .original import VersionJson

# 在不造成歧义的情况下 Instance 可以用 Game 代替以减小单词长度


class GameVersion(TypedDict):
    original: str
    fabric: str
    forge: str


class TimeRecord(TypedDict):
    start: float
    end: float


class Instance:
    def __init__(self, path: str):
        self.path = path

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def setting_path(self):
        return os.path.join(self.path, "FMCL", "settings.json")

    @property
    def setting(self):
        return Setting(self.setting_path)

    @property
    def is_isolate(self):
        return self.setting.get("isolate").unwrap_or(False)

    @property
    def java_path(self):
        return self.setting.get("game.java_path").unwrap_or("")

    @property
    def icon_path(self):
        return self.setting.get("icon.path").unwrap_or(":/image/grass@2x.png")

    @icon_path.setter
    def icon_path(self, value):
        self.setting.set("icon.path", value)

    @property
    def icon(self):
        return QIcon(self.icon_path)

    @property
    def game_directory(self):
        return (
            self.path
            if self.is_isolate
            else os.path.abspath(os.path.join(self.path, "..", ".."))
        )

    @property
    def support_mod(self) -> bool:
        for k, v in self.version.items():
            if k != "original" and v:
                return True
        return False

    @property
    def mods_path(self) -> str:
        return os.path.join(self.game_directory, "mods")

    @property
    def time_record_path(self) -> str:
        return os.path.join(self.path, "FMCL", "time_record.json")

    @property
    def time_records(self) -> list[TimeRecord]:
        try:
            return json.load(open(self.time_record_path, encoding="utf-8"))
        except:
            return []

    @property
    def version_json(self):
        verion_json: VersionJson = json.load(
            open(os.path.join(self.path, self.name + ".json"), encoding="utf-8")
        )
        if "inheritsFrom" in verion_json:
            inherit_path = os.path.join(
                self.path, verion_json["inheritsFrom"] + ".json"
            )
            # 兼容其它启动器
            # 不是所有的启动器都是像这样处理的
            if os.path.exists(inherit_path):
                verion_json = merge(
                    json.load(open(inherit_path, encoding="utf-8")),
                    verion_json,
                )
        return verion_json

    @property
    def version(self) -> GameVersion:
        original = ""
        fabric = ""
        forge = ""

        version_json = self.version_json
        version_json_str = str(version_json)

        if "net.fabricmc:fabric-loader" in version_json_str:
            fabric = re.findall(
                r"net.fabricmc:fabric-loader:([0-9\.]+)", version_json_str
            )
            if fabric:
                fabric = fabric[0].replace("+build", "")
            else:
                fabric = ""
        elif "minecraftforge" in version_json_str:
            forge = re.findall(
                r"net.minecraftforge:forge:[0-9\.]+-([0-9\.]+)", version_json_str
            )
            if forge:
                forge = forge[0]
            else:
                forge = re.findall(
                    r"net.minecraftforge:minecraftforge:([0-9\.]+)", version_json_str
                )
                if forge:
                    forge = forge[0]
                else:
                    forge = re.findall(
                        r"net.minecraftforge:fmlloader:[0-9\.]+-([0-9\.]+)",
                        version_json_str,
                    )
                if forge:
                    forge = forge[0]
                else:
                    forge = ""

        game_version: GameVersion = {
            "original": original,
            "fabric": fabric,
            "forge": forge,
        }

        # 从 PCL 下载的版本信息中获取版本号
        if "clientVersion" in version_json:
            game_version["original"] = version_json["clientVersion"]
            return game_version
        # 从 HMCL 下载的版本信息中获取版本号
        if "patches" in version_json:
            for patch in version_json["patches"]:
                if patch.get("id", "") == "game" and "version" in patch:
                    game_version["original"] = patch["version"]
                    return game_version
        # 从 Forge Arguments 中获取版本号
        if "arguments" in version_json and "game" in version_json["arguments"]:
            mark = False
            for argument in version_json["arguments"]["game"]:
                if mark:
                    game_version["original"] = argument
                    return game_version
                if argument == "--fml.mcVersion":
                    mark = True
        # 从继承版本中获取版本号
        if "inheritsFrom" in version_json:
            # 安装的时候如果重名会在最后加个'_'
            # 见install_fabric函数的相关代码
            game_version["original"] = version_json["inheritsFrom"].replace("_", "")
            return game_version
        # 从下载地址中获取版本号
        version = re.findall(r"launcher.mojang.com/mc/game/([^/])*", version_json_str)
        if version:
            game_version["original"] = version[0]
            return game_version
        # 从 Forge 版本中获取版本号
        version = re.findall(
            r"net.minecraftforge:fmlloader:([0-9\.]+)-[0-9\.]+", version_json_str
        )
        if version:
            game_version["original"] = version[0]
            return game_version
        # 从 Fabric 版本中获取版本号
        version = re.findall(r"net.fabricmc:intermediary:([0-9\.]+)", version_json_str)
        if version:
            game_version["original"] = version[0]
            return game_version
        # 从 jar 项中获取版本号
        if "jar" in version_json:
            game_version["original"] = version_json["jar"]
            return game_version
        if "id" in version_json:
            game_version["original"] = version_json["id"]
            return game_version
        logging.error(f"无法确定{self.name}的版本")
        return game_version

    def rename(self, name: str):
        if name == self.name:
            return
        version_json = self.version_json
        if "inheritsFrom" in version_json and version_json["inheritsFrom"] == name:
            Path(
                os.path.join(self.path, version_json["inheritsFrom"] + ".json")
            ).replace(os.path.join(self.path, version_json["inheritsFrom"] + "_.json"))
        Path(os.path.join(self.path, self.name + ".json")).replace(
            os.path.join(self.path, name + ".json")
        )
        Path(os.path.join(self.path, self.name + ".jar")).replace(
            os.path.join(self.path, name + ".jar")
        )
        new_instance = Instance(os.path.normpath(os.path.join(self.path, "..", name)))
        Path(self.path).replace(new_instance.path)
        return new_instance


def merge(a: dict, b: dict):
    for key, val in b.items():
        if key not in a:
            a[key] = val
            continue
        if isinstance(a[key], dict) and isinstance(b[key], dict):
            a[key] = merge(a[key], b[key])
        elif isinstance(a[key], list) and isinstance(b[key], list):
            a[key].extend(b[key])
        elif isinstance(a[key], list):
            a[key].append(b[key])
        else:
            a[key] = val
    return a
