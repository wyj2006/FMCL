import threading
from typing import Union

from game_selector import GameSelector
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from qfluentwidgets import SettingCard
from ui_fabric_selector import Ui_FabricSelector

from fmcllib.game import (
    FabricInfo,
    FabricInstaller,
    download_fabric_installer,
    get_fabric_installers,
    get_fabric_versions,
    install_fabric,
)


class FabricInfoViewer(SettingCard):
    selected = pyqtSignal()

    def __init__(self, fabric_info: FabricInfo):
        icon = QIcon(":/image/fabric@2x.png")
        title = fabric_info["loader"]["version"]
        content = fabric_info["intermediary"]["version"]
        super().__init__(icon, title, content)
        self.setIconSize(32, 32)
        self.fabric_info = fabric_info

    def mousePressEvent(self, a0):
        self.selected.emit()
        return super().mousePressEvent(a0)


class InstallerViewer(SettingCard):
    selected = pyqtSignal()

    def __init__(self, installer: FabricInstaller):
        icon = QIcon(":/image/fabric@2x.png")
        title = installer["version"]
        content = ""
        super().__init__(icon, title, content)
        self.setIconSize(32, 32)
        self.installer = installer

    def mousePressEvent(self, a0):
        self.selected.emit()
        return super().mousePressEvent(a0)


class FabricSelector(GameSelector, Ui_FabricSelector):
    _versionInfosGot = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.original_version = ""
        self.selected_viewer: Union[InstallerViewer, FabricInfoViewer] = None
        # 原版对应的Fabric或FabricInstaller的列表
        self.version_infos: dict[str, list] = {}
        self.viewers: dict[
            str, Union[list[FabricInfoViewer], list[InstallerViewer]]
        ] = {}

        self.version_filter.searchSignal.connect(lambda: self.filteViewers())
        self.version_filter.clearSignal.connect(lambda: self.filteViewers())

        self._versionInfosGot.connect(self.setupViewers)

    def on_originalChanged(self, version: str):
        self.original_version = version
        if version == "":
            self.display_name = self.tr("Fabric安装器")
        else:
            self.display_name = self.tr("Fabric")
        threading.Thread(
            target=lambda: self._versionInfosGot.emit(
                self.version_infos[version]
                if version in self.version_infos
                else self.version_infos.setdefault(
                    version,
                    (
                        # 在调用setdefault时, 这部分一定会执行
                        get_fabric_versions(version)
                        if version
                        else get_fabric_installers()
                    ),
                )
            ),
            daemon=True,
        ).start()

    def setupViewers(self, infos: Union[list[FabricInfo], list[FabricInstaller]]):
        if self.original_version not in self.viewers:
            self.viewers[self.original_version] = []
            for info in infos:
                viewer = (
                    FabricInfoViewer(info)
                    if self.original_version
                    else InstallerViewer(info)
                )
                viewer.selected.connect(
                    lambda info=info, viewer=viewer: (
                        setattr(self, "selected_viewer", viewer),
                        self.versionSelected.emit(
                            info["loader"]["version"]
                            if self.original_version
                            else info["version"]
                        ),
                    )
                )
                self.viewers[self.original_version].append(viewer)
                self.viewer_layout.insertWidget(self.viewer_layout.count() - 1, viewer)
        for version, viewers in self.viewers.items():
            for viewer in viewers:
                if version == self.original_version:
                    viewer.show()
                else:
                    viewer.hide()
        self.filteViewers()

    def filteViewers(self):
        id = self.version_filter.text()
        for viewer in self.viewers[self.original_version]:
            if (
                isinstance(viewer, FabricInfoViewer)
                and id in viewer.fabric_info["loader"]["version"]
                or isinstance(viewer, InstallerViewer)
                and id in viewer.installer["version"]
            ):
                viewer.show()
            else:
                viewer.hide()

    def download(self, name):
        if not isinstance(self.selected_viewer, InstallerViewer):
            QMessageBox.critical(
                self,
                self.tr("无法下载"),
                self.tr("Fabric加载器不能单独下载, 只能单独下载Fabric安装器"),
            )
            return
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return None
        url = self.selected_viewer.installer["url"]
        return lambda: download_fabric_installer(name, path, url)

    def install(self, name):
        if not isinstance(self.selected_viewer, FabricInfoViewer):
            QMessageBox.critical(
                self,
                self.tr("无法安装"),
                self.tr("Fabric安装器不能单独安装, 只能单独安装Fabric加载器"),
            )
            return
        return lambda: install_fabric(
            name,
            self.original_version,
            self.selected_viewer.fabric_info["loader"]["version"],
        )
