import json
import traceback

from PyQt6.Qsci import QsciLexerJSON, QsciScintilla
from PyQt6.QtCore import QEvent, pyqtSignal
from qfluentwidgets import FluentIcon, TransparentToolButton

from fmcllib import show_qerrormessage
from fmcllib.window import Window


class JsonEditor(QsciScintilla):
    saveRequest = pyqtSignal(object)  # 可能是包括dict在内的任何json object

    def __init__(self, content: str = "", parent=None):
        super().__init__(parent)
        self.resize(1000, 618)
        self.setWindowIcon(FluentIcon.CODE.icon())
        self.setWindowTitle(self.tr("Json代码编辑器"))

        self.setText(content)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setLexer(QsciLexerJSON(self))

        self.save_button = TransparentToolButton()
        self.save_button.setIcon(FluentIcon.SAVE.icon())
        self.save_button.setToolTip(self.tr("保存"))
        self.save_button.clicked.connect(self.save)

        self.titlebar_widgets = [
            {
                "index": 0,
                "widget": self.save_button,
                "alignment": "AlignRight",
            }
        ]

    def event(self, event: QEvent):
        match event.type():
            case QEvent.Type.Show:
                window = self.window()
                if not isinstance(window, Window):
                    return super().event(event)
                self.save_button.setFixedHeight(window.titleBar.height())
                self.save_button.setFixedWidth(window.titleBar.closeBtn.width())
        return super().event(event)

    def save(self):
        """保存, 失败返回0, 成功返回1"""
        content = self.text()
        try:
            self.saveRequest.emit(json.loads(content))
            return 1
        except:
            show_qerrormessage(
                self.tr("无法保存Json: ") + content,
                traceback.format_exc(),
                self,
            )
            return 0


class SettingJsonEditor(JsonEditor):
    pass
