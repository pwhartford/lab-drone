from serial import Serial 
from pathlib import Path 
import numpy as np 

#SAVE TIME 
N_SAMPLES = 10000
DATA_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

#SAVE DIR 
DATA_DIR = Path('/media/peter/share/Documents/Data/DroneData/HW_Sensor_Cal')

DATA_FILE = DATA_DIR / 'hw_cal_01.csv'

serialConnection = Serial(DATA_PORT, BAUD_RATE)
pressure = float(input('Enter the measured voltage: '))

while True: 

    try:
        data = np.zeros(N_SAMPLES)

        for sample in range(N_SAMPLES):
            data[sample] = serialConnection.readline()
        
        averageADCValue = np.nanmean(data)   

        with open(DATA_FILE, 'a') as file: 
            file.write('%f, %f'%(pressure, averageADCValue))
            file.write('\n')

        print('Saved data avg: %s'%averageADCValue)
        pressure = float(input('Enter the measured voltage: '))

    except: 
        print('Read Failed... retrying collection')
        continue 
    
   

    
