# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\Ui\About\About.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(About)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(About)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 980, 598))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.l_fmclversion = QtWidgets.QLabel(self.groupBox)
        self.l_fmclversion.setObjectName("l_fmclversion")
        self.gridLayout_2.addWidget(self.l_fmclversion, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.pb_opensourceurl = QtWidgets.QPushButton(self.groupBox)
        self.pb_opensourceurl.setObjectName("pb_opensourceurl")
        self.gridLayout_2.addWidget(self.pb_opensourceurl, 0, 2, 1, 1)
        self.pb_checkupdate = QtWidgets.QPushButton(self.groupBox)
        self.pb_checkupdate.setObjectName("pb_checkupdate")
        self.gridLayout_2.addWidget(self.pb_checkupdate, 0, 3, 1, 1)
        self.pb_feedback = QtWidgets.QPushButton(self.groupBox)
        self.pb_feedback.setObjectName("pb_feedback")
        self.gridLayout_2.addWidget(self.pb_feedback, 0, 4, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pb_openhmclurl = QtWidgets.QPushButton(self.groupBox_2)
        self.pb_openhmclurl.setObjectName("pb_openhmclurl")
        self.gridLayout_3.addWidget(self.pb_openhmclurl, 1, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.pb_openbangurl = QtWidgets.QPushButton(self.groupBox_2)
        self.pb_openbangurl.setObjectName("pb_openbangurl")
        self.gridLayout_3.addWidget(self.pb_openbangurl, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)
        self.pb_openmczwurl = QtWidgets.QPushButton(self.groupBox_2)
        self.pb_openmczwurl.setObjectName("pb_openmczwurl")
        self.gridLayout_3.addWidget(self.pb_openmczwurl, 2, 2, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem2, 0, 1, 1, 1)
        self.l_pythonversion = QtWidgets.QLabel(self.groupBox_3)
        self.l_pythonversion.setObjectName("l_pythonversion")
        self.gridLayout_4.addWidget(self.l_pythonversion, 0, 0, 1, 1)
        self.pb_aboutqt = QtWidgets.QPushButton(self.groupBox_3)
        self.pb_aboutqt.setObjectName("pb_aboutqt")
        self.gridLayout_4.addWidget(self.pb_aboutqt, 1, 2, 1, 1)
        self.l_pyqtversion = QtWidgets.QLabel(self.groupBox_3)
        self.l_pyqtversion.setObjectName("l_pyqtversion")
        self.gridLayout_4.addWidget(self.l_pyqtversion, 1, 0, 1, 1)
        self.pb_openpythonurl = QtWidgets.QPushButton(self.groupBox_3)
        self.pb_openpythonurl.setObjectName("pb_openpythonurl")
        self.gridLayout_4.addWidget(self.pb_openpythonurl, 0, 2, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem3, 1, 1, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "更多"))
        self.groupBox.setTitle(_translate("About", "关于"))
        self.l_fmclversion.setText(_translate("About", "Functional Minecraft Launcher"))
        self.pb_opensourceurl.setText(_translate("About", "打开开源网址"))
        self.pb_checkupdate.setText(_translate("About", "检查更新"))
        self.pb_feedback.setText(_translate("About", "反馈问题"))
        self.groupBox_2.setTitle(_translate("About", "鸣谢"))
        self.pb_openhmclurl.setText(_translate("About", "打开网址"))
        self.label.setText(_translate("About", "bangbang93: 提供镜像源"))
        self.label_2.setText(_translate("About", "huanghongxun: 提供技术帮助(HMCL)"))
        self.pb_openbangurl.setText(_translate("About", "打开网址"))
        self.label_3.setText(_translate("About", "我的世界中文站: 提供新闻"))
        self.pb_openmczwurl.setText(_translate("About", "打开网址"))
        self.groupBox_3.setTitle(_translate("About", "依赖"))
        self.l_pythonversion.setText(_translate("About", "Python"))
        self.pb_aboutqt.setText(_translate("About", "关于Qt"))
        self.l_pyqtversion.setText(_translate("About", "PyQt"))
        self.pb_openpythonurl.setText(_translate("About", "打开网址"))