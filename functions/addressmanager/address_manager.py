from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QTableWidgetItem, QWidget
from qfluentwidgets import FluentIcon
from ui_address_manager import Ui_AddressManager

from fmcllib.address import AddressRegisterInfo, getall_address


class AddressManager(QWidget, Ui_AddressManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.GLOBE.icon())

        self.viewer.setHorizontalHeaderLabels(
            [self.tr("名称"), self.tr("地址"), self.tr("端口")]
        )

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(1000)

    def refresh(self):
        registered: dict[str, AddressRegisterInfo] = getall_address()
        self.viewer.setRowCount(len(registered))
        for i, (name, value) in enumerate(registered.items()):
            self.viewer.setItem(i, 0, QTableWidgetItem(name))
            self.viewer.setItem(i, 1, QTableWidgetItem(value["ip"]))
            self.viewer.setItem(i, 2, QTableWidgetItem(value["port"]))
