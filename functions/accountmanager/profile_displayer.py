import logging
import threading
import traceback

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import (
    FluentIcon,
    IndeterminateProgressRing,
    SettingCard,
    TransparentToolButton,
)
from result import is_ok

from fmcllib.account import (
    AuthlibInjectorDict,
    ProfileDict,
    default_account_head,
    delete_account,
    get_account_head,
    refresh_account,
)
from fmcllib.setting import Setting


class ProfileDisplayer(SettingCard):
    deleted = pyqtSignal()
    selected = pyqtSignal(dict)

    headGot = pyqtSignal(QIcon)
    refreshRequest = pyqtSignal()

    def __init__(self, profile: ProfileDict, setting: Setting, parent=None):
        match profile["method"]:
            case "offline":
                method_name = self.tr("离线登录")
            case "authlib_injector":
                method_name = f'{self.tr("外置登录")}({profile["server_url"]})'
                if is_ok(result := setting.get("account.authlib_injector_servers")):
                    t: list[AuthlibInjectorDict] = result.ok_value
                    for i in t:
                        if (
                            i["url"] == profile["server_url"]
                            and (server_name := i["metadata"]["meta"].get("serverName"))
                            != None
                        ):
                            method_name = server_name
                            break
            case _:
                method_name = self.tr("未知方式")

        super().__init__(
            QIcon(default_account_head().scaled(32, 32)),
            profile["player_name"],
            method_name,
            parent,
        )
        self.setIconSize(32, 32)
        self.setObjectName("ProfileDisplayer")

        self.profile = profile
        self.setting = setting

        self.refresh_ring = IndeterminateProgressRing()
        self.refresh_ring.setStrokeWidth(2)
        self.refresh_ring.hide()
        self.hBoxLayout.addWidget(self.refresh_ring)

        self.refresh_button = TransparentToolButton()
        self.refresh_button.setIcon(FluentIcon.SYNC.icon())
        self.refresh_button.setToolTip(self.tr("刷新"))
        self.refresh_button.clicked.connect(
            lambda: (
                self.refresh_ring.setFixedSize(self.refresh_button.size()),
                self.refresh_ring.show(),
                self.refresh_button.hide(),
                threading.Thread(
                    target=self.refreshThread,
                    daemon=True,
                ).start(),
            )
        )
        self.hBoxLayout.addWidget(self.refresh_button)

        self.copy_uuid_button = TransparentToolButton()
        self.copy_uuid_button.setIcon(FluentIcon.COPY.icon())
        self.copy_uuid_button.setToolTip(self.tr("复制UUID"))
        self.copy_uuid_button.clicked.connect(self.copyUUID)
        self.hBoxLayout.addWidget(self.copy_uuid_button)

        self.delete_button = TransparentToolButton()
        self.delete_button.setIcon(FluentIcon.DELETE.icon())
        self.delete_button.setToolTip(self.tr("删除"))
        self.delete_button.clicked.connect(
            lambda: (
                delete_account(profile, setting),
                self.deleted.emit(),
            )
        )
        self.hBoxLayout.addWidget(self.delete_button)

        self.origin_style = self.styleSheet()

        self.refreshRequest.connect(self.refresh)
        self.headGot.connect(self.iconLabel.setIcon)

        threading.Thread(target=self.getAccountHead, daemon=True).start()

    def getAccountHead(self):
        self.headGot.emit(QIcon(get_account_head(self.profile).scaled(32, 32)))

    def refreshThread(self):
        try:
            refresh_account(self.profile, self.setting).unwrap()
            self.refresh_error = ""
        except Exception as e:
            logging.error(f"刷新失败: {traceback.format_exc()}")
            self.refresh_error = str(e)
        self.refreshRequest.emit()

    def refresh(self):
        self.setTitle(self.profile["player_name"])
        self.setContent(
            self.METHOD_MAP.get(self.profile["method"], self.profile["method"])
        )
        self.refresh_ring.hide()
        self.refresh_button.show()

        if self.refresh_error:
            QMessageBox.critical(self, self.tr("刷新失败"), self.refresh_error)
            self.refresh_error = ""

    def setSelected(self, selected: bool):
        if selected:
            self.setStyleSheet("QFrame#ProfileDisplayer{border:1px solid rgb(0,0,0)}")
        else:
            self.setStyleSheet(self.origin_style)

    def mouseDoubleClickEvent(self, event):
        self.selected.emit(self.profile)
        return super().mouseDoubleClickEvent(event)

    def copyUUID(self):
        QApplication.clipboard().setText(self.profile["uuid"])
        self.copy_uuid_button.setIcon(FluentIcon.ACCEPT.icon())
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(
            lambda: self.copy_uuid_button.setIcon(FluentIcon.COPY.icon())
        )
        self.timer.start(3000)
