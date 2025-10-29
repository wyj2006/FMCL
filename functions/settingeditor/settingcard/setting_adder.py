from PyQt6.QtWidgets import QDialog

from .ui_setting_adder import Ui_SettingAdder


class SettingAdder(QDialog, Ui_SettingAdder):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.attr_editor.setText("{}")

        self.value_editor.saveRequest.connect(
            lambda content: setattr(self, "value", content)
        )
        self.attr_editor.saveRequest.connect(
            lambda content: setattr(self, "attr", content)
        )

    def exec(self):
        return super().exec() and self.value_editor.save() and self.attr_editor.save()
