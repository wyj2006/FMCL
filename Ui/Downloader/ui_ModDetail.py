# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\Ui\Downloader\ModDetail.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModDetail(object):
    def setupUi(self, ModDetail):
        ModDetail.setObjectName("ModDetail")
        ModDetail.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(ModDetail)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(ModDetail)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pb_mcmod = QtWidgets.QPushButton(self.groupBox)
        self.pb_mcmod.setObjectName("pb_mcmod")
        self.gridLayout_2.addWidget(self.pb_mcmod, 2, 0, 1, 1)
        self.pb_curseforge = QtWidgets.QPushButton(self.groupBox)
        self.pb_curseforge.setObjectName("pb_curseforge")
        self.gridLayout_2.addWidget(self.pb_curseforge, 2, 1, 1, 1)
        self.l_name = QtWidgets.QLabel(self.groupBox)
        self.l_name.setObjectName("l_name")
        self.gridLayout_2.addWidget(self.l_name, 0, 0, 1, 2)
        self.l_describe = QtWidgets.QLabel(self.groupBox)
        self.l_describe.setObjectName("l_describe")
        self.gridLayout_2.addWidget(self.l_describe, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(ModDetail)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lw_modfiles = QtWidgets.QListWidget(self.groupBox_2)
        self.lw_modfiles.setObjectName("lw_modfiles")
        self.gridLayout_3.addWidget(self.lw_modfiles, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.retranslateUi(ModDetail)
        QtCore.QMetaObject.connectSlotsByName(ModDetail)

    def retranslateUi(self, ModDetail):
        _translate = QtCore.QCoreApplication.translate
        ModDetail.setWindowTitle(_translate("ModDetail", "Mod细节"))
        self.groupBox.setTitle(_translate("ModDetail", "信息"))
        self.pb_mcmod.setText(_translate("ModDetail", "Mod百科"))
        self.pb_curseforge.setText(_translate("ModDetail", "Curseforge"))
        self.l_name.setText(_translate("ModDetail", "名称"))
        self.l_describe.setText(_translate("ModDetail", "介绍"))
        self.groupBox_2.setTitle(_translate("ModDetail", "Mod文件"))
