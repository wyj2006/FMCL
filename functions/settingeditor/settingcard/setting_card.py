from typing import Any, Callable, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class SettingCard(QWidget):
    valueChanged = pyqtSignal(object)
    attrChanged = pyqtSignal(str, object)

    def __init__(
        self,
        getter: Callable[[], Any],
        attr_getter: Callable[[str, Optional[Any]], Any],
        setter: Callable[[Any], None] = lambda *_: None,
        attr_setter: Callable[[str, Any], None] = lambda *_: None,
        parent=None,
    ):
        super().__init__(parent)
        self.getter = getter
        self.attr_getter = attr_getter
        self.setter = setter
        self.attr_setter = attr_setter

        self.valueChanged.connect(self.setter)
        self.attrChanged.connect(self.attr_setter)

        self.postInit()

    def postInit(self):
        """子类的初始化方法"""
