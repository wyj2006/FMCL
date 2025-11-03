from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon

from fmcllib.window import Window

from .action import ActionMirror, ActionSource
from .common import event_to_command
from .widget import WidgetMirror, WidgetSource


class WindowSource(WidgetSource):
    KIND = "window"

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case ("ready",):
                self.socket.write(
                    f"{event_to_command(QEvent(QEvent.Type.WindowTitleChange),self.parent())}\0".encode()
                )
                for widget_info in getattr(self.parent(), "titlebar_widgets", []):
                    widget: QWidget = widget_info["widget"]
                    widget_source = WidgetSource(widget)
                    widget.installEventFilter(widget_source)
                    widget_info["widget_source"] = widget_source
                    self.socket.write(
                        " ".join(
                            [
                                "titlebar",
                                "widgets",
                                "add",
                                str(widget_info["index"]),
                                widget_source.name,
                                widget_info.get("stretch", "0"),
                                widget_info.get("alignment", "AlignLeft") + "\0",
                            ]
                        ).encode()
                    )
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
                    widget.titlebar_contextmenu_actions.append(ActionMirror(name))
                elif op == "remove":
                    for action in widget.titlebar_contextmenu_actions:
                        if isinstance(action, ActionMirror) and action.name == name:
                            widget.titlebar_contextmenu_actions.remove(action)
                            action.deleteLater()
                            break
        return super()._handleRecvData(args)

    def detach(self, datas):
        super().detach(datas)
        for widget_info in getattr(self.parent(), "titlebar_widgets", []):
            try:
                widget_info["widget_source"].deleteLater()
            except (RuntimeError, KeyError):
                pass


class WindowMirror(WidgetMirror):
    titlebarWidgetsChanged = pyqtSignal()

    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.layout().setContentsMargins(
            Window.BORDER_WIDTH,
            0,
            Window.BORDER_WIDTH,
            Window.BORDER_WIDTH,
        )
        self.titlebar_widgets = []

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case (
                "titlebar",
                "widgets",
                "add" | "remove" as op,
                index,
                name,
                stretch,
                alignment,
            ):
                if op == "add":
                    self.titlebar_widgets.append(
                        {
                            "index": int(index),
                            "widget": WidgetMirror(name),
                            "stretch": int(stretch),
                            "alignemnt": alignment,
                        }
                    )
                elif op == "remove":
                    for i in range(len(self.titlebar_widgets)):
                        widget_info = self.titlebar_widgets[i]
                        if (
                            widget_info["index"] == int(index)
                            and widget_info["widget"].name == name
                            and widget_info["stretch"] == int(stretch)
                            and widget_info["alignment"] == alignment
                        ):
                            self.titlebar_widgets.pop(i)
                            break
                self.titlebarWidgetsChanged.emit()
        return super()._handleRecvData(args)

    def detach(self, follow_commands=None):
        if self.detached:
            return

        while self.titlebar_widgets:
            self.titlebar_widgets.pop()["widget"].detach()

        self.addEmbedAction()

        return super().detach(follow_commands)

    def embed(self):
        super().embed()
        self.removeEmbedAction()

    def removeEmbedAction(self):
        if not hasattr(self, "embed_action"):
            return
        self.socket.write(
            f"titlebar contextmenu action remove {self.action_source.name}\0".encode()
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
            f"titlebar contextmenu action add {self.action_source.name}\0".encode()
        )

    def event(self, event):
        match event.type():
            case QEvent.Type.DeferredDelete | QEvent.Type.Close:
                self.removeEmbedAction()
        return super().event(event)
