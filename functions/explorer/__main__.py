import sys
from PyQt5.QtWidgets import *
from explorer import Explorer
from window import Window

app = QApplication([])
explorer = Explorer()
window = Window(explorer)
window.show()
sys.exit(app.exec())
