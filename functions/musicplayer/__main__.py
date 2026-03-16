import sys

from music_player import MusicPlayer

import resources as _
from fmcllib.application import SingleApplication
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

window = None
music_player = None


def handle():
    global window, music_player
    try:
        if music_player.isVisible():
            return
        music_player.show()
        if isinstance(music_player.window(), Window):
            window = music_player.window()
            window.show()
            window.activateWindow()
            return
        window = Window(music_player)
        window.show()
    except RuntimeError:
        main()


def main():
    global window, music_player
    music_player = MusicPlayer()
    music_player.installEventFilter(
        WindowSource(
            music_player,
            lambda w: Window(w).show(),
        )
    )
    window = Window(music_player)
    window.show()


app = SingleApplication(sys.argv)
app.firstAppConfirmed.connect(main)
app.otherAppConfirmed.connect(exit)
app.otherAppRun.connect(handle)
app.check("music_player")
sys.exit(app.exec())
