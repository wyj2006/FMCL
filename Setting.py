import json
import logging
import os
import shutil
import traceback
import multitasking
import psutil
import qtawesome as qta

from types import MappingProxyType
from typing import Any, Literal, TypedDict, Callable
from PyQt5.QtCore import QCoreApplication, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QFileDialog, qApp
from qfluentwidgets import setThemeColor, PrimaryPushButton, setTheme, Theme, qconfig
from Core.Function import Function
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

_translate = QCoreApplication.translate


# 默认设置路径
DEFAULT_SETTING_PATH = os.path.join("FMCL", "settings.json")
# 默认设置
DEFAULT_SETTING = {
    "system.startup_functions": [],
    "system.theme_color": "#00aa00",
    "system.temp_dir": "FMCL/Temp",
    "system.import_paths": [],
    "system.theme": "Light",
    "game.directories": [".minecraft"],
    "game.auto_choose_java": True,
    "game.java_paths": [],
    "game.width": 1000,
    "game.height": 618,
    "game.maxmem": 2048,
    "game.launch_commands": {
        "Main": {"program": "{java_path}", "args": "{default_args}"},
    },
    "users": [],
    "users.selectindex": 0,
    "users.authlibinjector_servers": [],
    "language.type": "简体中文",
}


class SettingAttr(TypedDict):
    """设置属性类型"""

    name: str  # 名称, 默认与id一样
    callback: list[Callable[[Any], None]]  # 回调函数, 在对应设置项被修改后调用
    enable_condition: Callable[
        ["Setting"], bool
    ]  # 启用条件, 禁用后, 它的子设置也会被禁用
    settingcard: Callable[[], QWidget]  # 设置卡片, 默认由SettingEditor设置
    side_widgets: list[Callable[[], QWidget]]  # 放在标签旁边的控件
    type: Literal["directory", "file", "color"]  # 非基本类型
    # 以下属性将用于List设置项
    static: bool  # 是否为静态(不可更改, 当成tuple)
    atleast: int  # 至少要有几项
    # 以下属性将用户Int或Float设置项
    min_value: int | float  # 最小值
    max_value: int | float  # 最大值


def qta_dark(app):
    dark_palette = QPalette()

    # base
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(51, 51, 51))
    dark_palette.setColor(QPalette.Light, QColor(180, 180, 180))
    dark_palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    dark_palette.setColor(QPalette.Dark, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
    dark_palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.Window, QColor(31, 31, 31))
    dark_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
    dark_palette.setColor(QPalette.Link, QColor(56, 252, 196))
    dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
    dark_palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

    # disabled
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(
        QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127)
    )

    app.style().unpolish(app)
    app.setPalette(dark_palette)


def qta_light(app):
    light_palette = QPalette()

    # base
    light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
    light_palette.setColor(QPalette.Light, QColor(180, 180, 180))
    light_palette.setColor(QPalette.Midlight, QColor(200, 200, 200))
    light_palette.setColor(QPalette.Dark, QColor(225, 225, 225))
    light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
    light_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Base, QColor(237, 237, 237))
    light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
    light_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    light_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
    light_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Link, QColor(0, 162, 232))
    light_palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
    light_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))

    # disabled
    light_palette.setColor(
        QPalette.Disabled, QPalette.WindowText, QColor(115, 115, 115)
    )
    light_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(115, 115, 115))
    light_palette.setColor(
        QPalette.Disabled, QPalette.ButtonText, QColor(115, 115, 115)
    )
    light_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(190, 190, 190))
    light_palette.setColor(
        QPalette.Disabled, QPalette.HighlightedText, QColor(115, 115, 115)
    )

    app.style().unpolish(app)
    app.setPalette(light_palette)


def set_qta_theme(theme: Theme):
    qta.reset_cache()
    if theme == Theme.LIGHT:
        qta_light(qApp)
    elif theme == Theme.DARK:
        qta_dark(qApp)


def set_theme(theme: str):
    theme = theme.title()
    if theme == "Light":
        setTheme(Theme.LIGHT)
    elif theme == "Dark":
        setTheme(Theme.DARK)
    elif theme == "Auto":
        setTheme(Theme.AUTO)
    else:
        logging.error(f"未知的主题:{theme}")
        return
    set_qta_theme(qconfig.theme)


