import qtawesome as qta
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QTreeWidgetItem, QWidget
from ui_task_manager import Ui_TaskManager

from fmcllib.task import getall_task


class TaskManager(QWidget, Ui_TaskManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("ei.tasks"))

        self.task_items: dict[int, QTreeWidgetItem] = {0: None}

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(1000)

    def refresh(self):
        exist_task = []
        for task in getall_task().values():
            exist_task.append(task)
            if task["parent"] not in self.task_items:
                continue
            if task["id"] in self.task_items:
                continue
            item = QTreeWidgetItem(self.task_items[task["parent"]])
            item.setText(0, str(task["id"]))
            item.setText(1, task["name"])
            item.setText(2, str(task["progress"]))
            item.setText(3, task["current_work"])
            self.task_view.addTopLevelItem(item)
            self.task_items[task["id"]] = item
        for task_id in tuple(self.task_items):
            if task_id not in exist_task:
                self.task_items.pop(task_id)
