from PyQt6.QtCore import QEvent, QObject, QSize, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import RoundMenu
from qframelesswindow import FramelessWindow


class Window(FramelessWindow):
    def __init__(self, client: QWidget):
        super().__init__()
        self.belonging = self.findChildren(QWidget)

        self.client = client
        self.client.setParent(self)
        self.client.move(0, self.titleBar.height())

        self.resize(self.client.size() + QSize(0, self.titleBar.height()))
        self.setWindowIcon(self.client.windowIcon())
        self.setWindowTitle(self.client.windowTitle())

        self.client.installEventFilter(self)

        self.titleBar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.titleBar.customContextMenuRequested.connect(self.showTitleBarContextMenu)

    def showTitleBarContextMenu(self):
        menu = RoundMenu()
        for action in getattr(self.client, "titlebar_contextmenu_actions", []):
            menu.addAction(action)
        if menu.actions():  # 有action再显示
            menu.exec(QCursor.pos())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.client:
            match event.type():
                case QEvent.Type.Close | QEvent.Type.DeferredDelete:
                    self.deleteLater()
                case QEvent.Type.ParentChange if watched.parent() != self:
                    self.deleteLater()
                case QEvent.Type.WindowTitleChange:
                    self.setWindowTitle(self.client.windowTitle())
                case QEvent.Type.WindowIconChange:
                    self.client.removeEventFilter(self)  # 不加会产生递归, 原因不详
                    self.setWindowIcon(self.client.windowIcon())
                    self.client.installEventFilter(self)
                case QEvent.Type.Resize:
                    self.resize(event.size() + QSize(0, self.titleBar.height()))
                    self.client.move(0, self.titleBar.height())
        return super().eventFilter(watched, event)

    def event(self, e: QEvent) -> bool:
        match e.type():
            case QEvent.Type.Resize | QEvent.Type.WindowStateChange:
                self.client.resize(self.width(), self.height() - self.titleBar.height())
                self.client.move(0, self.titleBar.height())
            case QEvent.Type.Close:
                self.client.close()
                self.deleteLater()
            case QEvent.Type.DeferredDelete:
                try:
                    self.client.removeEventFilter(self)
                except RuntimeError:
                    pass
                # 去除一些本不属于Window的控件
                queue = self.findChildren(
                    QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
                )
                while queue:
                    child = queue.pop(0)
                    if child in self.belonging:
                        queue.extend(
                            child.findChildren(
                                QWidget,
                                options=Qt.FindChildOption.FindDirectChildrenOnly,
                            )
                        )
                    else:
                        size = child.size()
                        child.setParent(None)
                        child.resize(size)
        return super().event(e)
