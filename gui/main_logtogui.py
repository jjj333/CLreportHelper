#!/usr/bin/env python3
# encoding: utf-8

"""
# File       : main_logtogui.py
# Time       : 2023/10/13 9:51
# Author     : author name
# @Software  : PyCharm
# version    : 
# Description: 程序退出也能在gui上显示报错信息的示例
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QEventLoop, QTimer, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from Ui_logtogui import Ui_MainWindow
import sys


def exceptOutConfig(exctype, value, tb):
    print('My Error Information:')
    print('Type:', exctype)
    print('Value:', value)
    print('Traceback:', tb)


class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class printThread(QThread):
    def run(self):
        for i in range(5):
            print(f"打印当前数值为：{i}.")
            self.sleep(1)
        print("End")
        print(1/0)  # 人为地引发一个异常


class ControlBoard(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ControlBoard, self).__init__()
        self.setupUi(self)
        # 下面将输出重定向到textBrowser中
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        self.pushButton.clicked.connect(self.bClicked)

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def bClicked(self):
        """Runs the main function."""
        print('Begin')
        # print(1/0)   #人为地引发一个异常，程序直接退出了，控制台出现了`Unhandled Python exception`错误
        self.printABCD()

    def printABCD(self):
        t = printThread(self)
        t.start()


if __name__ == "__main__":
    sys.excepthook = exceptOutConfig
    app = QApplication(sys.argv)
    win = ControlBoard()
    win.show()
    sys.exit(app.exec_())
