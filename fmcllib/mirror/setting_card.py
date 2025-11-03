import base64
import json

from .widget import WidgetSource


class SettingCardSource(WidgetSource):
    KIND = "setting_card"

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("ready",):
                self.parent().getter = self.getter
                self.parent().attr_getter = self.attr_getter
                self.parent().setter = self.setter
                self.parent().attr_setter = self.attr_setter
        return super()._handleRecvData(args)

    def getter(self):
        self.socket.write(b"get_setting\0")
        return json.loads(bytes(self.socket.readAll()))

    def attr_getter(self, attr_name, default=None):
        self.socket.write(
            f"get_setting_attr {attr_name} {base64.b64encode(json.dumps(default).encode()).decode()}\0".encode()
        )
        return json.loads(bytes(self.socket.readAll()))

    def setter(self, value):
        self.socket.write(
            f"set_setting {base64.b64encode(json.dumps(value).encode()).decode()}\0".encode()
        )

    def attr_setter(self, attr_name, value):
        return self.socket.write(
            f"set_setting_attr {attr_name} {base64.b64encode(json.dumps(value).encode()).decode()}\0".encode()
        )
