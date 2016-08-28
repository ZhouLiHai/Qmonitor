import math, random, sys, socket, struct
import binascii, datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Worker(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.father = parent
        self.poll = parent.GlobalPoll

    def __del__(self):
        self.exiting = True
        self.wait()

    def render(self, connection):
        self.connection = connection
        self.connection.settimeout(1)
        self.connection.send(b'\x68\x04\x07\x00\x00\x00')
        self.start()

    def Terminate(self):
        self.exiting = True

    def run(self):
        while not self.exiting:
            msg = bytes()
            try:
                msg += self.connection.recv(1024*1024)
            except socket.timeout:
                self.emit(SIGNAL("ShowMessage(QString)"), "[总召数据]")
                self.connection.send(b'\x68\x0e\x00\x00\x48\x00\x64\x01\x06\x00\x01\x00\x00\x00\x00\x14')
                continue
            # else:
            #     self.emit(SIGNAL("ShowMessage(QString)"), "检测到网络连接发生错误,连接可能已断开.")
            #     break

            # 判断报文长度
            if len(msg) < 7:
                continue

            while len(msg) > 0:
                # 报文没接收完整
                if msg[1] > len(msg):
                    break;

                data_len = msg[1] + 2
                dealmsg = msg[:data_len]
                msg = msg[data_len:]

                # 格式化报文
                formatstr = ""
                for m in dealmsg:
                    formatstr += "%02X " %m
                # print(formatstr)

                if dealmsg[6] == 21:
                    self.emit(SIGNAL("ShowMessage(QString)"), "[遥测报文]")
                    for i in range(dealmsg[7]):
                        addr = dealmsg[11+i*5+1] + dealmsg[11+i*5+2] * 256
                        data = dealmsg[11+i*5+4] + dealmsg[11+i*5+5] * 256

                        if dealmsg[11+i*5+5] * 256 > 0xFFFF/2:
                            data = (0xFFFF - data) * -1

                        self.emit(SIGNAL("RefAnalog(int, int)"), addr, data)

                if dealmsg[6] == 30:
                    self.emit(SIGNAL("ShowMessage(QString)"), "[SOE报文]")
                    states = ["分","合"]
                    addr = dealmsg[11+1] + dealmsg[11+2] * 256
                    data = dealmsg[11+4]
                    time = dealmsg[11+5] + dealmsg[11+6] * 256
                    soeinfo = "[%04d][%s] %02d年%02d月%02d日 %02d:%02d:%02d %03d" %(int(addr), states[data],int(dealmsg[22]),int(dealmsg[21]),int(dealmsg[20]),int(dealmsg[19]),int(dealmsg[18]),int(time//1000),int(time%1000))

                    self.emit(SIGNAL("AddSoeInfo(QString)"), soeinfo)

                if dealmsg[6] == 31:
                    self.emit(SIGNAL("ShowMessage(QString)"), "[SOE报文]")
                    states = ["不确定","分","合","中间状态"]
                    addr = dealmsg[11+1] + dealmsg[11+2] * 256
                    data = dealmsg[11+4]
                    time = dealmsg[11+5] + dealmsg[11+6] * 256
                    soeinfo = "[%04d][%s] %02d年%02d月%02d日 %02d:%02d:%02d %03d" %(int(addr), states[data],int(dealmsg[22]),int(dealmsg[21]),int(dealmsg[20]),int(dealmsg[19]),int(dealmsg[18]),int(time//1000),int(time%1000))

                    self.emit(SIGNAL("AddSoeInfo(QString)"), soeinfo)

                if dealmsg[6] == 1:
                    self.emit(SIGNAL("ShowMessage(QString)"), "[变位报文]")
                    for i in range(dealmsg[7]):
                        addr = dealmsg[11+i*4+1] + dealmsg[11+i*4+2] * 256
                        data = dealmsg[11+i*4+4]
                        self.emit(SIGNAL("RefRemote(int, int)"), addr, data)

                # if dealmsg[6] == 3:
                #     self.emit(SIGNAL("ShowMessage(QString)"), "[变位报文]")
                #     for i in range(dealmsg[7]):
                #         addr = dealmsg[11+i*4+1] + dealmsg[11+i*4+2] * 256
                #         data = dealmsg[11+i*4+4]
                #         self.emit(SIGNAL("RefRemote(int, int)"), addr, data)

                if dealmsg[6] == 45:
                    self.emit(SIGNAL("ShowMessage(QString)"), "[遥控反校]")
                    if dealmsg[8] == 0x09 and (dealmsg[15] == 0x80 or dealmsg[15] == 0x81):
                        self.emit(SIGNAL("CtrlSelectState(int)"), 1)
                    if dealmsg[8] == 0x09 and (dealmsg[15] == 0x00 or dealmsg[15] == 0x01):
                        self.emit(SIGNAL("CtrlSelectState(int)"), 0)
                    if dealmsg[8] == 0x0a and (dealmsg[15] == 0x80 or dealmsg[15] == 0x81):
                        self.emit(SIGNAL("ctrlProtect()"))

                if dealmsg[6] == 42:
                    value = dealmsg[28] * 256 + dealmsg[27]
                    self.emit(SIGNAL("AddSoeInfo(QString)"), "[故障电流] %5.2f(A)" %(value/100.0))
