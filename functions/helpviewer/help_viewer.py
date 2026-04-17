import json
import os

from PyQt6.QtCore import (
    QAbstractItemModel,
    QCoreApplication,
    QEvent,
    QModelIndex,
    QObject,
    Qt,
    QUrl,
    pyqtSlot,
)
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon
from result import Err, Ok, is_ok
from ui_help_viewer import Ui_HelpViewer

from fmcllib.filesystem import fileinfo, is_dir, listdir

translate = QCoreApplication.translate


class HelpItem:
    def __init__(self, path: str, parent=None):
        self.path = path
        self.name = os.path.basename(path)
        self.parent: HelpItem = parent
        self.page: str = None  # page.qml的路径
        self.children: list[HelpItem] = []

        for name in listdir(self.path).unwrap_or([]):
            path = os.path.join(self.path, name)
            if not is_dir(path).unwrap_or(False):
                continue
            self.children.append(HelpItem(path, self))

        match fileinfo(os.path.join(self.path, "attribute.json")):
            case Ok(t):
                attribute = json.load(open(t["native_paths"][0], encoding="utf-8"))
            case Err(_):
                attribute = {}

        self.name = translate(
            attribute.get("translation_context", ""),
            attribute.get("display_name", self.name),
        )

        if is_ok(result := fileinfo(os.path.join(self.path, "page.qml"))):
            self.page = result.ok_value["native_paths"][0]

    def get_child(self, row):
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def children_count(self):
        return len(self.children)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def data(self, column):
        match column:
            case 0:
                return self.name
        return None


class HelpIndexModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self.root_item = HelpItem("/helps")

    def getItem(self, index: QModelIndex) -> HelpItem:
        if index.isValid():
            return index.internalPointer()
        return self.root_item

    def columnCount(self, parent=QModelIndex()):
        return 1

    def rowCount(self, parent=QModelIndex()):
        return self.getItem(parent).children_count()

    def index(self, row, column, parent=QModelIndex()):
        parent_item = self.getItem(parent)
        child_item = parent_item.get_child(row)
        return self.createIndex(row, column, child_item)

    def parent(self, index: QModelIndex):
        child_item = self.getItem(index)
        parent_item = child_item.parent

        if parent_item == None:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        match role:
            case Qt.ItemDataRole.DisplayRole:
                try:  # 如果产生异常会被认为没有实现data函数
                    return self.getItem(index).data(index.column())
                except:
                    return None
        return None


class HelpViewer(QWidget, Ui_HelpViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.HELP.icon())

        self.splitter.setSizes([100, 300])

        self.pages: dict[QUrl, QQuickWidget] = {}

        self.tabbar.setAddButtonVisible(False)
        self.tabbar.setMovable(True)
        self.tabbar.tabCloseRequested.connect(
            lambda index: self.removePage(
                self.pages[QUrl(self.tabbar.tabItem(index).routeKey())]
            )
        )

        self.help_index.setModel(HelpIndexModel())

    @pyqtSlot(QModelIndex)
    def on_help_index_doubleClicked(self, index: QModelIndex):
        item: HelpItem = index.internalPointer()
        if item.page == None:
            return
        self.addPage(item)

    def eventFilter(self, a0: QObject, a1: QEvent):
        if isinstance(a0, QQuickWidget):
            match a1.type():
                case QEvent.Type.Close | QEvent.Type.DeferredDelete:
                    if a0.source() in self.pages:
                        self.pages.pop(a0.source())
        return super().eventFilter(a0, a1)

    @pyqtSlot(int)
    def on_page_stack_currentChanged(self, _):
        for item in self.tabbar.items:
            item.setSelected(False)
        widget: QQuickWidget = self.page_stack.currentWidget()
        if widget == None:
            return
        key = widget.source().toString()
        item = self.tabbar.tab(key)
        if item != None:
            item.setSelected(True)

    @pyqtSlot(int)
    def on_page_stack_widgetAdded(self, index):
        widget: QQuickWidget = self.page_stack.widget(index)
        key = widget.source().toString()
        if key in self.tabbar.itemMap:
            return
        self.tabbar.addTab(
            key,
            widget.windowTitle(),
            widget.windowIcon(),
            onClick=lambda: self.page_stack.setCurrentWidget(widget),
        )

    @pyqtSlot(bool)
    def on_detach_button_clicked(self, _):
        widget: QQuickWidget = self.page_stack.currentWidget()
        if widget == None:
            return
        self.removePage(widget)
        widget.setParent(None)
        widget.resize(self.size())
        widget.show()

    def addPage(self, item: HelpItem):
        url = QUrl.fromLocalFile(item.page)
        if url not in self.pages:
            self.pages[url] = QQuickWidget(url)
            self.pages[url].setWindowTitle(f"{item.name}({item.page})")
            self.pages[url].setWindowIcon(self.windowIcon())
            self.pages[url].installEventFilter(self)
        self.page_stack.addWidget(self.pages[url])
        self.page_stack.setCurrentWidget(self.pages[url])

    def removePage(self, widget: QQuickWidget):
        key = widget.source().toString()
        if key not in self.tabbar.itemMap:
            return
        self.tabbar.removeTabByKey(key)
        self.page_stack.removeWidget(widget)
