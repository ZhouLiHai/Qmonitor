import sys, socket, os
from ftplib import FTP

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from setting import *
from networker import *
import libconf, datetime
import telnetlib

QTextCodec.setCodecForTr(QTextCodec.codecForName('utf8'))

class Window(QMainWindow):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.setFont(QFont("微软雅黑",10))

		self.setGeometry(50, 50, 1200, 700)
		self.setWindowTitle(self.tr('配网终端维护软件'))

		# 创建连接参数
		self.GlobalIp = "192.168.0.200"
		self.GlobalPort = "2404"
		self.GlobalPoll = "1000"

		# 创建分裂器
		self.spliter = QSplitter(self)
		self.setCentralWidget(self.spliter)

		# 创建栈空间
		self.stack=QStackedWidget(self.spliter)
		self.stack.setGeometry(50, 50, self.geometry().width()/3, self.geometry().height())

		self.createActions()
		self.createMenus()

		# 创建遥测视图
		self.analoginfo01 = AnalogInfo(1)
		self.analoginfo02 = AnalogInfo(2)
		self.analoginfo03 = AnalogInfo(3)

		# 打开配置文件
		with open('config.cfg') as f:
			self.configFile = libconf.load(f)

		# 创建遥信和遥控视图
		self.remoteinfo = RemoteInfo(self.configFile)
		self.ctrlinfo = CtrlInfo(self)

		# 将视图添加到堆栈空间中
		self.stack.addWidget(self.analoginfo01)
		self.stack.addWidget(self.analoginfo02)
		self.stack.addWidget(self.analoginfo03)
		self.stack.addWidget(self.remoteinfo)
		self.stack.addWidget(self.ctrlinfo)

		# 设置分裂视图并添加堆栈空间和文本空间
		self.stack.setFrameStyle(QFrame.Panel|QFrame.Raised)
		self.textedit = QTextEdit();
		self.spliter.addWidget(self.stack)
		self.spliter.addWidget(self.textedit)

	def ShowMessage(self, msg):
		self.textedit.append("%s" %msg)

	def RefAnalog(self, addr, data):
		if addr >= 8001 and addr <= 8072:
			form = self.FindFormByAddr(addr)
			data = float(data) * form / 100.0
			addr = addr - 8001

			if addr // 24 == 0:
				self.analoginfo01.setValue(addr, data)
			if addr // 24 == 1:
				self.analoginfo02.setValue(addr, data)
			if addr // 24 == 2:
				self.analoginfo03.setValue(addr, data)
			self.textedit.append("地址%04d %8.3f" %(addr+8001, data))
			return

		if addr == 8073:
			self.analoginfo01.setFresh(data)
		if addr == 8074:
			self.analoginfo02.setFresh(data)
		if addr == 8075:
			self.analoginfo03.setFresh(data)

		self.textedit.append("地址%04d %8.3f" %(addr, data))

	def RefRemote(self, addr, data):
		states = ["分","合"]
		self.remoteinfo.setState(addr, data)
		self.textedit.append("地址:%04d 状态:%s" %(addr, states[data]))

	def AddSoeInfo(self, info):
		self.remoteinfo.addSoe(info)
		self.textedit.append(info)

	def CtrlSelectState(self, state):
		self.ctrlinfo.SelectState(state)
		if state == 0:
			QMessageBox.information(self,"消息", self.tr("遥控执行成功!"))

	def CtrlProtect(self):
		QMessageBox.information(self,"错误", self.tr("软压板保护,遥控无法执行!"))

	def FindFormByAddr(self, addr):
		aConfig = self.configFile['go']['analog']

		for aline in aConfig:
			if aline['n'] == addr:
				return aline['f']
		return 1

	def createActions(self):
		self.openAction=QAction(self.tr("网络连接设置"),self)
		self.connect(self.openAction,SIGNAL("triggered()"),self.OpenConnection)
		self.connectAction=QAction(self.tr("连接终端"),self)
		self.connect(self.connectAction,SIGNAL("triggered()"),self.DoConnect)
		self.disconnectAction=QAction(self.tr("断开连接"),self)
		self.connect(self.disconnectAction,SIGNAL("triggered()"),self.Terminate)
		self.rebootAction=QAction(self.tr("重启终端"),self)
		self.connect(self.rebootAction,SIGNAL("triggered()"),self.Reboot)
		self.uploadAction=QAction(self.tr("上传配置"),self)
		self.connect(self.uploadAction,SIGNAL("triggered()"),self.UpLoadSettingFile)

		self.analog01Action=QAction(self.tr("视图[遥测一]"),self)
		self.connect(self.analog01Action,SIGNAL("triggered()"),self.ChangeViewAnalog01)
		self.analog02Action=QAction(self.tr("视图[遥测二]"),self)
		self.connect(self.analog02Action,SIGNAL("triggered()"),self.ChangeViewAnalog02)
		self.analog03Action=QAction(self.tr("视图[遥测三]"),self)
		self.connect(self.analog03Action,SIGNAL("triggered()"),self.ChangeViewAnalog03)
		self.remoteAction=QAction(self.tr("视图[遥信]"),self)
		self.connect(self.remoteAction,SIGNAL("triggered()"),self.ChangeViewRemote)
		self.ctrlAction=QAction(self.tr("视图[遥控]"),self)
		self.connect(self.ctrlAction,SIGNAL("triggered()"),self.ChangeViewCtrl)

		self.miscSettingAction=QAction(self.tr("配置&综合设置"),self)
		self.connect(self.miscSettingAction,SIGNAL("triggered()"),self.mainSetting)
		self.formSettingAction=QAction(self.tr("配置&三遥设置"),self)
		self.connect(self.formSettingAction,SIGNAL("triggered()"),self.mainSetting)
		self.findSOEAction=QAction(self.tr("遥信点号速查"),self)
		self.connect(self.findSOEAction,SIGNAL("triggered()"),self.mainSetting)

		self.aboutAction=QAction(self.tr("关于"),self)
		self.connect(self.aboutAction,SIGNAL("triggered()"),self.OpenConnection)

	def createMenus(self):
		self.startMenu = self.menuBar().addMenu(self.tr("开始"))
		self.startMenu.addAction(self.openAction)
		self.startMenu.addAction(self.connectAction)
		self.startMenu.addAction(self.disconnectAction)
		self.startMenu.addAction(self.rebootAction)
		self.startMenu.addAction(self.uploadAction)

		self.viewMenu = self.menuBar().addMenu(self.tr("视图设定"))
		self.viewMenu.addAction(self.analog01Action)
		self.viewMenu.addAction(self.analog02Action)
		self.viewMenu.addAction(self.analog03Action)
		self.viewMenu.addAction(self.remoteAction)
		self.viewMenu.addAction(self.ctrlAction)

		self.settingMenu = self.menuBar().addMenu(self.tr("参数整定"))
		self.settingMenu.addAction(self.miscSettingAction)
		self.settingMenu.addAction(self.formSettingAction)
		self.settingMenu.addAction(self.findSOEAction)

		self.aboutMenu = self.menuBar().addMenu(self.tr("帮助&阅读"))
		self.aboutMenu.addAction(self.aboutAction)

	def OpenConnection(self):
		startSettingDialog = StartDialog(self)
		if startSettingDialog:
			startSettingDialog.show()

	def DoConnect(self):
		if hasattr(self, 'connection'):
			self.connection.close()

		if hasattr(self, 'msgwork'):
			self.msgwork.Terminate()
		# 添加连接线程
		self.msgwork = Worker(self)
		self.connect(self.msgwork, SIGNAL("ShowMessage(QString)"), self.ShowMessage)
		self.connect(self.msgwork, SIGNAL("RefAnalog(int, int)"), self.RefAnalog)
		self.connect(self.msgwork, SIGNAL("RefRemote(int, int)"), self.RefRemote)
		self.connect(self.msgwork, SIGNAL("AddSoeInfo(QString)"), self.AddSoeInfo)
		self.connect(self.msgwork, SIGNAL("CtrlSelectState(int)"), self.CtrlSelectState)
		self.connect(self.msgwork, SIGNAL("ctrlProtect()"), self.CtrlProtect)

		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(5)
			s.connect((self.GlobalIp, int(self.GlobalPort)))
		except socket.timeout:
			QMessageBox.information(self,"网络异常",self.tr("连接终端网络超时."))

		self.connection = s
		self.msgwork.render(s)

	def Terminate(self):
		sllf.connection.close()
		self.msgwork.Terminate()

	def Reboot(self):
		progressDialog=QProgressDialog(self)
		progressDialog.setMinimumDuration(5)
		progressDialog.setWindowTitle(self.tr("请等待"))
		progressDialog.setWindowModality(Qt.WindowModal)
		progressDialog.setLabelText(self.tr("开始重启终端..."))
		progressDialog.setCancelButtonText(self.tr("确定"))
		progressDialog.setRange(0,4)


		progressDialog.setValue(0)
		progressDialog.setLabelText(self.tr("正在尝试链接终端..."))
		QThread.msleep(100)
		tn = telnetlib.Telnet(self.GlobalIp)
		progressDialog.setValue(1)
		progressDialog.setLabelText(self.tr("正在验证用户名-密码..."))
		QThread.msleep(100)
		tn.read_until(b"ogin: ")
		tn.write(b"root\n")
		tn.read_until(b"assword: ")
		tn.write(b"root\n")
		progressDialog.setValue(2)
		progressDialog.setLabelText(self.tr("正在下发重启指令..."))
		QThread.msleep(100)
		tn.write(b"reboot\n")
		tn.read_all()
		progressDialog.setValue(3)
		progressDialog.setLabelText(self.tr("等待终端重启..."))
		QThread.msleep(100)
		tn.close()

	def UpLoadSettingFile(self):
		ftp=FTP()
		ftp.connect(self.GlobalIp, 21)#连接
		ftp.login('root','root')#登录，如果匿名登录则用空串代替即可
		ftp.cwd('/opt/')
		bufsize = 1024 * 1024
		file_handler = open("config.cfg",'rb')#以读模式在本地打开文件
		ftp.storbinary('STOR %s' % os.path.basename("config.cfg"),file_handler,bufsize)#上传文件
		ftp.quit()
		file_handler.close()

	def mainSetting(self):
		progressDialog=QProgressDialog(self)
		progressDialog.setMinimumDuration(5)
		progressDialog.setWindowTitle(self.tr("请等待"))
		progressDialog.setWindowModality(Qt.WindowModal)
		progressDialog.setLabelText(self.tr("开始重启终端..."))
		progressDialog.setCancelButtonText(self.tr("确定"))
		progressDialog.setRange(0,3)


		progressDialog.setValue(0)
		progressDialog.setLabelText(self.tr("正在尝试链接终端..."))
		QThread.msleep(200)
		# 下载配置文件
		ftp=FTP()
		ftp.connect(self.GlobalIp,21)

		progressDialog.setValue(1)
		progressDialog.setLabelText(self.tr("正在验证用户名和密码..."))
		QThread.msleep(200)
		ftp.login('root','root')
		bufsize = 1024 * 1024
		filename = "/opt/config.cfg"
		file_handler = open('config.cfg','wb')

		progressDialog.setValue(2)
		progressDialog.setLabelText(self.tr("正在载入配置文件..."))
		QThread.msleep(200)
		ftp.retrbinary('RETR %s' % os.path.basename(filename),file_handler.write,bufsize)
		ftp.quit()
		file_handler.close()

		progressDialog.setValue(3)
		progressDialog.setLabelText(self.tr("正在初始化配置界面..."))
		QThread.msleep(200)
		with open('config.cfg') as f:
			self.configFile = libconf.load(f)
			StockDialog(self.configFile, self).show()

	def ChangeViewAnalog01(self):
		self.stack.setCurrentIndex(0)

	def ChangeViewAnalog02(self):
		self.stack.setCurrentIndex(1)

	def ChangeViewAnalog03(self):
		self.stack.setCurrentIndex(2)

	def ChangeViewRemote(self):
		self.stack.setCurrentIndex(3)

	def ChangeViewCtrl(self):
		self.stack.setCurrentIndex(4)

