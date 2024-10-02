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

HW_CALIB_PATH = FOLDER / 'hw_cal_config_2.csv'
HW_CALIB_PATH_02 = FOLDER / '08_21_hw_cal.csv'

SETRA_CALIB_PATH = FOLDER / 'setra_cal_02.csv'
SETRA_CALIB_PATH_02 = FOLDER / 'setra_cal_03.csv'

setraCalibData = np.genfromtxt(SETRA_CALIB_PATH, delimiter = ',', skip_header=1)

setraVoltage = setraCalibData[:,1]
setraMMH20 = setraCalibData[:,0]
setraPa = setraMMH20*9.81

setraRegression = np.polyfit(setraVoltage, setraPa, 1)

setraCalibData_2 = np.genfromtxt(SETRA_CALIB_PATH_02, delimiter = ',', skip_header=1)

setraVoltage_2 = setraCalibData_2[:,1]
setraMMH20_2 = setraCalibData_2[:,0]
setraPa_2 = setraMMH20_2*9.81

setraRegression_2 = np.polyfit(setraVoltage_2, setraPa_2, 1)


setra_fig, setra_ax = plt.subplots() 

setraRegressionX = np.linspace(setraVoltage.min(), setraVoltage.max(), 100)
setraRegressionY = setraRegressionX*setraRegression[0] + setraRegression[1]

setra_ax.plot(setraRegressionX, setraRegressionY, linestyle = 'dashed', 
              label = r'Regression $P=%0.2f\times V + %0.2f$'%(setraRegression[0], setraRegression[1]))
setra_ax.plot(setraVoltage, setraPa, marker = '.', linestyle = 'none')
setra_ax.legend()
setra_ax.set_xlabel('Voltage $[V]$')
setra_ax.set_ylabel('Pressure $[Pa]$')


#%
hw_calib_array = np.genfromtxt(HW_CALIB_PATH, delimiter = ',')
hw_calib_array_02 = np.genfromtxt(HW_CALIB_PATH_02, delimiter = ',')

#First Calib
hw_voltage_array = hw_calib_array[1:,0]
hw_reading_array = hw_calib_array[1:,1]

hw_reading_array = hw_reading_array*5/1023

hw_pa_array = hw_voltage_array*setraRegression[0] + setraRegression[1]
hw_vel_array = np.sqrt(2*hw_pa_array/rho_air)

hw_xreg, hw_yreg, hw_Ein, hw_Eout, hw_coeffs = learning_regression(hw_reading_array, hw_vel_array, order = 4)
hw_coeffs = np.mean(hw_coeffs, axis = 0)

hw_reg_std =np.std(hw_yreg,axis=1)
epsilon_hw_calib = hw_Eout.mean()+hw_reg_std*1.96

hw_y = np.mean(hw_yreg, 1)


#Second Calib
hw_voltage_array_02 = hw_calib_array_02[1:,0]
hw_reading_array_02 = hw_calib_array_02[1:,1]

hw_reading_array_02 = hw_reading_array_02*5/1023

hw_pa_array_02 = hw_voltage_array_02*setraRegression_2[0] + setraRegression_2[1]
hw_vel_array_02 = np.sqrt(2*hw_pa_array_02/rho_air)

hw_xreg_02, hw_yreg_02, hw_Ein_02, hw_Eout_02, hw_coeffs_02 = learning_regression(hw_reading_array_02, hw_vel_array_02, order = 4)
hw_coeffs_02 = np.mean(hw_coeffs_02, axis = 0)


hw_reg_std_02 =np.std(hw_yreg_02,axis=1)
epsilon_hw_calib_02 = hw_Eout.mean()+hw_reg_std_02*1.96
hw_y_02 = np.mean(hw_yreg_02, 1)

# hw_vel_array[0] = 0

# %
fig, ax = plt.subplots() 



ax.plot(hw_xreg, hw_y, linestyle = 'dashed', color = 'b')
ax.plot(hw_reading_array, hw_vel_array, marker = '*', linestyle = 'none', markersize = 5, color = 'b', label = 'Configuration 1')

ax.fill_between(hw_xreg, hw_y + epsilon_hw_calib, hw_y-epsilon_hw_calib, alpha = 0.3, color = 'b')

ax.plot(hw_xreg_02, hw_y_02, linestyle = 'dashed', color = 'r')
ax.plot(hw_reading_array_02, hw_vel_array_02, marker = '>', linestyle = 'none', markersize = 5, color = 'r', label = 'Configuration 2')

ax.fill_between(hw_xreg_02, hw_y_02 + epsilon_hw_calib_02, hw_y_02-epsilon_hw_calib_02, alpha = 0.3, color = 'r')


#Generate label
hw_legend = '$U='
# hw_legend_02 = '$U='
# for ii in hw_coeffs:

for ii, coeff in enumerate(hw_coeffs):
    if coeff>=0:
        hw_legend+='+%0.2fV'%(coeff)

    else:
        hw_legend+='%0.2fV'%(coeff)

    if (4-ii)>1:
        hw_legend+='^%i'%(4-ii)

hw_legend +='$'
hw_legend = [hw_legend, 'Calibration Data']

ax.set_xlabel('HW Voltage $[V]$')
ax.set_ylabel('Velocity $[m/s]$')
ax.legend(shadow = True)


fig.tight_layout(pad = 2)

