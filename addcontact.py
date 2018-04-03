# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addcontact.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(240, 97)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(20, 20, 201, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.pushAdd = QtWidgets.QPushButton(Form)
        self.pushAdd.setGeometry(QtCore.QRect(74, 50, 91, 32))
        self.pushAdd.setObjectName("pushAdd")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "add contact"))
        self.pushAdd.setText(_translate("Form", "Add"))

