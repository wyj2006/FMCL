import json
import os

from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import Theme, setTheme, setThemeColor

_translate = QCoreApplication.translate


def setThemeFromStr(theme: str):
    if theme == "Light":
        setTheme(Theme.LIGHT)
    elif theme == "Dark":
        setTheme(Theme.DARK)
    elif theme == "Auto":
        setTheme(Theme.AUTO)


# 默认设置路径
DEFAULT_SETTING_PATH = os.path.join("FMCL", "settings.json")
# 默认设置
DEFAULT_SETTING = {
    "system.startup_functions": [],
    "system.theme_color": "#00ff00",
    "system.theme": ["Light", "Dark"],
    "launcher.width": 1000,
    "launcher.height": 618,
    "game.directories": [".minecraft"],
    "game.java_path": "java",
    "game.width": 1000,
    "game.height": 618,
    "game.maxmem": 2048,
    "users": [],
    "users.selectindex": 0,
    "language.type": "简体中文"
}


def defaultSettingAttr():
    return {
        "system": {
            "name": _translate("Setting", "系统")
        },
        "system.startup_functions": {
            "name": _translate("Setting", "启动项")
        },
        "system.theme_color": {
            "name": _translate("Setting", "主题颜色"),
            "callback": lambda a: setThemeColor(a)
        },
        "system.theme": {
            "name": _translate("Setting",  "主题"),
            "callback": lambda a: setThemeFromStr(a[0]),
            "static": True
        },
        "launcher": {
            "name": _translate("Setting", "启动器")
        },
        "launcher.width": {
            "name":  _translate("Setting", "启动器宽度")
        },
        "launcher.height": {
            "name":  _translate("Setting", "启动器高度")
        },
        "game": {
            "name": _translate("Setting",  "游戏")
        },
        "game.directories": {
            "name":  _translate("Setting", "游戏目录"),
            "method": "directory",
            "atleast": 1
        },
        "game.java_path": {
            "name": _translate("Setting", "Java路径")
        },
        "game.width": {
            "name":  _translate("Setting", "游戏窗口宽度")
        },
        "game.height": {
            "name": _translate("Setting", "游戏窗口高度")
        },
        "game.maxmem": {
            "name": _translate("Setting", "最大内存")
        },
        "users": {
            "name":  _translate("Setting", "用户")
        },
        "users.selectindex": {
            "name": _translate("Setting", "选择用户索引")
        },
        "language": {
            "name": _translate("Setting", "语言"),
        },
        "language.type": {
            "name": _translate("Setting", "语言类型")
        }
    }


class Setting(dict):
    """管理设置文件"""
    instances = {}
    new_count = {}

    def __new__(cls, setting_path: str = DEFAULT_SETTING_PATH):
        if setting_path not in Setting.instances:
            Setting.instances[setting_path] = super().__new__(cls)
            Setting.new_count[setting_path] = 0
        Setting.new_count[setting_path] += 1
        return Setting.instances[setting_path]

    def __init__(self, setting_path: str = DEFAULT_SETTING_PATH):
        if Setting.new_count[setting_path] > 1:  # 防止重复初始化
            return
        self.attrs = {}
        self.setting_path = setting_path
        if setting_path == DEFAULT_SETTING_PATH:
            self.add(DEFAULT_SETTING)
            self.loadFunctionSetting()
        if os.path.exists(setting_path):
            for key, val in json.load(open(setting_path, encoding="utf-8")).items():
                self[key] = val

    def add(self, new_setting: dict):
        """添加新的设置"""
        for key, val in new_setting.items():
            if key not in self:
                self[key] = val

        for id in new_setting:
            self.attrs[id] = {
                "name": id
            }

    def addAttr(self, attr: dict):
        """添加设置属性"""
        self.merge(self.attrs, attr)

    def merge(self, a: dict, b: dict):
        """合并a和b"""
        for key, val in b.items():
            if key not in a:
                a[key] = val
            elif isinstance(val, dict):
                self.merge(a[key], val)
            else:
                a[key] = val

    def getAttr(self, id: str, attr: str, default=None):
        """获取设置项的属性"""
        return self.attrs[id].get(attr, default)

    def sync(self):
        if not os.path.exists(os.path.dirname(self.setting_path)):
            os.makedirs(os.path.dirname(self.setting_path))
        json.dump(self,
                  open(self.setting_path, mode="w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    def set(self, id: str, val):
        self[id] = val
        self.sync()
        self.callback(id, val)

    def callback(self, id: str, val=None):
        if val == None:
            val = self.get(id)
        self.getAttr(id, "callback", lambda _: ...)(val)

    def loadFunctionSetting(self):
        """加载功能的设置"""
        from Kernel import Kernel
        for function in Kernel.getAllFunctions():
            self.add(getattr(function, "defaultSetting", lambda: {})())

    def loadFunctionSettingAttr(self):
        """加载功能的设置属性"""
        from Kernel import Kernel
        for function in Kernel.getAllFunctions():
            self.addAttr(
                getattr(function, "defaultSettingAttr", lambda: {})())
