import json
import logging
import threading
from functools import wraps
from typing import Callable, TypedDict

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


lock = threading.Lock()


def safe_function[T](func: Callable[..., T]):

    @wraps(func)
    def inner(*args, **kwargs) -> T:
        lock.acquire()
        try:
            ret = func(*args, **kwargs)
        except:
            raise
        finally:
            lock.release()
        return ret

    return inner


@safe_function
def create_task(name: str, parent_task_id=0) -> Result[int, str]:
    client.sendall(f'create "{name.replace('"','\\"')}" {parent_task_id}\0'.encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result["id"])


@safe_function
def remove_task(id: int) -> Result[None, str]:
    client.sendall(f"remove {id}\0".encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function
def modify_task(id: int, attr_name: str, value) -> Result[None, str]:
    client.sendall(
        f'modify {id} {attr_name} "{str(value).replace('"','\\"')}"\0'.encode()
    )
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function
def getall_task() -> dict[str, TaskDict]:
    client.sendall(f"getall\0".encode())
    return json.loads(client.recv(2**30))


@safe_function
def get_task(id: int) -> Result[TaskDict, str]:
    client.sendall(f"get {id}\0".encode())
    result = json.loads(client.recv(1024 * 1024))
    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result)
