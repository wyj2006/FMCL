# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\Functions\ModManager\ModManager.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModManager(object):
    def setupUi(self, ModManager):
        ModManager.setObjectName("ModManager")
        ModManager.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(ModManager)
        self.gridLayout.setObjectName("gridLayout")
        self.pb_refresh = QtWidgets.QPushButton(ModManager)
        self.pb_refresh.setObjectName("pb_refresh")
        self.gridLayout.addWidget(self.pb_refresh, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.pb_openmodir = QtWidgets.QPushButton(ModManager)
        self.pb_openmodir.setObjectName("pb_openmodir")
        self.gridLayout.addWidget(self.pb_openmodir, 0, 1, 1, 1)
        self.lw_mods = QtWidgets.QListWidget(ModManager)
        self.lw_mods.setResizeMode(QtWidgets.QListView.Adjust)
        self.lw_mods.setObjectName("lw_mods")
        self.gridLayout.addWidget(self.lw_mods, 1, 0, 1, 3)

        self.retranslateUi(ModManager)
        QtCore.QMetaObject.connectSlotsByName(ModManager)

    def retranslateUi(self, ModManager):
        _translate = QtCore.QCoreApplication.translate
        ModManager.setWindowTitle(_translate("ModManager", "Mod管理"))
        self.pb_refresh.setText(_translate("ModManager", "刷新"))
        self.pb_openmodir.setText(_translate("ModManager", "打开Mod文件夹"))
