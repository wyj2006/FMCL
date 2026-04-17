import threading

import iso8601
import qtawesome as qta
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, PushButton
from ui_modrinth_version import Ui_ModrinthVersion

from fmcllib.game.modrinth_api import (
    GetProjectResponse,
    VersionDependence,
    VersionFile,
    VersionResponse,
    get_project,
)
from fmcllib.task import download


class ModrinthVersion(QWidget, Ui_ModrinthVersion):
    dependentGot = pyqtSignal(dict, dict)  # VersionDependence,GetProjectResponse

    def __init__(self, version_info: VersionResponse):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(self.tr("版本") + ": " + version_info["name"])
        self.setWindowIcon(qta.icon("msc.versions"))

        self.depend_layout = QVBoxLayout()
        self.depend_group.viewLayout.addLayout(self.depend_layout)
        self.depend_group.setTitle(self.tr("依赖"))

        self.file_group.setTitle(self.tr("文件"))

        self.dependentGot.connect(self.addDependence)

        if not version_info["dependencies"]:
            self.dep_group.hide()
        for dependence in version_info["dependencies"]:
            threading.Thread(
                target=lambda dependence=dependence: self.dependentGot.emit(
                    dependence, get_project(dependence["project_id"]).unwrap()
                ),
                daemon=True,
            ).start()

        for file in version_info["files"]:
            download_button = PushButton()
            download_button.setText(self.tr("下载"))
            download_button.clicked.connect(lambda _, file=file: self.download(file))
            self.file_group.addGroup(
                FluentIcon.DOCUMENT.icon(),
                file["filename"],
                self.tr("主要文件") if file["primary"] else "",
                download_button,
            )

        for key, text in (
            ("downloads", str(version_info["downloads"])),
            (
                "date_published",
                iso8601.parse_date(version_info["date_published"]).strftime(
                    self.tr("%Y年%m月%d日 %H:%M:%S")
                ),
            ),
        ):
            getattr(self, f"{key}_label").setText(text)

    def download(self, file: VersionFile):
        filename, _ = QFileDialog.getSaveFileName(
            caption=self.tr("下载文件"), directory=file["filename"]
        )
        if not filename:
            return
        threading.Thread(
            target=download, args=(file["url"], filename), daemon=True
        ).start()

    def addDependence(
        self, dependence: VersionDependence, project_info: GetProjectResponse
    ):
        from modrinth_result import ModrinthResult

        # GetProjectResponse和SearchResponse的不同之处之一
        project_info["project_id"] = project_info["id"]
        w = ModrinthResult(project_info)
        # w.categories.deleteLater()
        w.description.setText(
            {
                "required": self.tr("必需"),
                "optional": self.tr("可选"),
                "incompatible": self.tr("不兼容"),
                "embedded": self.tr("嵌入"),
            }.get(dependence["dependency_type"], dependence["dependency_type"])
        )
        self.depend_layout.addWidget(w)
