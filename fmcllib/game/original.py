# https://zh.minecraft.wiki/w/Tutorial:%E7%BC%96%E5%86%99%E5%90%AF%E5%8A%A8%E5%99%A8?variant=zh-cn
# https://zh.minecraft.wiki/w/Tutorial:%E7%BC%96%E5%86%99%E5%90%AF%E5%8A%A8%E5%99%A8/version.json?variant=zh-cn
import json
import os
import platform
import sys
import threading
from typing import Literal, TypedDict

import requests
from result import Err, Ok, Result

from fmcllib.filesystem import fileinfo
from fmcllib.task import ATTR_CURRENT_WORK, Task, download, modify_task


class OriginalVersionInfo(TypedDict):
    id: str
    type: Literal["release", "snapshot", "old_beta", "old_alpha"]
    url: str
    time: str
    releaseTime: str


class Rule(TypedDict):
    action: Literal["allow", "disallow"]
    os: dict[Literal["name", "version", "arch"], str]


class OriginalLibrary(TypedDict, total=False):
    """VersionJson['libraries']每个元素的内容"""

    name: str
    downloads: dict[
        Literal["artifact", "classifiers"],
        dict[Literal["path", "sha1", "size", "url"], str | int],
    ]
    natives: dict[Literal["windows", "osx", "linux"], str]
    rules: list[Rule]


class LoggingClient(TypedDict):
    """VersionJson['logging']['client']的内容"""

    argument: str
    file: dict[Literal["id", "sha1", "size", "url"], str | int]
    type: str


class ArgumentDict(TypedDict):
    game: list[str | dict[Literal["rules", "value"], Rule]]
    jvm: list[str | dict[Literal["rules", "value"], Rule]]


class VersionJson(TypedDict, total=False):
    """版本json文件"""

    arguments: ArgumentDict
    minecraftArguments: str  # 1.13以前
    assetIndex: dict[Literal["id", "size", "totalSize", "url"], str | int]
    assets: str
    downloads: dict[
        Literal["client", "server"], dict[Literal["sha1", "size", "url"], str | int]
    ]
    libraries: list[OriginalLibrary]
    logging: dict[Literal["client"], LoggingClient]
    mainClass: str
    time: str
    type: Literal["release", "snapshot", "old_beta", "old_alpha"]
    id: str
    inheritsFrom: str


class AssetIndex(TypedDict):
    """资源索引文件"""

    objects: dict[str, dict[Literal["hash", "size"], str | int]]


def get_original_versions() -> list[OriginalVersionInfo]:
    r = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json")
    return json.loads(r.content)["versions"]


def download_original(
    name, path, json_url, is_client=True
) -> dict[Literal["json_path", "version_json", "jar_path"], str]:
    with Task(f"下载原版(名称:{name})") as task_id:
        json_path = os.path.join(path, name + ".json")

        modify_task(task_id, ATTR_CURRENT_WORK, "下载json文件")
        download(json_url, json_path, task_id)

        version_json: VersionJson = json.load(open(json_path, encoding="utf-8"))
        if is_client:
            jar_url = version_json["downloads"]["client"]["url"]
        else:
            jar_url = version_json["downloads"]["server"]["url"]
        jar_path = os.path.join(path, name + ".jar")

        modify_task(task_id, ATTR_CURRENT_WORK, "下载jar文件")
        download(jar_url, jar_path, task_id)
    return {"json_path": json_path, "version_json": version_json, "jar_path": jar_path}


def install_original(game_dir: str, name: str, json_path: str):
    version_json = json.load(open(json_path, encoding="utf-8"))
    version_json["id"] = name
    json.dump(version_json, open(json_path, mode="w", encoding="utf-8"), indent=4)

    with Task("安装原版") as task_id:
        t: list[threading.Thread] = []
        t.append(
            threading.Thread(
                target=install_libraries, args=(game_dir, version_json, task_id)
            )
        )
        t.append(
            threading.Thread(
                target=install_assets, args=(game_dir, version_json, task_id)
            )
        )

        for i in t:
            i.start()
        for i in t:
            i.join()