def defaultSettingAttr() -> dict[str, SettingAttr]:
    def choosejava():
        file, _ = QFileDialog.getOpenFileName(
            None, _translate("Setting", "选择Java"), filter="Java (java.*)"
        )
        if file and file not in Setting()["game.java_paths"]:
            Setting()["game.java_paths"].append(file)

    def checktempdir(temp_dir):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

    def choosetempdir():
        dir = QFileDialog.getExistingDirectory(
            None, _translate("Setting", "选择缓存文件夹")
        )
        if dir:
            Setting().set("system.temp_dir", dir)

    def cleantempdir():
        temp_dir = Setting()["system.temp_dir"]
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

    def choosegamedir():
        dir = QFileDialog.getExistingDirectory(
            None, _translate("Setting", "选择游戏文件夹")
        )
        if dir:
            Setting().get("game.directories").append(dir)

    def chooseimportpath():
        dir = QFileDialog.getExistingDirectory(
            None, _translate("Setting", "选择包含路径")
        )
        if dir:
            import_paths = Setting()["system.import_paths"]
            if dir not in import_paths:
                import_paths.append(dir)

    def chooseimportpathbutton():
        pb_chooseimportpath = PrimaryPushButton()
        pb_chooseimportpath.setText(_translate("Setting", "添加"))
        pb_chooseimportpath.clicked.connect(chooseimportpath)
        return pb_chooseimportpath

    def choosejavabutton():
        pb_choosejava = PrimaryPushButton()
        pb_choosejava.setText(_translate("Setting", "手动添加Java"))
        pb_choosejava.clicked.connect(choosejava)
        return pb_choosejava

    @multitasking.task
    def autofindjava():
        from Core import Java

        java_paths = Java.auto_find_java()
        Setting().set(
            "game.java_paths", list(set(Setting()["game.java_paths"] + java_paths))
        )

    def autofindjavabutton():
        pb_autofindjava = PrimaryPushButton()
        pb_autofindjava.setText(_translate("Setting", "自动查找Java"))
        pb_autofindjava.clicked.connect(lambda: autofindjava())
        return pb_autofindjava

    def choosetempdirbutton():
        pb_choosetempdir = PrimaryPushButton()
        pb_choosetempdir.setText(_translate("Setting", "选择文件夹"))
        pb_choosetempdir.clicked.connect(choosetempdir)
        return pb_choosetempdir

    def cleantempdirbutton():
        pb_cleantempdir = PrimaryPushButton()
        pb_cleantempdir.setText(_translate("Setting", "清理"))
        pb_cleantempdir.clicked.connect(cleantempdir)
        return pb_cleantempdir

    def choosegamedirbutton():
        pb_choosegamedir = PrimaryPushButton()
        pb_choosegamedir.setText(_translate("Setting", "选择文件夹"))
        pb_choosegamedir.clicked.connect(choosegamedir)
        return pb_choosegamedir

    return {
        "system": {"name": _translate("Setting", "系统")},
        "system.startup_functions": {"name": _translate("Setting", "启动项")},
        "system.theme_color": {
            "name": _translate("Setting", "主题颜色"),
            "callback": [lambda a: setThemeColor(a)],
            "type": "color",
        },
        "system.temp_dir": {
            "name": _translate("Setting", "缓存文件夹"),
            "side_widgets": [cleantempdirbutton, choosetempdirbutton],
            "callback": [checktempdir],
        },
        "system.import_paths": {
            "name": _translate("Setting", "包含路径"),
            "side_widgets": [chooseimportpathbutton],
        },
        "system.theme": {
            "name": _translate("Setting", "主题"),
            "callback": [set_theme],
        },
        "game": {"name": _translate("Setting", "游戏")},
        "game.directories": {
            "name": _translate("Setting", "游戏目录"),
            "type": "directory",
            "atleast": 1,
            "side_widgets": [choosegamedirbutton],
        },
        "game.auto_choose_java": {"name": _translate("Setting", "自动选择Java")},
        "game.java_paths": {
            "name": _translate("Setting", "Java路径"),
            "side_widgets": [choosejavabutton, autofindjavabutton],
            "static": True,
        },
        "game.width": {"name": _translate("Setting", "游戏窗口宽度")},
        "game.height": {"name": _translate("Setting", "游戏窗口高度")},
        "game.maxmem": {
            "name": _translate("Setting", "最大内存"),
            "min_value": 512,
            "max_value": int(psutil.virtual_memory().total / 1024 / 1024),
        },
        "game.launch_commands": {
            "name": _translate("Setting", "启动参数"),
        },
        "users": {"name": _translate("Setting", "用户")},
        "users.selectindex": {"name": _translate("Setting", "选择用户索引")},
        "users.authlibinjector_servers": {"name": _translate("Setting", "认证服务器")},
        "language": {
            "name": _translate("Setting", "语言"),
        },
        "language.type": {"name": _translate("Setting", "语言类型")},
    }


