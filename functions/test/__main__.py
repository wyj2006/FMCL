import sys
import threading
import time

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from qfluentwidgets import PushButton

import resources as _
from fmcllib.task import create_task, modify_task, remove_task


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
        task_id = create_task("Single", parent).unwrap()
        for i in range(n):
            modify_task(task_id, "progress", i / n)
        remove_task(task_id)

    def parent_task(self):
        parent_task = create_task("Parent").unwrap()
        self.single_task(parent_task, 50000)
        modify_task(parent_task, "current_work", "waiting")
        time.sleep(5)
        remove_task(parent_task)


app = QApplication(sys.argv)
test = Test()
test.show()
sys.exit(app.exec())
sys.exit(app.exec())
