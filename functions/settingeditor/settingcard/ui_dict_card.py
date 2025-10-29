# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dict_card.ui'
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


class Ui_DictCard(object):
    def setupUi(self, DictCard):
        if not DictCard.objectName():
            DictCard.setObjectName("DictCard")
        DictCard.resize(400, 300)
        self.gridLayout = QGridLayout(DictCard)
        self.gridLayout.setObjectName("gridLayout")
        self.add_button = TransparentToolButton(DictCard)
        self.add_button.setObjectName("add_button")

        self.gridLayout.addWidget(self.add_button, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.pair_layout = QFormLayout()
        self.pair_layout.setObjectName("pair_layout")

        self.gridLayout.addLayout(self.pair_layout, 0, 0, 1, 2)

        self.retranslateUi(DictCard)

        QMetaObject.connectSlotsByName(DictCard)

    # setupUi

    def retranslateUi(self, DictCard):
        DictCard.setWindowTitle(
            QCoreApplication.translate("DictCard", "DictCard", None)
        )
        # if QT_CONFIG(tooltip)
        self.add_button.setToolTip(
            QCoreApplication.translate("DictCard", "\u6dfb\u52a0", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.add_button.setText("")

    # retranslateUi
