import sys

from PyQt6.QtWidgets import QApplication
from task_manager import TaskManager

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = QApplication(sys.argv)
task_manager = TaskManager()
task_manager.installEventFilter(
    WindowSource(
        task_manager,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(task_manager)
window.show()
sys.exit(app.exec())
