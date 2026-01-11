import argparse
import sys

from game_manager import GameManager
from PyQt6.QtWidgets import QApplication, QFileDialog

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

tr = QApplication.translate

app = QApplication(sys.argv)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--instance-path",
    help=tr("GameMonitor", "游戏实例的路径"),
    default=None,
)
args = parser.parse_args()

if args.instance_path == None:
    instance_path = QFileDialog.getExistingDirectory()
    if not instance_path:
        exit()
else:
    instance_path = args.instance_path

game_manager = GameManager(instance_path)
game_manager.installEventFilter(
    WindowSource(
        game_manager,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(game_manager)
window.show()
sys.exit(app.exec())
