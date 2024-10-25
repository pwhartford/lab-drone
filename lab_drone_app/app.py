### Gui created by Peter Hartford, for interfacing with drone acquisition system
from PyQt6 import QtWidgets, QtGui
import sys 
from pathlib import Path
import os 
from gui.main_window_gui import MainWindow


#Current File Directory - pathlib is great for this
FILE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0,str(FILE_PATH))

#Change directory to current file path
os.chdir(FILE_PATH)


# Icon Path for 
ICON_PATH = Path(__file__).parent.absolute() / 'gui/icons/vki-blue.jpg'

def main(): 
    #Create Application Object
    app = QtWidgets.QApplication(sys.argv)   
    
    #Set extra stuff
    app.setDesktopFileName('python3.11.desktop')
    app.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))
    app.setApplicationName('dopplerlidarcontrol')
    app.setApplicationVersion('0.1')

    #Create window object and set icon 
    mainWindow = MainWindow()
    mainWindow.window.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))

    #Show the main window
    mainWindow.window.show()

    #Close on exit
    sys.exit(app.exec())    


if __name__ == '__main__':
    main()