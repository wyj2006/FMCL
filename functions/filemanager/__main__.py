import sys

from file_manager import FileManager
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.mirror import MirrorFilter
from fmcllib.window import Window

app = QApplication(sys.argv)
file_manager = FileManager()
file_manager.installEventFilter(
    MirrorFilter(
        file_manager,
        "window",
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(file_manager)
window.show()
sys.exit(app.exec())
