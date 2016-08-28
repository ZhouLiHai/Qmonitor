# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

class StockDialog(QDialog):
    def __init__(self, ptConfig, parent=None):
        super(StockDialog,self).__init__(parent)

        self.fWindows = parent
        self.setGeometry(50, 50, 1200, 600)
        self.setWindowTitle(self.tr("配网自动化终端综合配置"))
        self.setFont(QFont("微软雅黑",12))


        mainSplitter=QSplitter(Qt.Horizontal)
        mainSplitter.setOpaqueResize(True)

        listWidget=QListWidget(mainSplitter)
        listWidget.insertItem(0,self.tr("遥测参数配置"))
        listWidget.insertItem(1,self.tr("遥信参数配置"))
        listWidget.insertItem(2,self.tr("遥控参数配置"))
        listWidget.insertItem(3,self.tr("综合配置"))
        listWidget.insertItem(4,self.tr("调试参数"))
        listWidget.insertItem(5,self.tr("线路保护定值设置"))
        listWidget.insertItem(6,self.tr("遥信点号速查"))

        frame=QFrame(mainSplitter)
        stack=QStackedWidget()
        stack.setFrameStyle(QFrame.Panel)

        self.analogInfo=AnalogInfo(ptConfig)
        self.remoteInfo=RemoteInfo(ptConfig)
        self.ctrlInfo=CtrlInfo(ptConfig)
        self.miscInfo=MiscInfo(ptConfig)
        self.debugInfo=DebugInfo(ptConfig)
        self.protectInfo=ProtectInfo(ptConfig)
        self.soeInfo=SOEInfo()

        stack.addWidget(self.analogInfo)
        stack.addWidget(self.remoteInfo)
        stack.addWidget(self.ctrlInfo)
        stack.addWidget(self.miscInfo)
        stack.addWidget(self.debugInfo)
        stack.addWidget(self.protectInfo)
        stack.addWidget(self.soeInfo)

        amendPushButton=QPushButton(self.tr("确认修改"))
        closePushButton=QPushButton(self.tr("取消修改"))

        buttonLayout=QHBoxLayout()
        buttonLayout.addWidget(amendPushButton)
        buttonLayout.addWidget(closePushButton)

        mainLayout=QVBoxLayout(frame)
        # mainLayout.setSpacing(6)
        mainLayout.addWidget(stack)
        mainLayout.addLayout(buttonLayout)

        self.connect(listWidget,SIGNAL("currentRowChanged(int)"),stack,SLOT("setCurrentIndex(int)"))
        self.connect(amendPushButton,SIGNAL("clicked()"),self.Confirm)
        self.connect(closePushButton,SIGNAL("clicked()"),self,SLOT("close()"))

        layout=QHBoxLayout(self)
        mainSplitter.setStretchFactor(0,1)
        mainSplitter.setStretchFactor(1,5)
        layout.addWidget(mainSplitter)
        self.setLayout(layout)

    def Confirm(self):
        f = open('config.cfg','w')
        content = "go = {\n"
        content = self.miscInfo.AppendContent(content)
        content = self.debugInfo.AppendContent(content)
        content = self.analogInfo.AppendContent(content)
        content = self.remoteInfo.AppendContent(content)
        content = self.ctrlInfo.AppendContent(content)
        content = self.protectInfo.AppendContent(content)
        content += "}\n"
        f.write(content)
        f.close()
        self.fWindows.UpLoadSettingFile()
        self.close()

class M500SpinBox(QDoubleSpinBox):
    """docstring for M500SpinBox"""
    def __init__(self, nowvalue, parent=None):
        super(M500SpinBox, self).__init__(parent)

        self.setRange(0.0, 500.0)
        self.setSingleStep(1.0)
        self.setValue(nowvalue)

    def MGet(self):
        return self.value()

class M50SpinBox(QDoubleSpinBox):
    """docstring for M50SpinBox"""
    def __init__(self, nowvalue, parent=None):
        super(M50SpinBox, self).__init__(parent)

        self.setRange(0.0, 50.0)
        self.setSingleStep(1.0)
        self.setValue(nowvalue)

    def MGet(self):
        return self.value()

