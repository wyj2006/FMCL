import sys
import threading
import time

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from qfluentwidgets import PushButton

import resources as _
from fmcllib.task import (
    ATTR_CURRENT_WORK,
    ATTR_PROGRESS,
    Task,
    modify_task,
)


class Test(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("测试"))
        self.setLayout(QVBoxLayout())

        self.test_single_task_button = PushButton(self.tr("单任务"))
        self.test_single_task_button.clicked.connect(
            lambda: threading.Thread(target=self.single_task, daemon=True).start()
        )
        self.layout().addWidget(self.test_single_task_button)

        self.test_parent_task_button = PushButton(self.tr("父子任务"))
        self.test_parent_task_button.clicked.connect(
            lambda: threading.Thread(target=self.parent_task, daemon=True).start()
        )
        self.layout().addWidget(self.test_parent_task_button)

    def single_task(self, parent=0, n=10000):
        with Task("Single", parent) as task_id:
            for i in range(n):
                modify_task(task_id, ATTR_PROGRESS, i / n)

    def parent_task(self):
        with Task("Parent") as parent_task:
            self.single_task(parent_task, 50000)
            modify_task(parent_task, ATTR_CURRENT_WORK, "waiting")
            time.sleep(5)


app = QApplication(sys.argv)
test = Test()
test.show()
sys.exit(app.exec())
