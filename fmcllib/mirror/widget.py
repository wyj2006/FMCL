import base64
from typing import Callable

from PyQt6.QtCore import QEvent, QObject, Qt, QTimer
from PyQt6.QtGui import QWindow
from PyQt6.QtNetwork import QAbstractSocket
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from .base import Mirror, Source
from .common import event_to_command


class WidgetSource(Source):
    KIND = "widget"  # widget的派生类有很多, 它们的类型可能不一样

    def __init__(
        self,
        parent: QWidget,
        on_detach: Callable[[QWidget], None] = None,
        name=None,
    ):
        super().__init__(parent, self.KIND, name)
        self.on_detach = on_detach
        self.embeded = False

    def eventFilter(self, watched: QObject, event: QEvent):
        if watched == self.parent():
            if (
                event.type()
                in (
                    QEvent.Type.WindowTitleChange,
                    QEvent.Type.WindowIconChange,
                    QEvent.Type.Close,
                    QEvent.Type.Show,
                    QEvent.Type.DeferredDelete,
                    QEvent.Type.WinIdChange,
                )
                and self.embeded
            ):
                self.socket.write(f"{event_to_command(event,self.parent())}\0".encode())
        return super().eventFilter(watched, event)

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("ready",):
                widget: QWidget = self.parent()
                if widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed:
                    self.socket.write(f"setfixwidth {widget.width()}\0".encode())
                if widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Fixed:
                    self.socket.write(f"setfixheight {widget.height()}\0".encode())
            case ("embed",) if not self.embeded:
                widget: QWidget = self.parent()
                self.embeded = True
                widget.setParent(None)
                widget.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
                widget.show()
            case ("detach", follow_commands) if self.embeded:
                follow_commands = base64.b64decode(follow_commands)
                self.embeded = False
                # 等待Mirror彻底删除后再进行操作
                self.timer = QTimer(self)
                self.timer.setSingleShot(True)
                self.timer.timeout.connect(lambda c=follow_commands: self.detach(c))
                self.timer.start(200)

    def detach(self, follow_commands: bytes):
        widget: QWidget = self.parent()
        widget.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, False)
        widget.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        widget.show()  # 先让它正常显示一遍
        if self.on_detach:
            self.on_detach(widget)
        self.handleRecvData(follow_commands)  # 处理余下来的指令


class WidgetMirror(Mirror, QWidget):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.detached = True

        self.target_winid = None
        self.target_window = None
        self.target_widget = None

        self.socket.disconnected.connect(self.deleteLater)
        self.socket.connected.connect(self.embed)

    def embed(self):
        if not self.detached:
            return
        self.detached = False
        self.socket.write(b"embed\0")

    def detach(self, follow_commands=None):
        if follow_commands == None:
            follow_commands = []

        size = self.size()
        follow_commands.insert(0, f"resize {size.width()} {size.height()}")

        if self.detached:  # 不重复分离
            return
        self.detached = True

        self.socket.write(
            f"detach {base64.b64encode('\0'.join(follow_commands).encode()).decode()}\0".encode()
        )

        if self.target_widget != None:
            self.target_widget.deleteLater()
        if self.target_window != None:
            self.target_window.deleteLater()
        self.target_widget = self.target_window = None

    def event(self, event):
        match event.type():
            case QEvent.Type.Close:
                self.detach(["close"])
            case QEvent.Type.DeferredDelete:
                self.detach()
            case (
                QEvent.Type.WindowActivate | QEvent.Type.Show | QEvent.Type.FocusIn
            ) if (self.socket.state() == QAbstractSocket.SocketState.ConnectedState):
                pass  # self.socket.write(b"activate_window\0") #加了的话settingeditor会产生奇怪的bug
        return super().event(event)

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("change_winid", winid) if not self.detached:
                self.target_winid = int(winid)
                if self.target_widget != None:
                    self.layout().removeWidget(self.target_widget)
                    self.target_widget.deleteLater()
                self.target_window = QWindow.fromWinId(self.target_winid)
                self.target_widget = QWidget.createWindowContainer(self.target_window)
                self.layout().addWidget(self.target_widget)

                self.timer = QTimer(self)
                self.timer.setSingleShot(True)
                self.timer.timeout.connect(
                    lambda: (
                        self.socket.write(b"activate_window\0")
                        if self.isVisible()
                        else None
                    )
                )
                self.timer.start(500)