def install_libraries(game_dir: str, version_json: VersionJson, parent_task_id=0):
    with Task("安装库", parent_task_id) as task_id:
        t: list[threading.Thread] = []

        for library in version_json["libraries"]:
            if "rules" in library and not parse_rules(library["rules"]):
                continue
            if "artifact" in library["downloads"]:
                t.append(
                    threading.Thread(
                        target=download,
                        args=(
                            library["downloads"]["artifact"]["url"],
                            os.path.join(
                                game_dir,
                                "libraries",
                                library["downloads"]["artifact"]["path"],
                            ),
                        ),
                        kwargs={"parent_task_id": task_id},
                    )
                )
            if "classifiers" in library["downloads"]:
                natives_key = library["natives"][
                    {"win32": "windows", "linux": "linux", "darwin": "osx"}[
                        sys.platform
                    ]
                ]
                t.append(
                    threading.Thread(
                        target=download,
                        args=(
                            library["downloads"]["classifiers"][natives_key]["url"],
                            os.path.join(
                                game_dir,
                                "libraries",
                                library["downloads"]["classifiers"][natives_key][
                                    "path"
                                ],
                            ),
                        ),
                        kwargs={"parent_task_id": task_id},
                    )
                )

        for i in t:
            i.start()
        for i in t:
            i.join()


def download_asset_index(
    game_dir: str, version_json: VersionJson, parent_task_id=0
) -> AssetIndex:
    asset_id = version_json["assetIndex"]["id"]
    path = os.path.join(game_dir, "assets", "indexes", f"{asset_id}.json")
    if not os.path.exists(path):
        download(version_json["assetIndex"]["url"], path, parent_task_id)
    return json.load(open(path, encoding="utf-8"))


def install_assets(game_dir: str, version_json: VersionJson, parent_task_id=0):
    """会下载不存在或者被更改的资源文件"""
    with Task("安装资源", parent_task_id) as task_id:
        t: list[threading.Thread] = []

        asset_index = download_asset_index(game_dir, version_json, task_id)
        for path, info in asset_index["objects"].items():
            asset_hash = info["hash"]
            path = os.path.join(
                game_dir, "assets", "objects", asset_hash[:2], asset_hash
            )
            url = f"https://resources.download.minecraft.net/{asset_hash[:2]}/{asset_hash}"
            if not os.path.exists(path):  # 路径不存在说明这个资源要么没下载要么被更改
                t.append(
                    threading.Thread(
                        target=download,
                        args=(url, path),
                        kwargs={"parent_task_id": task_id},
                    )
                )

        for i in t:
            i.start()
        for i in t:
            i.join()


def parse_rules(rules: list[Rule]) -> bool:
    os_dict = {
        "name": {"Windows": "windows", "Linux": "linux", "Darwin": "osx"}[
            platform.system()
        ],
        "version": platform.version(),
        "arch": {"32bit": "x86", "64bit": "x64"}[platform.architecture()[0]],
    }
    for rule in rules:
        mismatch = False
        for key, val in rule.get("os", dict()).items():
            if key in os_dict and val != os_dict[key]:
                mismatch = True
                break
        # TODO features
        for key, val in rule.get("features", dict()).items():
            return False
        if rule["action"] == "allow" and mismatch:
            return False
        if rule["action"] == "disallow" and not mismatch:
            return False
    return True


def download_install_original(name, json_url) -> Result[None, str]:
    match fileinfo("/.minecraft"):
        case Ok(t):
            game_dir = t["native_paths"][-1]
            install_original(
                game_dir,
                name,
                download_original(
                    name, os.path.join(game_dir, "versions", name), json_url
                )["json_path"],
            )
            return Ok(None)
        case Err(e):
            return Err(e)
