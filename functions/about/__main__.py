import sys

from about import About
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = QApplication(sys.argv)
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
