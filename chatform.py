# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chatform.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(671, 290)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(280, 210, 381, 31))
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushSend = QtWidgets.QPushButton(Form)
        self.pushSend.setGeometry(QtCore.QRect(550, 250, 111, 31))
        self.pushSend.setObjectName("pushSend")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(280, 10, 381, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 261, 231))
        self.listWidget.setObjectName("listWidget")
        self.pushAdd = QtWidgets.QPushButton(Form)
        self.pushAdd.setGeometry(QtCore.QRect(10, 250, 111, 31))
        self.pushAdd.setObjectName("pushAdd")
        self.pushDelete = QtWidgets.QPushButton(Form)
        self.pushDelete.setGeometry(QtCore.QRect(160, 250, 111, 31))
        self.pushDelete.setObjectName("pushDelete")

        self.retranslateUi(Form)
        Form.destroyed.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "QtMessenger"))
        self.pushSend.setText(_translate("Form", "Send"))
        self.pushAdd.setText(_translate("Form", "Add contact"))
        self.pushDelete.setText(_translate("Form", "Delete contact"))

