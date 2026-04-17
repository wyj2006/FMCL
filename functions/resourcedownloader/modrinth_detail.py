import threading
import time

import qtawesome as qta
from modrinth_version import ModrinthVersion
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QListWidgetItem, QWidget
from qfluentwidgets import HyperlinkButton
from ui_modrinth_detail import Ui_ModrinthDetail

from fmcllib.game.modrinth_api import (
    GetProjectResponse,
    VersionResponse,
    get_project,
    list_project_versions,
)
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

widgets = []
windows = []


class ModrinthDetail(QWidget, Ui_ModrinthDetail):
    projectGot = pyqtSignal(dict)  # GetProjectResponse
    versionsGot = pyqtSignal(list)  # list[VersionResponse]

    def __init__(self, project_id: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("mdi.details"))
        self.project_id = project_id
        self.version_infos: dict[str, VersionResponse] = {}  # 键为QListWidgetItem的文本

        self.projectGot.connect(self.setupProject)
        self.versionsGot.connect(self.setupVersions)

        threading.Thread(
            target=lambda: self.projectGot.emit(get_project(project_id).unwrap()),
            daemon=True,
        ).start()

    def setupProject(self, project_info: GetProjectResponse):
        self.project_info = project_info
        self.setWindowTitle(self.tr("模组") + ": " + project_info["title"])

        button = HyperlinkButton()
        button.setText("Modrinth")
        button.setUrl(
            f"https://modrinth.com/{project_info["project_type"]}/{project_info["slug"]}"
        )
        self.url_layout.addWidget(button)

        for key, name in (
            ("issues_url", self.tr("反馈")),
            ("source_url", self.tr("源码")),
            ("wiki_url", "Wiki"),
            ("discord_url", "Discord"),
        ):
            if key not in project_info or project_info[key] == None:
                continue
            button = HyperlinkButton()
            button.setText(name)
            button.setUrl(project_info[key])
            self.url_layout.addWidget(button)

        from modrinth_result import ModrinthResult

        w = ModrinthResult(project_info)
        w.mouseDoubleClickEvent = lambda e: QWidget.mouseDoubleClickEvent(w, e)
        self.result_layout.addWidget(w)

        threading.Thread(
            target=lambda: self.versionsGot.emit(
                list_project_versions(self.project_id).unwrap()
            ),
            daemon=True,
        ).start()

    def setupVersions(self, version_infos: list[VersionResponse]):
        self.version_infos = {}
        for version_info in version_infos:
            self.version_infos[version_info["name"]] = version_info
            self.version_list.addItem(version_info["name"])

    @pyqtSlot(QListWidgetItem)
    def on_version_list_itemDoubleClicked(self, item: QListWidgetItem):
        widget = ModrinthVersion(self.version_infos[item.text()])
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
