from serial import Serial 
from pathlib import Path 
import numpy as np 
from time import time 
import matplotlib.pyplot as plt 
import multiprocessing

import matplotlib.animation as animation

#SAVE TIME 
N_SAMPLES = 20000
SAMPLE_FREQUENCY = 100 #Hz 
N_BATCHES = 10 #Number of times to do this recording
DATA_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
# OFFSET = 200

TIME_VIEW = 10 #s

INT_TO_V = 5/1023

#Temperature - Microchip MCP9701AT 
TC = 19.5/1e3 #V/C #Temperature Coefficient
V0C = 400/1e3 #V - Voltage at 0C 

#SAVE DIR 
DATA_DIR = Path('/media/peter/share/Documents/Data/DroneData/HW_Sensor_Cal')

DATA_FILE = DATA_DIR / '08_21_directionality_pitch.csv'

serialConnection = Serial(DATA_PORT, BAUD_RATE, timeout = 5)
# pressure = float(input('Enter the measured angle: '))
# pressure = float(input('Enter the measured voltage: '))

timeArray = np.linspace(0, TIME_VIEW, TIME_VIEW*SAMPLE_FREQUENCY)

dataArray = np.zeros((timeArray.shape[0],4))

dataArray[:,:] = 'nan'

print(timeArray.shape)
print(dataArray.shape)

#Plotting 
data_fig = plt.figure() 

data_ax = data_fig.subplots(2,1)

hwPlot, = data_ax[0].plot(timeArray, dataArray[:,0], color = 'b')
hwPlot2, = data_ax[0].plot(timeArray, dataArray[:,2], color = 'r')

tempPlot, = data_ax[1].plot(timeArray, dataArray[:,1], color = 'b')
tempPlot2, = data_ax[1].plot(timeArray, dataArray[:,3], color = 'r')

# hwPlot, = data_ax[0].plot(timeArray, dataArray)

data_ax[0].set_ylim(1, 3)
data_ax[1].set_ylim(15, 30)
data_ax[0].set_xlim(0, TIME_VIEW)
data_ax[1].set_xlim(0,   TIME_VIEW)

data_fig.canvas.draw()



while True: 
    try:
        # print(serialConnection.readline())
        ii = 0
        # data = np.zeros((N_SAMPLES))

        initialTime = time() 
        # serialConnection.flush() 
        data = 0
        while ii<N_SAMPLES:
            # serialConnection.flushInput() 
            if time()-initialTime >=1/SAMPLE_FREQUENCY:
                try:
                    # serialConnection.flushInput() 

                    # buffer += serialConnection.read(serialConnection.inWaiting())
                    # if '\n' in buffer:
                    #     last_received, buffer = buffer.split('\n')[-2:]
                    serialConnection.write(b'0')
                    # data = int(serialConnection.readline())*INT_TO_V


                    data = serialConnection.readline().decode('utf-8').split(',')
                    data = np.array([int(data[0]), int(data[1]), int(data[2]), int(data[3])])*INT_TO_V

                    #Convert to temp
                    data[1] = (data[1]-V0C)/TC
                    data[3] = (data[3]-V0C)/TC

                    # print('%0.3f V'%data)
                    #                 
                #Set Data to nan if reading fails 
                except ValueError:
                    data = np.array(['nan', 'nan', 'nan', 'nan'])
                    # data[ii] = 'nan'

                    # data = 'nan'
                
                except IndexError:
                    data = np.array(['nan', 'nan', 'nan', 'nan'])

                    # data = 'nan'

                dataArray=np.roll(dataArray,-1, axis = 0)
                dataArray[0,:] = data 
                              
                initialTime = time()
                # ii+=1           
                
                # print(data)
                hwPlot.set_ydata(dataArray[:,0])
                hwPlot2.set_ydata(dataArray[:,2])
                # print(dataArray[:,0])

                tempPlot.set_ydata(dataArray[:,1])
                tempPlot2.set_ydata(dataArray[:,3])


                # hwPlot.set_ydata(dataArray)
                data_fig.canvas.draw()

                plt.pause(0.1/SAMPLE_FREQUENCY)
                
                # print('Read Sample %s of %s'%(ii, N_SAMPLES), end = '\r')
        
        # #Set data to nan abov expected value
        # data[np.where(data>1023)] = 'nan'
        # # print(data)
        # averageADCValue = np.nanmean(data)   

        # with open(DATA_FILE, 'a') as file: 
        #     file.write('%f, %f'%(pressure, averageADCValue))
        #     file.write('\n')

        # print('\n Saved data avg: %0.2f'%averageADCValue)
        # pressure = float(input('Enter the measured voltage: '))

    except KeyboardInterrupt:
        print('Stopping Acquisition')
        break 

    # except: 
    #     print('Read Failed... retrying collection')
    #     continue 

