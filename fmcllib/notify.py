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

    def on_setting_value_changed(self, key: str):
        pass

    def on_setting_default_value_changed(self, key: str):
        pass

    def on_setting_attr_changed(self, key: str):
        pass

    def on_setting_created(self, key: str):
        pass

    def on_task_created(self, id: int):
        pass

    def on_task_removed(self, id: int):
        pass

    def on_function_started(self, path: str):
        pass

    def on_function_stopped(self, path: str):
        pass

    def on_address_registered(self, name: str):
        pass

    def on_address_unregistered(self, name: str):
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
                            subscriber.on_setting_value_changed(data["key"])
                        case "DefaultValueChanged":
                            subscriber.on_setting_default_value_changed(data["key"])
                        case "AttrChanged":
                            subscriber.on_setting_attr_changed(data["key"])
                        case "Created":
                            subscriber.on_setting_created(data["key"])
                if "id" in data and "kind" in data:
                    match data["kind"]:
                        case "Created":
                            subscriber.on_task_created(data["id"])
                        case "Removed":
                            subscriber.on_task_removed(data["id"])
                if "path" in data and "kind" in data:
                    match data["kind"]:
                        case "Started":
                            subscriber.on_function_started(data["path"])
                        case "Stopped":
                            subscriber.on_function_stopped(data["path"])
                if "name" in data and "kind" in data:
                    match data["kind"]:
                        case "Registered":
                            subscriber.on_address_registered(data["name"])
                        case "Unregistered":
                            subscriber.on_address_unregistered(data["name"])
        except:
            logging.error(traceback.format_exc())


receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()
