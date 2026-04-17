import argparse
import sys

from help_viewer import HelpItem, HelpViewer
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

translate = QCoreApplication.translate

parser = argparse.ArgumentParser()
parser.add_argument(
    "--path",
    help=translate("HelpViewer", "帮助的路径(不是本地路径)"),
    default=None,
)

args = parser.parse_args()
path = args.path

app = Application(sys.argv)
help_viewer = HelpViewer()
help_viewer.installEventFilter(
    WindowSource(
        help_viewer,
        on_detach=lambda w: Window(w).show(),
    )
)

window = Window(help_viewer)
window.show()

if path != None:
    QApplication.processEvents()
    help_viewer.addPage(HelpItem(path))

sys.exit(app.exec())
