# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'list_card.ui'
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
    QFormLayout,
    QGridLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)
from qfluentwidgets import TransparentToolButton


class Ui_ListCard(object):
    def setupUi(self, ListCard):
        if not ListCard.objectName():
            ListCard.setObjectName("ListCard")
        ListCard.resize(400, 300)
        self.gridLayout = QGridLayout(ListCard)
        self.gridLayout.setObjectName("gridLayout")
        self.add_button = TransparentToolButton(ListCard)
        self.add_button.setObjectName("add_button")

        self.gridLayout.addWidget(self.add_button, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.element_layout = QFormLayout()
        self.element_layout.setObjectName("element_layout")

        self.gridLayout.addLayout(self.element_layout, 0, 0, 1, 2)

        self.retranslateUi(ListCard)

        QMetaObject.connectSlotsByName(ListCard)

    # setupUi

    def retranslateUi(self, ListCard):
        ListCard.setWindowTitle(
            QCoreApplication.translate("ListCard", "ListCard", None)
        )
        # if QT_CONFIG(tooltip)
        self.add_button.setToolTip(
            QCoreApplication.translate("ListCard", "\u6dfb\u52a0", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.add_button.setText("")

    # retranslateUi
