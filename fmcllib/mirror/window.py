from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon

from fmcllib.window import Window

from .action import ActionMirror, ActionSource
from .common import event_to_command, handle_command
from .widget import WidgetMirror, WidgetSource


class WindowSource(WidgetSource):
    KIND = "window"

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("ready",):
                self.socket.write(
                    f"{event_to_command(QEvent(QEvent.Type.WindowTitleChange),self.parent())}\0".encode()
                )
            case ("embed",) if not self.embeded:
                window: Window = self.parent().window()
                if isinstance(window, Window):
                    self.titlebar = window.titleBar
                    self.titlebar.window().removeEventFilter(self.titlebar)
                    self.titlebar.setParent(None)  # 避免Window将上面的widget移除

                    for widget in (
                        self.titlebar.minBtn,
                        self.titlebar.maxBtn,
                        self.titlebar.closeBtn,
                    ):
                        self.titlebar.hBoxLayout.removeWidget(widget)
                        widget.setParent(None)  # 避免对后续的计算产生影响
                        widget.deleteLater()

                    # 转移这些行为
                    self.titlebar.mouseDoubleClickEvent = lambda e: self.socket.write(
                        f"titlebar event {event_to_command(e,self.titlebar)}\0".encode()
                    )
                    self.titlebar.mouseMoveEvent = lambda e: self.socket.write(
                        f"titlebar event {event_to_command(e,self.titlebar)}\0".encode()
                    )
                    self.titlebar.mousePressEvent = lambda e: self.socket.write(
                        f"titlebar event {event_to_command(e,self.titlebar)}\0".encode()
                    )

                    self.titlebar_source = WidgetSource(self.titlebar)
                    self.socket.write(
                        f"titlebar mirror {self.titlebar_source.name}\0".encode()
                    )
            case (
                "titlebar",
                "action",
                "add" | "remove" as op,
                name,
            ):
                widget: QWidget = self.parent()
                if op == "add":
                    widget.addAction(ActionMirror(name))
                elif op == "remove":
                    for action in widget.actions():
                        if isinstance(action, ActionMirror) and action.name == name:
                            widget.removeAction(action)
                            action.deleteLater()
                            break
        return super()._handleRecvData(args)

    def detach(self, datas):
        super().detach(datas)
        try:
            self.titlebar_source.deleteLater()
        except RuntimeError:
            pass


class WindowMirror(WidgetMirror):
    titlebarChanged = pyqtSignal()

    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.layout().setContentsMargins(
            Window.BORDER_WIDTH,
            0,
            Window.BORDER_WIDTH,
            Window.BORDER_WIDTH,
        )
        self.titlebar: WidgetMirror = None

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("titlebar", "mirror", name):
                self.titlebar = WidgetMirror(name)
                self.titlebarChanged.emit()
            case ("titlebar", "event", *event):
                window = self.window()
                if isinstance(window, Window):
                    handle_command(window.titleBar, " ".join(event))
        return super()._handleRecvData(args)

    def detach(self, follow_commands=None):
        if self.detached:
            return

        if self.titlebar != None:
            self.titlebar.detach(["close"])
            self.titlebar = None

        self.addEmbedAction()

        return super().detach(follow_commands)

    def embed(self):
        super().embed()
        self.removeEmbedAction()

    def removeEmbedAction(self):
        if not hasattr(self, "embed_action"):
            return
        self.socket.write(
            " ".join(
                [
                    "titlebar",
                    "action",
                    "remove",
                    self.action_source.name + "\0",
                ]
            ).encode(),
        )
        self.embed_action.deleteLater()
        delattr(self, "embed_action")

    def addEmbedAction(self):
        if hasattr(self, "embed_action"):
            return
        self.embed_action = QAction(self.tr("嵌入"), icon=FluentIcon.EMBED.icon())
        self.action_source = ActionSource(self.embed_action)
        self.embed_action.installEventFilter(self.action_source)
        self.embed_action.triggered.connect(self.embed)
        self.socket.write(
            " ".join(
                [
                    "titlebar",
                    "action",
                    "add",
                    self.action_source.name + "\0",
                ]
            ).encode()
        )

    def event(self, event):
        match event.type():
            case QEvent.Type.DeferredDelete | QEvent.Type.Close:
                self.removeEmbedAction()
        return super().event(event)
