# -*- coding:utf-8 -*-
from sys import argv, exit
from PyQt5.QtWidgets import QApplication, QHeaderView, QWidget, QDialog, QMenu, QAction, QComboBox, QDateEdit, \
    QAbstractSpinBox, QDateTimeEdit, QDoubleSpinBox, QLineEdit
from PyQt5.QtCore import Qt, QDate, QObject, pyqtSignal
from PyQt5.Qt import QCursor
from ui.info import Ui_Form
from threading import Thread
from alert import DialogWindow
from decimal import Decimal
import requests
import time

class SignalStore(QObject):
    _signal = pyqtSignal(str)


class FormWindow(QWidget, Ui_Form):
    closeSo = SignalStore()

    def __init__(self, contractNum=None):
        super(FormWindow, self).__init__()
        self.setupUi(self)
        self.contractNum = contractNum
        self.initUI()

    def initUI(self):
        '''
        槽函数
        '''

        self.tableWidget.resizeRowsToContents()  # 列自适应尺寸
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.queryDetail()
        self.tableWidget.customContextMenuRequested['QPoint'].connect(self.menu)
        self.spinBox.valueChanged.connect(self.calculate)
        self.doubleSpinBox_3.valueChanged.connect(self.calculate)
        self.spinBox_2.valueChanged.connect(self.calculate)
        self.doubleSpinBox_2.valueChanged.connect(self.calculate)
        self.pushButton.clicked.connect(self.updateContract)
        self.pushButton_2.clicked.connect(self.delContract)
        self.comboBox_2.currentTextChanged.connect(self.inputFapiao)
        self.comboBox_3.currentTextChanged.connect(self.makeFapiao)

    def makeFapiao(self):
        if self.comboBox_3.currentText()=="是":
            self.dateEdit_2.setEnabled(True)
        else:
            self.dateEdit_2.setEnabled(False)

    def inputFapiao(self):
        if self.comboBox_2.currentText()=="是":
            self.dateEdit.setEnabled(True)
            self.comboBox_4.setEnabled(True)
        else:
            self.dateEdit.setEnabled(False)
            self.comboBox_4.setEnabled(False)
            self.comboBox_4.setCurrentText("否")
    def delContract(self):

        contractNum = self.contract_line.text()
        if not contractNum:
            self.tips("请输入合同号")
            return
        so = SignalStore()
        methodName = "delProject"
        if not self.tips("请确认是否删除"):
            return
        dataParam = {
            "contractNum": contractNum
        }

        def calback(res):
            if res == "error":
                self.tips("系统异常")
            else:
                self.closeSo._signal.emit("0")
                self.window().close()

        def func():
            res = self.send(methodName, dataParam)
            so._signal.emit(res)

        t = Thread(target=func)
        so._signal.connect(calback)
        t.start()

    def updateContract(self):


        contractNum = self.contract_line.text()
        if not contractNum:
            self.tips("请输入合同号")
            return
        so = SignalStore()
        methodName = "updateProject"
        if not self.tips("请确认是否保存"):
            return
        # supplier = self.findChild(QLineEdit, 'lineEdit_10')

        dataParam = {
            "contractNum": contractNum,
            "supplier": self.lineEdit_10.text(),  # 供应商
            "custormer": self.lineEdit_3.text(),  # 客户
            "product": self.lineEdit.text(),
            "purchaseNum": self.spinBox_2.value(),
            "purchasePrice": self.doubleSpinBox_2.value(),
            "purchaseAmt": self.doubleSpinBox_4.value(),  # 采购金额
            "cost": self.doubleSpinBox_15.value(),  # 成本
            "receivedAmt": self.doubleSpinBox_13.value(),  # 累计收款金额
            "inputVat": self.doubleSpinBox_5.value(),  # 进项税额
            "saleNum": self.spinBox.value(),
            "salePrice": self.doubleSpinBox_3.value(),
            "saleAmt": self.doubleSpinBox.value(),  # 销售金额
            "inputAmt": self.doubleSpinBox_7.value(),  # 收入
            "paidAmt": self.doubleSpinBox_14.value(),  # 累计付款金额
            "outputVat": self.doubleSpinBox_6.value(),  # 销项税额
            "grossPft": self.doubleSpinBox_12.value(),  # 毛利
            "addTax": self.doubleSpinBox_9.value(),  # 增值税
            "surTax": self.doubleSpinBox_8.value(),  # 附加税
            "stampTax": self.doubleSpinBox_10.value(),  # 印花税
            "nt": self.doubleSpinBox_11.value(),  # 净利润
            "isInputFapiao": 0 if self.comboBox_2.currentText() == "否" else 1,  #
            "inputFapiaoDate": self.dateEdit.text(),  # 收票日期
            "isSend": 0 if self.comboBox_4.currentText() == "否" else 1,  #
            "isMakeFapiao": 0 if self.comboBox_3.currentText() == "否" else 1,  #
            "makeFapiaoDate": self.dateEdit_2.text(),  # 开票日期
            "pjStatus": self.comboBox.currentText(),  # 项目状态
            "reverse": self.lineEdit_4.text(),  # 备注
            "details": []
        }
        cur_row = self.tableWidget.rowCount()
        for row in range(cur_row):
            dataParam["details"].append({
                "recPayDate": self.tableWidget.cellWidget(row, 0).text(),
                "amt": self.tableWidget.cellWidget(row, 1).value(),
                "flag": 0 if self.tableWidget.cellWidget(row, 2).currentText() == "收入" else 1,
                "reverse": self.tableWidget.cellWidget(row, 3).text()
            })

        def calback(res):
            if res == "error":
                self.tips("系统异常")
            else:
                self.closeSo._signal.emit("0")

        def func():
            res = self.send(methodName, dataParam)
            so._signal.emit(res)

        t = Thread(target=func)
        so._signal.connect(calback)
        t.start()

    def recPayAmtCal(self):
        paidAmt = 0
        receivedAmt = 0
        cur_row = self.tableWidget.rowCount()
        for row in range(cur_row):
            flag = self.tableWidget.cellWidget(row, 2).currentText()
            if flag == "收入":
                receivedAmt = receivedAmt + self.tableWidget.cellWidget(row, 1).value()
            elif flag == "支出":
                paidAmt = paidAmt + self.tableWidget.cellWidget(row, 1).value()
        self.doubleSpinBox_13.setValue(receivedAmt)
        self.doubleSpinBox_14.setValue(paidAmt)

    def calculate(self):
        saleNum = self.spinBox.value()
        salePrice = self.doubleSpinBox_3.value()
        self.doubleSpinBox.setValue(saleNum * salePrice)
        purchageNum = int(self.spinBox_2.value())
        purchagePrice = self.doubleSpinBox_2.value()
        self.doubleSpinBox_4.setValue(purchageNum * purchagePrice)
        self.doubleSpinBox_15.setValue(self.doubleSpinBox_4.value() / 1.13)
        self.doubleSpinBox_5.setValue(self.doubleSpinBox_4.value() - self.doubleSpinBox_4.value() / 1.13)
        self.doubleSpinBox_7.setValue(self.doubleSpinBox.value() / 1.13)
        self.doubleSpinBox_6.setValue(round(self.doubleSpinBox.value() / 1.13 * 0.13, 2))
        self.doubleSpinBox_12.setValue(self.doubleSpinBox.value() - self.doubleSpinBox_4.value())
        self.doubleSpinBox_9.setValue(
            round((self.doubleSpinBox.value() - self.doubleSpinBox_4.value()) / 1.13 * 0.13, 2))
        self.doubleSpinBox_8.setValue(
            round((self.doubleSpinBox.value() - self.doubleSpinBox_4.value()) / 1.13 * 0.13 * 0.12, 2))
        self.doubleSpinBox_10.setValue(round(self.doubleSpinBox.value() / 1.13 * 0.0003, 2))
        self.doubleSpinBox_11.setValue(
            self.doubleSpinBox_12.value() - self.doubleSpinBox_9.value() - self.doubleSpinBox_8.value() - self.doubleSpinBox_10.value())

    def menu(self):
        cmenu = QMenu(self.tableWidget)
        addAction = QAction("添加", self)
        addAction.setData(1)
        cmenu.addAction(addAction)
        addAction.triggered.connect(lambda: self.addRow())
        self.addAction(addAction)
        delAction = QAction("删除", self)
        delAction.setData(1)
        cmenu.addAction(delAction)
        delAction.triggered.connect(self.delRow)
        self.addAction(delAction)
        cmenu.exec_(QCursor.pos())

    def addRow(self, date=time.strftime("%Y-%m-%d", time.localtime(time.time())), amt=0.00, flag=0, reverse=""):
        cur_row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(cur_row + 1)
        combox = QComboBox()
        combox.addItems(['收入', '支出'])
        combox.setCurrentText("收入" if flag == 0 else "支出")
        combox.setEditable(True)
        combox_line = combox.lineEdit()
        combox_line.setAlignment(Qt.AlignCenter)
        combox.currentTextChanged.connect(self.recPayAmtCal)

        dateEdit = QDateEdit()
        dateEdit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        dateEdit.setCurrentSection(QDateTimeEdit.YearSection)
        dateEdit.setDisplayFormat("yyyy-MM-dd")
        dateEdit.setAlignment(Qt.AlignCenter)
        dateEdit.setDate(QDate(*[int(s) for s in date.split("-")]))

        doubleSpinbox = QDoubleSpinBox()
        doubleSpinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        doubleSpinbox.setAlignment(Qt.AlignCenter)
        doubleSpinbox.setMaximum(1e+45)
        doubleSpinbox.setValue(amt)
        doubleSpinbox.valueChanged.connect(self.recPayAmtCal)

        lineEdit = QLineEdit(reverse)
        lineEdit.setAlignment(Qt.AlignCenter)
        self.tableWidget.setCellWidget(cur_row, 0, dateEdit)
        self.tableWidget.setCellWidget(cur_row, 1, doubleSpinbox)
        self.tableWidget.setCellWidget(cur_row, 2, combox)
        self.tableWidget.setCellWidget(cur_row, 3, lineEdit)

    def delRow(self):
        if self.tableWidget.currentRow() == -1:
            self.tips("请选中一条记录")
            return
        rowNum = self.tableWidget.currentRow()
        self.tableWidget.removeRow(rowNum)
        self.recPayAmtCal()

    def queryDetail(self):
        if self.contractNum == "":
            self.pushButton_2.setEnabled(False)
            self.contract_line.setEnabled(True)
            return

        methodName = "queryDetail"
        dataParam = {
            "contractNum": self.contractNum
        }
        pj = self.send(methodName, dataParam)
        if pj == "error":
            self.closeSo._signal.emit("0")
            self.window().close()
            return
        pj = eval(pj)

        self.contract_line.setText(pj["contractNum"])
        self.lineEdit_10.setText(pj["supplier"])  # 供应商
        self.lineEdit_3.setText(pj["custormer"])  # 客户
        self.lineEdit.setText(pj["product"])
        self.spinBox_2.setValue(pj["purchaseNum"])
        self.doubleSpinBox_2.setValue(pj["purchasePrice"])
        self.doubleSpinBox_4.setValue(pj["purchaseAmt"])  # 采购金额
        self.doubleSpinBox_15.setValue(pj["cost"])  # 成本
        self.doubleSpinBox_13.setValue(pj["receivedAmt"])  # 累计收款金额
        self.doubleSpinBox_5.setValue(pj["inputVat"])  # 进项税额
        self.spinBox.setValue(pj["saleNum"])
        self.doubleSpinBox_3.setValue(pj["salePrice"])
        self.doubleSpinBox.setValue(pj["saleAmt"])  # 销售金额
        self.doubleSpinBox_7.setValue(pj["inputAmt"])  # 收入
        self.doubleSpinBox_14.setValue(pj["paidAmt"])  # 累计付款金额
        self.doubleSpinBox_6.setValue(pj["outputVat"])  # 销项税额
        self.doubleSpinBox_12.setValue(pj["grossPft"])  # 毛利
        self.doubleSpinBox_9.setValue(pj["addTax"])  # 增值税
        self.doubleSpinBox_8.setValue(pj["surTax"])  # 附加税
        self.doubleSpinBox_10.setValue(pj["stampTax"])  # 印花税
        self.doubleSpinBox_11.setValue(pj["nt"])  # 净利润
        self.comboBox_2.setCurrentText("否" if pj["isInputFapiao"]==0 else "是") #是否收票
        if self.comboBox_2.currentText()=="是":
            self.dateEdit.setEnabled(True)
            self.comboBox_4.setEnabled(True)
        self.dateEdit.setDate(QDate(*[int(s) for s in pj["inputFapiaoDate"].split("-")]))  # 收票日期
        self.comboBox_4.setCurrentText("否" if pj["isSend"]==0 else "是")
        self.comboBox_3.setCurrentText("否" if pj["isMakeFapiao"]==0 else "是") #是否开票
        if self.comboBox_3.currentText()=="是":
            self.dateEdit_2.setEnabled(True)
        self.dateEdit_2.setDate(QDate(*[int(s) for s in pj["makeFapiaoDate"].split("-")]))  # 开票日期
        self.comboBox.setCurrentText(pj["pjStatus"])  # 项目状态
        self.lineEdit_4.setText(pj["reverse"])  # 备注
        if pj["details"] != []:
            for d in pj["details"]:
                self.addRow(date=d["recPayDate"], amt=d["amt"], flag=d["flag"], reverse=d["reverse"])

    def send(self, methodName, dataParam):
        from main import ip
        res = requests.post("{}/{}".format(ip, methodName), json=dataParam)
        if res.text != "error":
            res = eval(res.text)
        else:
            res = res.text
        return str(res)

    def tips(self, text):
        ui_dialog1 = DialogWindow(text=text)
        return ui_dialog1.exec_() == QDialog.Accepted

    def closeEvent(self, event):
        event.accept()
        self.closeSo._signal.emit("0")
        self.window().close()  # 退出程序


if __name__ == "__main__":
    app = QApplication(argv)
    ui = FormWindow()
    # ui=CandyWindow.createWindow(ui, title='启维台账工具', theme='blueGreen')
    ui.show()
    exit(app.exec_())