class StartDialog(QDialog):
	def __init__(self,parent=None):
		super(StartDialog,self).__init__(parent)

		self.setWindowTitle(self.tr("网络参数配置"))
		self.father = parent

		label1=QLabel(self.tr("IP地址:"))
		label2=QLabel(self.tr("端口号:"))
		label3=QLabel(self.tr("主站轮询周期(毫秒):"))

		self.ipLabel=QLineEdit("192.168.0.200")
		self.portLabel=QLineEdit("2404")
		self.pollLabel=QLineEdit("1000")

		self.okButton=QPushButton("保存")
		self.cancelButton=QPushButton("取消")

		layout=QGridLayout(self)
		layout.addWidget(label1,0,0)
		layout.addWidget(self.ipLabel,0,1)
		layout.addWidget(label2,1,0)
		layout.addWidget(self.portLabel,1,1)
		layout.addWidget(label3,2,0)
		layout.addWidget(self.pollLabel,2,1)
		layout.addWidget(self.okButton,3,0)
		layout.addWidget(self.cancelButton,3,1)
		layout.setSizeConstraint(QLayout.SetMaximumSize)

		# 设置按钮事件
		self.connect(self.okButton,SIGNAL("clicked()"),self.SetNetParas)
		self.connect(self.cancelButton,SIGNAL("clicked()"),self.Cancel)

	def SetNetParas(self):
		self.father.GlobalIp = self.ipLabel.text()
		self.father.GlobalPort = self.portLabel.text()
		self.father.GlobalPoll = self.pollLabel.text()
		self.father.textedit.append("地址:%s\n端口%s\n设定网络参数成功!\n" %(self.father.GlobalIp,self.father.GlobalPort))
		self.close()

	def Cancel(self):
		self.close()


