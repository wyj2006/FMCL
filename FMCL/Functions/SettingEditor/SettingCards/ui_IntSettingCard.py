# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\FMCL\Functions\SettingEditor\SettingCards\IntSettingCard.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IntSettingCard(object):
    def setupUi(self, IntSettingCard):
        IntSettingCard.setObjectName("IntSettingCard")
        IntSettingCard.resize(400, 300)
        IntSettingCard.setWindowTitle("")
        self.gridLayout = QtWidgets.QGridLayout(IntSettingCard)
        self.gridLayout.setObjectName("gridLayout")
        self.sb_val = SpinBox(IntSettingCard)
        self.sb_val.setObjectName("sb_val")
        self.gridLayout.addWidget(self.sb_val, 0, 0, 1, 1)

        self.retranslateUi(IntSettingCard)
        QtCore.QMetaObject.connectSlotsByName(IntSettingCard)

    def retranslateUi(self, IntSettingCard):
        pass
from qfluentwidgets import SpinBox
