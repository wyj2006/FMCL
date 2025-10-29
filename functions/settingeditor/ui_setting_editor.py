# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting_editor.ui'
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
    QSpacerItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import ScrollArea, SearchLineEdit, TreeView


class Ui_SettingEditor(object):
    def setupUi(self, SettingEditor):
        if not SettingEditor.objectName():
            SettingEditor.setObjectName("SettingEditor")
        SettingEditor.resize(1000, 618)
        self.gridLayout = QGridLayout(SettingEditor)
        self.gridLayout.setObjectName("gridLayout")
        self.search_input = SearchLineEdit(SettingEditor)
        self.search_input.setObjectName("search_input")

        self.gridLayout.addWidget(self.search_input, 0, 0, 1, 1)

        self.splitter = QSplitter(SettingEditor)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.navigation = TreeView(self.splitter)
        self.navigation.setObjectName("navigation")
        self.navigation.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.splitter.addWidget(self.navigation)
        self.navigation.header().setVisible(False)
        self.edit_area = ScrollArea(self.splitter)
        self.edit_area.setObjectName("edit_area")
        self.edit_area.setWidgetResizable(True)
        self.edit_area_content = QWidget()
        self.edit_area_content.setObjectName("edit_area_content")
        self.edit_area_content.setGeometry(QRect(0, 0, 69, 572))
        self.edit_layout = QVBoxLayout(self.edit_area_content)
        self.edit_layout.setObjectName("edit_layout")
        self.compress_spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.edit_layout.addItem(self.compress_spacer)

        self.edit_area.setWidget(self.edit_area_content)
        self.splitter.addWidget(self.edit_area)

        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)

        self.retranslateUi(SettingEditor)

        QMetaObject.connectSlotsByName(SettingEditor)

    # setupUi

    def retranslateUi(self, SettingEditor):
        SettingEditor.setWindowTitle(
            QCoreApplication.translate("SettingEditor", "\u8bbe\u7f6e", None)
        )

    # retranslateUi
