import logging
import traceback

from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import FluentIcon, RoundMenu

from fmcllib import show_qerrormessage
from fmcllib.filesystem import listdir
from fmcllib.function import Function


class FunctionViewer(QWidget):
    def __init__(self, function_path):
        super().__init__()
        self.function = Function(function_path)
        self.setLayout(QVBoxLayout())

        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.function.icon.pixmap(32, 32))
        self.icon_label.setFixedSize(QSize(32, 32))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel()
        self.name_label.setText(self.function.display_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.layout().addWidget(self.name_label)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.setToolTip(self.function.display_name)

    def showContextMenu(self):
        menu = RoundMenu()

        run_action = QAction(FluentIcon.PLAY.icon(), self.tr("运行"))
        run_action.triggered.connect(self.run)
        menu.addAction(run_action)

        menu.exec(QCursor.pos())

    def run(self):
        try:
            self.function.run().unwrap()
        except:
            show_qerrormessage(
                self.tr("运行{path}时出错").format(path=self.function.path),
                traceback.format_exc(),
                self,
            )

    def mouseDoubleClickEvent(self, a0):
        self.run()
        return super().mouseDoubleClickEvent(a0)


class Desktop(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            "QTableWidget::item:disabled {\n"
            "    background-color: #ffffff;\n"
            "}\n"
            "QTableWidget::item:disabled:hover {\n"
            "    background-color: #ffffff;\n"
            "}"
        )
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setIconSize(QSize(32, 32))
        self.setShowGrid(False)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

        self.cell_size = QSize(80, 80)

        self.refresh()

    def refresh(self):
        self.clear()

        self.setRowCount(self.height() // self.cell_size.height())
        self.setColumnCount(self.width() // self.cell_size.width())
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col, item)
                self.setColumnWidth(col, self.cell_size.width())
                self.setRowHeight(row, self.cell_size.height())
        row = 0
        col = 0
        for name in listdir("/desktop").unwrap_or([]):
            try:
                item = self.item(row, col)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                item_widget = FunctionViewer(f"/desktop/{name}")
                self.setCellWidget(row, col, item_widget)
                row += 1
                if row == self.rowCount():
                    row = 0
                    col += 1
            except:
                logging.error(f"无法显示功能'{name}'在桌面上:{traceback.format_exc()}")

    def event(self, a0: QEvent):
        match a0.type():
            case QEvent.Type.Resize:
                self.refresh()
        return super().event(a0)
