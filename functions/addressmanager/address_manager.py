from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QTableWidgetItem, QWidget
from qfluentwidgets import FluentIcon
from ui_address_manager import Ui_AddressManager

from fmcllib.address import getall_address


class AddressManager(QWidget, Ui_AddressManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.GLOBE.icon())

        self.viewer.setHorizontalHeaderLabels([self.tr("名称"), self.tr("地址")])

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(1000)

    def refresh(self):
        registered = getall_address()
        self.viewer.setRowCount(len(registered))
        for i, (name, value) in enumerate(registered.items()):
            for j, v in enumerate([name, value["address"]]):
                item = QTableWidgetItem(v)
                item.setToolTip(v)
                self.viewer.setItem(i, j, item)
