import sys

from about import About

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = Application(sys.argv)
about = About()
about.installEventFilter(
    WindowSource(
        about,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(about)
window.show()
sys.exit(app.exec())