class AnalogInfo(QWidget):
	def __init__(self, index, parent = None):
		super(AnalogInfo,self).__init__(parent)

		self.setFont(QFont("Consolas",12))

		# 建立基本元素
		label1=QLabel(self.tr("Uab1(V)"))
		label2=QLabel(self.tr("Ucb1(V)"))
		label3=QLabel(self.tr("Uab2(V)"))
		label4=QLabel(self.tr("Ucb2(V)"))

		label5=QLabel(self.tr("Ia1(A)"))
		label6=QLabel(self.tr("Ib1(A)"))
		label7=QLabel(self.tr("Ic1(A)"))
		label8=QLabel(self.tr("Ia2(A)"))
		label9=QLabel(self.tr("Ib2(A)"))
		label10=QLabel(self.tr("Ic2(A)"))
		label11=QLabel(self.tr("Ia3(A)"))
		label12=QLabel(self.tr("Ib3(A)"))
		label13=QLabel(self.tr("Ic3(A)"))
		label14=QLabel(self.tr("Ia4(A)"))
		label15=QLabel(self.tr("Ib4(A)"))
		label16=QLabel(self.tr("Ic4(A)"))

		label17=QLabel(self.tr("P1(Var)"))
		label18=QLabel(self.tr("Q1(W)"))
		label19=QLabel(self.tr("P2(Var)"))
		label20=QLabel(self.tr("Q2(W)"))
		label21=QLabel(self.tr("P3(Var)"))
		label22=QLabel(self.tr("Q3(W)"))
		label23=QLabel(self.tr("P4(Var)"))
		label24=QLabel(self.tr("Q4(W)"))

		label25=QLabel(self.tr("COS1"))
		label26=QLabel(self.tr("COS2"))
		label27=QLabel(self.tr("COS3"))
		label28=QLabel(self.tr("COS4"))

		label29=QLabel(self.tr("S1"))
		label30=QLabel(self.tr("S2"))
		label31=QLabel(self.tr("S3"))
		label32=QLabel(self.tr("S4"))

		label33=QLabel(self.tr("Hz(MHz)"))

		self.Labels = list()

		# 电压
		self.Labels.append(QLabel("000.00"))
		self.Labels[0].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("000.00"))
		self.Labels[1].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("000.00"))
		self.Labels[2].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("000.00"))
		self.Labels[3].setFrameStyle(QFrame.Panel|QFrame.Sunken)

		# 电流
		self.Labels.append(QLabel("00.000"))
		self.Labels[4].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[5].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[6].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[7].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[8].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[9].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[10].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[11].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[12].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[13].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[14].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("00.000"))
		self.Labels[15].setFrameStyle(QFrame.Panel|QFrame.Sunken)

		# 功率
		self.Labels.append(QLabel("0000.00"))
		self.Labels[16].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[17].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[18].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[19].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[20].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[21].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[22].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[23].setFrameStyle(QFrame.Panel|QFrame.Sunken)

		# COS
		self.Labels.append(QLabel("0.000"))
		self.Labels[24].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0.000"))
		self.Labels[25].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0.000"))
		self.Labels[26].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0.000"))
		self.Labels[27].setFrameStyle(QFrame.Panel|QFrame.Sunken)

		# S
		self.Labels.append(QLabel("0000.00"))
		self.Labels[28].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[29].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[30].setFrameStyle(QFrame.Panel|QFrame.Sunken)
		self.Labels.append(QLabel("0000.00"))
		self.Labels[31].setFrameStyle(QFrame.Panel|QFrame.Sunken)

		self.Labels.append(QLabel("0000.00"))
		self.Labels[32].setFrameStyle(QFrame.Panel|QFrame.Sunken)

		layout=QGridLayout(self)

		layout.addWidget(label1,0,0)
		layout.addWidget(self.Labels[0],0,1)
		layout.addWidget(label2,0,2)
		layout.addWidget(self.Labels[1],0,3)
		layout.addWidget(label3,0,4)
		layout.addWidget(self.Labels[2],0,5)
		layout.addWidget(label4,0,6)
		layout.addWidget(self.Labels[3],0,7)

		layout.addWidget(label5,1,0)
		layout.addWidget(self.Labels[4],1,1)
		layout.addWidget(label6,1,2)
		layout.addWidget(self.Labels[5],1,3)
		layout.addWidget(label7,1,4)
		layout.addWidget(self.Labels[6],1,5)

		# 频率位置
		layout.addWidget(label33,1,6)
		layout.addWidget(self.Labels[32],1,7)

		layout.addWidget(label8,2,0)
		layout.addWidget(self.Labels[7],2,1)
		layout.addWidget(label9,2,2)
		layout.addWidget(self.Labels[8],2,3)
		layout.addWidget(label10,2,4)
		layout.addWidget(self.Labels[9],2,5)

		layout.addWidget(label11,3,0)
		layout.addWidget(self.Labels[10],3,1)
		layout.addWidget(label12,3,2)
		layout.addWidget(self.Labels[11],3,3)
		layout.addWidget(label13,3,4)
		layout.addWidget(self.Labels[12],3,5)

		layout.addWidget(label14,4,0)
		layout.addWidget(self.Labels[13],4,1)
		layout.addWidget(label15,4,2)
		layout.addWidget(self.Labels[14],4,3)
		layout.addWidget(label16,4,4)
		layout.addWidget(self.Labels[15],4,5)

		layout.addWidget(label17,5,0)
		layout.addWidget(self.Labels[16],5,1)
		layout.addWidget(label19,5,2)
		layout.addWidget(self.Labels[18],5,3)
		layout.addWidget(label21,5,4)
		layout.addWidget(self.Labels[20],5,5)
		layout.addWidget(label23,5,6)
		layout.addWidget(self.Labels[22],5,7)

		layout.addWidget(label18,6,0)
		layout.addWidget(self.Labels[17],6,1)
		layout.addWidget(label20,6,2)
		layout.addWidget(self.Labels[19],6,3)
		layout.addWidget(label22,6,4)
		layout.addWidget(self.Labels[21],6,5)
		layout.addWidget(label24,6,6)
		layout.addWidget(self.Labels[23],6,7)

		layout.addWidget(label25,7,0)
		layout.addWidget(self.Labels[24],7,1)
		layout.addWidget(label26,7,2)
		layout.addWidget(self.Labels[25],7,3)
		layout.addWidget(label27,7,4)
		layout.addWidget(self.Labels[26],7,5)
		layout.addWidget(label28,7,6)
		layout.addWidget(self.Labels[27],7,7)

		layout.addWidget(label29,8,0)
		layout.addWidget(self.Labels[28],8,1)
		layout.addWidget(label30,8,2)
		layout.addWidget(self.Labels[29],8,3)
		layout.addWidget(label31,8,4)
		layout.addWidget(self.Labels[30],8,5)
		layout.addWidget(label32,8,6)
		layout.addWidget(self.Labels[31],8,7)

		layout.setMargin(15)
		layout.setSpacing(15)
		layout.setSizeConstraint(QLayout.SetMaximumSize)

	def setValue(self, line, data):
		line = line % 24
		self.Labels[line].setText("%08.3f" %data)
		if line >= 16:
			sqrtv01 = (float(self.Labels[16].text())**2 + float(self.Labels[17].text())**2) ** 0.5;
			sqrtv02 = (float(self.Labels[18].text())**2 + float(self.Labels[19].text())**2) ** 0.5;
			sqrtv03 = (float(self.Labels[20].text())**2 + float(self.Labels[21].text())**2) ** 0.5;
			sqrtv04 = (float(self.Labels[22].text())**2 + float(self.Labels[23].text())**2) ** 0.5;
			if sqrtv01 > 0:
				self.Labels[24].setText("%08.3f" %(float(self.Labels[16].text())/sqrtv01))
			if sqrtv02 > 0:
				self.Labels[25].setText("%08.3f" %(float(self.Labels[18].text())/sqrtv02))
			if sqrtv03 > 0:
				self.Labels[26].setText("%08.3f" %(float(self.Labels[20].text())/sqrtv03))
			if sqrtv04 > 0:
				self.Labels[27].setText("%08.3f" %(float(self.Labels[22].text())/sqrtv04))

			self.Labels[28].setText("%08.3f" %sqrtv01)
			self.Labels[29].setText("%08.3f" %sqrtv02)
			self.Labels[30].setText("%08.3f" %sqrtv03)
			self.Labels[31].setText("%08.3f" %sqrtv04)
	def setFresh(self, data):
		self.Labels[32].setText("%08.3f" %(float(data)/100.0))


