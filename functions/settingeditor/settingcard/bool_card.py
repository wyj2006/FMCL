from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import SwitchButton

from .setting_card import SettingCard


class BoolCard(SettingCard):
    def _init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.switch_button = SwitchButton()
        self.switch_button.setOnText("True")
        self.switch_button.setOffText("False")
        self.switch_button.setChecked(self.getter())
        self.switch_button.indicator.toggled.connect(
            lambda: self.valueChanged.emit(self.switch_button.indicator.isChecked())
        )
        layout.addWidget(self.switch_button)

        self.valueChanged.connect(self.switch_button.setChecked)
