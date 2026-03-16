import sys

from news import News

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = Application(sys.argv)
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