class AnalogSettingTable(QTableWidget):
    """docstring for AnalogSettingTable"""
    def __init__(self, ptConfig, parent=None):
        super(AnalogSettingTable, self).__init__(parent)

        # 获取配置信息
        self.lConfig = ptConfig['go']['analog']

        #  设置表格尺寸
        self.setColumnCount(7)
        self.setRowCount(len(self.lConfig))

        # 设置表格头
        self.setHorizontalHeaderItem(0,QTableWidgetItem(self.tr("遥测点号")))
        self.setHorizontalHeaderItem(1,QTableWidgetItem(self.tr("归一化系数")))
        self.setHorizontalHeaderItem(2,QTableWidgetItem(self.tr("死区阈值")))
        self.setHorizontalHeaderItem(3,QTableWidgetItem(self.tr("越限开关")))
        self.setHorizontalHeaderItem(4,QTableWidgetItem(self.tr("上限")))
        self.setHorizontalHeaderItem(5,QTableWidgetItem(self.tr("下限")))
        self.setHorizontalHeaderItem(6,QTableWidgetItem(self.tr("说明")))

        # 根据配置文件设置表格体
        for index in range(len(self.lConfig)):
            self.setItem(index, 0, QTableWidgetItem("%d" %self.lConfig[index]['n']))
            self.setCellWidget(index, 1, M50SpinBox(self.lConfig[index]['f']))
            self.setCellWidget(index, 2, M50SpinBox(self.lConfig[index]['th']))

            cbw=QComboBox()
            cbw.addItem("关闭")
            cbw.addItem("打开")
            cbw.setCurrentIndex(self.lConfig[index]['s'])
            self.setCellWidget(index,3,cbw)

            self.setCellWidget(index, 4, M500SpinBox(self.lConfig[index]['up']))
            self.setCellWidget(index, 5, M500SpinBox(self.lConfig[index]['down']))
            self.setItem(index, 6, QTableWidgetItem("%d" %self.lConfig[index]['l']))

    def AppendContent(self, content):
        content += "\tanalog = ( {\n"

        for index in range(self.rowCount()):
            content += "\t\t\tn = %s\n" %self.item(index, 0).text()
            content += "\t\t\tf = %f\n" %self.cellWidget(index, 1).MGet()
            content += "\t\t\tth = %f\n" %self.cellWidget(index, 2).MGet()
            content += "\t\t\ts = %d\n" %self.cellWidget(index, 3).currentIndex()
            content += "\t\t\tup = %f\n" %self.cellWidget(index, 4).MGet()
            content += "\t\t\tdown = %f\n" %self.cellWidget(index, 5).MGet()
            content += "\t\t\tl = %s\n" %self.item(index, 6).text()
            content += "\t\t\tla = 1.0\n"
            if index != self.rowCount() - 1:
                content += "\t\t}, {\n"
            else:
                content += "\t\t} )\n"

        return content

class AnalogInfo(QWidget):
    def __init__(self, ptConfig, parent=None):
        super(AnalogInfo,self).__init__(parent)

        self.table = AnalogSettingTable(ptConfig)

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(self.table,0,0)
        mainLayout.setSizeConstraint(QLayout.SetMaximumSize)

    def AppendContent(self, content):
        return self.table.AppendContent(content)

class M80SpinBox(QSpinBox):
    """docstring for M50SpinBox"""
    def __init__(self, nowvalue, parent=None):
        super(M80SpinBox, self).__init__(parent)

        self.setRange(0, 80)
        self.setSingleStep(1)
        self.setValue(nowvalue)

    def MGet(self):
        return self.value()

class RemoteSettingTable(QTableWidget):
    """docstring for RemoteSettingTable"""
    def __init__(self, ptConfig, parent=None):
        super(RemoteSettingTable, self).__init__(parent)

        # 获取配置信息
        self.lConfig = ptConfig['go']['remote']

        #  设置表格尺寸
        self.setColumnCount(4)
        self.setRowCount(len(self.lConfig))

        # 设置表格头
        self.setHorizontalHeaderItem(0,QTableWidgetItem(self.tr("遥信点号")))
        self.setHorizontalHeaderItem(1,QTableWidgetItem(self.tr("遥信类型")))
        self.setHorizontalHeaderItem(2,QTableWidgetItem(self.tr("观测点一")))
        self.setHorizontalHeaderItem(3,QTableWidgetItem(self.tr("观测点二")))

        # 根据配置文件设置表格体
        for index in range(len(self.lConfig)):
            self.setItem(index, 0, QTableWidgetItem("%d" %self.lConfig[index]['n']))

            cbw=QComboBox()
            cbw.addItem("遥信关闭")
            cbw.addItem("单点遥信")
            cbw.addItem("双点遥信")
            cbw.setCurrentIndex(self.lConfig[index]['t'])
            self.setCellWidget(index, 1, cbw)
            self.setCellWidget(index, 2, M80SpinBox(self.lConfig[index]['l0']))
            self.setCellWidget(index, 3, M80SpinBox(self.lConfig[index]['l1']))

    def AppendContent(self, content):
        content += "\tremote = ( {\n"
        for index in range(self.rowCount()):
            content += "\t\t\tn = %s\n" %self.item(index, 0).text()
            content += "\t\t\tt = %s\n" %self.cellWidget(index, 1).currentIndex()
            content += "\t\t\tl0 = %d\n" %self.cellWidget(index, 2).MGet()
            content += "\t\t\tl1 = %d\n" %self.cellWidget(index, 3).MGet()
            if index != self.rowCount() - 1:
                content += "\t\t}, {\n"
            else:
                content += "\t\t} )\n"

        return content