class ListSettingTrace(list):
    def __init__(self, l, op):
        super().__init__(l)
        self.op = op  # 对象被更改后的操作

    def append(self, __object) -> None:
        super().append(__object)
        self.op(list(self))

    def pop(self, __index=-1):
        ret = super().pop(__index)
        self.op(list(self))
        return ret

    def insert(self, __index, __object):
        super().insert(__index, __object)
        self.op(list(self))

    def extend(self, __iterable):
        super().extend(__iterable)
        self.op(list(self))

    def remove(self, __value):
        super().remove(__value)
        self.op(list(self))

    def sort(self, *args):
        super().sort(*args)
        self.op(list(self))

    def __setitem__(self, *args):
        super().__setitem__(*args)
        self.op(list(self))


class DictSettingTrace(dict):
    def __init__(self, d, op):
        super().__init__(d)
        self.op = op  # 对象被更改后的操作

    def __setitem__(self, *args):
        super().__setitem__(*args)
        self.op(dict(self))

    def pop(self) -> tuple:
        super().pop()
        self.op(dict(self))


class SettingMonitor(FileSystemEventHandler, QObject):
    __changed = pyqtSignal()

    def __init__(self, setting: "Setting"):
        super().__init__()
        self.setting = setting

        self.__changed.connect(self.setting.update)

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.src_path == self.setting.setting_path:
            self.__changed.emit()
        return super().on_any_event(event)


def merge(a, b):
    for key, val in b.items():
        if key not in a:
            a[key] = val
        elif isinstance(val, dict):
            merge(a[key], val)
        elif isinstance(val, list):
            a[key].extend(val)
        else:
            a[key] = val