class RemoteViewTable(QTableWidget):
	"""docstring for RemoteViewTable"""
	def __init__(self, ptConfig, parent=None):
		super(RemoteViewTable, self).__init__(parent)

		# 获取配置信息
		self.lConfig = ptConfig['go']['remote']

		# 设置表格尺寸
		self.setColumnCount(2)
		self.setRowCount(len(self.lConfig))

		# 设置表格头
		self.setHorizontalHeaderItem(0,QTableWidgetItem(self.tr("遥信点号")))
		self.setHorizontalHeaderItem(1,QTableWidgetItem(self.tr("遥信当前状态")))

		# 根据配置文件设置表格体
		for index in range(len(self.lConfig)):
			self.setItem(index, 0, QTableWidgetItem("%d" %self.lConfig[index]['n']))
			self.setItem(index, 1, QTableWidgetItem("分"))

class RemoteInfo(QWidget):
	def __init__(self, ptConfig, parent = None):
		super(RemoteInfo,self).__init__(parent)

		self.setFont(QFont("微软雅黑",12))

		self.table = RemoteViewTable(ptConfig)
		self.textedit = QTextEdit();

		mainLayout=QGridLayout(self)
		mainLayout.addWidget(self.textedit,0,1)
		mainLayout.addWidget(self.table,0,0)
		mainLayout.setSizeConstraint(QLayout.SetMaximumSize)

	def setState(self, addr, data):
		states = ["分","合"]
		for index in range(self.table.rowCount()):
			if int(self.table.item(index, 0).text()) == addr:
				self.table.item(index, 1).setText(states[data%2])
	def addSoe(self, info):
		self.textedit.append(info)

