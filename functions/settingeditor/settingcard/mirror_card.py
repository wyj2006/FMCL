import base64
import json

from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QApplication, QVBoxLayout

from fmcllib.mirror import WidgetMirror

from .setting_card import SettingCard


class MirrorCard(SettingCard):
    def _init(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        setting_card_name = self.attr_getter("setting_card")
        self.mirror = WidgetMirror(setting_card_name)
        self.mirror._handleRecvData = self._handleRecvData
        layout.addWidget(self.mirror)

        QApplication.instance().aboutToQuit.connect(self.mirror.close)

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("getter",):
                self.socket.write(f"{json.dumps(self.getter())}\0".encode())
            case ("attr_getter", attr_name, default):
                default = json.loads(base64.b64decode(default))
                self.socket.write(
                    f"{json.dumps(self.getter(attr_name,default))}\0".encode()
                )
            case ("setter", value):
                value = json.loads(base64.b64decode(value))
                self.setter(value)
            case ("attr_setter", attr_name, value):
                value = json.loads(base64.b64decode(value))
                self.attr_setter(attr_name, value)
        return self.mirror.__class__._handleRecvData(self.mirror, args)

    def event(self, event: QEvent):
        match event.type():
            case QEvent.Type.Close | QEvent.Type.DeferredDelete:
                self.mirror.close()
            case QEvent.Type.Show:
                self.mirror.show()
        return super().event(event)
