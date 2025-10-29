from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import LineEdit

from .setting_card import SettingCard


class StringCard(SettingCard):
    def _init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.line_edit = LineEdit()
        self.line_edit.setText(self.getter())
        self.line_edit.editingFinished.connect(
            lambda: self.valueChanged.emit(self.line_edit.text())
        )
        layout.addWidget(self.line_edit)

        self.valueChanged.connect(self.line_edit.setText)
