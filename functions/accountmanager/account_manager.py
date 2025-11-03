from authlib_injector_adder import AuthlibInjectorAdder
from authlib_injector_signiner import AuthlibInjectorSignIner
from offline_adder import OfflineAdder
from profile_displayer import ProfileDisplayer
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon, NavigationItemPosition
from ui_account_manager import Ui_AccountManager

from fmcllib.account import AuthlibInjectorDict, ProfileDict
from fmcllib.setting import Setting


class AccountManager(QWidget, Ui_AccountManager):
    def __init__(self, setting: Setting = None):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.PEOPLE.icon())

        # 账户信息是存在设置里的
        if setting == None:
            setting = Setting()
        self.setting = setting

        self.login_method_panel.setMenuButtonVisible(False)
        self.login_method_panel.setCollapsible(False)
        self.login_method_panel.setExpandWidth(self.login_method_panel.width())

        self.profile_displayers: list[ProfileDisplayer] = []

        self.refresh()

    def addOffline(self):
        adder = OfflineAdder(self.setting, self)
        if adder.exec():
            self.refresh()

    def addAuthlibInjector(self):
        adder = AuthlibInjectorAdder(self.setting, self)
        if adder.exec():
            self.refresh()

    def signinAuthlibInjector(self, authlib_injector: AuthlibInjectorDict):
        adder = AuthlibInjectorSignIner(authlib_injector, self.setting, self)
        if adder.exec():
            self.refresh()

    def refresh(self):
        for i in tuple(self.login_method_panel.items):
            self.login_method_panel.removeWidget(i)

        self.login_method_panel.addItem(
            "offline_account",
            FluentIcon.PEOPLE.icon(),
            self.tr("离线账号"),
            onClick=self.addOffline,
            selectable=False,
            tooltip=self.tr("离线账号"),
        )

        authlib_injector: AuthlibInjectorDict
        for authlib_injector in self.setting.get(
            "account.authlib_injector_servers"
        ).unwrap_or([]):
            meta = authlib_injector["metadata"]["meta"]
            name = authlib_injector["url"]
            if "serverName" in meta:
                name = meta["serverName"]
            self.login_method_panel.addItem(
                name,
                FluentIcon.TILES.icon(),
                name,
                onClick=lambda _, a=authlib_injector: self.signinAuthlibInjector(a),
                selectable=False,
                tooltip=name,
            )

        self.login_method_panel.addItem(
            "add_authlib_injector",
            FluentIcon.ADD.icon(),
            self.tr("添加外置登录服务器"),
            onClick=self.addAuthlibInjector,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
            tooltip=self.tr("添加外置登录服务器"),
        )

        while self.account_layout.count() > 1:  # 不删除spacer
            if (widget := self.account_layout.takeAt(0).widget()) != None:
                widget.deleteLater()

        while self.profile_displayers:
            self.profile_displayers.pop(0).deleteLater()

        profile: ProfileDict
        for i, profile in enumerate(self.setting.get("account.profiles").unwrap_or([])):
            displayer = ProfileDisplayer(profile, self.setting)
            displayer.deleted.connect(self.refresh)
            displayer.selected.connect(lambda _, i=i: self.setCurrentProfile(i))
            self.account_layout.insertWidget(i, displayer)
            self.profile_displayers.append(displayer)
        if (current := self.setting.get("account.current").unwrap_or(-1)) == -1:
            current = 0
        self.setCurrentProfile(current)

    def setCurrentProfile(self, current):
        for i, display in enumerate(self.profile_displayers):
            display.setSelected(i == current)
        self.setting.set("account.current", current)
