import traceback

from PyQt6.QtWidgets import QDialog, QDialogButtonBox
from ui_authlib_injector_adder import Ui_AuthlibInjectorAdder

from fmcllib import show_qerrormessage
from fmcllib.account import add_authlib_injector
from fmcllib.setting import Setting


class AuthlibInjectorAdder(QDialog, Ui_AuthlibInjectorAdder):
    def __init__(self, setting: Setting, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setting = setting

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.url.text())
        )
        self.url.textChanged.connect(
            lambda: self.buttonBox.button(
                QDialogButtonBox.StandardButton.Ok
            ).setEnabled(bool(self.url.text()))
        )

    def exec(self):
        ret = super().exec()
        if ret == 1:
            server_url = self.url.text()
            try:
                add_authlib_injector(server_url, self.setting)
            except:
                show_qerrormessage(
                    self.tr("无法添加服务器"),
                    traceback.format_exc(),
                    self,
                )
        return ret
