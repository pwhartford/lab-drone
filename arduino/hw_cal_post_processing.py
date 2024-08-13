#%% 
import pickle
from pathlib import Path
import numpy as np 
import matplotlib.pyplot as plt 

from bl_utils import learning_regression, plot_regression_results, plot_bl_profile, plot_log_profile

from pathlib import Path
import matplotlib.cm as cm
import pickle


rho_air = 1.225

FOLDER = Path('/media/peter/share/Documents/Data/DroneData/HW_Sensor_Cal')

HW_CALIB_PATH = FOLDER / 'hw_cal_01.csv'
SETRA_CALIB_PATH = FOLDER / 'SetraCal.csv'

setraCalibData = np.genfromtxt(SETRA_CALIB_PATH, delimiter = ',', skip_header=1)

setraVoltage = setraCalibData[:,0]
setraPa = setraCalibData[:,1]

setraRegression = np.polyfit(setraVoltage, setraPa, 1)

setra_fig, setra_ax = plt.subplots() 

setraRegressionX = np.linspace(setraVoltage.min(), setraVoltage.max(), 100)
setraRegressionY = setraRegressionX*setraRegression[0] + setraRegression[1]

setra_ax.plot(setraRegressionX, setraRegressionY, linestyle = 'dashed', 
              label = r'Regression $P=%0.2f\times V + %0.2f$'%(setraRegression[0], setraRegression[1]))
setra_ax.plot(setraVoltage, setraPa, marker = '.', linestyle = 'none')
setra_ax.legend()
setra_ax.set_xlabel('Voltage $[V]$')
setra_ax.set_ylabel('Pressure $[Pa]$')


#%%
hw_calib_array = np.genfromtxt(HW_CALIB_PATH, delimiter = ',')

#%%
hw_voltage_array = hw_calib_array[:,0]
hw_reading_array = hw_calib_array[:,1]

hw_pa_array = hw_voltage_array*setraRegression[0] + setraRegression[1]
hw_vel_array = np.sqrt(2*hw_pa_array/rho_air)

# %
fig, ax = plt.subplots() 


hw_xreg, hw_yreg, hw_Ein, hw_Eout, hw_coeffs = learning_regression(hw_reading_array, hw_vel_array, order = 4)
hw_coeffs = np.mean(hw_coeffs, axis = 0)

hw_reg_std =np.std(hw_yreg,axis=1)
epsilon_hw_calib = hw_Eout.mean()+hw_reg_std*1.96

hw_y = np.mean(hw_yreg, 1)

# hw_y = hw_coeffs[0]*hw_xreg**4 + hw_coeffs[1]*hw_xreg**3 + hw_coeffs[2]*hw_xreg**2 + hw_coeffs[3]*hw_xreg**1 + hw_coeffs[4]

ax.plot(hw_xreg, hw_y, linestyle = 'dashed')

ax.plot(hw_reading_array, hw_vel_array, marker = '.', linestyle = 'none')
hw_legend = ['$U = %0.3fV^4 %0.3fV^3+%0.3fV^2+%0.3fV+%0.3f$'%(hw_coeffs[0], hw_coeffs[1], hw_coeffs[2], hw_coeffs[3], hw_coeffs[4]), 'Calibration Data']

ax.set_xlabel('ADC Reading $[arb]$')
ax.set_ylabel('Velocity $[m/s]$')
ax.legend(hw_legend)