# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\FMCL\Functions\ModDownloader\ApiModItem.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ApiModItem(object):
    def setupUi(self, ApiModItem):
        ApiModItem.setObjectName("ApiModItem")
        ApiModItem.resize(400, 64)
        ApiModItem.setMinimumSize(QtCore.QSize(0, 64))
        ApiModItem.setWindowTitle("")
        self.gridLayout = QtWidgets.QGridLayout(ApiModItem)
        self.gridLayout.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 5, 1, 1)
        self.hl_categories = QtWidgets.QHBoxLayout()
        self.hl_categories.setObjectName("hl_categories")
        self.gridLayout.addLayout(self.hl_categories, 0, 2, 2, 2)
        self.l_description = QtWidgets.QLabel(ApiModItem)
        self.l_description.setText("")
        self.l_description.setObjectName("l_description")
        self.gridLayout.addWidget(self.l_description, 2, 1, 1, 5)
        self.l_title = QtWidgets.QLabel(ApiModItem)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.l_title.setFont(font)
        self.l_title.setText("")
        self.l_title.setObjectName("l_title")
        self.gridLayout.addWidget(self.l_title, 0, 1, 2, 1)
        self.hl_otherinfo = QtWidgets.QHBoxLayout()
        self.hl_otherinfo.setObjectName("hl_otherinfo")
        self.gridLayout.addLayout(self.hl_otherinfo, 0, 4, 2, 1)
        self.l_icon = PixmapLabel(ApiModItem)
        self.l_icon.setMinimumSize(QtCore.QSize(64, 0))
        self.l_icon.setMaximumSize(QtCore.QSize(64, 16777215))
        self.l_icon.setObjectName("l_icon")
        self.gridLayout.addWidget(self.l_icon, 0, 0, 3, 1)

        self.retranslateUi(ApiModItem)
        QtCore.QMetaObject.connectSlotsByName(ApiModItem)

    def retranslateUi(self, ApiModItem):
        pass
from qfluentwidgets import PixmapLabel
