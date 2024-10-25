#Matplotlib Settings
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#Use the QT Backend
matplotlib.use('Qt5Agg')

from PyQt6 import QtWidgets

class MplCanvas(Canvas):
    def __init__(self, proj3d = False):
        self.createFig(proj3d)

    def createFig(self, proj3d = False):
        # self.fig = matplotlib.figure.Figure()
        self.fig =plt.figure() 
        if proj3d:
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = self.fig.add_subplot(111)

        #Initialize Canvas Object with figure 
        Canvas.__init__(self, self.fig)
        
        #Set Size Policy 
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        
        #Update Geometry
        Canvas.updateGeometry(self)


# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent = None , navigationToolbar = False, proj3d = False):
        super(QtWidgets.QWidget, self).__init__(parent)
        #Create Plot Canvas 
        self.canvas = MplCanvas(proj3d)                  # Create canvas object
        
        #Box Layout For Plotting 
        self.vbl = QtWidgets.QVBoxLayout()      # Set box for plotting
        self.vbl.addWidget(self.canvas)
       
        #Set Layout, resize, and move 
        self.setLayout(self.vbl)
    
        #Navigation toolbar
        if navigationToolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.vbl.addWidget(self.toolbar)
        
        
    def toggle_toolbar(self,trigger):
        if trigger =='off':
            self.vbl.removeWidget(self.toolbar)
        
        if trigger == 'on':
            if not hasattr(self,'toolbar'):
                self.toolbar = NavigationToolbar(self.canvas, self)
            
            self.vbl.addWidget(self.toolbar)

    def change_theme(self, theme):
        self.theme = theme 

        #Use the colors from pyqtdarktheme
        if self.theme=='light':
            background_color = '#F8F9FA'
            axis_color = '#202124'
        else: 
            background_color = '#202124'
            axis_color = '#F8F9FA'

        #Set the figure and axis face colors
        self.canvas.fig.patch.set_facecolor(background_color)
        self.canvas.ax.patch.set_facecolor(background_color)

        #Set the edges of the axis
        for spines in self.canvas.ax.spines:
            self.canvas.ax.spines[spines].set_color(axis_color)

        #Set the labels
        self.canvas.ax.tick_params('both', colors = axis_color)
        self.canvas.ax.xaxis.label.set_color(axis_color)
        self.canvas.ax.yaxis.label.set_color(axis_color)
    

        #Do the same if there's a twin axies
        if hasattr(self, 'ax2'):
            self.ax2.patch.set_facecolor(background_color)
            self.ax2.patch.set_edgecolor(axis_color)

            for spines in self.ax2.spines:
                self.ax2.spines[spines].set_edgecolor(axis_color)

            self.ax2.tick_params('both', colors = axis_color)
            self.ax2.xaxis.label.set_color(axis_color)
            self.ax2.yaxis.label.set_color(axis_color)

        #Draw the canvas
        self.canvas.draw()

    def cla(self):
        self.canvas.ax.clear() 

        self.change_theme(self.theme)

        self.canvas.draw()

    def clf(self):
        self.canvas.fig.clf()
        self.canvas.ax = plt.axes() 
        
        self.change_theme(self.theme)
        self.canvas.draw()
        
    def twiny(self):
        self.ax2 = self.canvas.ax.twiny() 
        return self.ax2