#!/usr/bin/env python3
# encoding: utf-8

"""
# File       : crh_main.py
# Time       : 2023/10/27 9:28
# Author     : author name
# @Software  : PyCharm
# version    : v1
# Description: 实现协会报告自动虚拟打印成pdf并保存成需要的文件名-GUI版
"""


import sys
import threading
import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget

import crh
from gui.crh_Ui import Ui_MainWindow


class EmittingStr(QtCore.QObject):
    """控制台信息转移到textedit控件上显示"""
    textWritten = QtCore.pyqtSignal(str)  # 定义一个str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class WorkThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.stopped = False  # 添加标志位

    def run(self):
        while not self.stopped:
            print(f"22 {threading.current_thread().getName()} ID: {threading.get_ident()}")
            crh.go_for_launch()
            print("qqqqqqqqqqq")

    def stop(self):
        self.stopped = True
        print(f"33 {threading.current_thread().getName()} ID: {threading.get_ident()}")
        self.finished.emit()


class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainForm, self).__init__()
        self.work = None
        self.setupUi(self)

        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

        self.pushButton_1.clicked.connect(self.start_thread)
        self.pushButton_2.clicked.connect(self.stop_thread)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 32
        newTop = (screen.height() - size.height()) / 4
        self.move(int(newLeft), int(newTop))

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def start_thread(self):
        time.sleep(1)
        self.pushButton_1.setText("         打印中...        ")
        self.pushButton_1.setEnabled(False)
        QApplication.processEvents()
        time.sleep(0.5)
        self.work = self.work_start()

    def stop_thread(self):
        if self.work:
            crh.continue_saving = False
            self.pushButton_1.setEnabled(True)
            self.pushButton_1.setText("开始打印")
            self.work.stop()  # 调用子线程的停止方法
            self.work.wait()  # 等待子线程结束
            self.work.deleteLater()
            QApplication.processEvents()
            self.work = None

    def work_start(self):
        self.work = WorkThread()
        self.work.finished.connect(self.work_finished)  # 连接finished信号
        print(f"11 {threading.current_thread().getName()} ID: {threading.get_ident()}")
        self.work.start()
        return self.work

    def work_finished(self):
        print("子线程已完成任务")
        self.work = None
        self.pushButton_1.setEnabled(True)
        self.pushButton_1.setText("开始打印")


def main():
    app = QApplication(sys.argv)
    m_win = MyMainForm()
    m_win.center()
    m_win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
