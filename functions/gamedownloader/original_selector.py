import threading

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QSizePolicy, QSpacerItem, QWidget
from qfluentwidgets import SettingCard
from ui_original_selector import Ui_OriginalSelector

from fmcllib.game import OriginalVersionInfo, get_original_versions


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


class OriginalSelector(QWidget, Ui_OriginalSelector):
    versionsInfoGot = pyqtSignal()
    versionSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

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
        self.versions_info: list[OriginalVersionInfo] = []
        self.versionsInfoGot.connect(self.setupViewers)
        threading.Thread(
            target=lambda: (
                setattr(self, "versions_info", get_original_versions()),
                self.versionsInfoGot.emit(),
            ),
            daemon=True,
        ).start()

    def setupViewers(self):
        for version_info in self.versions_info:
            viewer = VersionInfoViewer(version_info)
            viewer.selected.connect(
                lambda viewer=viewer: (
                    setattr(self, "select_version_info", viewer.version_info),
                    self.versionSelected.emit(viewer.version_info["id"]),
                )
            )
            self.id_filter.searchSignal.connect(
                lambda _, viewer=viewer: self.filteViewer(viewer)
            )
            self.id_filter.clearSignal.connect(
                lambda viewer=viewer: self.filteViewer(viewer)
            )
            self.type_filter.currentIndexChanged.connect(
                lambda _, viewer=viewer: self.filteViewer(viewer)
            )
            self.viewer_layout.addWidget(viewer)
            self.filteViewer(viewer)
        self.viewer_layout.addSpacerItem(
            QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding)
        )

    def filteViewer(self, viewer: VersionInfoViewer):
        id = self.id_filter.text()
        type = self.type_filter.currentData()
        if id in viewer.version_info["id"] and type in viewer.version_info["type"]:
            viewer.show()
        else:
            viewer.hide()
