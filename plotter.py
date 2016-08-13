from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as Qwt
import ui_plot
import sys
import realTimeAudio


def plot():
    xs,ys,cl = realTimeAudio.calculate()
    print xs
    #c.setData(data['xs'],data['ys'])

    #c.setBrush(QtGui.QBrush(QtGui.QColor(data['cl']['r'], data['cl']['g'], data['cl']['b'], data['cl']['alpha'])))

    #uiplot.qwtPlot.replot()



app = QtGui.QApplication(sys.argv)

win_plot = ui_plot.QtGui.QMainWindow()
uiplot = ui_plot.Ui_win_plot()
uiplot.setupUi(win_plot)
c = Qwt.QwtPlotCurve()
c.attach(uiplot.qwtPlot)

uiplot.qwtPlot.setAxisScale(uiplot.qwtPlot.yLeft, 0, 1000)

uiplot.timer = QtCore.QTimer()
uiplot.timer.start(1.0)

win_plot.connect(uiplot.timer, QtCore.SIGNAL('timeout()'), plot)

win_plot.show()
code = app.exec_()