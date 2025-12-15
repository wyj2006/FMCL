import time

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtNetwork import QHostAddress
from PyQt6.QtWidgets import QApplication
from result import Err, Ok

from .common import (
    MirrorRegisterInfo,
    TcpServer,
    TcpSocket,
    get_mirror,
    handle_command,
    register_mirror,
    unregister_mirror,
)


class Source(QObject):
    def __init__(self, parent: QObject, kind: str, name=None):
        super().__init__(parent)
        self.kind = kind

        parent.installEventFilter(self)

        self.socket = TcpServer()
        self.socket.listen(QHostAddress("127.0.0.1"))
        self.socket.dataReceived.connect(self.handleRecvData)

        self.name = name or str(self.socket.serverPort())
        register_mirror(self.name, self.kind, self.socket.serverPort())

        QApplication.instance().aboutToQuit.connect(self.deleteLater)

    def handleRecvData(self, datas: bytes):
        for data in datas.decode().split("\0"):
            if not data:
                continue
            self._handleRecvData(handle_command(self.parent(), data))

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case _:
                pass

    def eventFilter(self, watched: QObject, event: QEvent):
        if watched == self.parent():
            match event.type():
                case QEvent.Type.DeferredDelete:
                    # 子对象不会收到DeferredDelete事件
                    self.beforeDelete()
        return super().eventFilter(watched, event)

    def beforeDelete(self):
        unregister_mirror(self.name)
        self.socket.close()
        self.parent().removeEventFilter(self)

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.DeferredDelete:
            self.beforeDelete()
        return super().event(event)


class Mirror:
    def __init__(self, name: str, parent=None):
        super().__init__(parent=parent)
        self.name = name
        for i in range(3):
            # 因为服务器的同步问题, 可能导致这里没有获取到正确信息
            match get_mirror(name):
                case Ok(reginfo):
                    self.reginfo: MirrorRegisterInfo = reginfo
                    break
                case Err(_):
                    time.sleep(0.1 + i / 10)
        else:
            raise Exception(f"{name}不存在")
        self.port = int(self.reginfo["port"])
        self.kind = self.reginfo["kind"]

        self.socket = TcpSocket()
        self.socket.connectToHost("127.0.0.1", self.port)
        self.socket.dataReceived.connect(self.handleRecvData)
        self.socket.connected.connect(lambda: self.socket.write(b"ready\0"))

    def handleRecvData(self, data: bytes):
        for data in data.decode().split("\0"):
            if not data:
                continue
            self._handleRecvData(handle_command(self, data))

    def _handleRecvData(self, args: tuple[str]):
        match args:
            case _:
                pass
