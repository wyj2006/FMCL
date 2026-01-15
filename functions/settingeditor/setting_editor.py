import json

from json_editor import SettingJsonEditor
from PyQt6.QtCore import (
    QAbstractItemModel,
    QCoreApplication,
    QEvent,
    QModelIndex,
    QPoint,
    Qt,
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import FluentIcon, PushButton, TransparentToolButton
from settingcard import dispatch_card
from ui_setting_editor import Ui_SettingEditor

from fmcllib.function import Function
from fmcllib.mirror import SettingCardSource, WindowSource
from fmcllib.setting import SETTING_DEFAULT_PATH, Setting
from fmcllib.window import Window

tr = QCoreApplication.translate


class SettingItem:
    def __init__(self, setting: Setting, key: str, keyword="", parent=None):
        self.setting = setting
        self.parent: SettingItem = parent
        self.key = key
        self.children: list[SettingItem] = []

        for name in self.setting.children(self.key).unwrap():
            child = SettingItem(
                self.setting,
                Setting.key_join(self.key, name),
                keyword,
                self,
            )
            # child的子节点都被过滤掉且child自身也被过滤掉
            if (
                not child.children
                and keyword not in child.key
                and keyword not in child.data(0)
            ):
                continue
            self.children.append(child)

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
        attr = self.setting.get_allattr(self.key).unwrap_or({})
        match column:
            case 0:
                return tr(
                    attr.get("translation_context", ""),
                    attr.get("display_name", self.key.split(".")[-1]),
                )
        return None


class SettingModel(QAbstractItemModel):
    def __init__(self, setting: Setting, keyword="", parent=None):
        super().__init__(parent)
        self.setting = setting
        self.root_item = SettingItem(setting, "", keyword)

    def getItem(self, index: QModelIndex) -> SettingItem:
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


class KeyWidget(QWidget):
    def __init__(self, key: str, setting: Setting):
        super().__init__()
        self.setting = setting
        self.setLayout(QVBoxLayout())

        attr = self.setting.get_allattr(key).unwrap()
        context = attr.get("translation_context", "")

        display_name = QLabel(text=tr(context, attr.get("display_name", key)))
        display_name.setToolTip(key)

        font = QFont()
        names = key.split(".")
        if len(names) == 1:
            font.setBold(True)
        font.setPointSize(max(10, 20 - len(names) * 2))
        display_name.setFont(font)

        self.layout().addWidget(display_name)

        if "description" in attr:
            description = QLabel(text=tr(context, attr["description"]))
            font = QFont()
            font.setPointSize(10)
            description.setFont(font)
            self.layout().addWidget(description)

        if self.setting.get(key).unwrap() != None:
            getter = lambda: self.setting.get(key).unwrap()
            attr_getter = lambda attr_name, default=None: self.setting.get_attr(
                key, attr_name
            ).unwrap_or(default)
            setter = lambda value: self.setting.set(key, value)
            attr_setter = lambda attr_name, value: self.setting.set_attr(
                key, attr_name, value
            )
            self.card = dispatch_card(getter, attr_getter, setter, attr_setter)
            self.layout().addWidget(self.card)

    def event(self, a0):
        match a0.type():
            case QEvent.Type.Close | QEvent.Type.DeferredDelete if hasattr(
                self, "card"
            ):
                # 确保MirrorCard能正常释放
                self.card.close()
        return super().event(a0)


class SettingEditor(QWidget, Ui_SettingEditor):
    def __init__(self, path=SETTING_DEFAULT_PATH):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.SETTING.icon())
        self.setWindowTitle(self.tr(f"设置: {path}"))
        self.splitter.setSizes([100, 300])
        # 因为可能存在MirrorCard, 为了减少麻烦, 关闭后就删除
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.path = path
        self.setting: Setting = Setting(path)
        self.key_widgets: dict[str, KeyWidget] = {}

        self.navigation.setModel(SettingModel(self.setting))

        self.search_input.searchSignal.connect(
            lambda keyword: self.setModel(SettingModel(self.setting, keyword))
        )
        self.search_input.clearSignal.connect(
            lambda: self.setModel(SettingModel(self.setting))
        )
        self.search_input.editingFinished.connect(
            lambda: self.setModel(SettingModel(self.setting, self.search_input.text()))
        )

        self.navigation.clicked.connect(
            lambda index: self.naviagate(index.internalPointer().key)
        )

        self.editinjson_button = TransparentToolButton(icon=FluentIcon.CODE.icon())
        self.editinjson_button.setToolTip(self.tr("在文件中编辑"))
        self.editinjson_button.clicked.connect(self.openJsonEditor)

        # mirror自己进程的source(SettingCardSource),
        # 会导致即使SettingEditor关闭了, 也还是存在着未关闭的widgets(即这些source),
        # 而这些widgets无法关闭, 也可能不会显示, 进而导致看似关闭了程序实际却没有的情况发生

        self.editinmanager_for_profile = PushButton(self.tr("在账号管理器中编辑"))
        self.editinmanager_for_profile.setWindowTitle(  # 为了用spy++调试
            "edit_in_account_manager_for_profile"
        )
        self.editinmanager_for_profile.setFixedHeight(32)
        self.editinmanager_for_profile.installEventFilter(
            SettingCardSource(
                self.editinmanager_for_profile,
                name="edit_in_account_manager_for_profile",
            )
        )
        self.editinmanager_for_profile.clicked.connect(
            lambda: Function.quick_run("/functions/accountmanager")
        )

        self.editinmanager_for_current = PushButton(self.tr("在账号管理器中编辑"))
        self.editinmanager_for_current.setWindowTitle(  # 为了用spy++调试
            "edit_in_account_manager_for_current"
        )
        self.editinmanager_for_current.setFixedHeight(32)
        self.editinmanager_for_current.installEventFilter(
            SettingCardSource(
                self.editinmanager_for_current,
                name="edit_in_account_manager_for_current",
            )
        )
        self.editinmanager_for_current.clicked.connect(
            lambda: Function.quick_run("/functions/accountmanager")
        )

        self.editinmanager_for_servers = PushButton(self.tr("在账号管理器中编辑"))
        self.editinmanager_for_servers.setWindowTitle(  # 为了用spy++调试
            "edit_in_account_manager_for_servers"
        )
        self.editinmanager_for_servers.setFixedHeight(32)
        self.editinmanager_for_servers.installEventFilter(
            SettingCardSource(
                self.editinmanager_for_servers,
                name="edit_in_account_manager_for_servers",
            )
        )
        self.editinmanager_for_servers.clicked.connect(
            lambda: Function.quick_run("/functions/accountmanager")
        )

        self.genCards()

    def setModel(self, model: SettingModel):
        self.navigation.setModel(model)
        # 查找所有没有被过滤掉的key
        keys = []
        queue = [QModelIndex()]
        while queue:
            parent = queue.pop(0)
            if (p := parent.internalPointer()) != None:
                keys.append(p.key)
            for i in range(model.rowCount(parent)):
                queue.append(model.index(i, 0, parent))

        for key, widget in self.key_widgets.items():
            if key in keys:
                widget.show()
            else:
                widget.hide()

    def openJsonEditor(self):
        if hasattr(self, "json_editor"):
            if self.json_editor.isVisible():
                return
            else:
                self.json_editor.deleteLater()
        self.json_editor = SettingJsonEditor(
            json.dumps(
                self.setting.generate_json().unwrap_or({}),
                indent=4,
            )
        )
        self.json_editor.installEventFilter(
            WindowSource(
                self.json_editor,
                lambda w: Window(w).show(),
            )
        )
        self.json_editor.saveRequest.connect(
            lambda content: list(
                self.setting.add_or_update(key, val) for key, val in content.items()
            )
        )
        self.json_editor_window = Window(self.json_editor)
        self.json_editor_window.show()

    def event(self, e: QEvent):
        match e.type():
            case QEvent.Type.Show:
                window = self.window()
                if not isinstance(window, Window):
                    return super().event(e)
                self.editinjson_button.setFixedHeight(window.titleBar.height())
                self.editinjson_button.setFixedWidth(window.titleBar.closeBtn.width())
                window.titleBar.hBoxLayout.insertWidget(
                    1, self.editinjson_button, 0, Qt.AlignmentFlag.AlignRight
                )
            case QEvent.Type.Close | QEvent.Type.DeferredDelete:
                # 确保MirrorCard能正常释放
                for i in self.key_widgets.values():
                    i.close()
        return super().event(e)

    def naviagate(self, key: str):
        if key not in self.key_widgets or not self.key_widgets[key].isVisible():
            return
        widget = self.key_widgets[key]
        pos = widget.mapTo(self.edit_area_content, QPoint(0, 0))
        self.edit_area.verticalScrollBar().setValue(pos.y())

    def genCards(self, key=""):
        if key == "":  # 根
            while self.edit_layout.count() > 0:
                item = self.edit_layout.takeAt(0)
                if item.widget() != None:
                    item.widget().deleteLater()
            for name in self.setting.children(key).unwrap():
                self.genCards(name)
            self.edit_layout.addItem(
                QSpacerItem(
                    0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
                )
            )
            return

        widget = KeyWidget(key, self.setting)
        self.key_widgets[key] = widget
        self.edit_layout.addWidget(widget)

        QApplication.processEvents()

        for name in self.setting.children(key).unwrap():
            self.genCards(Setting.key_join(key, name))
