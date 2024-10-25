#%% Imports and data

import matplotlib.pyplot as plt 
import numpy as np 
from pathlib import Path 
from bl_utils import learning_regression, plot_regression_results, plot_bl_profile, plot_log_profile

import plotly.express as px
import plotly.graph_objects as go
 
RHO_AIR = 1.225
HW_DATA_DIR = Path('/media/peter/share/Documents/Data/DroneData/hotwire/hw_2_cal_forward_facing')
# HW_DATA_DIR = Path('D:/Documents/Data/DroneData/hotwire/hw_2_cal_forward_facing')

fileList = [filePath for filePath in HW_DATA_DIR.glob('*.csv')]

validyneFig, validyneAx = plt.subplots() 

VAL_CALIB_PATH = Path('/media/peter/share/Documents/Data/DroneData/hotwire/valCalib1010.csv')
# VAL_CALIB_PATH = Path('D:/Documents/Data/DroneData/hotwire/valCalib1010.csv')


valCalibData = np.genfromtxt(VAL_CALIB_PATH, skip_header= 1, delimiter = ',')

valCalibVoltage = valCalibData[:,1]
valCalibPa = valCalibData[:,0]*9.81


validyneRegression = np.polyfit(valCalibVoltage, valCalibPa, 1)
validyneRegressionPoints = np.polyval(validyneRegression, valCalibVoltage)

validyneAx.plot(valCalibVoltage, validyneRegressionPoints, linestyle = 'dashed', color = 'r')
validyneAx.plot(valCalibVoltage, valCalibPa, linestyle = 'none', marker = '.', color = 'b')
validyneAx.set_xlabel('Voltage $[V]$')
validyneAx.set_ylabel('Pressure $[Pa]$')

#% Plotly test
plotlyFig = go.FigureWidget()

plotlyFig.update_layout(
    xaxis=dict(
        showline=True,
        showgrid=True,
        showticklabels=True,
        zeroline = False,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),
    yaxis=dict(
        showgrid=True,
        zeroline=False,
        showline=True,
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),
    autosize=True,
    showlegend=False,
    plot_bgcolor='white'
)


plotlyFig.add_trace(go.Scatter(x=valCalibVoltage, y=validyneRegressionPoints, 
                    mode = 'lines', line=dict(color='firebrick', width=2,
                    dash='dash')
                    ))

plotlyFig.add_trace(go.Scatter(x=valCalibVoltage, y=valCalibPa, 
                    mode = 'markers', marker=dict(color = 'royalblue')
                    ))

plotlyFig.update_layout(title='Validyne Regression',
                   xaxis_title=r'Validyne Voltage [V]',
                   yaxis_title=r'Pressure [Pa]')
plotlyFig.show()


#%% 

#Load hotwire data
valVoltageArray = np.zeros((len(fileList)))
hwVoltageArray = np.zeros((len(fileList)))
hwTempArray = np.zeros((len(fileList)))



for ii, filePath in enumerate(fileList): 
    valVoltageArray[ii] = float(filePath.name.split('.csv')[0])
    hwData = np.genfromtxt(filePath, delimiter = ',', skip_header=1)

    hwVoltageArray[ii] = hwData[:,1].mean()
    hwTempArray[ii] = (hwData[:,2].mean()-0.4)/0.0195


#%%
cal_fig, cal_ax  = plt.subplots() 

valPaArray = np.polyval(validyneRegression, valVoltageArray)
valVelArray = np.sqrt(2*valPaArray/RHO_AIR)
valVelArray[0] = 0
# valVelArray[1] = 0

hw_xreg, hw_yreg, hw_Ein, hw_Eout, hw_coeffs = learning_regression(hwVoltageArray, valVelArray, order = 3)
hw_coeffs = np.nanmean(hw_coeffs, axis = 0)
hw_reg_std = np.nanstd(hw_yreg,axis=1)
epsilon_hw_calib = hw_reg_std*1.96

hw_y = np.nanmean(hw_yreg, 1)

cal_ax.plot(hw_xreg, hw_y, linestyle = 'dashed', color = 'r')
cal_ax.fill_between(hw_xreg, hw_y + epsilon_hw_calib, hw_y-epsilon_hw_calib, alpha = 0.3, color = 'r')

cal_ax.set_xlabel('Hotwire Voltage [V]')
cal_ax.set_ylabel('Velocity [m/s]')
cal_ax.plot(hwVoltageArray, valVelArray, linestyle = 'none', marker = '.', color = 'k')

print(hwVoltageArray[np.where(valVoltageArray==0.065)])
print(valVelArray[np.where(valVoltageArray==0.065)])

#Plotly
hwCalPlotly = go.FigureWidget()

hwCalPlotly.update_layout(
    xaxis=dict(
        showline=True,
        showgrid=True,
        showticklabels=True,
        zeroline = False,
        linecolor = 'black',
        # linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),
    yaxis=dict(
        showgrid=True,
        zeroline=False,
        showline=True,
        showticklabels=True,
        linecolor = 'black',
        # linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),
    autosize=True,
    showlegend=False,
    plot_bgcolor='white'
)

hwCalPlotly.add_trace(go.Scatter(x=hw_xreg, y=hw_y, 
                    mode = 'lines', line=dict(color='firebrick', width=1,
                    dash='dash')
                    ))
hwCalPlotly.add_trace(go.Scatter(x=hw_xreg, y=hw_y-epsilon_hw_calib, 
                    mode = 'lines',line=dict(color='firebrick', width=2),
                            line_color="rgba(0,0,0,0)",
                    ))

hwCalPlotly.add_trace(
    go.Scatter(
        x=hw_xreg,
        y=hw_y+epsilon_hw_calib,
        fill="tonexty",
        mode="lines",
        # line_color="firebrick",
        line_color="rgba(0,0,0,0)",
        fillcolor='rgba(178, 34, 34, 0.1)'

    )
)

hwCalPlotly.add_trace(go.Scatter(x=hwVoltageArray, y=valVelArray, 
                    mode = 'markers', marker = dict(size = 2, color = 'black', line=dict(color='black', width=1),
                    )
                    ))



hwCalPlotly.update_layout(title='Hotwire Regression',
                   xaxis_title=r'Hotwire Voltage [V]',
                   yaxis_title=r'Velocity [m/s]')
#%% 3D Cal Ax 
cal_fig_3d = plt.figure() 
cal_ax_3d = plt.axes(projection = '3d')
cal_ax_3d.plot(hwVoltageArray, hwTempArray, valVelArray, marker = '.', linestyle = 'none')
