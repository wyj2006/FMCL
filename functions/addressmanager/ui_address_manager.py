# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'address_manager.ui'
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
    QTableWidgetItem,
    QWidget,
)
from qfluentwidgets import TableWidget


class Ui_AddressManager(object):
    def setupUi(self, AddressManager):
        if not AddressManager.objectName():
            AddressManager.setObjectName("AddressManager")
        AddressManager.resize(1000, 618)
        self.gridLayout = QGridLayout(AddressManager)
        self.gridLayout.setObjectName("gridLayout")
        self.viewer = TableWidget(AddressManager)
        if self.viewer.columnCount() < 3:
            self.viewer.setColumnCount(3)
        self.viewer.setObjectName("viewer")
        self.viewer.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.viewer.setRowCount(0)
        self.viewer.setColumnCount(3)
        self.viewer.horizontalHeader().setProperty("showSortIndicator", False)
        self.viewer.horizontalHeader().setStretchLastSection(True)

        self.gridLayout.addWidget(self.viewer, 0, 0, 1, 1)

        self.retranslateUi(AddressManager)

        QMetaObject.connectSlotsByName(AddressManager)

    # setupUi

    def retranslateUi(self, AddressManager):
        AddressManager.setWindowTitle(
            QCoreApplication.translate(
                "AddressManager", "\u7f51\u5740\u7ba1\u7406\u5668", None
            )
        )

    # retranslateUi
