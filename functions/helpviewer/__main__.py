import sys

from help_viewer import HelpViewer

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = Application(sys.argv)
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
