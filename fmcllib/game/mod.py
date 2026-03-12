import itertools
import json
import logging
import os
import traceback
from zipfile import ZipFile

import qtawesome as qta
import toml
from PyQt6.QtGui import QImage, QPixmap


class Mod:
    @staticmethod
    def is_mod(path: str) -> bool:
        return os.path.splitext(path)[1] in (".jar", ".disabled")

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.description = ""
        self.icon: QPixmap = qta.icon("mdi.puzzle-outline").pixmap(32, 32)
        self.version = ""
        self.authors: list[str] = []
        self.url = ""

        def adjust(content: str | bytes):
            """调整文件内容来保证能够正常解析"""
            if isinstance(content, bytes):
                content = content.decode(errors="ignore")
            in_str = False  # 判断是否进入文本中的字符串中
            new_content = ""
            for i in content:
                if in_str:
                    if i == "\\":  # 防止把'\'变成两个'\\'
                        new_content += "\\"
                    else:
                        new_content += repr(i)[1:-1]
                else:
                    new_content += i
                if i == '"':
                    in_str = not in_str
            return new_content

        zipfile = ZipFile(self.path)
        for zipinfo in zipfile.filelist:
            if (
                "icon.png" in zipinfo.filename
                or "logo.png" in zipinfo.filename  # 有这些名称的可能是图标
                or (
                    zipinfo.filename.endswith(".png") and "/" not in zipinfo.filename
                )  # 在根目录下的图片可能是图标
            ):
                self.icon = QPixmap.fromImage(
                    QImage.fromData(zipfile.open(zipinfo.filename).read())
                )
            elif "fabric.mod.json" == zipinfo.filename:
                try:
                    config = json.loads(adjust(zipfile.open(zipinfo.filename).read()))
                    self.name = config["name"]
                    self.description = config.get("description", "")
                    self.version = config["version"]
                    for i in config.get("authors", []) + config.get("contributors", []):
                        if isinstance(i, dict):
                            self.authors.append(i["name"])
                        else:
                            self.authors.append(i)
                    if "contact" in config and "homepage" in config["contact"]:
                        self.url = config["contact"]["homepage"]
                except:
                    logging.error(
                        f"{self.name}: 从{zipinfo.filename}中获取模组信息失败:\n{traceback.format_exc()}"
                    )
            elif "mods.toml" in zipinfo.filename:
                try:
                    config = toml.loads(adjust(zipfile.open(zipinfo.filename).read()))
                    self.name = config["mods"][0]["displayName"]
                    self.version = config["mods"][0]["version"]
                    self.description = config["mods"][0].get("description", "")
                    try:
                        self.authors = [config["mods"][0]["authors"]]
                    except KeyError:
                        self.authors = [config.get("authors", "")]

                    self.url = config["mods"][0].get("displayURL", "")

                    if "${file.jarVersion}" in self.version:
                        MANIFESTMF = (
                            zipfile.open("META-INF/MANIFEST.MF")
                            .read()
                            .decode("utf-8")
                            .split("\n")
                        )
                        for i in MANIFESTMF:
                            if "Implementation-Version" in i:
                                self.version = self.version.replace(
                                    "${file.jarVersion}", i.split(":")[-1].strip()
                                )
                                break
                except:
                    logging.error(
                        f"{self.name}: 从{zipinfo.filename}中获取模组信息失败:\n{traceback.format_exc()}"
                    )
            elif ".info" in zipinfo.filename:
                try:
                    config = json.loads(adjust(zipfile.open(zipinfo.filename).read()))
                    if isinstance(config, list):
                        config = config[0]
                    else:
                        config = config["modList"][0]
                    self.name = config.get("name", "")
                    self.version = config.get("version", "")
                    self.description = config.get("description", "")
                    if "authorList" in config:
                        self.authors = config["authorList"]
                    elif "authors" in config:
                        self.authors = config["authors"]
                    self.url = config.get("url", "")
                except:
                    logging.error(
                        f"{self.name}: 从{zipinfo.filename}中获取模组信息失败:\n{traceback.format_exc()}"
                    )

        self.authors = list(itertools.chain(self.authors))

    def enable(self):
        name, ext = os.path.splitext(self.path)
        if ext != ".disabled":
            return
        os.rename(self.path, name)
        self.path = name

    def disable(self):
        _, ext = os.path.splitext(self.path)
        if ext != ".jar":
            return
        new_path = f"{self.path}.disabled"
        os.rename(self.path, new_path)
        self.path = new_path

    def delete(self):
        os.remove(self.path)

    @property
    def is_disabled(self):
        return os.path.splitext(self.path)[1] == ".disabled"
        return os.path.splitext(self.path)[1] == ".disabled"
