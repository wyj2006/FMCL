import base64
import json
import logging
from typing import Literal, TypedDict

from PyQt6.QtCore import QBuffer, QEvent, QIODevice, QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtNetwork import QTcpServer, QTcpSocket
from result import Err, Ok, Result

from fmcllib.address import getall_address, register_address, unregister_address

NAME_PREFIX = "@mirror"


class MirrorRegisterInfo(TypedDict):
    name: str
    kind: Literal["window", "action", "widget"]
    port: str


class TcpSocket(QTcpSocket):
    dataReceived = pyqtSignal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.readyRead.connect(lambda: self.dataReceived.emit(bytes(self.readAll())))

    def write(self, data):
        return (super().write(data), self.flush())[0]


class TcpServer(QTcpServer):
    dataReceived = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.connections: list[QTcpSocket] = []
        self.newConnection.connect(
            lambda: self.handleConnection(self.nextPendingConnection())
        )

    def handleConnection(self, conn: QTcpSocket):
        conn.readyRead.connect(lambda: self.dataReceived.emit(bytes(conn.readAll())))
        self.connections.append(conn)
        conn.disconnected.connect(lambda: self.connections.remove(conn))

    def write(self, data):
        for conn in self.connections:
            conn.write(data)
            conn.flush()

    def readAll(self):
        if len(self.connections) > 1:
            logging.warning(
                f"{self.serverAddress()}有多个连接, 只读第一个({self.connections[0].localAddress()})"
            )
        return self.connections[0].readAll()


def icon_to_data(icon: QIcon) -> bytes:
    icon_image = icon.pixmap(16).toImage()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    icon_image.save(buffer, "png")
    data = bytes(buffer.buffer())
    buffer.close()
    return data


def event_to_command(event: QEvent, source: QObject) -> str:
    match event.type():
        case QEvent.Type.WinIdChange:
            return f"change_winid {int(source.winId())}"
        case QEvent.Type.WindowTitleChange:
            return f"change_windowtitle {source.windowTitle()}"
        case QEvent.Type.WindowIconChange:
            return f"change_windowicon {icon_to_data(source.windowIcon())}"
        case QEvent.Type.Resize:
            size = source.size()
            return f"resize {size.width()} {size.height()}"
        case QEvent.Type.Show:
            return "show"
        case QEvent.Type.Hide:
            return "hide"
        case QEvent.Type.Close:
            return "close"
        case QEvent.Type.DeferredDelete:
            return "deletelater"
        case _:
            return "nop"


def handle_command(target: QObject, command: str) -> tuple[str]:
    args = command.split()
    match args:
        case ("nop",):
            pass
        case ("change_windowtitle", title):
            target.setWindowTitle(title)
        case ("change_windowicon", *_):
            data = eval(command[len(args[0]) :])
            icon_image = QImage.fromData(data)
            if not icon_image.isNull():
                target.setWindowIcon(QIcon(QPixmap.fromImage(icon_image)))
        case ("settext", text):
            target.setText(text)
        case ("seticon", *_):
            data = eval(command[len(args[0]) :])
            icon_image = QImage.fromData(data)
            if not icon_image.isNull():
                target.setIcon(QIcon(QPixmap.fromImage(icon_image)))
        case ("close",):
            target.close()
        case ("resize", width, height):
            target.resize(int(width), int(height))
        case ("focusin",):
            target.setFocus()
        case ("move", x, y):
            target.move(int(x), int(y))
        case ("setfixwidth", width):
            target.setFixedWidth(int(width))
        case ("setfixheight", height):
            target.setFixedHeight(int(height))
        case ("setfixsize", width, height):
            target.setFixedSize(int(width), int(height))
        case ("destroy",):
            target.destroy()
        case ("show",):
            target.show()
        case ("hide",):
            target.hide()
        case ("activate_window",):
            target.activateWindow()
        case ("deletelater",):
            target.deleteLater()
    return args


def gen_address_name(reginfo: MirrorRegisterInfo):
    return f"{NAME_PREFIX}{base64.b64encode(json.dumps(reginfo).encode()).decode()}"


def register_mirror(name: str, kind: str, port: int):
    reginfo: MirrorRegisterInfo = {"name": name, "kind": kind, "port": str(port)}
    register_address(
        gen_address_name(reginfo),
        "127.0.0.1",
        port,
    )


def unregister_mirror(name: str):
    for i in getall_mirror().values():
        if i["name"] == name:
            unregister_address(gen_address_name(i))
            break


def get_mirror(name: str) -> Result[MirrorRegisterInfo, str]:
    for i in getall_mirror().values():
        if i["name"] == name:
            return Ok(i)
    return Err(f"Cannot found {name}")


def getall_mirror() -> dict[str, MirrorRegisterInfo]:
    result = {}
    for i in getall_address().values():
        if not i["name"].startswith(NAME_PREFIX):
            continue
        reginfo: MirrorRegisterInfo = json.loads(
            base64.b64decode(i["name"][len(NAME_PREFIX) :])
        )
        result[reginfo["name"]] = reginfo
    return result
