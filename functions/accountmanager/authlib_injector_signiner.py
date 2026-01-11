import logging
import threading
import traceback
from dataclasses import dataclass
from typing import Union

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox
from qfluentwidgets import StateToolTip
from result import is_err
from ui_authlib_injector_signiner import Ui_AuthlibInjectorSignIner

from fmcllib.account import AuthlibInjectorDict, signin_authlib_injector
from fmcllib.setting import Setting


@dataclass
class SignInStart:
    pass


@dataclass
class SigningIn:
    pass


@dataclass
class SignInSuccess:
    pass


@dataclass
class SignInFail:
    error_message: str


type SignInState = Union[SignInStart, SigningIn, SignInSuccess, SignInFail]


class AuthlibInjectorSignIner(QDialog, Ui_AuthlibInjectorSignIner):
    signinFinished = pyqtSignal()

    def __init__(
        self, authlib_injector: AuthlibInjectorDict, setting: Setting, parent=None
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.setting = setting
        self.authlib_injector = authlib_injector

        self.setOkButtonState()
        self.username.textChanged.connect(self.setOkButtonState)
        self.password.textChanged.connect(self.setOkButtonState)

        if (
            server_name := authlib_injector["metadata"]["meta"].get("serverName")
        ) != None:
            self.server_name.setText(self.server_name.text() + server_name)
        else:
            self.server_name.hide()

        links = authlib_injector["metadata"]["meta"].get("links", dict())
        if (homepage_link := links.get("homepage")) != None:
            self.homepage_link.setUrl(homepage_link)
        else:
            self.homepage_link.hide()
        if (register_link := links.get("register")) != None:
            self.register_link.setUrl(register_link)
        else:
            self.register_link.hide()

        self.signin_state: SignInState = SignInStart()
        self.signinFinished.connect(self.accept)

    def setOkButtonState(self):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.username.text()) and bool(self.password.text())
        )

    def signin(self):
        username = self.username.text()
        password = self.password.text()
        try:
            if is_err(
                result := signin_authlib_injector(
                    self.authlib_injector,
                    username,
                    password,
                    self.setting,
                )
            ):
                # 传递错误信息而不是unwrap的错误信息
                raise Exception(result.err_value)
            self.signin_state = SignInSuccess()
        except Exception as e:
            logging.error(f"登录失败: {traceback.format_exc()}")
            self.signin_state = SignInFail(str(e))
        self.signinFinished.emit()

    def accept(self):
        match self.signin_state:
            case SignInStart():
                self.state_tooltip = StateToolTip(
                    self.tr("正在登录"), self.tr("请稍后"), self
                )
                self.state_tooltip.move(
                    (self.width() - self.state_tooltip.width()) // 2,
                    (self.height() - self.state_tooltip.height()) // 2,
                )
                self.state_tooltip.show()

                self.buttonBox.setEnabled(False)

                self.signin_state = SigningIn()

                threading.Thread(target=self.signin, daemon=True).start()
            case SignInSuccess():
                self.state_tooltip.setContent(self.tr("登录成功"))
                super().accept()
            case SignInFail(error_message):
                self.state_tooltip.setContent(self.tr("登录失败"))
                QMessageBox.critical(self, self.tr("登陆失败"), str(error_message))
                super().accept()
