from typing import Union

import qtawesome as qta
from desktop import Desktop
from PyQt6.QtCore import QEvent, QObject, QPoint, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QSplitter,
    QStackedWidget,
    QWidget,
)
from qfluentwidgets import FluentIcon, RoundMenu, TabItem, TransparentToolButton
from start import Start
from taskbar import TaskBar

from fmcllib.mirror import WindowMirror, getall_mirror
from fmcllib.setting import Setting
from fmcllib.window import Window


class Explorer(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Functional Minecraft Launcher")
        self.setObjectName("explorer")
        self.resize(1000, 618)

        self.start = Start()
        self.desktop = Desktop()
        self.addWidget(self.desktop)

        self.start_button = TransparentToolButton(QApplication.instance().windowIcon())
        self.start_button.setCheckable(True)
        self.start_button.clicked.connect(self.toggleStart)
        # 让start_button checked的样式与hover的样式一样
        origin_stylesheet = self.start_button.styleSheet()
        insert_index = origin_stylesheet.find("TransparentToolButton:hover")
        self.start_button.setStyleSheet(
            origin_stylesheet[:insert_index]
            + "TransparentToolButton:checked,"
            + origin_stylesheet[insert_index:]
        )

        self.desktop_button = TransparentToolButton(qta.icon("ph.desktop"))
        self.desktop_button.setToolTip(self.tr("显示桌面"))
        self.desktop_button.clicked.connect(self.showDesktop)

        self.task_bar = TaskBar()
        self.task_bar.tabCloseRequested.connect(
            lambda index: self.captured_windows[
                self.task_bar.tabItem(index).routeKey()
            ].close()
        )

        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.task_bar)

        widget = QWidget()
        self.titlebar_layout = QHBoxLayout()
        self.titlebar_layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.titlebar_layout)
        self.splitter.addWidget(widget)

        self.captured_windows: dict[str, WindowMirror] = {}

        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture)
        self.capture_timer.start(1000)

        QApplication.instance().aboutToQuit.connect(self.on_aboutToQuit)

        self.currentChanged.connect(self.on_explorer_currentChanged)

    def event(self, e: QEvent):
        match e.type():
            case QEvent.Type.Show:
                window = self.window()
                if not isinstance(window, Window):
                    return super().event(e)
                window.titleBar.hBoxLayout.takeAt(0)
                # 调整start在window中的位置, 防止展开时位置出错
                self.start.navigation_interface.pos = lambda: QPoint(
                    0, window.titleBar.height()
                )
                self.start_button.setFixedHeight(window.titleBar.height())
                self.start_button.setFixedWidth(window.titleBar.closeBtn.width())
                window.titleBar.hBoxLayout.insertWidget(0, self.start_button)

                self.task_bar.setFixedHeight(window.titleBar.height())
                window.titleBar.hBoxLayout.insertWidget(1, self.splitter, 1)

                self.desktop_button.setFixedSize(window.titleBar.closeBtn.size())
                window.titleBar.hBoxLayout.insertWidget(
                    2, self.desktop_button, 0, Qt.AlignmentFlag.AlignRight
                )
        return super().event(e)

    def showStart(self):
        self.addWidget(self.start)
        self.setCurrentWidget(self.start)

    def hideStart(self):
        self.start.collapsePanel()
        self.removeWidget(self.start)

    def toggleStart(self):
        if self.currentWidget() == self.start:
            self.hideStart()
        else:
            self.showStart()

    def showDesktop(self):
        while self.count() > 1:
            super().removeWidget(self.widget(1))

    @pyqtSlot(int)
    def on_explorer_currentChanged(self, _):
        if self.currentWidget() != self.start:
            self.hideStart()
            self.start_button.setChecked(False)
        else:
            self.start_button.setChecked(True)
        for item in self.task_bar.items:
            item.setSelected(False)
        if (window_mirror := self.currentWidget()) in self.captured_windows.values():
            name = window_mirror.name
            item = self.task_bar.tab(name)
            item.setSelected(True)
        self.updateTitleBar(getattr(self.currentWidget(), "titlebar", None))

    def updateTitleBar(self, titlebar: QWidget):
        window = self.window()
        if not isinstance(window, Window):
            return
        while self.titlebar_layout.count() > 0:
            item = self.titlebar_layout.takeAt(0)
            if item.widget() != None:
                item.widget().setParent(None)
        if titlebar != None:
            self.titlebar_layout.addWidget(titlebar)
        if self.titlebar_layout.count() > 0:
            self.splitter.setSizes([800, 200])
            self.splitter.setStyleSheet(
                """QSplitter::handle{
                    background-color:rgb(235,235,235);
                }"""
            )
        else:
            self.splitter.setSizes([4, 0])
            self.splitter.setStyleSheet(
                """QSplitter::handle{
                    background-color:rgba(255,255,255,0);
                }"""
            )

    def addWidget(self, window_mirror: Union[WindowMirror, QWidget]):
        # 使用widgetAdded信号会因为比currentChanged信号后发出产生错误
        if not isinstance(window_mirror, WindowMirror):
            return super().addWidget(window_mirror)
        if window_mirror.name in self.task_bar.itemMap:
            return super().addWidget(window_mirror)
        item = self.task_bar.addTab(
            window_mirror.name,
            window_mirror.windowTitle(),
            window_mirror.windowIcon(),
            onClick=lambda wm=window_mirror: (
                (
                    self.addWidget(wm),
                    self.setCurrentWidget(wm),
                )
                if self.currentWidget() != wm
                else QStackedWidget.removeWidget(self, wm)
            ),
        )
        item.setToolTip(window_mirror.windowTitle())
        item.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        item.customContextMenuRequested.connect(self.showItemRightMenu)
        return super().addWidget(window_mirror)

    def removeWidget(self, window_mirror: Union[WindowMirror, QWidget]):
        # 使用widgetRemoved信号会因为index不匹配出问题
        super().removeWidget(window_mirror)
        if not isinstance(window_mirror, WindowMirror):
            return
        self.task_bar.removeTabByKey(window_mirror.name)

    def capture(self):
        if Setting().get("explorer.embed_window").unwrap_or(True) == False:
            return
        registered = getall_mirror()
        for name, val in registered.items():
            if val["kind"] != "window" or name in self.captured_windows:
                continue
            window_mirror = self.captured_windows[name] = WindowMirror(name)
            window_mirror.titlebarChanged.connect(
                lambda wm=window_mirror: (
                    self.updateTitleBar(wm.titlebar)
                    if wm == self.currentWidget()
                    else None
                )
            )
            self.addWidget(window_mirror)
            self.setCurrentWidget(window_mirror)
            window_mirror.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent):
        if isinstance(watched, WindowMirror):
            match event.type():
                case QEvent.Type.Close:
                    self.removeWidget(watched)
                case QEvent.Type.Show:
                    if self.indexOf(watched) == -1:
                        self.addWidget(watched)
                        self.setCurrentWidget(watched)
                case QEvent.Type.DeferredDelete:
                    watched.removeEventFilter(self)
                    self.captured_windows.pop(watched.name)
                    self.removeWidget(watched)
                case QEvent.Type.WindowTitleChange:
                    item = self.task_bar.tab(watched.name)
                    if item != None:
                        title = watched.windowTitle()
                        item.setText(title)
                        item.setToolTip(title)
                case QEvent.Type.WindowIconChange:
                    if (window_mirror := self.task_bar.tab(watched.name)) != None:
                        window_mirror.setIcon(watched.windowIcon())
        return super().eventFilter(watched, event)

    def showItemRightMenu(self):
        menu = RoundMenu(parent=self)

        item: TabItem = self.sender()
        window_mirror: WindowMirror = self.captured_windows[item.routeKey()]

        detach_action = QAction(self.tr("分离"), icon=FluentIcon.LINK.icon())
        detach_action.triggered.connect(
            lambda: (
                window_mirror.detach(),
                self.removeWidget(window_mirror),
            )
        )
        menu.addAction(detach_action)

        close_action = QAction(self.tr("关闭"), icon=FluentIcon.CLOSE.icon())
        close_action.triggered.connect(window_mirror.close)
        menu.addAction(close_action)

        menu.exec(
            item.mapToGlobal(  # 下方居中
                QPoint((item.width() - menu.size().width()) // 2, item.height())
            )
        )

    def on_aboutToQuit(self):
        if Setting().get("explorer.detach_on_quit").unwrap_or(True):
            for window_mirror in tuple(self.captured_windows.values()):
                window_mirror.detach()
        else:
            for window_mirror in tuple(self.captured_windows.values()):
                window_mirror.close()