class Setting:
    """设置"""

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
        self.attrs: dict[str, SettingAttr] = {}
        self.setting_path = setting_path
        self.attr_path = os.path.splitext(setting_path)[0] + f".attrs.py"

        self.modifiedsetting = {}  # 修改过的设置
        self.defaultsetting = {}  # 默认设置

        if setting_path == DEFAULT_SETTING_PATH:
            self.add(DEFAULT_SETTING)
            self.addAttr(defaultSettingAttr())
            self.loadFunctionSetting()
            self.loadFunctionSettingAttr()
        if os.path.exists(setting_path):
            for key, val in json.load(open(setting_path, encoding="utf-8")).items():
                self.modifiedsetting[key] = val
        if os.path.exists(self.attr_path):
            for key, val in eval(open(self.attr_path, encoding="utf-8").read()).items():
                if key not in self.attrs:
                    self.attrs[key] = {}
                self.attrs[key] |= val

        self.monitor = SettingMonitor(self)
        self.observer = Observer()
        # 一直找到存在的path并监视
        path = os.path.dirname(self.setting_path)
        while not os.path.exists(path):
            path = os.path.dirname(path)
        logging.debug(f"{setting_path} 监视 {path}")
        self.observer.schedule(self.monitor, path)
        self.observer.start()

    def update(self):
        """更新设置(不包括属性)"""
        try:
            if os.path.exists(self.setting_path):
                for key, val in json.load(
                    open(self.setting_path, encoding="utf-8")
                ).items():
                    self.set(key, val)
            else:
                self.restore("")
        except json.JSONDecodeError:
            logging.error(traceback.format_exc())

    def add(self, new_setting: dict):
        """添加新的默认设置"""
        for key, val in new_setting.items():
            if key not in self.defaultsetting:
                if isinstance(val, list):  # 让默认设置不可变
                    val = tuple(val)
                elif isinstance(val, dict):
                    val = MappingProxyType(val)
                self.defaultsetting[key] = val

        for item_id in new_setting:
            splitid = item_id.split(".")
            for i in range(len(splitid)):
                id = ".".join(splitid[: i + 1])
                if id not in self.attrs:
                    self.attrs[id] = {"name": id}

    def addAttr(self, attr: dict[str, SettingAttr]):
        """添加设置属性"""
        for key, val in attr.items():
            if key not in self.attrs:
                self.attrs[key] = val
                continue
            # 防止之前已经加载过
            self.attrs[key] |= val

    def getAttr(self, id: str, attr: str, default=None):
        """获取设置项的属性"""
        if id not in self.attrs:
            self.attrs[id] = {"name": id}
        return self.attrs[id].get(attr, default)

    def sync(self):
        if not os.path.exists(os.path.dirname(self.setting_path)):
            os.makedirs(os.path.dirname(self.setting_path))
        json.dump(
            self.modifiedsetting,
            open(self.setting_path, mode="w", encoding="utf-8"),
            ensure_ascii=False,
            indent=4,
        )

        def clear(data: dict):
            attrs = {}
            for key, val in data.items():
                for k, v in val.items():
                    if k in (
                        "name",
                        "callback",
                        "enable_condition",
                        "settingcard",
                        "side_widgets",
                        "type",
                        "static",
                        "atleast",
                        "min_value",
                        "max_value",
                    ):
                        continue
                    if key not in attrs:
                        attrs[key] = {}
                    if isinstance(v, dict):
                        nv = clear(v)
                        if nv:
                            attrs[key][k] = nv
                    else:
                        attrs[key][k] = v
            return attrs

        attrs = clear(self.attrs)
        if attrs:
            open(self.attr_path, mode="w", encoding="utf-8").write(str(attrs))

    def set(self, id: str, val):
        if isinstance(val, list) and list(val) == list(self[id]):
            return
        if isinstance(val, dict) and dict(val) == dict(self[id]):
            return
        if val == self[id]:
            return
        self[id] = val
        self.sync()
        self.callback(id, val)

    def callback(self, id: str, val=None):
        if val == None:
            val = self.get(id)
        for i in self.getAttr(id, "callback", tuple()):
            i(val)

    def loadFunctionSetting(self):
        """加载功能的设置"""
        for function in Function.get_all():
            self.add(function.get_default_setting())

    def loadFunctionSettingAttr(self):
        """加载功能的设置属性"""
        for function in Function.get_all():
            self.addAttr(function.get_default_settingattr())

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        if key in self.modifiedsetting:
            val = self.modifiedsetting[key]
        elif key in self.defaultsetting:
            val = self.defaultsetting[key]
        else:
            raise KeyError(key)
        if isinstance(val, tuple):
            val = list(val)
        elif isinstance(val, MappingProxyType):
            val = dict(val)
        if isinstance(val, list):
            val = ListSettingTrace(val, lambda v: self.set(key, v))
        elif isinstance(val, dict):
            val = DictSettingTrace(val, lambda v: self.set(key, v))
        return val

    def items(self):
        return (self.defaultsetting | self.modifiedsetting).items()

    def __setitem__(self, key, value):
        self.modifiedsetting[key] = value
        if key in self.defaultsetting and self.defaultsetting[key] == value:
            self.modifiedsetting.pop(key)

    def restore(self, id):
        """恢复默认设置"""
        for id_ in (self.defaultsetting | self.modifiedsetting).keys():
            if id in id_:
                self.set(id_, self.defaultsetting[id_])

    def __contains__(self, key):
        return key in self.modifiedsetting or key in self.defaultsetting

    def __del__(self):
        self.observer.stop()
        return super().__del__()
