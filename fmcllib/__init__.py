import logging
import socket
import sys
import traceback

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QErrorMessage, QWidget

from .address import get_address

tr = QCoreApplication.translate
logging_address = get_address("logging").unwrap()


class RemoteHandler(logging.Handler):
    def __init__(self, level=0):
        super().__init__(level)
        self.socket = socket.socket()
        self.socket.connect(logging_address)

    def emit(self, record):
        self.socket.sendall(
            f'{record.levelname.lower()} "{record.processName}|{record.threadName}" {record.msg}\0'.encode()
        )


def excepthook(*args):
    sys.__excepthook__(*args)
    show_qerrormessage(
        tr("FMCLLib", "出现严重错误"),
        "".join(traceback.format_exception(*args)).strip(),
    )
    exit(1)


def show_qerrormessage(title: str, message: str, parent: QWidget = None):
    w = QErrorMessage(parent)
    if parent == None:
        w.resize(500, 309)
    else:
        w.resize(parent.window().width() * 2 // 3, parent.window().height() * 2 // 3)
    w.setWindowTitle(title)
    w.showMessage(message.replace("\n", "<br>"))
    logging.error(f"{title}: {message}")
    w.exec()


if getattr(sys, "use_kernel_logging", True):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(RemoteHandler())

if getattr(sys, "handle_uncaught_exceptions", True):
    sys.excepthook = excepthook
