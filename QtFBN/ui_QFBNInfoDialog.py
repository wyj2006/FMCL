# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\QtFBN\QFBNInfoDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QFBNInfoDialog(object):
    def setupUi(self, QFBNInfoDialog):
        QFBNInfoDialog.setObjectName("QFBNInfoDialog")
        QFBNInfoDialog.resize(500, 309)
        QFBNInfoDialog.setWindowTitle("")
        QFBNInfoDialog.setAutoFillBackground(False)
        QFBNInfoDialog.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(QFBNInfoDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pb_ok = QtWidgets.QPushButton(QFBNInfoDialog)
        self.pb_ok.setObjectName("pb_ok")
        self.gridLayout.addWidget(self.pb_ok, 1, 0, 1, 1)
        self.pb_cancel = QtWidgets.QPushButton(QFBNInfoDialog)
        self.pb_cancel.setObjectName("pb_cancel")
        self.gridLayout.addWidget(self.pb_cancel, 1, 1, 1, 1)
        self.l_msg = QtWidgets.QLabel(QFBNInfoDialog)
        self.l_msg.setText("")
        self.l_msg.setObjectName("l_msg")
        self.gridLayout.addWidget(self.l_msg, 0, 0, 1, 2)

        self.retranslateUi(QFBNInfoDialog)
        QtCore.QMetaObject.connectSlotsByName(QFBNInfoDialog)

    def retranslateUi(self, QFBNInfoDialog):
        _translate = QtCore.QCoreApplication.translate
        self.pb_ok.setText(_translate("QFBNInfoDialog", "确定"))
        self.pb_cancel.setText(_translate("QFBNInfoDialog", "取消"))
