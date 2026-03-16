import argparse
import sys
import traceback

from nbt_viewer import NBTViewer
from nbtlib import load
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QFileDialog

import resources as _
from fmcllib import show_qerrormessage
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

translate = QCoreApplication.translate

parser = argparse.ArgumentParser()
parser.add_argument(
    "--path",
    help=translate("NBTViewer", "NBT文件路径"),
    default=None,
)


app = Application(sys.argv)

args = parser.parse_args()
if args.path != None:
    path = args.path
else:
    path, _ = QFileDialog.getOpenFileName(caption=translate("NBTViewer", "选择NBT文件"))

if not path:
    exit(0)

try:
    nbt_file = load(path)
except:
    show_qerrormessage(translate("NBTViewer", "无法加载NBT文件"), traceback.format_exc())
    exit(1)

nbt_viewer = NBTViewer(nbt_file)
nbt_viewer.installEventFilter(
    WindowSource(
        nbt_viewer,
        on_detach=lambda w: Window(w).show(),
    )
)

window = Window(nbt_viewer)
window.show()

sys.exit(app.exec())
