import sys

from java_manager import JavaManager
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = QApplication(sys.argv)
java_manager = JavaManager()
java_manager.installEventFilter(
    WindowSource(
        java_manager,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(java_manager)
window.show()
sys.exit(app.exec())
