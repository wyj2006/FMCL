import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import TypedDict, Union
from zipfile import ZipFile

from PyQt6.QtGui import QIcon
from result import Err, Ok, Result

from fmcllib import VERSION
from fmcllib.account import get_current_user
from fmcllib.setting import Setting
from fmcllib.task import ATTR_CURRENT_WORK, Task, modify_task

from .fabric import (
    FabricInfo,
    FabricInstaller,
    FabricIntermediary,
    FabricLaunchMeta,
    FabricLibCommon,
    FabricLibraries,
    FabricLoader,
    download_fabric_installer,
    get_fabric_installers,
    get_fabric_versions,
    install_fabric,
)
from .original import (
    OriginalLibrary,
    OriginalVersionInfo,
    VersionJson,
    download_install_original,
    download_original,
    get_original_versions,
    install_original,
    parse_rules,
)

# 在不造成歧义的情况下 Instance 可以用 Game 代替以减小单词长度


class GameVersion(TypedDict):
    original: str
    fabric: str
    forge: str


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


def get_launch_program(instance_path: str):
    return Instance(instance_path).java_path


def get_launch_args(instance_path: str) -> Result[list[str], str]:
    with Task(f"获取运行参数: {instance_path}") as task_id:
        game_name = os.path.basename(instance_path)
        instance_path = os.path.abspath(instance_path)
        game_dir = os.path.abspath(os.path.join(instance_path, "..", ".."))

        instance = Instance(instance_path)
        verion_json: VersionJson = instance.version_json

        modify_task(task_id, ATTR_CURRENT_WORK, "拼接游戏参数")
        jvm_args: list[str] = []
        game_args: list[str] = []
        if "minecraftArguments" in verion_json:
            game_args.extend(verion_json["minecraftArguments"].split())
        else:
            for arg in verion_json["arguments"]["game"]:
                if isinstance(arg, str):
                    game_args.append(arg)
                elif isinstance(arg, dict) and parse_rules(arg["rules"]):
                    if isinstance(arg["value"], list):
                        game_args.extend(arg["value"])
                    else:
                        game_args.append(arg["value"])

            for arg in verion_json["arguments"]["jvm"]:
                if isinstance(arg, str):
                    jvm_args.append(arg)
                elif isinstance(arg, dict) and parse_rules(arg["rules"]):
                    if isinstance(arg["value"], list):
                        jvm_args.extend(arg["value"])
                    else:
                        jvm_args.append(arg["value"])

        modify_task(task_id, ATTR_CURRENT_WORK, "拼接class_path")
        class_path = []
        library: Union[OriginalLibrary, FabricLibCommon]
        for library in verion_json["libraries"]:
            if "rules" in library and not parse_rules(library["rules"]):
                continue
            if "downloads" in library:  # 原版格式
                if "artifact" not in library["downloads"]:
                    continue
                path = os.path.join(
                    game_dir, "libraries", library["downloads"]["artifact"]["path"]
                )
            else:  # 模组加载器格式
                lib_name = library["name"]
                package, name, version = lib_name.split(":")
                package = package.replace(".", "/")
                path = f"{package}/{name}/{version}/{name}-{version}.jar"
                path = os.path.join(game_dir, "libraries", path)
            class_path.append(path)
        class_path.append(os.path.join(instance_path, game_name + ".jar"))

        modify_task(task_id, ATTR_CURRENT_WORK, "解压natives库文件")
        natives_path = os.path.join(instance_path, "natives")
        for library in verion_json["libraries"]:
            if "rules" in library and not parse_rules(library["rules"]):
                continue
            if "downloads" not in library or "natives" not in library:
                continue
            natives_key = library["natives"][
                {"win32": "windows", "linux": "linux", "darwin": "osx"}[sys.platform]
            ]
            path = os.path.join(
                game_dir,
                "libraries",
                library["downloads"]["classifiers"][natives_key]["path"],
            )
            ZipFile(path).extractall(natives_path)

        modify_task(task_id, ATTR_CURRENT_WORK, "替换游戏参数")
        match get_current_user():
            case Ok(t):
                user_profile = t
            case Err(e):
                return Err(e)
        replacement = {
            "${auth_player_name}": user_profile["player_name"],
            "${version_name}": game_name,
            "${game_directory}": (instance_path if instance.is_isolate else game_dir),
            "${assets_root}": os.path.join(game_dir, "assets"),
            "${assets_index_name}": verion_json["assetIndex"]["id"],
            "${auth_uuid}": user_profile["uuid"],
            "${auth_access_token}": user_profile.get(
                "access_token", "${auth_access_token}"
            ),
            "${version_type}": "FMCL",
            "${natives_directory}": natives_path,
            "${classpath}": ";".join(class_path),
            "${launcher_name}": "FMCL",
            "${launcher_version}": VERSION,
        }
        for i in range(len(jvm_args)):
            for key, val in replacement.items():
                jvm_args[i] = jvm_args[i].replace(key, val)
        for i in range(len(game_args)):
            for key, val in replacement.items():
                game_args[i] = game_args[i].replace(key, val)

        args: list[str] = jvm_args + [verion_json["mainClass"]] + game_args
        return Ok(args)
