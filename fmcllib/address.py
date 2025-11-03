import json
import os
from typing import TypedDict

from result import Err, Ok, Result

from fmcllib.safe_socket import SafeSocket

port = int(os.environ.get("FMCL_ADDRESS_SERVER_PORT", "1024"))
address = ("127.0.0.1", port)

client = SafeSocket()
client.connect(address)


class AddressRegisterInfo(TypedDict):
    name: str
    ip: str
    port: str


def register_address(name: str, ip: str, port: int):
    client.sendall(f"register {name} {ip} {port}\0".encode())


def unregister_address(name: str):
    client.sendall(f"unregister {name}\0".encode())


def get_address(name: str) -> Result[tuple[str, int], str]:
    client.sendall(f"get {name}\0".encode())
    result: AddressRegisterInfo = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok((result["ip"], int(result["port"])))


def getall_address() -> dict[str, AddressRegisterInfo]:
    client.sendall(f"getall\0".encode())
    return json.loads(client.recv(1024 * 1024))
