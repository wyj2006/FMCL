from PyQt6.QtGui import QAction

from .base import Mirror, Source
from .common import icon_to_data


class ActionSource(Source):
    def __init__(self, parent, name=None):
        super().__init__(parent, "action", name)

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("ready",):
                aciton: QAction = self.parent()
                self.socket.write(f"settext {aciton.text()}\0".encode())
                self.socket.write(f"seticon {icon_to_data(aciton.icon())}\0".encode())
            case ("trigger",):
                action: QAction = self.parent()
                action.trigger()


class ActionMirror(Mirror, QAction):
    def __init__(self, name: str):
        super().__init__(name)
        self.triggered.connect(lambda: self.socket.write(b"trigger\0"))
