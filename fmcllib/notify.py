import json
import logging
import threading
import traceback
from socket import AF_INET, SOCK_DGRAM, socket
from time import time

from result import Err, Ok, Result

from fmcllib.address import get_service_connection
from fmcllib.wrapper import safe_function

client = get_service_connection("notify")
lock = threading.Lock()

receiver = socket(AF_INET, SOCK_DGRAM)
receiver.bind(("127.0.0.1", 0))
subscribed = False
subscribers: list[Subscriber] = []


class Subscriber:
    def __init__(self):
        subscribers.append(self)

    def on_setting_valuechanged(self, key: str):
        pass

    def on_setting_defaultvaluechanged(self, key: str):
        pass

    def on_setting_attrchanged(self, key: str):
        pass

    def on_setting_created(self, key: str):
        pass


@safe_function(lock)
def subscribe(address: str) -> Result[None, str]:
    client.sendall(f"subscribe {address}\0".encode())
    result = json.loads(client.recv(1024 * 1024))

    if "error_msg" in result:
        return Err(result["error_msg"])
    return Ok(None)


subscribe(f"127.0.0.1:{receiver.getsockname()[1]}").unwrap()


def receive():
    while True:
        try:
            data = json.loads(receiver.recv(1024 * 1024))
            for subscriber in subscribers:
                if "key" in data and "kind" in data:
                    match data["kind"]:
                        case "ValueChanged":
                            subscriber.on_setting_valuechanged(data["key"])
                        case "DefaultValueChanged":
                            subscriber.on_setting_defaultvaluechanged(data["key"])
                        case "AttrChanged":
                            subscriber.on_setting_attrchanged(data["key"])
                        case "Created":
                            subscriber.on_setting_created(data["key"])
        except:
            logging.error(traceback.format_exc())


threading.Thread(target=receive, daemon=True).start()
