import sys
from recorder import *
import web
import signal
import clapper
import config
import colour

run = True
calc = True

def plot():
    xs,ys,cl = calculate()
    if xs == None:
        return
    c.setData(xs, ys)

    c.setBrush(QtGui.QBrush(QtGui.QColor(cl['r'], cl['g'], cl['b'], cl['alpha'])))
    uiplot.qwtPlot.replot()


def calculate():
    if SR.newAudio==False: return None, None, None
    desired = config.config['sample_size']
    xs,ys=SR.fft(desired=desired)

    #print r,g,b,alpha
    #print ys.max(), ys.ptp(), ys.sum(), ys.mean()

    mean = ys.mean()

    claps = clapper.add(mean)
    if (claps == 2): toggle()

    if calc == False: return  None, None, None

    cl = colour.calculate_colour(ys)
    SR.newAudio=False

    return xs,ys,cl

def toggle(state=None):
    global calc
    if (state != None): calc = state
    else: calc = not calc

def exit(signal, frame):
    global run
    run = False

    if app != None:
        app.exit()

def close():
    print 'exiting...'
    SR.close()
    web.stop()
    sys.exit()

signal.signal(signal.SIGINT, exit)

app = None

if __name__ == "__main__":
    web.start()

    SR=SwhRecorder()
    SR.setup()
    SR.continuousStart()


    ### DISPLAY WINDOWS
    if '-p' in sys.argv:
        from PyQt4 import QtCore, QtGui
        import PyQt4.Qwt5 as Qwt
        import ui_plot

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
    else:
        while run:
            calculate()
    close()

