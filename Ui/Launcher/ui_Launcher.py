# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\Ui\Launcher\Launcher.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Launcher(object):
    def setupUi(self, Launcher):
        Launcher.setObjectName("Launcher")
        Launcher.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(Launcher)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(Launcher)
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pb_manageversion = QtWidgets.QPushButton(self.widget)
        self.pb_manageversion.setObjectName("pb_manageversion")
        self.gridLayout_2.addWidget(self.pb_manageversion, 2, 2, 1, 1)
        self.pb_chooseversion = QtWidgets.QPushButton(self.widget)
        self.pb_chooseversion.setObjectName("pb_chooseversion")
        self.gridLayout_2.addWidget(self.pb_chooseversion, 2, 1, 1, 1)
        self.pb_start = QtWidgets.QPushButton(self.widget)
        self.pb_start.setObjectName("pb_start")
        self.gridLayout_2.addWidget(self.pb_start, 2, 0, 1, 1)
        self.quickWidget = QtQuickWidgets.QQuickWidget(self.widget)
        self.quickWidget.setObjectName("quickWidget")
        self.gridLayout_2.addWidget(self.quickWidget, 0, 0, 1, 3)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        self.retranslateUi(Launcher)
        QtCore.QMetaObject.connectSlotsByName(Launcher)

    def retranslateUi(self, Launcher):
        _translate = QtCore.QCoreApplication.translate
        Launcher.setWindowTitle(_translate("Launcher", "启动"))
        self.pb_manageversion.setText(_translate("Launcher", "版本管理"))
        self.pb_chooseversion.setText(_translate("Launcher", "选择版本"))
        self.pb_start.setText(_translate("Launcher", "开始游戏"))
from PyQt5 import QtQuickWidgets