class RemoteInfo(QWidget):
    def __init__(self, ptConfig, parent=None):
        super(RemoteInfo,self).__init__(parent)

        self.table = RemoteSettingTable(ptConfig)

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(self.table,0,0)
        mainLayout.setSizeConstraint(QLayout.SetMaximumSize)

    def AppendContent(self, content):
        return self.table.AppendContent(content)


class CtrlSettingTable(QTableWidget):
    """docstring for CtrlSettingTable"""
    def __init__(self, ptConfig, parent=None):
        super(CtrlSettingTable, self).__init__(parent)

        # 获取配置信息
        self.lConfig = ptConfig['go']['ctrl']

        #  设置表格尺寸
        self.setColumnCount(4)
        self.setRowCount(len(self.lConfig))

        # 设置表格头
        self.setHorizontalHeaderItem(0,QTableWidgetItem(self.tr("遥控点号")))
        self.setHorizontalHeaderItem(1,QTableWidgetItem(self.tr("遥控固件号")))
        self.setHorizontalHeaderItem(2,QTableWidgetItem(self.tr("遥控时间")))
        self.setHorizontalHeaderItem(3,QTableWidgetItem(self.tr("软压板")))

        # 根据配置文件设置表格体
        for index in range(len(self.lConfig)):
            self.setItem(index, 0, QTableWidgetItem("%d" %self.lConfig[index]['n']))
            self.setItem(index, 1, QTableWidgetItem("%d" %self.lConfig[index]['l']))
            self.setItem(index, 2, QTableWidgetItem("%d" %self.lConfig[index]['ot']))

            cbw=QComboBox()
            cbw.addItem("退出")
            cbw.addItem("投入")
            cbw.setCurrentIndex(self.lConfig[index]['s'])
            self.setCellWidget(index,3,cbw)

    def AppendContent(self, content):
        content += "\tctrl = ( {\n"
        for index in range(self.rowCount()):
            content += "\t\t\tn = %s\n" %self.item(index, 0).text()
            content += "\t\t\tl = %s\n" %self.item(index, 1).text()
            content += "\t\t\tot = %s\n" %self.item(index, 2).text()
            content += "\t\t\ts = %d\n" %self.cellWidget(index, 3).currentIndex()
            if index != self.rowCount() - 1:
                content += "\t\t}, {\n"
            else:
                content += "\t\t} )\n"

        return content

class CtrlInfo(QWidget):
    def __init__(self, ptConfig, parent=None):
        super(CtrlInfo,self).__init__(parent)

        self.table = CtrlSettingTable(ptConfig)

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(self.table,0,0)
        mainLayout.setSizeConstraint(QLayout.SetMaximumSize)

    def AppendContent(self, content):
        return self.table.AppendContent(content)

class M10000SpinBox(QSpinBox):
    """docstring for M10000SpinBox"""
    def __init__(self, nowvalue, parent=None):
        super(M10000SpinBox, self).__init__(parent)

        self.setRange(0, 10000)
        self.setSingleStep(1)
        self.setValue(nowvalue)

    def MGet(self):
        return self.value()

class M600SpinBox(QSpinBox):
    """docstring for M600SpinBox"""
    def __init__(self, nowvalue, parent=None):
        super(M600SpinBox, self).__init__(parent)

        self.setRange(0, 600)
        self.setSingleStep(1)
        self.setValue(nowvalue)

    def MGet(self):
        return self.value()

