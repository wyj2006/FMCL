import threading

import requests
from modrinth_detail import ModrinthDetail
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget
from ui_modrinth_result import Ui_ModrinthResult

from fmcllib.game.modrinth_api import SearchHit
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

icon_cache = {}

widgets = []
windows = []


class ModrinthResult(QWidget, Ui_ModrinthResult):
    def __init__(self, hit: SearchHit):
        super().__init__()
        self.setupUi(self)
        self.hit = hit

        self.title.setText(hit["title"])
        self.description.setText(hit["description"])

        self.categories.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for category in hit["categories"]:
            label = QLabel()
            label.setText(category)
            label.setStyleSheet("border:1px solid black")
            self.categories.addWidget(label)

        threading.Thread(target=self.setupIcon, daemon=True).start()

    def setupIcon(self):
        icon_url = self.hit["icon_url"]
        if icon_url in icon_cache:
            r = icon_cache[icon_url]
        else:
            r = requests.get(icon_url).content
            icon_cache[icon_url] = r
        self.icon_label.setPixmap(
            QPixmap.fromImage(QImage.fromData(r)).scaled(self.icon_label.size())
        )

    def mouseDoubleClickEvent(self, a0):
        widget = ModrinthDetail(self.hit["project_id"])
        widget.installEventFilter(
            WindowSource(
                widget,
                on_detach=lambda w: Window(w).show(),
            )
        )
        window = Window(widget)
        window.show()

        widgets.append(widget)
        windows.append(window)

        return super().mouseDoubleClickEvent(a0)
