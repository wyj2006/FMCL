# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'card_header.ui'
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
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QSizePolicy, QWidget
from qfluentwidgets import TransparentToolButton


class Ui_CardHeader(object):
    def setupUi(self, CardHeader):
        if not CardHeader.objectName():
            CardHeader.setObjectName("CardHeader")
        CardHeader.resize(400, 300)
        self.gridLayout = QGridLayout(CardHeader)
        self.gridLayout.setObjectName("gridLayout")
        self.moveup_button = TransparentToolButton(CardHeader)
        self.moveup_button.setObjectName("moveup_button")

        self.gridLayout.addWidget(self.moveup_button, 2, 0, 1, 1)

        self.label = QLabel(CardHeader)
        self.label.setObjectName("label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)

        self.movedown_button = TransparentToolButton(CardHeader)
        self.movedown_button.setObjectName("movedown_button")

        self.gridLayout.addWidget(self.movedown_button, 2, 1, 1, 1)

        self.delete_button = TransparentToolButton(CardHeader)
        self.delete_button.setObjectName("delete_button")

        self.gridLayout.addWidget(self.delete_button, 1, 0, 1, 3)

        self.retranslateUi(CardHeader)

        QMetaObject.connectSlotsByName(CardHeader)

    # setupUi

    def retranslateUi(self, CardHeader):
        CardHeader.setWindowTitle(
            QCoreApplication.translate("CardHeader", "CardHeader", None)
        )
        # if QT_CONFIG(tooltip)
        self.moveup_button.setToolTip(
            QCoreApplication.translate("CardHeader", "\u4e0a\u79fb", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.moveup_button.setText("")
        self.label.setText("")
        # if QT_CONFIG(tooltip)
        self.movedown_button.setToolTip(
            QCoreApplication.translate("CardHeader", "\u4e0b\u79fb", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.movedown_button.setText("")
        # if QT_CONFIG(tooltip)
        self.delete_button.setToolTip(
            QCoreApplication.translate("CardHeader", "\u5220\u9664", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.delete_button.setText("")

    # retranslateUi
