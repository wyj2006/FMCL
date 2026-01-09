import logging
import os
import traceback
from typing import TypedDict

import javaproperties


class JavaInfo(TypedDict):
    path: str
    implementor: str
    arch: str
    version: str


def get_java_info(java_path: str) -> JavaInfo:
    """
    java_path是java.exe的路径
    """
    path = os.path.dirname(java_path)  # java.exe所处的目录
    properties = javaproperties.load(
        open(os.path.join(path, "..", "release"), encoding="utf-8")
    )
    return {
        "path": java_path.replace("\\", "/"),
        # 这些属性有引号
        "implementor": eval(properties["IMPLEMENTOR"]),
        "arch": eval(properties["OS_ARCH"]),
        "version": eval(properties["JAVA_VERSION"]),
    }


def auto_find_java() -> list[JavaInfo]:
    """自动查找Java"""
    javas: list[JavaInfo] = []
    for _, val in os.environ.items():
        for path in val.split(";"):
            try:
                if not os.path.exists(path):
                    continue
                if os.path.isfile(path):
                    continue
                logging.info(f"在{path}中查找Java")
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    if not os.path.isfile(full_path):
                        continue
                    if name != "java.exe":
                        continue
                    java_path = os.path.join(path, name)
                    logging.info(f"找到Java: {java_path}")
                    javas.append(get_java_info(java_path))
            except:
                logging.error(f"尝试查找'{path}'出错: {traceback.format_exc()}")
    return javas
