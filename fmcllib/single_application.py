import hashlib
import logging
import socket
import threading
import traceback

from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtWidgets import QApplication
from result import is_ok

from fmcllib.address import get_address, register_address, unregister_address


class SingleApplication(QApplication):
    firstAppConfirmed = pyqtSignal()  # 这是第一个应用
    otherAppConfirmed = pyqtSignal()  # 这不是第一个应用
    otherAppRun = pyqtSignal()  # 其它应用运行

    def check(self, port_name: str):
        self.port_name = port_name
        if is_ok(result := get_address(port_name)):
            self.socket = socket.socket()
            self.socket.connect(result.ok_value)
            self.socket.sendall(port_name.encode())
            self.otherAppConfirmed.emit()
            return
        self.port = int.from_bytes(hashlib.md5(port_name.encode()).digest()[:2])
        register_address(port_name, "127.0.0.1", self.port)

        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", self.port))
        self.socket.listen()
        # 使用线程处理, 这样可以允许main中有死循环
        handler = threading.Thread(target=self.listen, daemon=True)
        handler.start()
        self.firstAppConfirmed.emit()

    def listen(self):
        while True:
            try:
                conn, address = self.socket.accept()
                # 防止address服务在测试连接的时候误发消息
                if conn.recv(1024).decode() == self.port_name:
                    self.otherAppRun.emit()
            except:
                logging.error(traceback.format_exc())

    def event(self, event: QEvent):
        match event.type():
            case QEvent.Type.Quit:
                try:
                    unregister_address(self.port_name)
                except:
                    pass
        return super().event(event)
