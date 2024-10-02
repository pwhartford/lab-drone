import socket
import struct 
import numpy as np 
import io 
from scipy import signal 
from PyQt5.QtCore import QThread, pyqtSignal




#Spectrum settings
VIEW_SPECTRUM = False 
NPERSEG_FACTOR = 4


SAMPLE_FREQUENCY_DESIRED = 10000
SAMPLE_NUMBER_DESIRED = 1000
CHANNELS_DESIRED = [0,5,1,4]

DATA_FOLDER = '/home/vki/Documents/Data/server_record_test'



class DAQFunctionWrapper(QThread):
    daqSettingsUpdateSignal = pyqtSignal(list, float, int)
    def __init__(self, host, port, plotCanvas):
        super(DAQFunctionWrapper, self).__init__() 

        self.host = host 
        self.port = port
        self.plotCanvas = plotCanvas

        #Default channel list and port
        self.channelListDesired = CHANNELS_DESIRED
        self.sampleFrequencyDesired = SAMPLE_FREQUENCY_DESIRED
        self.sampleNumberDesired = SAMPLE_NUMBER_DESIRED

        #Flags for interfacing 
        self.connected = False
        self.updateSettingsFlag = False

    # Functions for reading/writing data
    def read_data(self, dtype = 'float'):
        data_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
        data = np.frombuffer(self.connection.read(data_len), dtype = dtype)

        return data 

    def write_data(self, data):
        #Create stream object to handle binary data
        stream = io.BytesIO()

        #Tell the DAQ Client the length of the data (uses stream object to do this)
        stream.write(data)
        self.connection.write(struct.pack('<L', stream.tell()))
        self.connection.flush()
        stream.seek(0)

        #Send data as double
        self.connection.write(stream.read())
        stream.seek(0)
        stream.truncate()
        self.connection.flush()

    def connect(self):
        self.start() 

    def disconnect(self):
        self.terminate()

    def run(self):
        #Connnect to the socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as daqClientSocket:
            print('[DAQ Client] Connecting to DAQ on %s:%s'%(self.host, self.port))

            #Create connection
            daqClientSocket.connect((self.host, self.port))
            
            #Create a file in memory to pass data between the two 
            self.connection = daqClientSocket.makefile('rwb')

            print('[DAQ Client] Connected to DAQ')
            
            #Read the intitial frequency and ignore 
            self.read_daq_settings()

            handshake = np.array([0], dtype = 'float')

            ii = 0
            while True:
                if self.updateSettingsFlag:
                    self.update_settings()
                    self.updateSettingsFlag = False 

                    ii = 0
                
                #Write the handshake
                self.write_data(handshake)

                #Read the data from the server
                xArray = self.read_data()
                dataArray = self.read_data()
            
                #Pass if data array is not the right shape 
                if dataArray.shape[0]==1:
                    if int(dataArray[0])==1:
                        print('[DAQ Client] DAQ is recording...', end = '\r')

                    continue 
        
                #Try to reshape the array
                else: 
                    try:
                        dataArray = dataArray.reshape(self.sampleNumber, self.numChannels)
                    
                        # if CONVERT_VELOCITY: 
                        #     dataArray = HW_CALIB[0]*dataArray**4 + HW_CALIB[1]*dataArray**3 + HW_CALIB[2]*dataArray**2 + HW_CALIB[3]*dataArray**1 + HW_CALIB[4]

                    except ValueError: 
                        print('[DAQ Client] Error reshaping array rereading settings')
                        readCommand = np.array([3], dtype = 'float')
                        self.write_data(readCommand)
                        self.read_daq_settings()
                        
                        continue 
                
                #Draw the plot if first iteration (needs to change in future)
                if ii==0:
                    self.draw_initial_plot(xArray, dataArray)
                
                else:
                    self.update_plot(xArray, dataArray)

                ii +=1 
                print('[DAQ Client] Number of Data Blocks Read %i'%(ii), end = '\r')

    def update_plot(self, xArray, dataArray):
        if self.numChannels==1:
            if VIEW_SPECTRUM:
                welchFrequency, welchOutput = signal.welch(dataArray[:,0], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                
                self.lines.set_data(welchFrequency, welchOutput)
            
            else:
                self.lines.set_data(xArray, dataArray)

        else:
            if VIEW_SPECTRUM:
                for dataIter in range(self.numChannels):
                    if dataIter==0:
                        welchFrequency, welchOutput = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                        welchOutput = np.array([welchOutput])
                    else:
                        _, welchOutputNew = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)

                        welchOutput = np.concatenate([welchOutput, [welchOutputNew]], axis =0)

                for plotIter, line in enumerate(self.lines):
                    line.set_data(welchFrequency, welchOutput[plotIter, :])
            
            else:
                for plotIter, line in enumerate(self.lines):
                    line.set_data(xArray, dataArray[:,plotIter])

        #Update the plot 
        self.plotCanvas.canvas.draw() 


    def update_settings(self):
        print('[DAQ Client] Setting Desired sample frequency and channels')    
        
        #Set desired sample frequency
        handshake = np.array([2, self.sampleFrequencyDesired, self.sampleNumberDesired], dtype = 'float')
        
        self.write_data(handshake)

        #Set the desired channels 
        channelArray =  np.array(self.channelListDesired, dtype = 'uint8')
        self.write_data(channelArray)

        #Set the data folder 
        dataFolderArray = bytes(DATA_FOLDER, encoding = 'utf8')
        self.write_data(dataFolderArray)

        self.read_daq_settings()


    def read_daq_settings(self):   
        print('[DAQ Client] Reading updated channel data')

        #Read the initial information from connecting 
        self.channels = self.read_data()
        sampleInfo = self.read_data()
        self.sampleFrequency = sampleInfo[0] 
        self.sampleNumber = int(sampleInfo[1])

        self.numChannels = self.channels.shape[0]

        self.daqSettingsUpdateSignal.emit(list(self.channels), self.sampleFrequency, self.sampleNumber)

        print('[DAQ Client] Streaming data from DAQ - %s Channels - Sample Frequency: %0.2f - Sample Number: %i '%(self.numChannels, self.sampleFrequency, self.sampleNumber))

    def set_daq_settings(self, channelList, sampleFrequency, sampleNumber):
        self.sampleFrequencyDesired = sampleFrequency 
        self.sampleNumberDesired = sampleNumber 
        self.channelListDesired = channelList 

        self.updateSettingsFlag = True 

    def draw_initial_plot(self, xArray, dataArray):
        self.plotCanvas.cla() 
        #Plot for a single channel 
        if self.numChannels==1:
            if VIEW_SPECTRUM:
                welchFrequency, welchOutput = signal.welch(dataArray[:,0], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                self.lines, = self.plotCanvas.canvas.ax.plot(welchFrequency, welchOutput)

            else:
                self.lines, = self.plotCanvas.canvas.ax.plot(xArray, dataArray)
            
    
        #Plottting for multiple channels
        else:
            if VIEW_SPECTRUM:
                #Calculate welch for all channels 
                for dataIter in range(self.numChannels):
                    if dataIter==0:
                        welchFrequency, welchOutput = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                        welchOutput = np.array([welchOutput])
                    else:
                        _, welchOutputNew = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)

                        welchOutput = np.concatenate([welchOutput, [welchOutputNew]], axis =0)

                self.lines = self.plotCanvas.canvas.ax.plot(welchFrequency, welchOutput.T)
        
            #Plot the regular data if no stream
            else:
                self.lines = self.plotCanvas.canvas.ax.plot(xArray, dataArray)
            
 

        #Set axes labels for PSD or time series 
        if VIEW_SPECTRUM:
            self.plotCanvas.canvas.ax.set_ylabel('PSD $[V^2/Hz]$')
            self.plotCanvas.canvas.ax.set_xlabel('Frequency $[Hz]$')
            self.plotCanvas.canvas.ax.set_xscale('log')
            self.plotCanvas.canvas.ax.set_xlim(welchFrequency.min(), welchFrequency.max())
            self.plotCanvas.canvas.ax.set_ylim(1e-10, 1e-4)
        else:
            self.plotCanvas.canvas.ax.set_ylabel('Voltage $[V]$')
            self.plotCanvas.canvas.ax.set_xlabel('Time $[s]$')
            self.plotCanvas.canvas.ax.set_ylim(0, 3.3)
            self.plotCanvas.canvas.ax.set_xlim(xArray.min(), xArray.max())

        legendList = ['Channel %i'%channel for channel in self.channels]
        self.plotCanvas.canvas.ax.legend(legendList, bbox_to_anchor = (1,1))

        #Set tight layout and draw 
        self.plotCanvas.canvas.fig.tight_layout()
        self.plotCanvas.canvas.draw()

        