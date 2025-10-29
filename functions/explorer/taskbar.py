from typing import Callable

from qfluentwidgets import TabBar, TabItem


class TaskBar(TabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAddButtonVisible(False)
        self.itemLayout.setContentsMargins(5, 0, 5, 0)
        self.item_onclick: dict[TabItem, Callable] = {}
        self.mouse_moved = False
        self.window_pos = None

    def insertTab(self, index, routeKey, text, icon=None, onClick=None):
        item = super().insertTab(index, routeKey, text, icon, onClick)
        item.setFixedHeight(self.height())
        item.pressed.disconnect(self._onItemPressed)
        item.released.connect(self._onItemReleased)
        if onClick:
            self.item_onclick[item] = onClick
            item.pressed.disconnect(onClick)
        else:
            self.item_onclick[item] = lambda: None
        return item

    def _onItemReleased(self):
        index = self.items.index(self.sender())
        self.tabBarClicked.emit(index)

        if index != self.currentIndex():
            self.setCurrentIndex(index)
            self.currentChanged.emit(index)

        if not self.mouse_moved:
            self.item_onclick[self.sender()]()

    def mousePressEvent(self, e):
        self.mouse_moved = False
        self.window_pos = self.window().pos()
        return super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        self.mouse_moved = self.window().pos() != self.window_pos
        return super().mouseMoveEvent(e)
