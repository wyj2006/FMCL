from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class Searcher(QWidget):
    searchFinished = pyqtSignal(list)  # list[QWidget]

    def search(self, query: str):
        pass
