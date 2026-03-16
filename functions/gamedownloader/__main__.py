import sys

import __main__
from game_downloader import GameDownloader

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = Application(sys.argv)
game_downloader = GameDownloader()
game_downloader.installEventFilter(
    WindowSource(
        game_downloader,
        # 防止被销毁, 否则分离后会出问题(但似乎目前只有GameDownloader出现了这个问题)
        on_detach=lambda w: (setattr(__main__, "window", Window(w)), window.show()),
    )
)
window = Window(game_downloader)
window.show()
sys.exit(app.exec())
