from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import SpinBox

from .setting_card import SettingCard


class IntCard(SettingCard):
    def _init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.span_box = SpinBox(self)
        self.span_box.setValue(self.getter())
        self.span_box.valueChanged.connect(self.valueChanged.emit)
        layout.addWidget(self.span_box)

        self.valueChanged.connect(self.span_box.setValue)