class ProtectTable(QTableWidget):
    """docstring for ProtectTable"""
    def __init__(self, ptConfig, parent=None):
        super(ProtectTable, self).__init__(parent)

        # 获取配置信息
        self.lConfig = ptConfig['go']['protect']

        #  设置表格尺寸
        self.setColumnCount(16)
        self.setRowCount(len(self.lConfig))

        # 设置表格头
        self.setHorizontalHeaderItem(0,QTableWidgetItem(self.tr("保护点号")))
        self.setHorizontalHeaderItem(1,QTableWidgetItem(self.tr("一段保护状态")))
        self.setHorizontalHeaderItem(2,QTableWidgetItem(self.tr("一段保护值")))
        self.setHorizontalHeaderItem(3,QTableWidgetItem(self.tr("一段保护时间")))
        self.setHorizontalHeaderItem(4,QTableWidgetItem(self.tr("二段保护状态")))
        self.setHorizontalHeaderItem(5,QTableWidgetItem(self.tr("二段保护值")))
        self.setHorizontalHeaderItem(6,QTableWidgetItem(self.tr("二段保护时间")))
        self.setHorizontalHeaderItem(7,QTableWidgetItem(self.tr("三段保护状态")))
        self.setHorizontalHeaderItem(8,QTableWidgetItem(self.tr("三段保护值")))
        self.setHorizontalHeaderItem(9,QTableWidgetItem(self.tr("三段保护时间")))
        self.setHorizontalHeaderItem(10,QTableWidgetItem(self.tr("重合闸")))
        self.setHorizontalHeaderItem(11,QTableWidgetItem(self.tr("重合时间")))
        self.setHorizontalHeaderItem(12,QTableWidgetItem(self.tr("复归")))
        self.setHorizontalHeaderItem(13,QTableWidgetItem(self.tr("复归时间")))
        self.setHorizontalHeaderItem(14,QTableWidgetItem(self.tr("遥控号")))
        self.setHorizontalHeaderItem(15,QTableWidgetItem(self.tr("遥控状态")))

        # 根据配置文件设置表格体
        for index in range(len(self.lConfig)):
            self.setItem(index, 0, QTableWidgetItem("%d" %self.lConfig[index]['n']))

            cbw1=QComboBox()
            cbw1.addItem("退出")
            cbw1.addItem("告警投入")
            cbw1.addItem("保护投入")
            cbw1.addItem("全投入")
            cbw1.setCurrentIndex(self.lConfig[index]['s1'])
            self.setCellWidget(index,1,cbw1)
            self.setCellWidget(index, 2, M10000SpinBox(self.lConfig[index]['v1']))
            self.setCellWidget(index, 3, M10000SpinBox(self.lConfig[index]['t1']))

            cbw2=QComboBox()
            cbw2.addItem("退出")
            cbw2.addItem("告警投入")
            cbw2.addItem("保护投入")
            cbw2.addItem("全投入")
            cbw2.setCurrentIndex(self.lConfig[index]['s2'])
            self.setCellWidget(index,4,cbw2)
            self.setCellWidget(index, 5, M10000SpinBox(self.lConfig[index]['v2']))
            self.setCellWidget(index, 6, M10000SpinBox(self.lConfig[index]['t2']))

            cbw3=QComboBox()
            cbw3.addItem("退出")
            cbw3.addItem("告警投入")
            cbw3.addItem("保护投入")
            cbw3.addItem("全投入")
            cbw3.setCurrentIndex(self.lConfig[index]['s3'])
            self.setCellWidget(index,7,cbw3)
            self.setCellWidget(index, 8, M10000SpinBox(self.lConfig[index]['v3']))
            self.setCellWidget(index, 9, M10000SpinBox(self.lConfig[index]['t3']))

            cbw4=QComboBox()
            cbw4.addItem("关闭")
            cbw4.addItem("打开")
            cbw4.setCurrentIndex(self.lConfig[index]['sr'])
            self.setCellWidget(index, 10, cbw4)
            self.setCellWidget(index, 11, M10000SpinBox(self.lConfig[index]['tr']))

            cbw5=QComboBox()
            cbw5.addItem("关闭")
            cbw5.addItem("打开")
            cbw5.setCurrentIndex(self.lConfig[index]['sf'])
            self.setCellWidget(index, 12, cbw5)
            self.setCellWidget(index, 13, M600SpinBox(self.lConfig[index]['tf']))

            cbw6=QComboBox()
            cbw6.addItem("遥控一路")
            cbw6.addItem("遥控二路")
            cbw6.addItem("遥控三路")
            cbw6.addItem("遥控四路")
            cbw6.addItem("遥控五路")
            cbw6.addItem("遥控六路")
            cbw6.setCurrentIndex(self.lConfig[index]['c'])
            self.setCellWidget(index,14,cbw6)

            cbw8=QComboBox()
            cbw8.addItem("遥控分")
            cbw8.addItem("遥控合")
            cbw8.setCurrentIndex(self.lConfig[index]['w'])
            self.setCellWidget(index,15,cbw8)

    def AppendContent(self, content):
        content += "\tprotect = ( {\n"
        for index in range(self.rowCount()):
            content += "\t\t\tn = %s\n" %self.item(index, 0).text()
            content += "\t\t\ts1 = %d\n" %self.cellWidget(index, 1).currentIndex()
            content += "\t\t\tv1 = %d\n" %self.cellWidget(index, 2).MGet()
            content += "\t\t\tt1 = %d\n" %self.cellWidget(index, 3).MGet()
            content += "\t\t\ts2 = %d\n" %self.cellWidget(index, 4).currentIndex()
            content += "\t\t\tv2 = %d\n" %self.cellWidget(index, 5).MGet()
            content += "\t\t\tt2 = %d\n" %self.cellWidget(index, 6).MGet()
            content += "\t\t\ts3 = %d\n" %self.cellWidget(index, 7).currentIndex()
            content += "\t\t\tv3 = %d\n" %self.cellWidget(index, 8).MGet()
            content += "\t\t\tt3 = %d\n" %self.cellWidget(index, 9).MGet()
            content += "\t\t\tsr = %d\n" %self.cellWidget(index, 10).currentIndex()
            content += "\t\t\ttr = %d\n" %self.cellWidget(index, 11).MGet()
            content += "\t\t\tsf = %d\n" %self.cellWidget(index, 12).currentIndex()
            content += "\t\t\ttf = %d\n" %self.cellWidget(index, 13).MGet()
            content += "\t\t\tc = %d\n" %self.cellWidget(index, 14).currentIndex()
            content += "\t\t\tw = %d\n" %self.cellWidget(index, 15).currentIndex()
            if index != self.rowCount() - 1:
                content += "\t\t}, {\n"
            else:
                content += "\t\t} )\n"

        return content

