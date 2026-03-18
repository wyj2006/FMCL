import json
import threading
from typing import Optional, TypedDict

from result import Err, Ok, Result

from fmcllib.address import get_service_connection
from fmcllib.wrapper import safe_function

client = get_service_connection("utils")
lock = threading.Lock()


class AssetInfo(TypedDict):
    url: str
    name: str
    browser_download_url: str


class LatestInfo(TypedDict):
    tag_name: str
    assets: list[AssetInfo]
    body: str


@safe_function(lock)
def check_update() -> Result[Optional[LatestInfo], str]:
    client.sendall(b"check-update\0")
    result = json.loads(client.recv(1024 * 1024))

    if result != None and "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result)


@safe_function(lock)
def apply_update(new_version_path: str) -> Result[None, str]:
    client.sendall(f'apply-update "{new_version_path}"\0'.encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def quit():
    client.sendall(b"quit\0")


@safe_function(lock)
def restart() -> Result[None, str]:
    client.sendall(b"restart\0")
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)
