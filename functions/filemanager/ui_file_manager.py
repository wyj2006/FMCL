# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'file_manager.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QGridLayout,
    QHeaderView,
    QSizePolicy,
    QWidget,
)
from qfluentwidgets import TreeView


class Ui_FileManager(object):
    def setupUi(self, FileManager):
        if not FileManager.objectName():
            FileManager.setObjectName("FileManager")
        FileManager.resize(1000, 618)
        self.gridLayout = QGridLayout(FileManager)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.entries_view = TreeView(FileManager)
        self.entries_view.setObjectName("entries_view")
        self.entries_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.gridLayout.addWidget(self.entries_view, 0, 0, 1, 1)

        self.retranslateUi(FileManager)

        QMetaObject.connectSlotsByName(FileManager)

    # setupUi

    def retranslateUi(self, FileManager):
        FileManager.setWindowTitle(
            QCoreApplication.translate(
                "FileManager", "\u6587\u4ef6\u7ba1\u7406\u5668", None
            )
        )

    # retranslateUi
