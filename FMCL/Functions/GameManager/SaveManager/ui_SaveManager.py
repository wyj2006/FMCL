# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\FMCL\Functions\GameManager\SaveManager\SaveManager.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SaveManager(object):
    def setupUi(self, SaveManager):
        SaveManager.setObjectName("SaveManager")
        SaveManager.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(SaveManager)
        self.gridLayout.setObjectName("gridLayout")
        self.lw_saves = ListWidget(SaveManager)
        self.lw_saves.setObjectName("lw_saves")
        self.gridLayout.addWidget(self.lw_saves, 0, 0, 1, 1)

        self.retranslateUi(SaveManager)
        QtCore.QMetaObject.connectSlotsByName(SaveManager)

    def retranslateUi(self, SaveManager):
        _translate = QtCore.QCoreApplication.translate
        SaveManager.setWindowTitle(_translate("SaveManager", "存档管理"))
from qfluentwidgets import ListWidget