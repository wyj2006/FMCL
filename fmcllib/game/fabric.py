import json
import os
import threading
import time
from typing import Literal, TypedDict

import requests
from result import Err, Ok, Result

from fmcllib.filesystem import fileinfo
from fmcllib.task import ATTR_CURRENT_WORK, Task, download, modify_task


class FabricLoader(TypedDict):
    separator: str
    build: int
    maven: str
    version: str
    stable: bool


class FabricIntermediary(TypedDict):
    maven: str
    version: str
    stable: bool


class FabricLibCommon(TypedDict):
    name: str
    url: str
    md5: str
    sha1: str
    sha256: str
    sha512: str
    size: int


class FabricLibraries(TypedDict):
    client: list
    common: list[FabricLibCommon]
    server: list
    development: list


class FabricLaunchMeta(TypedDict):
    version: int
    min_java_version: int
    libraries: FabricLibraries
    mainClass: dict[Literal["client", "server"], str]


class FabricInfo(TypedDict):
    loader: FabricLoader
    intermediary: FabricIntermediary
    launcherMeta: FabricLaunchMeta


class FabricInstaller(TypedDict):
    url: str
    maven: str
    version: str
    stable: bool


def get_fabric_installers() -> list[FabricInstaller]:
    r = requests.get("https://meta.fabricmc.net/v2/versions/installer")
    return json.loads(r.content)


def get_fabric_versions(original_version: str) -> list[FabricInfo]:
    r = requests.get(f"https://meta.fabricmc.net/v2/versions/loader/{original_version}")
    return json.loads(r.content)


def download_fabric_installer(
    name: str, path: str, url: str
) -> dict[Literal["file_path"], str]:
    file_path = os.path.join(path, name + ".jar" if not name.endswith(".jar") else "")
    download(url, file_path)
    return {"file_path": file_path}


def install_fabric(
    name: str, original_version: str, loader_version: str
) -> Result[None, str]:
    match fileinfo("/.minecraft"):
        case Ok(t):
            game_dir = t["native_paths"][-1]
        case Err(e):
            return Err(e)
    with Task(f"安装Fabric(名称:{name})") as task_id:
        modify_task(task_id, ATTR_CURRENT_WORK, "安装库")

        r = requests.get(
            f"https://meta.fabricmc.net/v2/versions/loader/{original_version}/{loader_version}"
        )
        fabric_info: FabricInfo = json.loads(r.content)

        install_fabric_libraries(game_dir, fabric_info, task_id)

        modify_task(task_id, ATTR_CURRENT_WORK, "调整json文件")

        # 原版的json文件
        version_json_path = os.path.join(game_dir, "versions", name, name + ".json")
        while not os.path.exists(version_json_path):
            time.sleep(1)
        r = requests.get(
            f"https://meta.fabricmc.net/v2/versions/loader/{original_version}/{loader_version}/profile/json"
        )
        profile = json.loads(r.content)
        if name == profile["inheritsFrom"]:
            profile["inheritsFrom"] = f"{profile['inheritsFrom']}_"

        inherit_path = os.path.join(
            game_dir, "versions", name, profile["inheritsFrom"] + ".json"
        )
        if os.path.exists(inherit_path):
            os.remove(inherit_path)
        os.rename(version_json_path, inherit_path)

        open(version_json_path, mode="w", encoding="utf-8").write(json.dumps(profile))
    return Ok(None)


def install_fabric_libraries(game_dir: str, fabric_info: FabricInfo, parent_task_id=0):
    t = []

    for library in fabric_info["launcherMeta"]["libraries"]["common"]:
        lib_name = library["name"]
        package, name, version = lib_name.split(":")
        package = package.replace(".", "/")
        path = f"{package}/{name}/{version}/{name}-{version}.jar"
        t.append(
            threading.Thread(
                target=download,
                args=(
                    f"{library['url']}/{path}",
                    os.path.join(game_dir, "libraries", path),
                ),
                kwargs={"parent_task_id": parent_task_id},
                daemon=True,
            )
        )

    for i in t:
        i.start()
    for i in t:
        i.join()
