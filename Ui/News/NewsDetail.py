import webbrowser
from Core.News import News
from QtFBN.QFBNWidget import QFBNWidget
from Ui.News.ui_NewsDetail import Ui_NewsDetail
from Translate import tr
from PyQt5.QtCore import pyqtSlot
import qtawesome as qta


class NewsDetail(QFBNWidget, Ui_NewsDetail):
    def __init__(self, info, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(qta.icon("fa.newspaper-o"))
        self.setWindowTitle(tr("新闻详情")+":"+info["title"])
        self.pb_openurl.setText(tr("打开网址"))

        self.info = info
        News().get_news_detail(self.info)
        self.l_title.setText(self.info["title"])
        self.te_body.setHtml(str(self.info["article_body"]))

    @pyqtSlot(bool)
    def on_pb_openurl_clicked(self, _):
        webbrowser.open(self.info["article_url"])