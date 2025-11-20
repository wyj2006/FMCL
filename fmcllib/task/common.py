import json
from typing import TypedDict

from result import Err, Ok, Result

from fmcllib.address import get_service_connection

client = get_service_connection("task")


class TaskDict(TypedDict):
    id: str
    name: str
    progress: float
    current_work: str
    parent: int
    children: list[int]


def create_task(name: str, parent=0) -> Result[int, str]:
    client.sendall(f'create "{name.replace('"','\\"')}" {parent}\0'.encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result["id"])


def remove_task(id: int) -> Result[None, str]:
    client.sendall(f"remove {id}\0".encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


def modify_task(id: int, attr_name: str, value) -> Result[None, str]:
    client.sendall(
        f'modify {id} {attr_name} "{str(value).replace('"','\\"')}"\0'.encode()
    )
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


def getall_task() -> dict[str, TaskDict]:
    client.sendall(f"getall\0".encode())
    return json.loads(client.recv(1024 * 1024))


def get_task(id: int) -> Result[TaskDict, str]:
    client.sendall(f"get {id}\0".encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result)
