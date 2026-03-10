import threading
import time
import webbrowser
from typing import Literal, TypedDict

import qtawesome as qta
import requests
from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QResizeEvent
from PyQt6.QtWidgets import QApplication, QFrame, QWidget
from ui_news import Ui_News
from ui_news_entry import Ui_NewsEntry


class NewsPageImageDict(TypedDict):
    title: str
    url: str
    dimensions: dict[Literal["width", "height"], int]


class NewsEntryDict(TypedDict):
    title: str
    category: str
    date: str
    text: str
    playPageImage: dict[Literal["title", "url"], str]
    newsPageImage: NewsPageImageDict
    readMoreLink: str
    newsType: list[str]
    id: str


class MinecraftNews(TypedDict):
    version: int
    entries: list[NewsEntryDict]


class NewsEntry(QFrame, Ui_NewsEntry):
    WIDTH = 300

    def __init__(self, entry: NewsEntryDict):
        super().__init__()
        self.setupUi(self)
        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(self.WIDTH)
        self.image_label.setFixedHeight(self.WIDTH // 2)
        self.entry = entry

        self.title_label.setText(entry["title"])
        self.text_label.setText(entry["text"])
        self.date_label.setText(entry["date"])

        threading.Thread(target=self.getImage, daemon=True).start()

    def getImage(self):
        for _ in range(10):
            try:
                data = requests.get(
                    f'https://launchercontent.mojang.com/{self.entry["newsPageImage"]["url"]}'
                ).content
                self.image_label.setPixmap(
                    QPixmap.fromImage(QImage.fromData(data)).scaled(
                        self.image_label.size()
                    )
                )
                break
            except:
                time.sleep(3)

    def event(self, a0):
        match a0.type():
            case QEvent.Type.Enter:
                self.setStyleSheet("QFrame#NewsEntry{border:1px solid black;}")
            case QEvent.Type.Leave:
                self.setStyleSheet("QFrame#NewsEntry{border:none;}")
            case QEvent.Type.MouseButtonRelease:
                webbrowser.open(self.entry["readMoreLink"])
        return super().event(a0)


class News(QWidget, Ui_News):
    newsGot = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("fa5.newspaper"))

        self.max_col = 0
        self.cur_row = self.cur_col = 0
        self.news_entries: list[NewsEntry] = []

        self.newsGot.connect(self.setEntries)
        threading.Thread(target=self.getNews, daemon=True).start()

    def getNews(self):
        news: MinecraftNews = requests.get(
            "https://launchercontent.mojang.com/news.json"
        ).json()
        self.newsGot.emit(news)

    def setEntries(self, news: MinecraftNews):
        self.news_entries = []
        for entry in news["entries"]:
            news_entry = NewsEntry(entry)
            self.addEntry(news_entry)
            self.news_entries.append(news_entry)
            QApplication.instance().processEvents()

    def addEntry(self, widget: QWidget):
        self.gl_entries.addWidget(widget, self.cur_row, self.cur_col)
        self.cur_col += 1
        if self.cur_col == self.max_col:
            self.cur_row += 1
            self.cur_col = 0

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.cur_col = self.cur_row = 0
        self.max_col = self.width() // NewsEntry.WIDTH
        for news_entry in self.news_entries:
            self.addEntry(news_entry)
        return super().resizeEvent(a0)
