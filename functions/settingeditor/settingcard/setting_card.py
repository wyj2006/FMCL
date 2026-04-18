from typing import Any, Callable, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from fmcllib.notify import Subscriber


class CardSubscriber(Subscriber):
    def __init__(self, card: SettingCard):
        super().__init__()
        self.card = card

    def on_setting_value_changed(self, key):
        if self.card.key != key:
            return
        self.card.valueChanged.emit(self.card.getter())

    def on_setting_attr_changed(self, key):
        if self.card.key != key:
            return
        self.card.attrChanged.emit(self.card.attr_getter())


class SettingCard(QWidget):
    valueChanged = pyqtSignal(object)
    attrChanged = pyqtSignal(str, object)

    def __init__(
        self,
        getter: Callable[[], Any],
        attr_getter: Callable[[str, Optional[Any]], Any],
        setter: Callable[[Any], None] = lambda *_: None,
        attr_setter: Callable[[str, Any], None] = lambda *_: None,
        key=None,  # 只用于过滤通知
        parent=None,
    ):
        super().__init__(parent)
        self.getter = getter
        self.attr_getter = attr_getter
        self.setter = setter
        self.attr_setter = attr_setter

        self.valueChanged.connect(self.setter)
        self.attrChanged.connect(self.attr_setter)

        self.key = key
        self.subscriber = CardSubscriber(self)

        self.postInit()

    def postInit(self):
        """子类的初始化方法"""
