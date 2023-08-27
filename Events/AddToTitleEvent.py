from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget


class AddToTitleEvent(QEvent):
    """添加到标题栏事件"""
    EventType = QEvent.registerEventType()

    def __init__(self, widget: QWidget, place="left", index=0, sender: QWidget = None):
        """
        sender指的是事件的发送者,一般给嵌入的控件使用
        """
        super().__init__(self.EventType)
        self.widget = widget
        self.place = place
        self.index = index
        self.sender = sender
