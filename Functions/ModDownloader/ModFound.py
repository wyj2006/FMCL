import multitasking
from Core import Requests
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget

from .ui_ModFound import Ui_ModFound


class ModFound(QWidget, Ui_ModFound):
    def __init__(self, foundmod: dict):
        super().__init__()
        self.setupUi(self)
        self.foundmod = foundmod
        self.l_title.setText(self.foundmod["title"])
        self.l_description.setText(self.foundmod["description"])
        self.setIcon()

    @multitasking.task
    def setIcon(self):
        r = Requests.get(self.foundmod["icon_url"], try_time=-1, timeout=5)
        image = QImage.fromData(r.content)
        pixmap = QPixmap.fromImage(image)
        self.l_icon.setPixmap(pixmap.scaled(64, 64))
