from PyQt6.QtCore import QEvent, QMetaObject, QObject, QPoint, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QStackedWidget, QWidget
from qfluentwidgets import FluentIcon, RoundMenu, TabItem, TransparentToolButton
from start import Start
from taskbar import TaskBar

from fmcllib.mirror import MirrorFilter, MirrorRegisterInfo, MirrorWidget, getall_mirror
from fmcllib.setting import Setting
from fmcllib.window import Window


class Explorer(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Functional Minecraft Launcher")
        self.setObjectName("explorer")
        self.resize(1000, 618)

        self.start = Start()

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

        self.task_bar = TaskBar()
        self.task_bar.tabCloseRequested.connect(
            lambda index: self.killMirror(
                self.captured_widgets[self.task_bar.tabItem(index).routeKey()]
            )
        )

        self.detached_widgets: dict[str, dict] = {}
        self.captured_widgets: dict[str, MirrorWidget] = {}
        self.titlebar_widgets = []

        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture)
        self.capture_timer.start(1000)

        QApplication.instance().aboutToQuit.connect(self.on_aboutToQuit)

        self.currentChanged.connect(self.on_explorer_currentChanged)
        # QMetaObject.connectSlotsByName(self)

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
                window.titleBar.hBoxLayout.insertWidget(1, self.task_bar, 1)
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

    @pyqtSlot(int)
    def on_explorer_currentChanged(self, index):
        if self.currentWidget() != self.start:
            self.hideStart()
            self.start_button.setChecked(False)
        else:
            self.start_button.setChecked(True)
        for item in self.task_bar.items:
            item.setSelected(False)
        if (mirror_widget := self.currentWidget()) in self.captured_widgets.values():
            name = mirror_widget.name
            item = self.task_bar.tab(name)
            item.setSelected(True)
            self.updateTitleBarWidgets(mirror_widget.titlebar_widgets)
        else:
            self.updateTitleBarWidgets([])

    def updateTitleBarWidgets(self, titlebar_widgets: list):
        window = self.window()
        if not isinstance(window, Window):
            return
        window.removeTitleBarWidgets()
        self.titlebar_widgets = titlebar_widgets[:]
        for widget_info in self.titlebar_widgets:
            index: int = widget_info["index"]
            widget: QWidget = widget_info["widget"]
            stretch: int = widget_info.get("stretch", 0)
            alignment = widget_info.get("alignment", "AlignLeft")
            index += 2
            window.titleBar.hBoxLayout.insertWidget(
                index, widget, stretch, getattr(Qt.AlignmentFlag, alignment)
            )

    def capture(self):
        if Setting().get("explorer.embed_window").unwrap_or(True) == False:
            return
        registered: dict[str, MirrorRegisterInfo] = getall_mirror()
        for name, val in registered.items():
            if (
                val["kind"] != "window"
                or name in self.captured_widgets
                or name in self.detached_widgets
            ):
                continue
            mirror_widget = self.captured_widgets[name] = MirrorWidget(name)
            item = self.task_bar.addTab(
                mirror_widget.name,
                mirror_widget.windowTitle(),
                mirror_widget.windowIcon(),
                onClick=lambda: (
                    (
                        self.addWidget(mirror_widget),
                        self.setCurrentWidget(mirror_widget),
                    )
                    if self.currentWidget() != mirror_widget
                    else self.removeWidget(mirror_widget)
                ),
            )
            item.setToolTip(mirror_widget.windowTitle())
            item.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            item.customContextMenuRequested.connect(self.showItemRightMenu)

            mirror_widget.titlebarWidgetsChanged.connect(
                lambda: (
                    self.updateTitleBarWidgets(mirror_widget.titlebar_widgets)
                    if mirror_widget == self.currentWidget()
                    else None
                )
            )
            self.addWidget(mirror_widget)
            self.setCurrentWidget(mirror_widget)
            mirror_widget.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent):
        if isinstance(watched, MirrorWidget) and watched.name in self.captured_widgets:
            match event.type():
                case QEvent.Type.DeferredDelete:
                    watched.removeEventFilter(self)
                    self.captured_widgets.pop(watched.name)
                    self.task_bar.removeTabByKey(watched.name)
                    self.removeWidget(watched)
                case QEvent.Type.WindowTitleChange:
                    item = self.task_bar.tab(watched.name)
                    title = watched.windowTitle()
                    item.setText(title)
                    item.setToolTip(title)
                case QEvent.Type.WindowIconChange:
                    self.task_bar.tab(watched.name).setIcon(watched.windowIcon())
        return super().eventFilter(watched, event)

    def killMirror(self, mirror_widget: MirrorWidget):
        mirror_widget.kill()

    def showItemRightMenu(self):
        menu = RoundMenu(parent=self)

        item: TabItem = self.sender()
        mirror_widget: MirrorWidget = self.captured_widgets[item.routeKey()]

        detach_action = QAction(self.tr("分离"), icon=FluentIcon.LINK.icon())
        detach_action.triggered.connect(lambda: self.detach(mirror_widget))
        menu.addAction(detach_action)

        close_action = QAction(self.tr("关闭"), icon=FluentIcon.CLOSE.icon())
        close_action.triggered.connect(lambda: self.killMirror(mirror_widget))
        menu.addAction(close_action)

        menu.exec(
            item.mapToGlobal(  # 下方居中
                QPoint((item.width() - menu.size().width()) // 2, item.height())
            )
        )

    def embed(self, name: str):
        info = self.detached_widgets.pop(name)
        info["socket"].write(
            f"titlebar contextmenu action remove {info['action_mirror_filter'].name}\0".encode()
        )
        info["socket"].close()  # 关闭之前的连接
        info["action"].deleteLater()

    def detach(self, mirror_widget: MirrorWidget):
        mirror_widget_name = mirror_widget.name
        embed_action = QAction(self.tr("嵌入"), icon=FluentIcon.MINIMIZE.icon())
        embed_mirror_filter = MirrorFilter(embed_action, "action")
        embed_action.installEventFilter(embed_mirror_filter)
        embed_action.triggered.connect(lambda: self.embed(mirror_widget_name))
        mirror_widget.socket.write(
            f"titlebar contextmenu action add {embed_mirror_filter.name}\0".encode()
        )
        self.detached_widgets[mirror_widget.name] = {
            "action": embed_action,
            "action_mirror_filter": embed_mirror_filter,
            "socket": mirror_widget.socket,
        }
        mirror_widget.detach()

    def on_aboutToQuit(self):
        if Setting().get("explorer.detach_on_quit").unwrap_or(True):
            for i in tuple(self.captured_widgets.values()):
                i.detach()
        else:
            for mirror_widget in tuple(self.captured_widgets.values()):
                self.killMirror(mirror_widget)
        for i in tuple(self.detached_widgets.keys()):
            # 借用这个函数移除actions
            self.embed(i)
