import threading

from fabric_selector import FabricSelector
from game_selector import GameSelector
from original_selector import OriginalSelector
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon
from ui_game_downloader import Ui_GameDownloader

from fmcllib.function import Function
from fmcllib.setting import Setting


class GameDownloader(QWidget, Ui_GameDownloader):
    versionChanged = pyqtSignal(str, str)  # version为空代表没有选择

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.DOWNLOAD.icon())

        self.game_dirs.addItems(Setting().get("game.dirs").unwrap_or([]))

        self.selectors: dict[str, GameSelector] = {
            "original": OriginalSelector,
            "fabric": FabricSelector,
        }
        for key in self.selectors:
            getattr(self, f"select_{key}").toggled.connect(
                lambda checked, key=key: self.on_select_toggled(checked, key)
            )

    def on_select_toggled(self, checked: bool, key: str):
        if checked:
            if isinstance(self.selectors[key], type):
                self.selectors[key] = self.selectors[key]()
                selector = self.selectors[key]
                selector.versionSelected.connect(
                    lambda version: getattr(self, f"select_{key}").setText(
                        f"{selector.display_name}:{version}"
                    )
                )
                selector.versionSelected.connect(self.autoSetInstanceName)
                selector.versionSelected.connect(
                    lambda version: self.versionChanged.emit(key, version)
                )

                if key == "fabric":
                    selector: FabricSelector
                    self.versionChanged.connect(
                        lambda key, version: (
                            selector.on_originalChanged(version)
                            if key == "original"
                            else None
                        )
                    )
                    self.versionChanged.connect(
                        lambda key, _: (
                            self.pivot.setItemText("fabric", selector.display_name)
                            if key == "original" and key in self.pivot.items
                            else None
                        )
                    )
                    if isinstance(self.selectors["original"], OriginalSelector):
                        selector.on_originalChanged(
                            self.selectors["original"].select_version_info["id"]
                        )
                    else:
                        selector.on_originalChanged("")
            selector = self.selectors[key]
            self.pivot.addItem(
                key,
                selector.display_name,
                lambda: self.selector_stack.setCurrentWidget(selector),
            )
            self.selector_stack.addWidget(selector)
            self.selector_stack.setCurrentWidget(selector)
        else:
            selector = self.selectors[key]
            getattr(self, f"select_{key}").setText(selector.display_name)
            self.selector_stack.removeWidget(selector)
            self.pivot.removeWidget(key)
            self.autoSetInstanceName()
            self.versionChanged.emit(key, "")

    @pyqtSlot(int)
    def on_selector_stack_currentChanged(self, _):
        if self.selector_stack.currentWidget() == None:
            return
        for key, selector in self.selectors.items():
            if selector == self.selector_stack.currentWidget():
                self.pivot.setCurrentItem(key)
                break

    @property
    def default_instance_name(self):
        a = []
        for key, selector in self.selectors.items():
            if (
                not isinstance(selector, type)
                and self.selector_stack.indexOf(selector) == -1
                or not hasattr(selector, "selected_version")
            ):
                continue
            a.append(
                (selector.display_name if key != "original" else "")
                + selector.selected_version
            )
        return "-".join(a)

    def autoSetInstanceName(self):
        if self.auto_set_instance_name.isChecked():
            self.instance_name.setText(self.default_instance_name)

    @pyqtSlot(bool)
    def on_download_button_clicked(self, _):
        t = []
        name = self.instance_name.text()
        for _, selector in self.selectors.items():
            if (
                not isinstance(selector, type)
                and self.selector_stack.indexOf(selector) == -1
                or not hasattr(selector, "selected_version")
            ):
                continue
            if (f := selector.download(name)) == None:
                return
            t.append(f)
        # 解决依赖问题
        threading.Thread(target=lambda: list([i() for i in t]), daemon=True).start()

    @pyqtSlot(bool)
    def on_download_install_button_clicked(self, _):
        t = []
        name = self.instance_name.text()
        game_dir = self.game_dirs.currentText()
        for _, selector in self.selectors.items():
            if (
                not isinstance(selector, type)
                and self.selector_stack.indexOf(selector) == -1
                or not hasattr(selector, "selected_version")
            ):
                continue
            if (f := selector.install(name, game_dir)) == None:
                return
            t.append(f)
        # 解决依赖问题
        threading.Thread(target=lambda: list([i() for i in t]), daemon=True).start()

    @pyqtSlot(bool)
    def on_add_dir_button_clicked(self, _):
        Function.quick_run("/functions/settingeditor", "--key", "game.dirs")
