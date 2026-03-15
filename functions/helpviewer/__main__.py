import sys

from help_viewer import HelpViewer
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = QApplication(sys.argv)
help_viewer = HelpViewer()
help_viewer.installEventFilter(
    WindowSource(
        help_viewer,
        on_detach=lambda w: Window(w).show(),
    )
)
help_viewer.show()
window = Window(help_viewer)
window.show()
sys.exit(app.exec())
