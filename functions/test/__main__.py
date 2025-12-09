import sys
import threading

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from qfluentwidgets import PushButton

import resources as _
from fmcllib.task import create_task, modify_task, remove_task


class Test(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("测试"))
        self.setLayout(QVBoxLayout())

        self.test_task_button = PushButton(self.tr("任务"))
        self.test_task_button.clicked.connect(
            lambda: threading.Thread(target=self.task, daemon=True).start()
        )
        self.layout().addWidget(self.test_task_button)

    def task(self):
        task_id = create_task("Infinite").unwrap()
        n = 10000
        for i in range(n):
            modify_task(task_id, "progress", i / n)
        remove_task(task_id)


app = QApplication(sys.argv)
test = Test()
test.show()
sys.exit(app.exec())
