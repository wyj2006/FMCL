import time

from result import Err, Ok

from .common import MirrorRegisterInfo, TcpSocket, get_mirror, handle_command


class MirrorBase:
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        while True:
            # 因为服务器的同步问题, 可能导致这里没有获取到正确信息
            match get_mirror(name):
                case Ok(reginfo):
                    self.reginfo: MirrorRegisterInfo = reginfo
                    break
                case Err(_):
                    time.sleep(0.1)
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
            self._handleRecvData(data)

    def _handleRecvData(self, data: bytes):
        match handle_command(self, data):
            case _:
                pass
