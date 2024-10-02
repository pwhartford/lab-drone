import socket
import struct 
import numpy as np 
import io 
import time
import matplotlib.pyplot as plt 
from scipy import signal 

#Pi config
PI_ADDRESS = "10.240.2.207"
PORT = 8000

#Spectrum settings
VIEW_SPECTRUM = False 
NPERSEG_FACTOR = 4

#Hotwire calibration... this is old and poor, needs to be handled better
CONVERT_VELOCITY = False 

HW_CALIB = np.array([  -45.73898678,   365.82689509, -1052.03748077,  1313.97835161,
        -606.88071301])


SAMPLE_FREQUENCY_DESIRED = 10000
SAMPLE_NUMBER_DESIRED = 100000
CHANNELS_DESIRED = [0,4]

FILENAME = 'testsysctl.txt'



#Functions for reading/writing data
def read_data(connection, dtype = 'float'):
    data_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
    data = np.frombuffer(connection.read(data_len), dtype = dtype)

    return data 

def write_data(stream, connection, data):
   #Tell the client the length of the data (uses stream object to do this)
    stream.write(data)
    connection.write(struct.pack('<L', stream.tell()))
    connection.flush()
    stream.seek(0)

    #Send data as double
    connection.write(stream.read())
    stream.seek(0)
    stream.truncate()
    connection.flush()

#Figure to view data
streamFig, streamAx = plt.subplots()


#Handshake to server for sending regular data
handshake = np.array([1])


#IO stream for handling byte conversion 
stream = io.BytesIO()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    print('[Client] Connecting to DAQ on %s:%s'%(PI_ADDRESS, PORT))

    #Create connection
    clientSocket.connect((PI_ADDRESS, PORT))
    
    #Create a file in memory to pass data between the two 
    connection = clientSocket.makefile('rwb')

    print('[Client] Connected to DAQ')
    

    #Read the initial information from connecting 
    channels = read_data(connection)
    sampleInfo = read_data(connection)
    sampleFrequency = sampleInfo[0] 
    sampleNumber = sampleInfo[1]

    numChannels = channels.shape[0]

    print('[Client] Streaming data from DAQ - %s Channels - Sample Frequency: %0.2f - Sample Number: %i '%(numChannels, sampleFrequency, sampleNumber))

    #Sending a record command
    handshake = np.array([1, SAMPLE_NUMBER_DESIRED], dtype = 'float')
    write_data(stream, connection, handshake)

    fileName = bytes(FILENAME, encoding = 'utf8')
    write_data(stream, connection, fileName)

    ii = 0
    while True:
        handshake = np.array([0], dtype = 'float')

        #Write the handshake
        write_data(stream, connection, handshake)

        #Read the data from the server
        
        xArray = read_data(connection)
        dataArray = read_data(connection)
    
        #Pass if data array is not the right shape 
        if dataArray.shape[0]>1:
            dataArray = dataArray.reshape(int(sampleNumber),numChannels)
            
            if CONVERT_VELOCITY: 
                dataArray = HW_CALIB[0]*dataArray**4 + HW_CALIB[1]*dataArray**3 + HW_CALIB[2]*dataArray**2 + HW_CALIB[3]*dataArray**1 + HW_CALIB[4]

        else: continue 

        





        if ii==0:
            #Plot for a single channel 
            if numChannels==1:
                if VIEW_SPECTRUM:
                    welchFrequency, welchOutput = signal.welch(dataArray[:,0], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                    lines, = streamAx.plot(welchFrequency, welchOutput)

                else:
                    lines, = streamAx.plot(xArray, dataArray)
                
                streamAx.legend('Channel: %i'%channels[0])
           
            #Plottting for multiple channels
            else:
                if VIEW_SPECTRUM:
                    for dataIter in range(numChannels):
                        if dataIter==0:
                            welchFrequency, welchOutput = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                            welchOutput = np.array([welchOutput])
                        else:
                            _, welchOutputNew = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)

                            welchOutput = np.concatenate([welchOutput, [welchOutputNew]], axis =0)

                    lines = streamAx.plot(welchFrequency, welchOutput.T)
               
                #Plot the regular data if not 
                else:
                    lines = streamAx.plot(xArray, dataArray)
                
                legendList = ['Channel %i'%channel for channel in channels]
                streamAx.legend(legendList)

            #Set axes labels for PSD or time series 
            if VIEW_SPECTRUM:
                streamAx.set_ylabel('PSD $[V^2/Hz]$')
                streamAx.set_xlabel('Frequency $[Hz]$')
                streamAx.set_xscale('log')
                streamAx.set_yscale('log')
                streamAx.set_xlim(welchFrequency.min(), welchFrequency.max())
                streamAx.set_ylim(1e-10, 1e-4)
            else:
                streamAx.set_ylabel('Voltage $[V]$')
                streamAx.set_xlabel('Time $[s]$')
                streamAx.set_ylim(0, 3.3)
                streamAx.set_xlim(xArray.min(), xArray.max())

        #Update the plot 
        else:
            if numChannels==1:
                if VIEW_SPECTRUM:
                    welchFrequency, welchOutput = signal.welch(dataArray[:,0], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                    
                    lines.set_data(welchFrequency, welchOutput)
                
                else:
                    lines.set_data(xArray, dataArray)

            else:
                if VIEW_SPECTRUM:
                    for dataIter in range(numChannels):
                        if dataIter==0:
                            welchFrequency, welchOutput = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)
                            welchOutput = np.array([welchOutput])
                        else:
                            _, welchOutputNew = signal.welch(dataArray[:,dataIter], fs = sampleFrequency, nperseg = sampleNumber//NPERSEG_FACTOR)

                            welchOutput = np.concatenate([welchOutput, [welchOutputNew]], axis =0)

                    for plotIter, line in enumerate(lines):
                        line.set_data(welchFrequency, welchOutput[plotIter, :])
                
                else:
                    for plotIter, line in enumerate(lines):
                        line.set_data(xArray, dataArray[:,plotIter])

        #Update the plot 
        plt.pause(0.001)


        ii +=1 
        print('[Client] Number of Data Blocks Read %i'%(ii), end = '\r')


