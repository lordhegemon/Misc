import sys
import os
import ModuleAgnostic as ma
from platUIProcess import *
import time
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPainter, QMouseEvent, QGuiApplication, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QPersistentModelIndex, QModelIndex, QAbstractTableModel


class PlatRecorder(AddPlat):
    def __init__(self):
        self.foo = 'foo'
        self.main()
        pass

    def main(self):
        print("foo")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = PlatRecorder()
    w.show()
    print('Data Retrieval Time: ', time.perf_counter() - time_start)
    sys.excepthook = except_hook
    sys.exit(app.exec_())
