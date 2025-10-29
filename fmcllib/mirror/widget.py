from PyQt6.QtCore import QEvent, QTimer, pyqtSignal
from PyQt6.QtGui import QWindow
from PyQt6.QtNetwork import QAbstractSocket
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from fmcllib.window import Window

from .base import MirrorBase
from .common import handle_command


class MirrorWidget(MirrorBase, QWidget):
    titlebarWidgetsChanged = pyqtSignal()

    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.setLayout(QVBoxLayout())
        if self.kind == "window":
            self.layout().setContentsMargins(
                Window.BORDER_WIDTH,
                0,
                Window.BORDER_WIDTH,
                Window.BORDER_WIDTH,
            )
        elif self.kind == "widget":
            self.layout().setContentsMargins(0, 0, 0, 0)

        self.target_winid = None
        self.target_window = None
        self.target_widget = None

        self.socket.disconnected.connect(self.detach)
        self.socket.connected.connect(lambda: self.socket.write(b"embed\0"))

        self.titlebar_widgets = []

    def _handleRecvData(self, data: bytes):
        self.from_system = False
        match handle_command(self, data):
            case ("change_winid", winid):
                self.target_winid = int(winid)
                if self.target_widget != None:
                    self.layout().removeWidget(self.target_widget)
                    self.target_widget.deleteLater()
                self.target_window = QWindow.fromWinId(self.target_winid)
                self.target_widget = QWidget.createWindowContainer(self.target_window)
                self.layout().addWidget(self.target_widget)

                self.timer = QTimer(self)
                self.timer.timeout.connect(
                    lambda: (
                        (
                            self.socket.write(b"activate_window\0")
                            if self.isVisible()
                            else None
                        ),
                        self.timer.stop(),
                    )
                )
                self.timer.start(500)
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
                            "widget": MirrorWidget(name),
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

    def kill(self):
        self.detach(["close"])

    def detach(self, other_commands=None):
        for widget_info in self.titlebar_widgets:
            widget_info["widget"].detach()

        if other_commands == None:
            other_commands = []

        size = self.size()
        self.socket.write(
            f"detach resize {size.width()} {size.height()};{';'.join(other_commands)}\0".encode()
        )
        self.deleteLater()

    def event(self, event):
        match event.type():
            case QEvent.Type.Close:
                self.detach()
            case (
                QEvent.Type.WindowActivate | QEvent.Type.Show | QEvent.Type.FocusIn
            ) if (self.socket.state() == QAbstractSocket.SocketState.ConnectedState):
                self.socket.write(b"activate_window\0")
        return super().event(event)