class ProtectInfo(QWidget):
    def __init__(self, ptConfig, parent=None):
        super(ProtectInfo,self).__init__(parent)

        self.table = ProtectTable(ptConfig)

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(self.table,0,0)
        mainLayout.setSizeConstraint(QLayout.SetMaximumSize)

    def AppendContent(self, content):
        return self.table.AppendContent(content)


class MiscInfo(QWidget):
    def __init__(self, ptConfig, parent=None):
        super(MiscInfo,self).__init__(parent)

        self.setFont(QFont("微软雅黑",10))

        label1=QLabel(self.tr("遥信去抖(毫秒)"))
        label2=QLabel(self.tr("活化周期(秒)"))
        label3=QLabel(self.tr("活化时间(秒)"))
        label4=QLabel(self.tr("自动活化开关"))
        label5=QLabel(self.tr("终端故障SOE点号"))
        label6=QLabel(self.tr("有压鉴别(一)SOE点号"))
        label7=QLabel(self.tr("有压鉴别(二)SOE点号"))
        label8=QLabel(self.tr("有压鉴别(三)SOE点号"))
        label9=QLabel(self.tr("自动复归SOE点号"))
        label10=QLabel(self.tr("手动复归SOE点号"))
        label11=QLabel(self.tr("远程复归SOE点号"))
        label12=QLabel(self.tr("有压鉴别阈值(伏)"))
        label13=QLabel(self.tr("越限时间(毫秒)"))
        label14=QLabel(self.tr("越限SOE起始号"))
        label15=QLabel(self.tr("软件版本"))

        self.Label1=M10000SpinBox(ptConfig['go']["YaoXin_QuDou"])
        self.Label2=M10000SpinBox(ptConfig['go']["HuoHua_ZhouQi"])
        self.Label3=M10000SpinBox(ptConfig['go']["HuoHua_ShiJian"])
        self.Label4=QComboBox()
        self.Label4.addItem("关闭")
        self.Label4.addItem("打开")
        self.Label4.setCurrentIndex(ptConfig['go']["HuoHua_KaiGuan"])
        self.Label5=M10000SpinBox(ptConfig['go']["SOE_GuZhang"])
        self.Label6=M10000SpinBox(ptConfig['go']["SOE_YouYA_1"])
        self.Label7=M10000SpinBox(ptConfig['go']["SOE_YouYA_2"])
        self.Label8=M10000SpinBox(ptConfig['go']["SOE_YouYA_3"])
        self.Label9=M10000SpinBox(ptConfig['go']["SOE_FuGui_ZiDong"])
        self.Label10=M10000SpinBox(ptConfig['go']["SOE_FuGui_SouDong"])
        self.Label11=M10000SpinBox(ptConfig['go']["SOE_FuGui_Net"])
        self.Label12=M600SpinBox(ptConfig['go']["YouYa_JianBie"])
        self.Label13=M10000SpinBox(ptConfig['go']["YueXian_ShiJian"])
        self.Label14=M10000SpinBox(ptConfig['go']["YueXian_SOE_Start"])
        self.Label15=QLineEdit("V%06.3f" %(ptConfig['go']["Version"]/1000.0))

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(label1,0,0)
        mainLayout.addWidget(label2,1,0)
        mainLayout.addWidget(label3,2,0)
        mainLayout.addWidget(label4,3,0)
        mainLayout.addWidget(label5,4,0)
        mainLayout.addWidget(label6,5,0)
        mainLayout.addWidget(label7,6,0)
        mainLayout.addWidget(label8,7,0)
        mainLayout.addWidget(label9,8,0)
        mainLayout.addWidget(label10,9,0)
        mainLayout.addWidget(label11,10,0)
        mainLayout.addWidget(label12,11,0)
        mainLayout.addWidget(label13,12,0)
        mainLayout.addWidget(label14,13,0)
        mainLayout.addWidget(label15,14,0)

        mainLayout.addWidget(self.Label1,0,1)
        mainLayout.addWidget(self.Label2,1,1)
        mainLayout.addWidget(self.Label3,2,1)
        mainLayout.addWidget(self.Label4,3,1)
        mainLayout.addWidget(self.Label5,4,1)
        mainLayout.addWidget(self.Label6,5,1)
        mainLayout.addWidget(self.Label7,6,1)
        mainLayout.addWidget(self.Label8,7,1)
        mainLayout.addWidget(self.Label9,8,1)
        mainLayout.addWidget(self.Label10,9,1)
        mainLayout.addWidget(self.Label11,10,1)
        mainLayout.addWidget(self.Label12,11,1)
        mainLayout.addWidget(self.Label13,12,1)
        mainLayout.addWidget(self.Label14,13,1)
        mainLayout.addWidget(self.Label15,14,1)

        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

    def AppendContent(self, content):
        content += "\tYaoXin_QuDou = %d\n" %self.Label1.MGet()
        content += "\tHuoHua_ZhouQi = %d\n" %self.Label2.MGet()
        content += "\tHuoHua_ShiJian = %d\n" %self.Label3.MGet()
        content += "\tHuoHua_KaiGuan = %d\n" %self.Label4.currentIndex()
        content += "\tSOE_GuZhang = %d\n" %self.Label5.MGet()
        content += "\tSOE_YouYA_1 = %d\n" %self.Label6.MGet()
        content += "\tSOE_YouYA_2 = %d\n" %self.Label7.MGet()
        content += "\tSOE_YouYA_3 = %d\n" %self.Label8.MGet()
        content += "\tSOE_FuGui_ZiDong = %d\n" %self.Label9.MGet()
        content += "\tSOE_FuGui_SouDong = %d\n" %self.Label10.MGet()
        content += "\tSOE_FuGui_Net = %d\n" %self.Label11.MGet()
        content += "\tYouYa_JianBie = %d\n" %self.Label12.MGet()
        content += "\tYueXian_ShiJian = %d\n" %self.Label13.MGet()
        content += "\tYueXian_SOE_Start = %d\n" %self.Label14.MGet()
        content += "\tVersion = %d\n" %(float(self.Label15.text()[1:])*1000)

        return content

