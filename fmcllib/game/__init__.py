import json
import os
import sys
from typing import Union
from zipfile import ZipFile

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
    Setting(os.path.join(instance_path, "FMCL", "settings.json")).get(
        "game.java_path"
    ).unwrap_or("java")


def get_launch_args(instance_path: str) -> Result[list[str], str]:
    with Task(f"获取运行参数: {instance_path}") as task_id:
        game_name = os.path.basename(instance_path)
        instance_path = os.path.abspath(instance_path)
        game_dir = os.path.abspath(os.path.join(instance_path, "..", ".."))

        verion_json: VersionJson = json.load(
            open(os.path.join(instance_path, game_name + ".json"), encoding="utf-8")
        )
        if "inheritsFrom" in verion_json:
            verion_json = merge(
                json.load(
                    open(
                        os.path.join(
                            instance_path, verion_json["inheritsFrom"] + ".json"
                        ),
                        encoding="utf-8",
                    )
                ),
                verion_json,
            )

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
            "${game_directory}": (
                game_dir
                if not Setting(os.path.join(instance_path, "FMCL", "settings.json"))
                .get("isolate")
                .unwrap_or(False)
                else instance_path
            ),
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
