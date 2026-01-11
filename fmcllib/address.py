import json
import os
import socket
import sys
import threading
from typing import TypedDict

from result import Err, Ok, Result

from fmcllib.wrapper import safe_function

lock = threading.Lock()


class AddressRegisterInfo(TypedDict):
    name: str
    address: str


def parse_address(address: str) -> tuple[str, int]:
    host, port = address.split(":")
    return (host, int(port))


@safe_function(lock)
def get_address(name: str) -> Result[str, str]:
    if name == "address":  # 自己的地址
        return Ok(f"127.0.0.1:{os.environ.get("FMCL_ADDRESS_SERVER_PORT", "1024")}")

    client.sendall(f"get {name}\0".encode())
    result: AddressRegisterInfo = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(result["address"])


def get_service_connection(service_name: str) -> socket.socket:
    """
    获得与服务的连接
    包含了与服务进行连接的前置工作
    """
    import __main__

    s = socket.socket()
    s.connect(parse_address(get_address(service_name).unwrap()))
    # 用来区分与服务的不同连接
    s.sendall(
        f"{getattr(sys,'service_connection_id',os.path.basename(os.path.dirname(__main__.__file__)))}\0".encode()
    )
    s.recv(1024)  # 等待服务器回应
    return s


client = get_service_connection("address")


@safe_function(lock)
def register_address(name: str, address: str) -> Result[None, str]:
    client.sendall(f"register {name} {address}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


@safe_function(lock)
def unregister_address(name: str):
    client.sendall(f"unregister {name}\0".encode())
    client.recv(1024 * 1024)  # 一定是空字典


@safe_function(lock)
def getall_address() -> dict[str, AddressRegisterInfo]:
    client.sendall(f"getall\0".encode())
    return json.loads(client.recv(1024 * 1024))
