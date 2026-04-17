import qtawesome as qta
from modrinth_searcher import ModrinthSearcher
from PyQt6.QtCore import QEvent, pyqtSlot
from PyQt6.QtWidgets import QApplication, QListWidgetItem, QWidget
from searcher import Searcher
from ui_resource_downloader import Ui_ResourceDownloader


class ResourceDownloader(QWidget, Ui_ResourceDownloader):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("mdi.earth"))
        self.splitter.setSizes([100, 400])

        self.searchers: dict[str, Searcher] = {"Modrinth": ModrinthSearcher()}
        for name, searcher in self.searchers.items():
            self.searcher_tab.addItem(
                name,
                name,
                lambda _, a=searcher: self.searcher_stack.setCurrentWidget(a),
            )
            searcher.searchFinished.connect(
                lambda a: [
                    (self.addSearchResult(i), QApplication.instance().processEvents())
                    for i in a
                ]
            )
            self.searcher_stack.addWidget(searcher)

        self.search_input.searchSignal.connect(self.search)

    @pyqtSlot(int)
    def on_searcher_stack_currentChanged(self, _):
        for name, searcher in self.searchers.items():
            if searcher == self.searcher_stack.currentWidget():
                self.searcher_tab.setCurrentItem(name)
                break

    def search(self):
        self.search_results.clear()
        query = self.search_input.text()
        for name, searcher in self.searchers.items():
            if not getattr(self, f"{name.lower()}_enable").isChecked():
                continue
            searcher.search(query)

    def addSearchResult(self, widget: QWidget):
        item = QListWidgetItem()
        item.setSizeHint(widget.size())
        self.search_results.addItem(item)
        self.search_results.setItemWidget(item, widget)

    def event(self, a0):
        match a0.type():
            case QEvent.Type.Close | QEvent.Type.DeferredDelete:
                # 在同时有ResourceDownloader和ModrinthDetail时关闭Explorer,
                # 会导致ResourceDownloader的窗口无法正常关闭, 具体原因不详
                import modrinth_detail
                import modrinth_result

                if all(
                    [
                        not i.isVisible()
                        for i in modrinth_result.widgets + modrinth_detail.widgets
                    ]
                ):
                    QApplication.instance().quit()
        return super().event(a0)
