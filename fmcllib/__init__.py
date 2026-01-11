import base64
import faulthandler
import logging
import sys
import traceback

from PyQt6.QtCore import (
    QCoreApplication,
    QMessageLogContext,
    QtMsgType,
    qInstallMessageHandler,
)
from PyQt6.QtWidgets import QApplication, QErrorMessage, QWidget

from .address import get_service_connection

tr = QCoreApplication.translate
VERSION = "4.0.0"


class RemoteHandler(logging.Handler):
    def __init__(self, level=0):
        super().__init__(level)
        self.client = get_service_connection("logging")

    def emit(self, record):
        try:
            msg = record.msg % record.args
        except:
            msg = record.msg
        self.client.sendall(
            " ".join(
                [
                    record.levelname.lower(),
                    f'"{record.threadName}"',
                    base64.b64encode(str(msg).encode()).decode() + "\0",
                ]
            ).encode()
        )
        self.client.recv(1024 * 1024)  # 忽略结果


def excepthook(*args):
    sys.__excepthook__(*args)
    show_qerrormessage(
        tr("FMCLLib", "出现严重错误"),
        "".join(traceback.format_exception(*args)).strip(),
    )
    exit(1)


def show_qerrormessage(title: str, message: str, parent: QWidget = None):
    if QApplication.instance() == None:
        app = QApplication(sys.argv)

    w = QErrorMessage(parent)
    if parent == None:
        w.resize(500, 309)
    else:
        w.resize(parent.window().width() * 2 // 3, parent.window().height() * 2 // 3)
    w.setWindowTitle(title)
    w.showMessage(message.replace("\n", "<br>"))
    logging.error(f"{title}: {message}")
    w.exec()


def qt_message_handler(msg_type: QtMsgType, context: QMessageLogContext, msg: str):
    log = {
        QtMsgType.QtDebugMsg: logging.debug,
        QtMsgType.QtWarningMsg: logging.warning,
        QtMsgType.QtCriticalMsg: logging.critical,
        QtMsgType.QtFatalMsg: logging.critical,
        QtMsgType.QtSystemMsg: logging.info,
        QtMsgType.QtInfoMsg: logging.info,
    }[msg_type]
    log(f"File {context.file} at {context.line} in {context.function}: {msg}")


qInstallMessageHandler(qt_message_handler)


if getattr(sys, "use_kernel_logging", True):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(RemoteHandler())

if getattr(sys, "handel_faults", True):
    sys.excepthook = excepthook
    faulthandler.enable(open("fault_dump.txt", mode="w", encoding="utf-8"))
