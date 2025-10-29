from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import PushButton

from .setting_card import SettingCard


class DefaultCard(SettingCard):
    def _init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.button = PushButton(self.tr("在文件中编辑"))
        layout.addWidget(self.button)
