from qframelesswindow import FramelessWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Window(FramelessWindow):
    def __init__(self, client: QWidget):
        super().__init__()
        self.client = client
        self.resize(self.client.size() + self.titleBar.size())

    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        # 绘制标题
        painter.setFont(QFont("Microsoft YaHei", 10))
        title = self.windowTitle()
        painter.drawText(self.geometry(), Qt.AlignmentFlag.AlignCenter, title)
        return super().paintEvent(a0)