class DebugInfo(QWidget):
    def __init__(self, ptConfig, parent=None):
        super(DebugInfo,self).__init__(parent)

        self.setFont(QFont("微软雅黑",10))

        label1=QLabel(self.tr("卡尔曼滤波开关"))
        label2=QLabel(self.tr("常规滤波开关"))
        label3=QLabel(self.tr("滤波长度(常规滤波)"))
        label4=QLabel(self.tr("高斯滤波开关"))
        label5=QLabel(self.tr("滤波参数(高斯滤波)"))
        label6=QLabel(self.tr("滤波长度(高斯滤波)"))
        label7=QLabel(self.tr("功率修正开关"))
        label8=QLabel(self.tr("功率修正参数"))
        label9=QLabel(self.tr("直流量系数一"))
        label10=QLabel(self.tr("直流量系数二"))


        self.Label1=QComboBox()
        self.Label1.addItem("关闭")
        self.Label1.addItem("打开")
        self.Label1.setCurrentIndex(ptConfig['go']["LvBo_KalMan"])
        self.Label2=QComboBox()
        self.Label2.addItem("关闭")
        self.Label2.addItem("打开")
        self.Label2.setCurrentIndex(ptConfig['go']["LvBo_Normal"])
        self.Label3=M10000SpinBox(ptConfig['go']["ChangDu_Normal"])

        self.Label4=QComboBox()
        self.Label4.addItem("关闭")
        self.Label4.addItem("打开")
        self.Label4.setCurrentIndex(ptConfig['go']["LvBo_Gaussian"])

        self.Label5=M600SpinBox(ptConfig['go']["CanShu_Gaussian"])
        self.Label6=M600SpinBox(ptConfig['go']["ChangDu_Gaussian"])

        self.Label7=QComboBox()
        self.Label7.addItem("关闭")
        self.Label7.addItem("打开")
        self.Label7.setCurrentIndex(ptConfig['go']["XiuZheng_KaiGuan"])

        self.Label8=M600SpinBox(ptConfig['go']["XiuZheng_GongLv"])
        self.Label9=M10000SpinBox(ptConfig['go']["ZhiLiu_CanShu_1"])
        self.Label10=M10000SpinBox(ptConfig['go']["ZhiLiu_CanShu_2"])

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(label1,0,0)
        mainLayout.addWidget(label2,1,0)
        mainLayout.addWidget(label3,2,0)
        mainLayout.addWidget(label4,3,0)
        mainLayout.addWidget(label5,4,0)
        mainLayout.addWidget(label6,5,0)
        mainLayout.addWidget(label7,6,0)
        mainLayout.addWidget(label8,7,0)
        mainLayout.addWidget(label9,8,0)
        mainLayout.addWidget(label10,9,0)

        mainLayout.addWidget(self.Label1,0,1)
        mainLayout.addWidget(self.Label2,1,1)
        mainLayout.addWidget(self.Label3,2,1)
        mainLayout.addWidget(self.Label4,3,1)
        mainLayout.addWidget(self.Label5,4,1)
        mainLayout.addWidget(self.Label6,5,1)
        mainLayout.addWidget(self.Label7,6,1)
        mainLayout.addWidget(self.Label8,7,1)
        mainLayout.addWidget(self.Label9,8,1)
        mainLayout.addWidget(self.Label10,9,1)

        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

    def AppendContent(self, content):
        content += "\tLvBo_KalMan = %d\n" %self.Label1.currentIndex()
        content += "\tLvBo_Normal = %d\n" %self.Label2.currentIndex()
        content += "\tChangDu_Normal = %d\n" %self.Label3.MGet()
        content += "\tLvBo_Gaussian = %d\n" %self.Label4.currentIndex()
        content += "\tCanShu_Gaussian = %d\n" %self.Label5.MGet()
        content += "\tChangDu_Gaussian = %d\n" %self.Label6.MGet()
        content += "\tXiuZheng_KaiGuan = %d\n" %self.Label7.currentIndex()
        content += "\tXiuZheng_GongLv = %d\n" %self.Label8.MGet()
        content += "\tZhiLiu_CanShu_1 = %d\n" %self.Label9.MGet()
        content += "\tZhiLiu_CanShu_2 = %d\n" %self.Label10.MGet()

        return content

