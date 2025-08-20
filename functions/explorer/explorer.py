from PyQt5.QtWidgets import QWidget
from ui_explorer import Ui_Explorer


class Explorer(QWidget, Ui_Explorer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
