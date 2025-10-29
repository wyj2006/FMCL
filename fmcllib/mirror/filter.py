from typing import Callable

from PyQt6.QtCore import QEvent, QObject, QSize, Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtNetwork import QHostAddress
from PyQt6.QtWidgets import QApplication, QSizePolicy, QWidget

from .action import MirrorAction
from .common import (
    TcpServer,
    event_to_command,
    handle_command,
    icon_to_data,
    register_mirror,
    unregister_mirror,
)


class MirrorFilter(QObject):
    screen_size: QSize = None  # 屏幕的大小

    def __init__(
        self, parent: QObject, kind: str, on_detach: Callable[[QWidget], None] = None
    ):
        super().__init__(parent)
        self.kind = kind  # 镜像的那个控件的类型
        self.on_detach = on_detach if on_detach != None else lambda w: w.show()
        self.embeded = False

        parent.installEventFilter(self)

        self.socket = TcpServer()
        self.socket.listen(QHostAddress("127.0.0.1"))
        self.socket.dataReceived.connect(self.handleRecvData)

        self.name = str(self.socket.serverPort())
        register_mirror(self.name, self.kind, self.socket.serverPort())
        self.registered = True

        QApplication.instance().aboutToQuit.connect(self.deleteLater)

    def eventFilter(self, watched: QObject, event: QEvent):
        if watched == self.parent():
            match event.type():
                case QEvent.Type.DeferredDelete:
                    # 子对象不会收到DeferredDelete事件
                    self.beforeDelete()
                # 下面两个事件的处理是为了防止parent关闭后继续被Explorer捕获
                case QEvent.Type.Show if (
                    self.kind == "window" and self.registered == False
                ):
                    self.registered = True
                    register_mirror(self.name, self.kind, self.socket.serverPort())
                case QEvent.Type.Close if (
                    self.kind == "window" and self.registered == True
                ):
                    self.registered = False
                    unregister_mirror(self.name)

            if self.kind in ("window", "widget") and (
                event.type()
                in (
                    QEvent.Type.WindowTitleChange,
                    QEvent.Type.WindowIconChange,
                    QEvent.Type.Close,
                )
                or (event.type() == QEvent.Type.WinIdChange and self.embeded)
            ):
                self.socket.write(f"{event_to_command(event,self.parent())}\0".encode())
        return super().eventFilter(watched, event)

    def beforeDelete(self):
        unregister_mirror(self.name)
        self.socket.close()
        self.parent().removeEventFilter(self)

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.DeferredDelete:
            self.beforeDelete()
        return super().event(event)

    def handleRecvData(self, datas: bytes):
        for data in datas.decode().split("\0"):
            if not data:
                continue
            match handle_command(self.parent(), data):
                case ("ready",):
                    # 防止address服务在检测连接时发送这些信息
                    self.onReady()
                case ("embed",) if self.kind in ("window", "widget"):
                    widget: QWidget = self.parent()
                    self.embeded = True
                    widget.setParent(None)
                    widget.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
                    widget.show()
                case ("detach", *_) if self.kind in ("window", "widget"):
                    self.embeded = False
                    # 等待MirrorWidget彻底删除后再进行操作
                    self.timer = QTimer(self)
                    self.timer.timeout.connect(
                        lambda d=data: self.detach(d[7:].encode())
                    )
                    self.timer.start(200)
                case (
                    "titlebar",
                    "contextmenu",
                    "action",
                    "add" | "remove" as op,
                    name,
                ):
                    widget: QWidget = self.parent()
                    if not hasattr(widget, "titlebar_contextmenu_actions"):
                        widget.titlebar_contextmenu_actions = []
                    if op == "add":
                        widget.titlebar_contextmenu_actions.append(MirrorAction(name))
                    elif op == "remove":
                        for action in widget.titlebar_contextmenu_actions:
                            if isinstance(action, MirrorAction) and action.name == name:
                                widget.titlebar_contextmenu_actions.remove(action)
                                action.deleteLater()
                                break
                case ("trigger",):
                    action: QAction = self.parent()
                    action.trigger()

    def detach(self, datas: bytes):
        widget: QWidget = self.parent()
        widget.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, False)
        widget.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        self.on_detach(widget)
        self.handleRecvData(datas.replace(b";", b"\0"))  # 处理余下来的指令
        for widget_info in getattr(self.parent(), "titlebar_widgets", []):
            if (mirror_filter := widget_info.get("mirror_filter", None)) != None:
                try:
                    mirror_filter.deleteLater()
                except RuntimeError:
                    pass
        self.timer.stop()

    def onReady(self):
        match self.kind:
            case "window":
                self.socket.write(
                    f"{event_to_command(QEvent(QEvent.Type.WindowTitleChange),self.parent())}\0".encode()
                )
                for widget_info in getattr(self.parent(), "titlebar_widgets", []):
                    widget: QWidget = widget_info["widget"]
                    widget_mirror_filter = MirrorFilter(widget, "widget")
                    widget.installEventFilter(widget_mirror_filter)
                    widget_info["mirror_filter"] = widget_mirror_filter
                    self.socket.write(
                        " ".join(
                            [
                                "titlebar",
                                "widgets",
                                "add",
                                str(widget_info["index"]),
                                widget_mirror_filter.name,
                                widget_info.get("stretch", "0"),
                                widget_info.get("alignment", "AlignLeft") + "\0",
                            ]
                        ).encode()
                    )
            case "action":
                aciton: QAction = self.parent()
                self.socket.write(f"settext {aciton.text()}\0".encode())
                self.socket.write(f"seticon {icon_to_data(aciton.icon())}\0".encode())
            case "widget":
                widget: QWidget = self.parent()
                if widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed:
                    self.socket.write(f"setfixwidth {widget.width()}\0".encode())
                if widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Fixed:
                    self.socket.write(f"setfixheight {widget.height()}\0".encode())
