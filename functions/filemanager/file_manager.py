import os

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon
from ui_file_manager import Ui_FileManager

from fmcllib.filesystem import fileinfo, listdir


class FileSystemItem:
    def __init__(self, path, parent=None):
        self.parent: FileSystemItem = parent
        self.children: list[FileSystemItem] = []
        self.fileinfo = fileinfo(path).unwrap()
        self.path = self.fileinfo["path"]
        self.children_loaded = False

    def load_children(self):
        if self.children_loaded:
            return
        for name in listdir(self.path).unwrap():
            self.children.append(FileSystemItem(os.path.join(self.path, name), self))
        self.children_loaded = True

    def get_child(self, row):
        self.load_children()
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def children_count(self):
        self.load_children()
        return len(self.children)

    def row(self):
        if self.parent:
            self.parent.load_children()
            return self.parent.children.index(self)
        return 0

    def data(self, column):
        match column:
            case 0:
                return self.fileinfo["name"]
            case 1:
                return self.fileinfo["path"]
            case 2:
                return ";".join(self.fileinfo["native_paths"])
        return None


class FileSystemModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.root_item = FileSystemItem("/")

    def getItem(self, index: QModelIndex) -> FileSystemItem:
        if index.isValid():
            return index.internalPointer()
        return self.root_item

    def columnCount(self, parent=QModelIndex()):
        return len(self.root_item.fileinfo)

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 1
        return self.getItem(parent).children_count()

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            return self.createIndex(row, column, self.root_item)
        parent_item = self.getItem(parent)
        child_item = parent_item.get_child(row)
        return self.createIndex(row, column, child_item)

    def parent(self, index: QModelIndex):
        child_item = self.getItem(index)
        parent_item = child_item.parent

        if parent_item == None:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        match role:
            case Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.ToolTipRole:
                try:
                    return self.getItem(index).data(index.column())
                except:
                    return None
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            headers = [self.tr("名称"), self.tr("路径"), self.tr("本地路径")]
            if section < len(headers):
                return headers[section]
        return None


class FileManager(QWidget, Ui_FileManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.FOLDER.icon())

        self.fs_model = FileSystemModel()
        self.entries_view.setModel(self.fs_model)
