# To the poor soul who has to debug this... good luck! 
from PyQt6 import QtWidgets

#Import the main window panel and the extra widgets
from gui.panels.main_window import Ui_MainWindow
from gui.extra_widgets import MplWidget

#Dark theme and configurations
import qdarktheme
from pathlib import Path
from configparser import ConfigParser

from functions.daq_stream_functions import DAQFunctionWrapper

CONFIG_PATH = Path(__file__).parent.parent.absolute() / 'config'


#Pi config
# PI_ADDRESS = "10.240.2.207"
PI_ADDRESS = "10.42.0.37"


PORT = 8000

class MainWindow(Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.window = QtWidgets.QMainWindow()
        self.setupUi(self.window)
        
        self.livePlotCanvas = MplWidget(navigationToolbar = True)
        self.livePlotLayout.addWidget(self.livePlotCanvas)     

        #Configuration file and Settings
        self.config_file = CONFIG_PATH / 'default.conf'
        self.auto_load_settings()

        #Functionality for interfacing with daq server 
        self.streamFunctionWrapper = DAQFunctionWrapper(self.ipEdit.text(), 
                                                    self.portSpinBox.value(),
                                                    self.livePlotCanvas)

        self.streamFunctionWrapper.daqSettingsUpdateSignal.connect(self.update_daq_information)



        #Settings bar 
        self.actionLight.triggered.connect(lambda: self.change_theme('light'))
        self.actionDark.triggered.connect(lambda: self.change_theme('dark'))

        # self.actionSave.triggered.connect(lambda: self.save_settings())

        self.loadButton.clicked.connect(self.update_workspace)
        self.recordButton.clicked.connect(self.record)
        self.workspace = Path('/')

        self.connectButton.clicked.connect(self.connect_to_daq)

        for channelBox in self.activeChannelBox.children():
            channelBox.clicked.connect(self.update_daq_settings)
        
        self.sampleFrequencyBox.valueChanged.connect(self.update_daq_settings)
        self.sampleNumberBox.valueChanged.connect(self.update_daq_settings)

    def change_theme(self, theme):
        self.settings['App Settings']['theme'] = theme
        qdarktheme.setup_theme(theme)

        #Change the theme of the plots
        self.livePlotCanvas.change_theme(theme)

    def auto_load_settings(self):
        #Use config parser 
        self.settings = ConfigParser()

        if self.config_file.exists():
            self.settings.read(self.config_file)
        else:
            self.default_settings()
        
        self.set_settings()

    def save_settings(self):
        self.get_settings()
        with open(self.config_file, 'w') as settings_file:
            self.settings.write(settings_file)


    def auto_load_settings(self):
        #Use config parser 
        self.settings = ConfigParser()

        if self.config_file.exists():
            self.settings.read(self.config_file)
        else:
            self.default_settings()
        
        self.set_settings()

    def set_settings(self):
        self.change_theme(self.settings['App Settings']['theme'])

        self.ipEdit.setText(self.settings['Host Settings']['ip'])
        self.portSpinBox.setValue(int(self.settings['Host Settings']['port']))
        self.workspace = Path(self.settings['Record Settings']['record-folder'])

    def get_settings(self):
        #Driver Settings
        # self.settings['Driver Settings']['default-driver'] = self.driverBox.currentText()
        # self.settings['Driver Settings']['default-bins'] = self.binBox.currentText()

        pass 

    def default_settings(self):
        #List of default settings for application
        self.settings['App Settings'] = {}
        self.settings['App Settings']['theme'] = 'light'

        self.settings['Host Settings'] = {} 
        self.settings['Host Settings']['ip'] = PI_ADDRESS
        self.settings['Host Settings']['port'] = '8000'

        #Default Record Settings
        self.settings['Record Settings'] = {}
        self.settings['Record Settings']['record-folder'] = '/'
        self.settings['Record Settings']['record-time'] = '10' 

        self.set_settings()
        self.save_settings()

 
    def connect_to_daq(self):
        if self.connectButton.text()=='Connect':
            self.streamFunctionWrapper.connect() 
            self.connectButton.setText('Disconnect')

        elif self.connectButton.text()=='Disconnect':
            self.streamFunctionWrapper.disconnect()
            self.connectButton.setText('Connect')


    def update_workspace(self):
        self.workspace = Path(QtWidgets.QFileDialog.getExistingDirectory(directory = str(self.workspace), \
                                                      caption = 'Open a Save Folder'))
                                                                              
    def record(self):
        filepath = self.recordNameEdit.text() 
        filepath +='.csv'
        savePath = self.workspace / filepath 
        print('Trying to record to %s'%savePath)

        self.streamFunctionWrapper.savePath = savePath 
        self.streamFunctionWrapper.localSaveFlag = True 

    def update_daq_settings(self):
        channelList = []
        for widget in self.activeChannelBox.children():
            if widget.isChecked():
                channelList.append(int(widget.objectName().split('channelBox')[-1]))
        
        channelList = sorted(channelList)
        

        self.streamFunctionWrapper.set_daq_settings(channelList, self.sampleFrequencyBox.value(), self.sampleNumberBox.value())            


    def update_daq_information(self, channels, sampleFrequency, sampleNumber):
        self.sampleFrequencyBox.setValue(sampleFrequency)
        self.sampleNumberBox.setValue(sampleNumber)

        for widget in self.activeChannelBox.children():
            boxNumber = int(widget.objectName().split('channelBox')[-1])
            if boxNumber in channels:
                widget.setChecked(True)
      
    