import threading

from modrinth_result import ModrinthResult
from PyQt6.QtCore import pyqtSignal
from result import is_ok
from searcher import Searcher
from ui_modrinth_searcher import Ui_ModrinthSearcher

from fmcllib.game.modrinth_api import (
    SearchResponse,
    get_categories,
    get_gameversions,
    get_loaders,
    get_projec_types,
    search_project,
)


class ModrinthSearcher(Searcher, Ui_ModrinthSearcher):
    responseProcessReq = pyqtSignal(dict)  # SearchResponse

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.responseProcessReq.connect(self.processResponse)
        threading.Thread(target=self.setupFilters, daemon=True).start()

    def setupFilters(self):
        for game_version in get_gameversions().ok_value:
            self.game_version.addItem(game_version["version"])
        for category in get_categories().ok_value:
            self.category.addItem(category["name"])
        for loader in get_loaders().ok_value:
            self.loader.addItem(loader["name"])
        self.project_type.addItems(
            [
                {
                    "mod": self.tr("模组"),
                    "modpack": self.tr("整合包"),
                    "resourcepack": self.tr("材质包"),
                    "shader": self.tr("着色器"),
                    "plugin": self.tr("插件"),
                    "datapack": self.tr("数据包"),
                    "minecraft_java_server": self.tr("服务端"),
                }.get(i, i)
                for i in get_projec_types()
            ]
        )

    def search(self, query: str):
        facets = []
        if self.game_version.currentIndex() != 0:
            facets.append(f"versions={self.game_version.currentText()}")
        if self.category.currentIndex() != 0:
            facets.append(f"categories={self.category.currentText()}")
        if self.loader.currentIndex() != 0:
            # loaders are lumped in with categories in search
            facets.append(f"categories={self.loader.currentText()}")
        if self.project_type.currentIndex() != 0:
            facets.append(f"project_type={self.project_type.currentText()}")
        threading.Thread(
            target=lambda: (
                self.responseProcessReq.emit(result.ok_value)
                if is_ok(
                    result := search_project(
                        query,
                        facets=f"[{str(facets).replace("'","\"")}]" if facets else "",
                        offset=self.offset.value(),
                        limit=self.limit.value(),
                        index=[
                            "relevance",
                            "downloads",
                            "follows",
                            "newest",
                            "updated",
                        ][self.index.currentIndex()],
                    )
                )
                else None
            ),
            daemon=True,
        ).start()

    def processResponse(self, response: SearchResponse):
        self.searchFinished.emit([ModrinthResult(i) for i in response["hits"]])
