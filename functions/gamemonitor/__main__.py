import argparse
import sys

from game_monitor import GameMonitor
from PyQt6.QtWidgets import QApplication, QFileDialog

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

tr = QApplication.translate

app = QApplication(sys.argv)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--game-path",
    help=tr("GameMonitor", "要运行的游戏所在的目录(一般在.minecraft/versions文件夹下)"),
    default=None,
)
args = parser.parse_args()

if args.game_path == None:
    game_path = QFileDialog.getExistingDirectory()
    if not game_path:
        exit()
else:
    game_path = args.game_path

game_monitor = GameMonitor(game_path)
game_monitor.installEventFilter(
    WindowSource(
        game_monitor,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(game_monitor)
window.show()
sys.exit(app.exec())
