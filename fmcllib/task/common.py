import json
import threading
from typing import TypedDict

from result import Err, Ok, Result

from fmcllib.address import get_service_connection
from fmcllib.wrapper import safe_function

client = get_service_connection("task")
lock = threading.Lock()


class TaskDict(TypedDict):
    id: str
    name: str
    progress: float
    current_work: str
    parent: int
    children: list[int]


@safe_function(lock)
def create_task(name: str, parent_task_id=0) -> Result[int, str]:
    client.sendall(f'create "{name.replace('"','\\"')}" {parent_task_id}\0'.encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result["id"])


@safe_function(lock)
def remove_task(id: int) -> Result[None, str]:
    client.sendall(f"remove {id}\0".encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def modify_task(id: int, attr_name: str, value) -> Result[None, str]:
    client.sendall(
        f'modify {id} {attr_name} "{str(value).replace('"','\\"')}"\0'.encode()
    )
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def getall_task() -> dict[str, TaskDict]:
    client.sendall(f"getall\0".encode())
    return json.loads(client.recv(2**30))


@safe_function(lock)
def get_task(id: int) -> Result[TaskDict, str]:
    client.sendall(f"get {id}\0".encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result)
