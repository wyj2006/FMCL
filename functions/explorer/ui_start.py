# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'start.ui'
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
    QApplication,
    QGridLayout,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)
from qfluentwidgets import NavigationInterface


class Ui_Start(object):
    def setupUi(self, Start):
        if not Start.objectName():
            Start.setObjectName("Start")
        Start.resize(1000, 618)
        self.gridLayout = QGridLayout(Start)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.navigation_interface = NavigationInterface(Start)
        self.navigation_interface.setObjectName("navigation_interface")

        self.gridLayout.addWidget(self.navigation_interface, 0, 0, 1, 1)

        self.stackWidget = QStackedWidget(Start)
        self.stackWidget.setObjectName("stackWidget")

        self.gridLayout.addWidget(self.stackWidget, 0, 1, 1, 1)

        self.retranslateUi(Start)

        QMetaObject.connectSlotsByName(Start)

    # setupUi

    def retranslateUi(self, Start):
        Start.setWindowTitle(QCoreApplication.translate("Start", "\u5f00\u59cb", None))

    # retranslateUi
