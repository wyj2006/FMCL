import json
import os
import sys
from typing import TypedDict

from result import Err, Ok, Result

from fmcllib.safe_socket import SafeSocket


class AddressRegisterInfo(TypedDict):
    name: str
    ip: str
    port: str


def get_address(name: str) -> Result[tuple[str, int], str]:
    if name == "address":  # 自己的地址
        return Ok(
            ("127.0.0.1", int(os.environ.get("FMCL_ADDRESS_SERVER_PORT", "1024")))
        )

    client.sendall(f"get {name}\0".encode())
    result: AddressRegisterInfo = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok((result["ip"], int(result["port"])))


def get_service_connection(service_name: str) -> SafeSocket:
    """
    获得与服务的连接
    包含了与服务进行连接的前置工作
    """
    import __main__

    socket = SafeSocket()
    socket.connect(get_address(service_name).unwrap())
    # 用来区分与服务的不同连接
    socket.sendall(
        f"{getattr(sys,'service_connection_id',os.path.basename(os.path.dirname(__main__.__file__)))}\0".encode()
    )
    socket.recv(1024)  # 等待服务器回应
    return socket


client = get_service_connection("address")


def register_address(name: str, ip: str, port: int):
    client.sendall(f"register {name} {ip} {port}\0".encode())


def unregister_address(name: str):
    client.sendall(f"unregister {name}\0".encode())


def getall_address() -> dict[str, AddressRegisterInfo]:
    client.sendall(f"getall\0".encode())
    return json.loads(client.recv(1024 * 1024))
