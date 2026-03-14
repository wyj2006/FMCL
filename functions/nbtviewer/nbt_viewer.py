import qtawesome as qta
from nbtlib import Array, Base, Compound, File, List
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QWidget
from ui_nbt_viewer import Ui_NBTViewer


class NBTItem:
    def __init__(self, tag: Base, name="root", parent=None):
        self.tag = tag
        self.name = name
        self.parent: NBTItem = parent
        self.children = []
        match tag:
            case Compound():
                for key, val in tag.items():
                    self.children.append(NBTItem(val, key, self))
            case Array() | List():
                for i, v in enumerate(tag):
                    self.children.append(NBTItem(v, str(i), self))

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
        match (column, self.tag):
            case (0, _):
                return self.name
            case (1, Compound() | List() | Array()):
                return self.tag.__class__.__name__
            case (1, _):
                return str(self.tag)
        return None


class NBTModel(QAbstractItemModel):
    def __init__(self, nbt_file: File):
        super().__init__()
        self.root_item = NBTItem(nbt_file)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        match section:
            case 0:
                return self.tr("键/索引")
            case 1:
                return self.tr("值")
        return None

    def getItem(self, index: QModelIndex) -> NBTItem:
        if index.isValid():
            return index.internalPointer()
        return self.root_item

    def columnCount(self, parent):
        return 2

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


class NBTViewer(QWidget, Ui_NBTViewer):
    def __init__(self, nbt_file: File):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("msc.preview"))
        self.nbt_file = nbt_file
        self.nbt.setModel(NBTModel(nbt_file))
