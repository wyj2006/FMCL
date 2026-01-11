from PyQt6.QtCore import QDir, QSize, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QListWidgetItem

from .ui_icon_selector import Ui_IconSelector


class IconSelector(QDialog, Ui_IconSelector):
    user_icon_paths = set()

    def __init__(self, cur_icon_path: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cur_icon_path = cur_icon_path

        self.icon_paths = list(
            map(
                lambda x: x.filePath(),
                QDir(":/image").entryInfoList(["*.png", "*.jpg", "*.jpeg", ".bmp"]),
            )
        )
        if self.cur_icon_path not in self.icon_paths:
            self.user_icon_paths.add(self.cur_icon_path)
        self.icon_paths = list(self.user_icon_paths) + self.icon_paths

        for icon_path in self.icon_paths:
            item = QListWidgetItem()
            item.setSizeHint(QSize(80, 80))
            item.setText(icon_path)
            item.setToolTip(icon_path)
            item.setIcon(QIcon(icon_path))
            self.icon_list.addItem(item)

    @pyqtSlot(QListWidgetItem)
    def on_icon_list_itemDoubleClicked(self, item: QListWidgetItem):
        self.icon_path = item.text()
        self.accept()

    def exec(self):
        if super().exec() and self.icon_list.currentItem() != None:
            self.icon_path = self.icon_list.currentItem().text()
            return 1
        else:
            return 0
