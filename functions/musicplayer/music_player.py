import logging

from mutagen import File, FileType, MutagenError
from PyQt6.QtCore import QEvent, Qt, QUrl, pyqtSlot
from PyQt6.QtWidgets import QTableWidgetItem, QWidget
from qfluentwidgets import (
    FluentIcon,
    InfoBar,
    InfoBarIcon,
    InfoBarPosition,
    TransparentToolButton,
)
from ui_music_player import Ui_MusicPlayer

from fmcllib.function import Function
from fmcllib.setting import Setting
from fmcllib.window import Window


class MusicPlayer(QWidget, Ui_MusicPlayer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(FluentIcon.MUSIC.icon())

        self.refresh_button = TransparentToolButton()
        self.refresh_button.setIcon(FluentIcon.SYNC.icon())
        self.refresh_button.setToolTip(self.tr("刷新"))
        self.refresh_button.clicked.connect(self.refresh)

        self.setting_button = TransparentToolButton()
        self.setting_button.setIcon(FluentIcon.SETTING.icon())
        self.setting_button.setToolTip(self.tr("设置"))
        self.setting_button.clicked.connect(
            lambda: Function.quick_run(
                "/functions/settingeditor", "--key", "music_player.musics"
            )
        )

        self.playing_row = 0
        self.player.positionChanged.connect(self.onPositionChanged)

        self.refresh()

    @property
    def player(self):
        return self.play_bar.player

    @pyqtSlot(int, int)
    def on_music_list_cellDoubleClicked(self, row: int, _):
        self.playing_row = row
        self.setSource(QUrl.fromLocalFile(self.music_list.item(row, 4).text()))
        self.player.play()

    def onPositionChanged(self, position: int):
        if position != self.player.duration():
            return
        self.playing_row = (self.playing_row + 1) % self.music_list.rowCount()
        item = self.music_list.item(self.playing_row, 4)
        if item == None:
            return
        self.setSource(QUrl.fromLocalFile(item.text()))
        self.player.play()

    def setSource(self, source: QUrl):
        self.player.setSource(source)
        self.playing_music.setText(self.tr("正在播放: ") + source.path())

    def refresh(self):
        music_paths: list[str] = Setting().get("music_player.musics").unwrap_or([])

        self.music_list.clearContents()
        self.music_list.setRowCount(len(music_paths))
        self.playing_row = self.playing_row % self.music_list.rowCount()

        for i, music_path in enumerate(music_paths):
            try:
                music_file: FileType = File(music_path)
                if music_file == None:
                    raise MutagenError()
            except MutagenError:
                logging.error(f"无法解析文件: {music_path}")
                w = InfoBar(
                    icon=InfoBarIcon.ERROR,
                    title=self.tr("无法解析文件"),
                    content=music_path,
                    orient=Qt.Orientation.Vertical,  # vertical layout
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000,
                    parent=self,
                )
                w.show()
                continue

            item = QTableWidgetItem()
            item.setText(music_path)
            self.music_list.setItem(i, 4, item)

            for key, val in music_file.tags.items():
                for col, tag in (
                    (0, "title"),
                    (1, "artist"),
                    (2, "album"),
                    (3, "year"),
                ):
                    item = QTableWidgetItem()
                    if key == tag:
                        item.setText(", ".join(val))
                        self.music_list.setItem(i, col, item)

        self.setSource(
            QUrl.fromLocalFile(self.music_list.item(self.playing_row, 4).text())
        )

    def event(self, a0: QEvent):
        match a0.type():
            case QEvent.Type.Show:
                window = self.window()
                if not isinstance(window, Window):
                    return super().event(a0)
                self.refresh_button.setFixedHeight(window.titleBar.height())
                self.refresh_button.setFixedWidth(window.titleBar.closeBtn.width())
                window.titleBar.hBoxLayout.insertWidget(
                    1, self.refresh_button, 0, Qt.AlignmentFlag.AlignRight
                )

                self.setting_button.setFixedSize(self.refresh_button.size())
                window.titleBar.hBoxLayout.insertWidget(
                    1, self.setting_button, 0, Qt.AlignmentFlag.AlignRight
                )
        return super().event(a0)
        return super().event(a0)
