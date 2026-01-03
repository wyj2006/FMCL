from abc import abstractmethod
from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class GameSelector(QWidget):
    versionSelected = pyqtSignal(str)
    selected_version: str
    display_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.versionSelected.connect(
            lambda version: setattr(self, "selected_version", version)
        )

    @abstractmethod
    def download(self, name: str, *args, **kwargs) -> Callable: ...
    @abstractmethod
    def install(self, name: str, *args, **kwargs) -> Callable: ...
