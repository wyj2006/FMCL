import json
import os
from typing import Callable, TypedDict

from result import Err, Ok, Result

from fmcllib.address import get_service_connection

client = get_service_connection("filesystem")
current_dir = "/"


class FileInfo(TypedDict):
    name: str
    path: str
    native_paths: list[str]
    error_msg: str


def fileinfo(path: str) -> Result[FileInfo, str]:
    client.sendall(f"fileinfo {os.path.join(current_dir,path)}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result)


def listdir(path: str) -> Result[list[str], str]:
    client.sendall(f"listdir {os.path.join(current_dir,path)}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result["names"])


def mount_native(path: str, native_path: str) -> Result[None, str]:
    client.sendall(
        f"mount_native {os.path.join(current_dir,path)} {native_path}\0".encode()
    )
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


def unmount_native(path: str, native_path: str) -> Result[None, str]:
    client.sendall(
        f"unmount_native {os.path.join(current_dir,path)} {native_path}\0".encode()
    )
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


def makedirs(path: str) -> Result[None, str]:
    client.sendall(f"makedirs {path}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


def readall[T](path: str, handler: Callable[[list[bytes]], T] = None) -> Result[T, str]:
    """读取path中的所有内容, 并通过handler处理这些内容"""
    match fileinfo(path):
        case Ok(info):
            contents = []
            for native_path in info["native_paths"]:
                if os.path.isfile(native_path):
                    contents.append(open(native_path, mode="rb").read())
            if handler == None:
                return Ok(contents)
            return Ok(handler(contents))
        case Err(e):
            return Err(e)
