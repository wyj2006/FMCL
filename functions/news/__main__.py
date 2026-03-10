import sys

from news import News
from PyQt6.QtWidgets import QApplication

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = QApplication(sys.argv)
news = News()
news.installEventFilter(
    WindowSource(
        news,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(news)
window.show()
sys.exit(app.exec())
