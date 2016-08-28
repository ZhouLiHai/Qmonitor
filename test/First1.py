from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

QTextCodec.setCodecForTr(QTextCodec.codecForName('utf8'))

class MyTable(QTableWidget):
	def __init__(self, parent=None):
		super(MyTable,self).__init__(parent)
		self.setColumnCount(5)
		self.setRowCount(2)
		self.setItem(0,0,QTableWidgetItem(self.tr('性别')))
		self.setItem(0,1,QTableWidgetItem(self.tr('姓名')))
		self.setItem(0,2,QTableWidgetItem(self.tr('出生日期')))
		self.setItem(0,3,QTableWidgetItem(self.tr('职业')))
		self.setItem(0,4,QTableWidgetItem(self.tr('收入')))

		cbw = QComboBox()
		cbw.addItem("男")
		cbw.addItem("女")
		self.setCellWidget(1,0,cbw)

		self.setItem(1,1,QTableWidgetItem("Tom"))

		dte1 = QDateTimeEdit()
		dte1.setDateTime(QDateTime.currentDateTime())
		dte1.setDisplayFormat("yy/mm/dd")
		dte1.setCalendarPopup(True)
		self.setCellWidget(1,2,dte1)

		cbw2=QComboBox()
		cbw2.addItem("Worker")
		cbw2.addItem("Famer")
		cbw2.addItem("Doctor")
		cbw2.addItem("Lawyer")
		cbw2.addItem("Soldier")
		self.setCellWidget(1,3,cbw2)

		sb1=QSpinBox()
		sb1.setRange(1000,10000)
		self.setCellWidget(1,4,sb1)



app=QApplication(sys.argv)
myqq=MyTable()
myqq.setWindowTitle("My Table")
myqq.show()
app.exec_()