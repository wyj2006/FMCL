import sys

from game_downloader import GameDownloader
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = QApplication(sys.argv)
game_downloader = GameDownloader()
game_downloader.installEventFilter(
    WindowSource(
        game_downloader,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(game_downloader)
window.show()
sys.exit(app.exec())
