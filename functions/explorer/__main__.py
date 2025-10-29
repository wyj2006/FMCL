import sys

from explorer import Explorer
from PyQt6.QtGui import QIcon

import resources as _
from fmcllib.single_application import SingleApplication
from fmcllib.window import Window

window = None
explorer = None


def handle():
    global window, explorer
    while explorer == None:
        pass
    if explorer.isVisible():
        return
    if isinstance(explorer.window(), Window):
        window = explorer.window()
        window.show()
        return
    window = Window(explorer)
    window.show()


def main():
    global window, explorer
    app.setWindowIcon(QIcon(":/icon/fmcl.ico"))
    explorer = Explorer()
    window = Window(explorer)
    window.show()


app = SingleApplication(sys.argv)
app.firstAppConfirmed.connect(main)
app.otherAppConfirmed.connect(exit)
app.otherAppRun.connect(handle)
app.check("explorer")
sys.exit(app.exec())
