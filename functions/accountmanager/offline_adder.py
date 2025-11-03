from uuid import UUID, uuid5

from PyQt6.QtWidgets import QDialog, QDialogButtonBox
from ui_offline_adder import Ui_OfflineAdder

from fmcllib.account import DEFAULT_SKIN_PATH, add_account


class OfflineAdder(QDialog, Ui_OfflineAdder):
    def __init__(self, setting, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setting = setting

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.player_name.text())
        )
        self.player_name.textChanged.connect(
            lambda: self.buttonBox.button(
                QDialogButtonBox.StandardButton.Ok
            ).setEnabled(bool(self.player_name.text()))
        )

    def exec(self):
        ret = super().exec()
        if ret == 1:
            player_name = self.player_name.text()
            uuid = self.uuid.text()
            if not uuid:
                uuid = str(uuid5(UUID("0" * 32), player_name))
            uuid = uuid.replace("-", "")
            add_account(
                {
                    "method": "offline",
                    "player_name": player_name,
                    "uuid": uuid,
                    "skin": {"url": "qrc" + DEFAULT_SKIN_PATH},
                },
                self.setting,
            )
        return ret