class SOETable(QTableWidget):
    """docstring for SOETable"""
    def __init__(self, parent=None):
        super(SOETable, self).__init__(parent)

        #  设置表格尺寸
        self.setColumnCount(3)
        self.setRowCount(50)

        # 设置表格头
        self.setHorizontalHeaderItem(0,QTableWidgetItem(self.tr("遥信点号")))
        self.setHorizontalHeaderItem(1,QTableWidgetItem(self.tr("含义")))
        self.setHorizontalHeaderItem(2,QTableWidgetItem(self.tr("说明")))

        for x in range(12):
            self.setItem(x, 0, QTableWidgetItem("%d" %(6201 + x)))
            self.setItem(x, 1, QTableWidgetItem("线路[%d]故障,合表示瞬时故障,分代表永久故障" %(1 + x)))
            self.setItem(x, 2, QTableWidgetItem(""))
        for x in range(3):
            self.setItem(x+12, 0, QTableWidgetItem("%d" %(6902 + x)))
            self.setItem(x+12, 1, QTableWidgetItem("线路[%d]有压,合表示有压,分代表失压" %(1 + x)))
            self.setItem(x+12, 2, QTableWidgetItem(""))
        for x in range(3):
            self.setItem(x+15, 0, QTableWidgetItem(""))
            self.setItem(x+15, 1, QTableWidgetItem(""))
            self.setItem(x+15, 2, QTableWidgetItem(""))
        for x in range(12):
            ABC = ['A相','B相','C相']
            self.setItem(x+18, 0, QTableWidgetItem("%d" %(6801 + x)))
            self.setItem(x+18, 1, QTableWidgetItem("线路[%d]电流[%s]越限" %((x)//3+1, ABC[(x)%3])))
            self.setItem(x+18, 2, QTableWidgetItem(""))

        self.setItem(30, 0, QTableWidgetItem("6901"))
        self.setItem(30, 1, QTableWidgetItem("设备状态异常,合表示异常发生,分表示异常恢复"))
        self.setItem(30, 2, QTableWidgetItem(""))

        self.setItem(31, 0, QTableWidgetItem("6601"))
        self.setItem(31, 1, QTableWidgetItem("自动复归"))
        self.setItem(31, 2, QTableWidgetItem(""))

        self.setItem(32, 0, QTableWidgetItem("6602"))
        self.setItem(32, 1, QTableWidgetItem("手动复归"))
        self.setItem(32, 2, QTableWidgetItem(""))

        self.setItem(32, 0, QTableWidgetItem("6603"))
        self.setItem(32, 1, QTableWidgetItem("远程复归"))
        self.setItem(32, 2, QTableWidgetItem(""))

        self.setItem(33, 0, QTableWidgetItem("6001-6072"))
        self.setItem(33, 1, QTableWidgetItem("硬件遥信,保留地址域,代表设备硬件遥信"))
        self.setItem(33, 2, QTableWidgetItem(""))

        self.setItem(34, 0, QTableWidgetItem("6073"))
        self.setItem(34, 1, QTableWidgetItem("电池活化状态"))
        self.setItem(34, 2, QTableWidgetItem(""))

        self.setItem(35, 0, QTableWidgetItem("6074"))
        self.setItem(35, 1, QTableWidgetItem("电池欠压告警"))
        self.setItem(35, 2, QTableWidgetItem(""))

        self.setItem(36, 0, QTableWidgetItem("6075"))
        self.setItem(36, 1, QTableWidgetItem("交流电源一,合表示失电,分表示上电"))
        self.setItem(36, 2, QTableWidgetItem(""))

        self.setItem(37, 0, QTableWidgetItem("6076"))
        self.setItem(37, 1, QTableWidgetItem("交流电源二,合表示失电,分表示上电"))
        self.setItem(37, 2, QTableWidgetItem(""))

        self.setItem(38, 0, QTableWidgetItem("6077"))
        self.setItem(38, 1, QTableWidgetItem("遥控就地,分:切除"))
        self.setItem(38, 2, QTableWidgetItem(""))

        self.setItem(39, 0, QTableWidgetItem("6078"))
        self.setItem(39, 1, QTableWidgetItem("电源故障"))
        self.setItem(39, 2, QTableWidgetItem(""))

        self.setItem(40, 0, QTableWidgetItem("6079"))
        self.setItem(40, 1, QTableWidgetItem("遥控远方,分切除"))
        self.setItem(40, 2, QTableWidgetItem(""))


class SOEInfo(QWidget):
    def __init__(self, parent=None):
        super(SOEInfo,self).__init__(parent)

        self.table = SOETable()

        mainLayout=QGridLayout(self)
        mainLayout.addWidget(self.table,0,0)
        mainLayout.setSizeConstraint(QLayout.SetMaximumSize)