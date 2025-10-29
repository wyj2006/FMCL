from PyQt6.QtGui import QAction

from .base import MirrorBase


class MirrorAction(MirrorBase, QAction):
    def __init__(self, name: str):
        super().__init__(name)
        self.triggered.connect(lambda: self.socket.write(b"trigger\0"))
