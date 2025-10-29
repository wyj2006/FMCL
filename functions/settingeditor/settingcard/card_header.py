from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon

from .ui_card_header import Ui_CardHeader


class CardHeader(QWidget, Ui_CardHeader):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.delete_button.setIcon(FluentIcon.DELETE.icon())
        self.moveup_button.setIcon(FluentIcon.UP.icon())
        self.movedown_button.setIcon(FluentIcon.DOWN.icon())
