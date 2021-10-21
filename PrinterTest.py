from PyQt5 import QtChart, QtCore, QtGui, QtPrintSupport, QtWidgets
import sys
import random


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle(self.tr('Chart Printing'))
        self.chart = QtChart.QChart()
        self.chart_view = QtChart.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.buttonPreview = QtWidgets.QPushButton('Preview', self)
        self.buttonPreview.clicked.connect(self.handle_preview)
        self.buttonPrint = QtWidgets.QPushButton('Print', self)
        self.buttonPrint.clicked.connect(self.handle_print)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.chart_view, 0, 0, 1, 2)
        layout.addWidget(self.buttonPreview, 1, 0)
        layout.addWidget(self.buttonPrint, 1, 1)
        self.create_chart()

    def create_chart(self):
        self.chart.setTitle("Chart Print Preview and Print Example")
        for i in range(5):
            series = QtChart.QLineSeries()
            series.setName("Line {}".format(i + 1))
            series.append(0, 0)
            for i in range(1, 10):
                series.append(i, random.randint(1, 9))
            series.append(10, 10)
            self.chart.addSeries(series)
        self.chart.createDefaultAxes()

    def handle_print(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        if dialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            self.handle_paint_request(printer)

    def handle_preview(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handle_paint_request)
        dialog.exec_()

    def handle_paint_request(self, printer):
        painter = QtGui.QPainter(printer)
        painter.setViewport(self.chart_view.rect())
        painter.setWindow(self.chart_view.rect())
        self.chart_view.render(painter)
        painter.end()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
