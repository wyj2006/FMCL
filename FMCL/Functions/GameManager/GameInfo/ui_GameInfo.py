# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\FMCL\Functions\GameManager\GameInfo\GameInfo.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GameInfo(object):
    def setupUi(self, GameInfo):
        GameInfo.setObjectName("GameInfo")
        GameInfo.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(GameInfo)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(GameInfo)
        self.scrollArea.setStyleSheet("QScrollArea{\n"
"    border:none;\n"
"}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1000, 618))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.widget_2 = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget_2.setObjectName("widget_2")
        self.gl_versions = QtWidgets.QGridLayout(self.widget_2)
        self.gl_versions.setObjectName("gl_versions")
        self.gridLayout_2.addWidget(self.widget_2, 1, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
        self.widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget.setObjectName("widget")
        self.gl_info = QtWidgets.QGridLayout(self.widget)
        self.gl_info.setObjectName("gl_info")
        self.pb_opendir = PushButton(self.widget)
        self.pb_opendir.setObjectName("pb_opendir")
        self.gl_info.addWidget(self.pb_opendir, 1, 1, 1, 1)
        self.pb_resourcepack = PushButton(self.widget)
        self.pb_resourcepack.setObjectName("pb_resourcepack")
        self.gl_info.addWidget(self.pb_resourcepack, 1, 2, 1, 1)
        self.l_logo = QtWidgets.QLabel(self.widget)
        self.l_logo.setText("")
        self.l_logo.setObjectName("l_logo")
        self.gl_info.addWidget(self.l_logo, 0, 0, 2, 1)
        self.le_name = LineEdit(self.widget)
        self.le_name.setObjectName("le_name")
        self.gl_info.addWidget(self.le_name, 0, 1, 1, 5)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gl_info.addItem(spacerItem1, 1, 5, 1, 1)
        self.pb_delete = PushButton(self.widget)
        self.pb_delete.setObjectName("pb_delete")
        self.gl_info.addWidget(self.pb_delete, 1, 4, 1, 1)
        self.pb_shaderpack = PushButton(self.widget)
        self.pb_shaderpack.setObjectName("pb_shaderpack")
        self.gl_info.addWidget(self.pb_shaderpack, 1, 3, 1, 1)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(GameInfo)
        QtCore.QMetaObject.connectSlotsByName(GameInfo)

    def retranslateUi(self, GameInfo):
        _translate = QtCore.QCoreApplication.translate
        GameInfo.setWindowTitle(_translate("GameInfo", "游戏信息"))
        self.pb_opendir.setText(_translate("GameInfo", "打开文件夹"))
        self.pb_resourcepack.setText(_translate("GameInfo", "资源包文件夹"))
        self.pb_delete.setText(_translate("GameInfo", "删除"))
        self.pb_shaderpack.setText(_translate("GameInfo", "光影包文件夹"))
from qfluentwidgets import LineEdit, PushButton
