# -*- coding:utf-8 -*-
from sys import argv,exit
from PyQt5.QtWidgets import QApplication,QDialog
from PyQt5.QtCore import Qt
from ui.dialog import Ui_Dialog


class DialogWindow(QDialog,Ui_Dialog):
    def __init__(self,text=""):
        super(DialogWindow,self).__init__()
        self.setupUi(self)
        self.label.setText(text)
        self.setWindowFlags(Qt.WindowTitleHint)




if __name__ == "__main__":
    app = QApplication(argv)
    ui = DialogWindow("你好啊")
    # ui=CandyWindow.createWindow(ui, title='提示', theme='blueGreen')
    ui.show()
    exit(app.exec_())
