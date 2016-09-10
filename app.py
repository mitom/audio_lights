import sys
from recorder import *
import web
import signal
import clapper
import config
import colour
from yeelight import *

run = True

def plot():
    xs,ys,cl = calculate()
    if xs == None:
        return
    c.setData(xs, ys)
    saturation = cl['alpha']
    if saturation < 115: saturation = 115
    if saturation > 210: saturation = 210
    c.setBrush(QtGui.QBrush(QtGui.QColor(cl['r'], cl['g'], cl['b'], saturation)))
    uiplot.qwtPlot.replot()


def calculate():
    global c_active
    if SR.newAudio==False or c_active is False: return None, None, None
    if c_active is not config.config['active']:
        if config.config['active'] is False:
            light.update(True)
            return None, None, None
        c_active = config.config['active']
    desired = config.config['sample_size']
    xs,ys=SR.fft(desired=desired, trimBy=config.config['trim'], logScale=False, divBy=config.config['scale'])


    if config.config['clapper']:
        mean = ys.mean()
        claps = clapper.add(mean)
        if (claps == 2): toggle()

    if calc == False: return  None, None, None

    cl = colour.calculate_colour(ys)
    SR.newAudio=False

    if config.config['active']: light.update(cl)

    return xs,ys,cl

def toggle(state=None):
    global calc
    if (state != None): calc = state
    else: calc = not calc

    if (not calc): light.update(True)

def exit(signal, frame):
    global run
    run = False

    if app != None:
        app.exit()

def close():
    print 'exiting...'
    light.update(False)
    light.stop()
    SR.close()
    web.stop()
    sys.exit()

signal.signal(signal.SIGINT, exit)

app = None

if __name__ == "__main__":
    web.start()
    c_active = config.config['active']
    calc = not config.config['clapper']

    SR=SwhRecorder()
    SR.setup()
    SR.continuousStart()

    light = LightController()
    light.start()
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

