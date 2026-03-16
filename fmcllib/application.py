import logging
import os
import socket
import threading
import traceback

from PyQt6.QtCore import QEvent, QTranslator, pyqtSignal
from PyQt6.QtWidgets import QApplication
from result import is_ok

from fmcllib.address import (
    get_address,
    parse_address,
    register_address,
    unregister_address,
)
from fmcllib.filesystem import fileinfo, listdir
from fmcllib.setting import Setting


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        load_translations()


class SingleApplication(Application):
    firstAppConfirmed = pyqtSignal()  # 这是第一个应用
    otherAppConfirmed = pyqtSignal()  # 这不是第一个应用
    otherAppRun = pyqtSignal()  # 其它应用运行

    def check(self, port_name: str):
        self.port_name = port_name
        if is_ok(result := get_address(port_name)):
            self.socket = socket.socket()
            self.socket.connect(parse_address(result.ok_value))
            self.socket.sendall(port_name.encode())
            self.otherAppConfirmed.emit()
            return

        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", 0))

        self.port = self.socket.getsockname()[1]
        logging.info(f"{port_name}监听端口{self.port}")
        register_address(port_name, f"127.0.0.1:{self.port}")

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


def load_translations():
    app = QApplication.instance()
    translators = []

    lang = Setting().get("system.language").unwrap_or("zh_CN")
    for name in listdir("/translations").unwrap_or([]):
        if os.path.splitext(name)[1] != ".qm" or lang not in name:
            continue
        if not is_ok(result := fileinfo(f"/translations/{name}")):
            continue
        for native_path in result.ok_value["native_paths"]:
            translator = QTranslator()
            translators.append(translator)

            if translator.load(native_path) and app.installTranslator(translator):
                logging.info(f"已加载: {native_path}")
            else:
                logging.error(f"无法加载: {native_path}")
    app.translators = translators
