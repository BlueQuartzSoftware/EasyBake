# This Python file uses the following encoding: utf-8
#!/usr/bin/env python3
import sys
import os


from PySide2.QtWidgets import QApplication, QWidget, QMainWindow
from PySide2.QtCore import QFile, QIODevice, QObject
from ui_mainwindow import Ui_MainWindow
from mainwindowimpl import MainWindow




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("EasyBake")
    window = MainWindow()
    window.show()
#    window.resize(800,800)
#    app.processEvents()

    sys.exit(app.exec_())