class CtrlInfo(QWidget):
	def __init__(self, parent = None):
		super(CtrlInfo,self).__init__(parent)

		self.setFont(QFont("微软雅黑",12))
		self.father = parent

		label1=QLabel(self.tr("遥控路号:"))
		label2=QLabel(self.tr("遥控状态:"))
		label3=QLabel(self.tr("遥控预选:"))

		# 反校状态需要被更新
		self.label4=QLabel(self.tr("未反校"))

		label5=QLabel(self.tr("遥控执行:"))
		label6=QLabel(self.tr("电池活化:"))
		label7=QLabel(self.tr("对时:"))
		label8=QLabel(self.tr("系统复归:"))

		self.ComboBoxLine=QComboBox()
		self.ComboBoxLine.insertItem(0,self.tr("遥控一"))
		self.ComboBoxLine.insertItem(1,self.tr("遥控二"))
		self.ComboBoxLine.insertItem(2,self.tr("遥控三"))
		self.ComboBoxLine.insertItem(3,self.tr("遥控四"))
		self.ComboBoxLine.insertItem(4,self.tr("遥控五"))
		self.ComboBoxLine.insertItem(5,self.tr("遥控六"))
		self.ComboBoxLine.insertItem(6,self.tr("遥控七"))
		self.ComboBoxLine.insertItem(7,self.tr("遥控八"))
		self.ComboBoxLine.insertItem(8,self.tr("遥控九"))
		self.ComboBoxLine.insertItem(9,self.tr("遥控十"))
		self.ComboBoxLine.insertItem(10,self.tr("遥控十一"))
		self.ComboBoxLine.insertItem(11,self.tr("遥控十二"))

		self.ComboBoxState=QComboBox()
		self.ComboBoxState.insertItem(0,self.tr("开关分闸"))
		self.ComboBoxState.insertItem(1,self.tr("开关合闸"))

		self.selectButton=QPushButton(self.tr("遥控预选"))
		self.actionButton=QPushButton(self.tr("遥控执行"))
		self.HuohuaButton=QPushButton(self.tr("电池活化"))
		self.TingzhiButton=QPushButton(self.tr("活化停止"))
		self.CatchTimeButton=QPushButton(self.tr("对时"))
		self.RecoverButton=QPushButton(self.tr("系统复归"))

		self.timeEdit1 = QLineEdit("%02d" %(datetime.datetime.now().year-2000))
		self.timeEdit2 = QLineEdit("%02d" %datetime.datetime.now().month)
		self.timeEdit3 = QLineEdit("%02d" %datetime.datetime.now().day)
		self.timeEdit4 = QLineEdit("%02d" %datetime.datetime.now().hour)
		self.timeEdit5 = QLineEdit("%02d" %datetime.datetime.now().minute)
		self.timeEdit6 = QLineEdit("%02d" %datetime.datetime.now().second)

		timelabel1=QLabel(self.tr("年:"))
		timelabel2=QLabel(self.tr("月:"))
		timelabel3=QLabel(self.tr("日:"))
		timelabel4=QLabel(self.tr("时:"))
		timelabel5=QLabel(self.tr("分:"))
		timelabel6=QLabel(self.tr("秒:"))


		ctrlLayout=QGridLayout()
		ctrlLayout.addWidget(label1,0,0)
		ctrlLayout.addWidget(self.ComboBoxLine,0,1)
		ctrlLayout.addWidget(label2,0,2)
		ctrlLayout.addWidget(self.ComboBoxState,0,3)

		ctrlLayout.addWidget(label3,1,0)
		ctrlLayout.addWidget(self.selectButton,1,1)
		ctrlLayout.addWidget(self.label4,1,2)
		ctrlLayout.addWidget(label5,2,0)
		ctrlLayout.addWidget(self.actionButton,2,1)

		ctrlGroupBox = QGroupBox(self.tr("遥控区"))
		ctrlGroupBox.setLayout(ctrlLayout)

		timeLayout=QGridLayout()
		timeLayout.addWidget(label7,0,0)
		timeLayout.addWidget(timelabel1,1,0)
		timeLayout.addWidget(self.timeEdit1,1,1)
		timeLayout.addWidget(timelabel2,1,2)
		timeLayout.addWidget(self.timeEdit2,1,3)
		timeLayout.addWidget(timelabel3,1,4)
		timeLayout.addWidget(self.timeEdit3,1,5)
		timeLayout.addWidget(timelabel4,2,0)
		timeLayout.addWidget(self.timeEdit4,2,1)
		timeLayout.addWidget(timelabel5,2,2)
		timeLayout.addWidget(self.timeEdit5,2,3)
		timeLayout.addWidget(timelabel6,2,4)
		timeLayout.addWidget(self.timeEdit6,2,5)

		timeLayout.addWidget(self.CatchTimeButton,3,0)

		timeGroupBox = QGroupBox(self.tr("对时区"))
		timeGroupBox.setLayout(timeLayout)

		miscLayout=QGridLayout()
		miscLayout.addWidget(label6,0,0)
		miscLayout.addWidget(self.HuohuaButton,0,1)
		miscLayout.addWidget(self.TingzhiButton,0,2)
		miscLayout.addWidget(label8,1,0)
		miscLayout.addWidget(self.RecoverButton,1,1)

		miscGroupBox = QGroupBox(self.tr("杂项"))
		miscGroupBox.setLayout(miscLayout)

		mainLayout = QVBoxLayout(self)
		mainLayout.addWidget(ctrlGroupBox)
		mainLayout.addWidget(timeGroupBox)
		mainLayout.addWidget(miscGroupBox)

		mainLayout.setSizeConstraint(QLayout.SetFixedSize)

		self.connect(self.selectButton,SIGNAL("clicked()"),self.select)
		self.connect(self.actionButton,SIGNAL("clicked()"),self.action)

		self.connect(self.HuohuaButton,SIGNAL("clicked()"),self.huohua)
		self.connect(self.TingzhiButton,SIGNAL("clicked()"),self.huohuatingzhi)
		self.connect(self.RecoverButton,SIGNAL("clicked()"),self.recover)
		self.connect(self.CatchTimeButton,SIGNAL("clicked()"),self.catchtime)

	def catchtime(self):
		msg = b'\x68\x14\x00\x00\x00\x00\x67\x01\x06\x00\x01\x00\x00\x00\x00\x00'

		year = bytes([int(self.timeEdit1.text())])
		month = bytes([int(self.timeEdit2.text())])
		day = bytes([int(self.timeEdit3.text())])
		hour = bytes([int(self.timeEdit4.text())])
		minute = bytes([int(self.timeEdit5.text())])
		second = bytes([int((int(self.timeEdit6.text())*1000)/256)])
		append = second + minute + hour + day + month + year

		msg += append
		print(msg)
		self.father.connection.send(msg)


	def SelectState(self, state):
		if state == 1:
			self.label4.setText("反校成功")
		else:
			self.label4.setText("未反校")
	def select(self):
		msg = b'\x68\x0e\x7e\x02\x06\x00\x2d\x01\x07\x00\x01\x00'

		line = bytes([self.ComboBoxLine.currentIndex()+0x01])
		state = bytes([self.ComboBoxState.currentIndex()+0x80])
		msg += line + b'\x60\x00' + state

		self.father.connection.send(msg)
	def action(self):
		msg = b'\x68\x0e\x7e\x02\x06\x00\x2d\x01\x07\x00\x01\x00'

		line = bytes([self.ComboBoxLine.currentIndex()+0x01])
		state = bytes([self.ComboBoxState.currentIndex()+0x00])
		msg += line + b'\x60\x00' + state

		self.father.connection.send(msg)

	def huohua(self):
		msg = b'\x68\x0e\x7e\x02\x06\x00\x2d\x01\x07\x00\x01\x00'
		line = bytes([22])
		msg += line + b'\x60\x00\x00'

		self.father.connection.send(msg)

	def huohuatingzhi(self):
		msg = b'\x68\x0e\x7e\x02\x06\x00\x2d\x01\x07\x00\x01\x00'
		line = bytes([23])
		msg += line + b'\x60\x00\x00'

		self.father.connection.send(msg)

	def recover(self):
		msg = b'\x68\x0e\x7e\x02\x06\x00\x2d\x01\x07\x00\x01\x00'
		line = bytes([25])
		msg += line + b'\x60\x00\x00'

		self.father.connection.send(msg)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())
