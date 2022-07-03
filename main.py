# -*- coding:utf-8 -*-
from sys import argv,exit
from PyQt5.QtWidgets import QMainWindow,QApplication,QComboBox,QAbstractItemView,QHeaderView,QTableWidget,QPushButton,QTableWidgetItem,QDialog,QMenu,QAction
from PyQt5.QtCore import QObject,pyqtSignal,Qt
from PyQt5.Qt import QCursor
from threading import Thread
from ui import Ui_MainWindow
from QCandyUi import CandyWindow
from window import FormWindow
from alert import DialogWindow
import requests
from json import load
from decimal import Decimal
with open('./conf/conf.json','r',encoding="utf-8") as f:
    config = load(f)
ip = config["请求地址"]


class SignalStore(QObject):
    _signal=pyqtSignal(str)


class Mainwindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Mainwindow,self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        '''
        槽函数
        '''

        self.tableWidget.resizeRowsToContents()#列自适应尺寸
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.customContextMenuRequested['QPoint'].connect(self.menu)
        self.pushButton_3.clicked.connect(lambda :self.queryButton(0))
        self.pushButton_7.clicked.connect(lambda :self.queryButton(-1))
        self.pushButton_6.clicked.connect(lambda :self.queryButton(1))


    def menu(self):
        cmenu=QMenu(self.tableWidget)
        addAction = QAction("添加", self)
        addAction.setData(1)
        cmenu.addAction(addAction)
        addAction.triggered.connect(lambda :self.addRow())
        self.addAction(addAction)
        cmenu.exec_(QCursor.pos())

    def addRow(self,contractNum=""):
        self.details(contractNum)
    def queryButton(self,mode):
        '''

        :param mode: -1 上页 0 首页 1 下页
        :return:
        '''
        pageNo = int(self.label_3.text()[1:].split("页")[0])
        total=int(self.label_3.text().split("共")[1].split("页")[0])

        if mode==-1 and pageNo<2:
            return

        elif mode==1 and pageNo==0:
            return

        elif mode==1 and pageNo==total:
            return

        so = SignalStore()
        methodName="queryProject"
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
            if res=="error":
                self.tips("系统异常")
            else:
                res=eval(res)
                count = res[0]
                projectList = res[1]
                self.label_3.setText("第{}页,共{}页".format(pageNo1, count))
                self.tableWidget.setRowCount(len(projectList))
                row = 0
                for p in projectList:
                    contractNum = QPushButton(str(p["contractNum"]))
                    contractNum.clicked.connect(lambda :self.details())
                    self.tableWidget.setCellWidget(row,0,contractNum)

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

                    self.tableWidget.setItem(row, 5, QTableWidgetItem(str(p["receivedAmt"])))
                    self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 6, QTableWidgetItem(str(p["paidAmt"])))
                    self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 7, QTableWidgetItem(str(p["nt"])))
                    self.tableWidget.item(row, 7).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 8, QTableWidgetItem(p["inputFapiaoDate"]))
                    self.tableWidget.item(row, 8).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 9, QTableWidgetItem(p["makeFapiaoDate"]))
                    self.tableWidget.item(row, 9).setTextAlignment(Qt.AlignCenter)

                    self.tableWidget.setItem(row, 10, QTableWidgetItem(p["pjStatus"]))
                    self.tableWidget.item(row, 10).setTextAlignment(Qt.AlignCenter)


                    self.tableWidget.setItem(row, 11, QTableWidgetItem(p["reverse"]))
                    self.tableWidget.item(row, 11).setTextAlignment(Qt.AlignCenter)

                    row = row + 1
        def func():
            res = self.send(methodName, dataParam)
            so._signal.emit(str(res))


        t=Thread(target=func)
        so._signal.connect(calback)
        t.start()










    def details(self,contractNum=None):
        if contractNum==None:
            contractNum=self.tableWidget.cellWidget(self.tableWidget.currentRow(),0).text()
        ui1 = FormWindow(contractNum)
        ui1 = CandyWindow.createWindow(ui1, title='明细',ico_path='./conf/ico.png', theme='blueGreen')
        ui1.show()


    def updateRes(self):

        cur_row = self.tableWidget.rowCount()
        pjLst=[]
        for row in range(cur_row):
            try:
                contractNum=self.tableWidget.item(row,0).text()
            except:
                self.tips("请先输入合同编号")
                return
            try:
                supplier=self.tableWidget.item(row,1).text()# 供应商
            except:
                supplier=""
            try:
                custormer=self.tableWidget.item(row,2).text()# 客户
            except:
                custormer=""
            try:
                purchaseAmt=int(float(self.tableWidget.item(row,3).text())*100)#采购金额
            except:
                purchaseAmt=0
            try:
                saleAmt=int(float(self.tableWidget.item(row,4).text())*100)  # 销售金额
            except:
                saleAmt=0
            try:
                receivedAmt=int(float(self.tableWidget.cellWidget(row,5).text())*100)#累计收款金额
            except:
                receivedAmt=0
            try:
                paidAmt=int(float(self.tableWidget.cellWidget(row,6).text())*100) # 累计付款金额
            except:
                paidAmt=0

            # "nt":int(float(self.tableWidget.item(row,8).text()*100)) # 净利润
            try:
                inputFapiaoDate=self.tableWidget.item(row,8).text()  # 收票日期
            except:
                inputFapiaoDate=""
            try:
                makeFapiaoDate=self.tableWidget.item(row,9).text() # 开票日期
            except:
                makeFapiaoDate=""
            try:
                pjStatus=self.tableWidget.cellWidget(row,10).currentText()  # 项目状态
            except:
                pjStatus="进行中"
            try:
                reverse=self.tableWidget.item(row,11).text()  # 备注
            except:
                reverse=""
            pjLst.append(
                {
            "contractNum":contractNum,
            "supplier":supplier,# 供应商
            "custormer":custormer,# 客户
            "purchaseAmt":purchaseAmt,#采购金额
            "saleAmt":saleAmt,  # 销售金额
            "receivedAmt":receivedAmt,#累计收款金额
            "paidAmt":paidAmt, # 累计付款金额
            # "nt":int(float(self.tableWidget.item(row,8).text()*100)), # 净利润
            "inputFapiaoDate":inputFapiaoDate,  # 收票日期
            "makeFapiaoDate":makeFapiaoDate, # 开票日期
            "pjStatus":pjStatus,  # 项目状态
            "reverse":reverse  # 备注
                }
            )
        if not self.tips("请确认是否修改"):
            return

        so = SignalStore()
        methodName="updateProject"

        dataParam = {

            "pjLst": pjLst
        }
        def calback(res):
            if res=="error":
                self.tips("系统异常")

        def func():
            res=self.send(methodName, dataParam)
            so._signal.emit(res)


        t=Thread(target=func)
        so._signal.connect(calback)
        t.start()

    def tips(self,text):
        ui_dialog1 = DialogWindow(text)
        ui_dialog2 = CandyWindow.createWindow(ui_dialog1, title='提示', ico_path='.conf/ico.png', theme='blueGreen')
        ui_dialog2.show()
        ui_dialog1.buttonBox.accepted.connect(lambda: ok_func(ui_dialog2))
        ui_dialog1.buttonBox.rejected.connect(lambda: cancle_func(ui_dialog2))
        def ok_func(ui):
            ui.close()
        def cancle_func(ui):
            ui.close()
        return ui_dialog1.exec_()==QDialog.Accepted

    def send(self,methodName,dataParam):
        res = requests.post("{}/{}".format(ip, methodName), json=dataParam)
        print(res.text)
        if res.text!="error":
            res = eval(res.text)
        return str(res)

if __name__ == "__main__":
    app = QApplication(argv)
    ui = Mainwindow()
    ui=CandyWindow.createWindow(ui, title='启维台账工具',ico_path='./conf/ico.png',theme='blueGreen')
    ui.show()
    exit(app.exec_())
