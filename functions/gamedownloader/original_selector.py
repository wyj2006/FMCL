import threading

from game_selector import GameSelector
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog, QSizePolicy, QSpacerItem
from qfluentwidgets import SettingCard
from ui_original_selector import Ui_OriginalSelector

from fmcllib.game import (
    OriginalVersionInfo,
    download_install_original,
    download_original,
    get_original_versions,
)


class VersionInfoViewer(SettingCard):
    selected = pyqtSignal()

    def __init__(self, version_info: OriginalVersionInfo):
        match version_info["type"]:
            case "release":
                icon = QIcon(":/image/grass@2x.png")
            case "snapshot":
                icon = QIcon(":/image/command@2x.png")
            case "old_alpha" | "old_beta":
                icon = QIcon(":/image/craft_table@2x.png")
            case _:
                icon = QIcon(":/image/fmcl.png")
        title = version_info["id"]
        content = version_info["releaseTime"].replace("T", " ").replace("+", " ")
        super().__init__(icon, title, content)
        self.setIconSize(32, 32)
        self.version_info = version_info

    def mousePressEvent(self, a0):
        self.selected.emit()
        return super().mousePressEvent(a0)


class OriginalSelector(GameSelector, Ui_OriginalSelector):
    _versionInfosGot = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.display_name = self.tr("原版")

        for i, v in enumerate(("", "release", "snapshot", "old")):
            self.type_filter.setItemData(i, v)
        for i, v in enumerate(
            (
                ":/image/grass@2x.png",
                ":/image/command@2x.png",
                ":/image/craft_table@2x.png",
            )
        ):
            self.type_filter.setItemIcon(i + 1, QIcon(v))

        self.select_version_info: OriginalVersionInfo = {"id": ""}

        self.version_filter.searchSignal.connect(lambda: self.filteViewers())
        self.version_filter.clearSignal.connect(lambda: self.filteViewers())
        self.type_filter.currentIndexChanged.connect(lambda: self.filteViewers())

        self._versionInfosGot.connect(self.setupViewers)
        threading.Thread(
            target=lambda: self._versionInfosGot.emit(get_original_versions()),
            daemon=True,
        ).start()

    def setupViewers(self, version_infos):
        for version_info in version_infos:
            viewer = VersionInfoViewer(version_info)
            viewer.selected.connect(
                lambda viewer=viewer: (
                    setattr(self, "select_version_info", viewer.version_info),
                    self.versionSelected.emit(viewer.version_info["id"]),
                )
            )
            self.viewer_layout.addWidget(viewer)
        self.viewer_layout.addSpacerItem(
            QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding)
        )
        self.filteViewers()

    def filteViewers(self):
        id = self.version_filter.text()
        type = self.type_filter.currentData()
        for i in range(self.viewer_layout.count()):
            viewer = self.viewer_layout.itemAt(i)
            if viewer.widget() == None:
                continue
            viewer = viewer.widget()
            if id in viewer.version_info["id"] and type in viewer.version_info["type"]:
                viewer.show()
            else:
                viewer.hide()

    def download(self, name):
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return None
        url = self.select_version_info["url"]
        return lambda: download_original(name, path, url)

    def install(self, name, game_dir):
        url = self.select_version_info["url"]
        return lambda: download_install_original(game_dir, name, url)
