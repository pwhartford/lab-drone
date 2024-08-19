from serial import Serial 
from pathlib import Path 
import numpy as np 
from time import time 


#SAVE TIME 
N_SAMPLES = 1000
DATA_PORT = '/dev/ttyACM1'
BAUD_RATE = 57600

#SAVE DIR 
DATA_DIR = Path('/media/peter/share/Documents/Data/DroneData/HW_Sensor_Cal')

DATA_FILE = DATA_DIR / 'hw_cal_02.csv'

serialConnection = Serial(DATA_PORT, BAUD_RATE)
pressure = float(input('Enter the measured voltage: '))


while True: 
    try:
        # print(serialConnection.readline())
        initialTime = time() 
        array = np.frombuffer(serialConnection.readline(N_SAMPLES), dtype = 'uint8')
        # print('Sample Frequency %0.2f Hz'%(1/(time()-intitialTime)), end = '\r')
        print('Array Size: %s'%array.shape[0])
        
        #Write handshake
        if array.shape[0]<N_SAMPLES:
            continue 
        
        print('Sample Frequency: %s'%(N_SAMPLES/(time()-initialTime)))

        averageADCValue = np.mean(array)   

        with open(DATA_FILE, 'a') as file: 
            file.write('%f, %f'%(pressure, averageADCValue))
            file.write('\n')

        print('Saved data avg: %s'%averageADCValue)
        pressure = float(input('Enter the measured voltage: '))

    except KeyboardInterrupt:
        print('Stopping Acquisition')
        break 

    # except: 
    #     print('Read Failed... retrying collection')
    #     continue 
    
   

    
