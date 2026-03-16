from enum import Enum

from qfluentwidgets import ComboBox

from fmcllib.setting import Setting

SUPPORT_LANG = ["zh_CN", "en_US"]


class LangCode(Enum):
    """语言代码"""

    zh = "简体中文"
    en = "English"


class TerritoryCode(Enum):
    """地区代码"""

    CN = "中国"
    US = "US"


class LangChooser(ComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)

        self.addItems(list(map(code_to_str, SUPPORT_LANG)))
        self.setCurrentIndex(
            SUPPORT_LANG.index(Setting().get("system.language").unwrap_or("zh_CN"))
        )

        self.currentIndexChanged.connect(self.onCurrentIndexChanged)

    def onCurrentIndexChanged(self, index: int):
        Setting().set("system.language", SUPPORT_LANG[index])


def code_to_str(code: str) -> str:
    """将语言代码转换成可读字符串"""
    code = code.replace("-", "_")
    code = code.split("_")
    lang = LangCode.__members__[code[0].lower()].value
    if len(code) > 1:
        territory = TerritoryCode.__members__[code[1].upper()].value
    else:
        territory = ""
    if territory:
        return f"{lang}({territory})"
    else:
        return f"{lang}"
