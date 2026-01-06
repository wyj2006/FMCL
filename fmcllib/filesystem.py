import json
import os
import threading
from typing import Callable, TypedDict

from result import Err, Ok, Result

from fmcllib.address import get_service_connection
from fmcllib.wrapper import safe_function

client = get_service_connection("filesystem")
current_dir = "/"
lock = threading.Lock()


class FileInfo(TypedDict):
    name: str
    path: str
    native_paths: list[str]
    error_msg: str


@safe_function(lock)
def fileinfo(path: str) -> Result[FileInfo, str]:
    client.sendall(f"fileinfo {os.path.join(current_dir,path)}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result)


@safe_function(lock)
def listdir(path: str) -> Result[list[str], str]:
    client.sendall(f"listdir {os.path.join(current_dir,path)}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result["names"])


@safe_function(lock)
def mount_native(path: str, native_path: str) -> Result[None, str]:
    client.sendall(
        f"mount-native {os.path.join(current_dir,path)} {native_path}\0".encode()
    )
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def unmount_native(path: str, native_path: str) -> Result[None, str]:
    client.sendall(
        f"unmount-native {os.path.join(current_dir,path)} {native_path}\0".encode()
    )
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def mount(target_path, source_path: str) -> Result[None, str]:
    client.sendall(
        f"mount {os.path.join(current_dir,target_path)} {os.path.join(current_dir,source_path)}\0".encode()
    )
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def unmount(target_path, source_path: str) -> Result[None, str]:
    client.sendall(
        f"unmount {os.path.join(current_dir,target_path)} {os.path.join(current_dir,source_path)}\0".encode()
    )
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
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
