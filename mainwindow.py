# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!
import glob
import hashlib
import threading
from multiprocessing import Queue

import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
import Client

chunk_size = 1024



class interfacer (threading.Thread):

    def __init__(self, ui):
        threading.Thread.__init__(self)
        self.ui = ui

    def run(self):
        while True:
            #TODO: dosyalistesi, mesaj falan diye ayikla
            print("interfacequeue bekleniyor")
            s = Client.interfaceQueue.get()
            print("String = " + s)
            fList = s.split(":")
            for x in fList:
                self.ui.listWidget.addItem(x.split(",")[0])



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(912, 674)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(60, 130, 63, 20))
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(190, 100, 104, 70))
        self.textEdit.setObjectName("textEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(60, 220, 63, 20))
        self.label_2.setObjectName("label_2")
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(190, 200, 104, 70))
        self.textEdit_2.setObjectName("textEdit_2")
        self.textEdit_2.setText("1")
        self.textEdit_3 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_3.setGeometry(QtCore.QRect(460, 30, 281, 51))
        self.textEdit_3.setObjectName("textEdit_3")
        self.connect = QtWidgets.QPushButton(self.centralwidget)
        self.connect.setGeometry(QtCore.QRect(220, 300, 84, 28))
        self.connect.setObjectName("connect")
        self.connect.clicked.connect(self.on_click)
        self.search = QtWidgets.QPushButton(self.centralwidget)
        self.search.setGeometry(QtCore.QRect(780, 40, 84, 28))
        self.search.setObjectName("search")
        self.search.clicked.connect(self.search_file)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(490, 160, 256, 251))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemDoubleClicked.connect(Client.findFilemd5)
        self.listWidget.itemDoubleClicked.connect(create_meta)
        self.textEdit.raise_()
        self.label.raise_()
        self.textEdit.raise_()
        self.label_2.raise_()
        self.textEdit_2.raise_()
        self.textEdit_3.raise_()
        self.connect.raise_()
        self.search.raise_()
        self.listWidget.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 912, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def on_click(self):
        ip = self.textEdit.toPlainText()
        port = self.textEdit_2.toPlainText()
        port = int(port)
        print(ip, port)
        Client.get_cList(ip, port)

    def search_file(self):
        fname = self.textEdit_3.toPlainText()
        print(fname)
        Client.findFile(fname)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.connect.setText(_translate("MainWindow", "PushButton"))

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_fileList(path):

    #TODO : db'ye yazilacak
    #TODO: splash'e eklenecek
    os.chdir(sys.path[0])
    with open('files.txt', 'w') as f:
        os.chdir(sys.path[0] +"/shared")
        for file in glob.glob("*.*"):
            filemd5 = md5(file)
            f.write(file + ":" +  str(filemd5) + ":" + str(os.stat(file).st_size) + "\n")
            print("File - md5 - size:" + str(filemd5) + file + str(os.stat(file).st_size))
        f.close()

def create_meta(item):
    os.makedirs(os.path.dirname(sys.path[0] + "/tmp/meta.txt"), exist_ok=True)
    os.chdir(sys.path[0] + "/tmp")
    fmd5 = Client.files[item.text()][0]
    fsize = Client.files[item.text()][1]
    fname = item.text()
    with open('meta.txt', 'a') as f:
        os.chdir(sys.path[0] +"/tmp")
        chunkstr = ""
        for i in range(0, int(int(fsize) / chunk_size)):
            chunkstr = chunkstr + str(i) + "/"
        f.write(fmd5 + ":" +  fname + ":" + chunkstr)

        print("File - md5 - size:" + str(fmd5) + fname + fsize)
        f.close()
    with open(fmd5 +".tmp", "wb") as out:
        out.truncate(int(fsize))

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    create_fileList("aaa")
    ct = Client.connectionThread()
    ct.start()
    interfaceThread = interfacer(ui)
    interfaceThread.start()
    sys.exit(app.exec_())

