import serial 
import numpy as np 
from pathlib import Path 
import datetime 

SAVE_PATH = Path('/path/to/folder')
FILENAME = 'filename.csv'
FILE_PATH = SAVE_PATH / FILENAME 

DEVICE = '/dev/ttyUSB0'
BAUD = 115200

#Make the save directory
SAVE_PATH.mkdir(exist_ok=True, parents = True)

#Create a header for the file 
if not FILE_PATH.exists():
    with open(FILE_PATH, 'w'):
        FILE_PATH.write('Timestamp, Wind Speed (m/s), Horizontal Wind Direction (degrees), U Vector (U), V Vector(V), W Vector (W), Temperature (deg C), Relative Humidity (%), Absolute Pressure (hPa), Air Density (kg/m^3), Pitch Angle (deg), Roll Angle (deg), Magnetic Heading Angle (deg)')

with open(FILE_PATH, 'a') as fileWriter:
    with serial.Serial(DEVICE, BAUD) as serialConnection:
        #Returns a numpy array with data organized (according to this: https://www.licor.com/env/support/LI-550/topics/connecting.html#top)
        #[Wind Speed (m/s), Horizontal Wind Direction (degrees), U Vector (U), V Vector(V), W Vector (W), Temperature (deg C), Relative Humidity (%), Absolute Pressure (hPa), Air Density (kg/m^3), Pitch Angle (deg), Roll Angle (deg), Magnetic Heading Angle (deg)]

        #Read the data from the serial port
        data = serialConnection.readline().decode('utf8').split()
        timestamp = datetime.datetime.now() 
        
        #Create a numpy array to store the values 
        dataArray = np.zeros((len(data)//2))
        
        #Split the data into the relevant channels 
        for ii, point in enumerate(data): 
            if ii%2==1:
                dataArray[ii//2] = float(data[ii])

        dataArray = np.concatentate([[timestamp], dataArray])
    
        np.savetxt(FILE_PATH, dataArray)