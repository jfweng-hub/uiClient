# -*- coding:utf-8 -*-
from sys import argv, exit
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QHeaderView, QPushButton, QTableWidgetItem, \
    QDialog, QMenu, QAction
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.Qt import QCursor
from threading import Thread
from ui.ui import Ui_MainWindow
from QCandyUi import CandyWindow
from window import FormWindow
from alert import DialogWindow
import requests
from json import load
from os import system
from decimal import Decimal
from wtfile import writeFile
with open('./conf/conf.json', 'r', encoding="utf-8") as f:
    config = load(f)
ip = config["请求地址"]


class SignalStore(QObject):
    _signal = pyqtSignal(str)


class Mainwindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        '''
        槽函数
        '''

        self.tableWidget.resizeRowsToContents()  # 列自适应尺寸
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格不可编辑
        self.tableWidget.customContextMenuRequested['QPoint'].connect(self.menu)  # 菜单
        self.pushButton_3.clicked.connect(lambda: self.queryButton(0))  # 首次查询
        self.pushButton_7.clicked.connect(lambda: self.queryButton(-1))  # 上页
        self.pushButton_6.clicked.connect(lambda: self.queryButton(1))  # 下页
        self.pushButton_5.clicked.connect(self.export)  # 导出

    def export(self):
        self.pushButton_5.setEnabled(False)
        so = SignalStore()
        methodName = "queryExport"
        dataParam = {}

        def calback(res):
            if res == "error":
                self.tips("系统异常")
            else:
                self.pushButton_5.setEnabled(True)
                res = eval(res)
                text=writeFile(res)
                print(text)
                if text:
                    self.tips(text)
                    return

                if self.tips("导出成功，是否打开"):
                    system(r'start ./conf/台账.xlsx')

        def func():
            res = self.send(methodName, dataParam)
            so._signal.emit(str(res))

        t = Thread(target=func)
        so._signal.connect(calback)
        t.start()

    def menu(self):
        cmenu = QMenu(self.tableWidget)
        addAction = QAction("添加", self)
        addAction.setData(1)
        cmenu.addAction(addAction)
        addAction.triggered.connect(lambda: self.addRow())
        self.addAction(addAction)
        cmenu.exec_(QCursor.pos())

    def addRow(self, contractNum=""):
        self.details(contractNum)

    def queryButton(self, mode):
        '''

        :param mode: -1 上页 0 首页 1 下页
        :return:
        '''
        pageNo = int(self.label_3.text()[1:].split("页")[0])
        total = int(self.label_3.text().split("共")[1].split("页")[0])

        if mode == -1 and pageNo < 2:
            return

        elif mode == 1 and pageNo == 0:
            return

        elif mode == 1 and pageNo == total:
            return

        so = SignalStore()
        methodName = "queryProject"

        if mode == 0:
            pageNo1 = 1
        elif mode == -1:
            pageNo1 = pageNo - 1
        else:
            pageNo1 = pageNo + 1

        dataParam = {
            "contractNum": self.lineEdit.text(),
            "pjStatus": self.comboBox.currentText(),
            "pageNo": pageNo1
        }

        def calback(res):
            if res == "error":
                self.tips("系统异常")
            else:
                res = eval(res)
                count = res[0]
                projectList = res[1]
                if count==0:
                    self.label_3.setText("第0页，共0页")
                    return
                self.label_3.setText("第{}页，共{}页".format(pageNo1, count))
                self.tableWidget.setRowCount(len(projectList))
                row = 0
                for p in projectList:
                    contractNum = QPushButton(str(p["contractNum"]))
                    contractNum.clicked.connect(lambda: self.details())
                    self.tableWidget.setCellWidget(row, 0, contractNum)

                    self.tableWidget.setItem(row, 1, QTableWidgetItem(p["supplier"]))
                    self.tableWidget.item(row, 1).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 2, QTableWidgetItem(p["custormer"]))
                    self.tableWidget.item(row, 2).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 3, QTableWidgetItem(p["product"]))
                    self.tableWidget.item(row, 3).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 4, QTableWidgetItem(str(p["purchaseAmt"])))
                    self.tableWidget.item(row, 4).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 5, QTableWidgetItem(str(p["saleAmt"])))
                    self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 6, QTableWidgetItem(str(p["receivedAmt"])))
                    self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 7, QTableWidgetItem(str(p["paidAmt"])))
                    self.tableWidget.item(row, 7).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 8, QTableWidgetItem(str(p["nt"])))
                    self.tableWidget.item(row, 8).setTextAlignment(Qt.AlignCenter)

                    # self.tableWidget.setItem(row, 9, QTableWidgetItem(p["inputFapiaoDate"]))
                    # self.tableWidget.item(row, 9).setTextAlignment(Qt.AlignCenter)
                    #
                    # self.tableWidget.setItem(row, 10, QTableWidgetItem(p["makeFapiaoDate"]))
                    # self.tableWidget.item(row, 10).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 9, QTableWidgetItem(p["pjStatus"]))
                    self.tableWidget.item(row, 9).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 10, QTableWidgetItem(p["reverse"]))
                    self.tableWidget.item(row, 10).setTextAlignment(Qt.AlignCenter)

                    row = row + 1

        def func():
            res = self.send(methodName, dataParam)
            so._signal.emit(str(res))

        t = Thread(target=func)
        so._signal.connect(calback)
        t.start()

    def details(self, contractNum=None):
        if contractNum == None:
            contractNum = self.tableWidget.cellWidget(self.tableWidget.currentRow(), 0).text()
        self.ui1 = FormWindow(contractNum=contractNum)
        self.ui1.closeSo._signal.connect(lambda: self.queryButton(0))
        self.ui1.show()

    def tips(self, text):
        self.ui_dialog1 = DialogWindow(text)
        return self.ui_dialog1.exec_() == QDialog.Accepted

    def send(self, methodName, dataParam):
        res = requests.post("{}/{}".format(ip, methodName), json=dataParam)
        if res.text != "error":
            res = eval(res.text)
        else:
            res = res.text
        return str(res)

    def closeEvent(self, event):
        event.accept()
        exit(0)  # 退出程序


if __name__ == "__main__":
    app = QApplication(argv)
    ui = Mainwindow()
    ui = CandyWindow.createWindow(ui, title='启维台账工具', ico_path='./conf/ico.png', theme='blueGreen')
    ui.show()
    exit(app.exec_())
