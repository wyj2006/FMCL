# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\王永健\PCG\FMCL\Functions\LanguageChooser\LanguageChooser.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LanguageChooser(object):
    def setupUi(self, LanguageChooser):
        LanguageChooser.setObjectName("LanguageChooser")
        LanguageChooser.resize(1000, 618)
        self.gridLayout = QtWidgets.QGridLayout(LanguageChooser)
        self.gridLayout.setObjectName("gridLayout")
        self.cb_lang = QtWidgets.QComboBox(LanguageChooser)
        self.cb_lang.setObjectName("cb_lang")
        self.gridLayout.addWidget(self.cb_lang, 0, 0, 1, 1)

        self.retranslateUi(LanguageChooser)
        QtCore.QMetaObject.connectSlotsByName(LanguageChooser)

    def retranslateUi(self, LanguageChooser):
        _translate = QtCore.QCoreApplication.translate
        LanguageChooser.setWindowTitle(_translate("LanguageChooser", "语言选择"))
