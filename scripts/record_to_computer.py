import socket
import struct 
import numpy as np 
import io 
import time
import matplotlib.pyplot as plt 
from scipy import signal 
from pathlib import Path

DATA_PATH = Path('/media/peter/share/Documents/Data/DroneData/hotwire/')
CALIB_FILE = DATA_PATH / 'hw_2_calib_front_facing.csv'

DATA_PATH.mkdir(exist_ok=True, parents = True)


if not CALIB_FILE.exists(): 
    with open(CALIB_FILE, 'w') as calibFile:
        calibFile.write('Voltage Transducer (V), Mean HW Voltage (V), Mean Temperature (C)\n')

#Pi config
PI_ADDRESS = "10.240.2.207"
PORT = 8000

SET_FREQUENCY = False 
SAMPLE_FREQUENCY_DESIRED = 10000
SAMPLE_TIME_DESIRED = 10 #10s recording 
SAMPLE_NUMBER_DESIRED = SAMPLE_TIME_DESIRED*SAMPLE_FREQUENCY_DESIRED #10 second recording 
# CHANNELS_DESIRED = [0,4] #for hotwire 1 
CHANNELS_DESIRED = [1,5] #for hotwire 2
# CHANNELS_DESIRED = [2,6] #for hotwire 3

#This is basically meaningless atm 
DATA_FOLDER = '/home/vki/Documents/Data/server_record_test'


#Functions for reading/writing data
def read_data(connection, dtype = 'float'):
    data_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
    data = np.frombuffer(connection.read(data_len), dtype = dtype)

    return data 

def write_data(connection, data):
    #Create stream object to handle binary data
    stream = io.BytesIO()

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



#Handshake to server for sending regular data
handshake = np.array([0])


#IO stream for handling byte conversion 
stream = io.BytesIO()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    print('[Client] Connecting to DAQ on %s:%s'%(PI_ADDRESS, PORT))

    #Create connection
    clientSocket.connect((PI_ADDRESS, PORT))
    
    #Create a file in memory to pass data between the two 
    connection = clientSocket.makefile('rwb')

    print('[Client] Connected to DAQ')
    
    channels = read_data(connection)
    sampleInfo = read_data(connection)

    if SET_FREQUENCY:
        print('[Client] Setting Desired sample frequency and channels')    
        #Set desired sample frequency
        handshake = np.array([2, SAMPLE_FREQUENCY_DESIRED, SAMPLE_NUMBER_DESIRED], dtype = 'float')
        write_data(connection, handshake)

        #Set the desired channels 
        channelArray =  np.array(CHANNELS_DESIRED, dtype = 'uint8')
        write_data(connection, channelArray)

        #Set the data folder 
        dataFolderArray = bytes(DATA_FOLDER, encoding = 'utf8')
        write_data(connection, dataFolderArray)

        #Read the initial information from connecting 
        channels = read_data(connection)
        sampleInfo = read_data(connection)
    
    sampleFrequency = sampleInfo[0] 
    sampleNumber = sampleInfo[1]
    numChannels = channels.shape[0]

    print('[Client] Streaming data from DAQ - %s Channels - Sample Frequency: %0.2f - Sample Number: %i '%(numChannels, sampleFrequency, sampleNumber))
    
    #Same handshake 
    handshake = np.array([0], dtype = 'float')

    while True:
        transducerVoltage = float(input('Current transducer voltage reading: '))

        #Write the handshake
        write_data(connection, handshake)

        #Read the data from the server
        xArray = read_data(connection)
        dataArray = read_data(connection)

        #Read data again to get most recent
        #Write the handshake
        write_data(connection, handshake)

        #Read the data from the server
   
        print('Reading')
        xArray = read_data(connection)
        dataArray = read_data(connection)
  
        try:
            dataArray = dataArray.reshape(int(sampleNumber),numChannels)
        
        except ValueError: continue 

        #Update the plot 
        meanVoltage = np.mean(dataArray[:,0])
        meanTemperature = (np.mean(dataArray[:,1])-0.4)/(0.0195)

        print('Mean Voltage: %0.2f, Mean Temperature %0.2f'%(meanVoltage, meanTemperature), end = '\n')
       
        with open(CALIB_FILE, 'a') as calibFile:
            calibFile.write('%s, %s, %s\n'%(transducerVoltage,meanVoltage,meanTemperature)) 
        
        
        

