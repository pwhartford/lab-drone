
# Import mavutil
from pymavlink import mavutil
from pymavlink.quaternion import QuaternionBase
import sys 
import time 
import math 
import numpy as np 
import matplotlib.pyplot as plt 
import pymavlink.dialects.v20.all as dialect

#General settings 
# USB_PORT = '/dev/ttyUSB0'
# USB_PORT = '/dev/ttyACM1'
USB_PORT = 'tcp://:5760'


TAKEOFF_ALTITUDE = 5 #m 
TAKEOFF_WAIT = 5


WAIT_TIME = 10 #seconds - time to wait in 

#Automatically put the drone in guided mode 
SET_GUIDED_MODE = True
RUN_COMMANDS = True
TAKEOFF_VEHICLE = True 
LAND_VEHICLE = True  
SET_ATTITUDE = True


#Arm/Disarm
ARM_VEHICLE = True 
DISARM_VEHICLE = False 

YAW_ANGLE = 180 #degrees - desired yaw (probably 0 for ease of flight)
YAW_RATE = 1 #deg/s

#Irrelevant (offset from vehicle position)
USE_OFFSET_FRAME = False
SET_LOITER = False 

#Grid information 
GRID_SPACING = 5 #m
N_POINTS_X = 2
N_POINTS_Y = 2
N_POINTS_Z = 2 

X_MIN = 0 
Y_MIN = 0
Z_MIN = 10


#Generate grid 
#Calculate maximum
X_MAX = GRID_SPACING*N_POINTS_X + X_MIN
Y_MAX = GRID_SPACING*N_POINTS_Y + Y_MIN
Z_MAX = GRID_SPACING*N_POINTS_Z + Z_MIN

#Calculate arrays of points 
xArray = np.arange(X_MIN, X_MAX, GRID_SPACING)
yArray = np.arange(Y_MIN, Y_MAX, GRID_SPACING)
zArray = -np.arange(Z_MIN, Z_MAX, GRID_SPACING)


#Generate the grid of points to test
for ii, yPoint in enumerate(yArray):
    if ii==0:
        xyPoints = np.concatenate([[xArray], [np.ones(xArray.shape)*yPoint]], axis = 0)
    else:
        xyPoints = np.concatenate([xyPoints, np.concatenate([[xArray], [np.ones(xArray.shape)*yPoint]], axis = 0)], axis = 1)


for ii, height in enumerate(zArray):
    if ii==0:
        TEST_ARRAY = np.concatenate([xyPoints, [np.ones(xyPoints.shape[1])*height]], axis = 0)
    else:
        TEST_ARRAY = np.concatenate([TEST_ARRAY, np.concatenate([xyPoints, [np.ones(xyPoints.shape[1])*height]], axis = 0)], axis = 1)    

#Transpose array (for easy reading)
TEST_ARRAY = TEST_ARRAY.T

#Create figure for plotting 
testFig = plt.figure() 
testAx = plt.axes(projection = '3d')

print('Previewing grid points, will be adjusted by home position')

#Preview Grid 
testAx.plot(TEST_ARRAY[:,0], TEST_ARRAY[:,1], -TEST_ARRAY[:,2], marker = '.', linestyle = 'none', color = 'b')

#Set labels 
testAx.set_xlabel('X Position [m] (North)')
testAx.set_ylabel('Y Position [m] (East)')
testAx.set_zlabel('Altitute [m]')

testAx.set_xlim(X_MIN-GRID_SPACING,  X_MAX+GRID_SPACING)
testAx.set_ylim(Y_MIN-GRID_SPACING, Y_MAX+GRID_SPACING)
testAx.set_zlim(0, Z_MAX+GRID_SPACING)

#Show initial plot
plt.pause(1) 


# This sends relative to current drone position
if USE_OFFSET_FRAME:
    FRAME = mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED

#This sends relative to home position
else:
    #Local NED frame (relative to initial GPS position)
    FRAME = mavutil.mavlink.MAV_FRAME_LOCAL_NED



# Create the connection
# connection = mavutil.mavlink_connection(USB_PORT, baud=57600)
connection = mavutil.mavlink_connection('tcp:127.0.0.1:5762')


#Wait for a heartbeat signal
print('Waiting for heartbeat')
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (connection.target_system, connection.target_component))


#Read home position data
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
    242, #Code for home position message
    1e6, #Sample period (us)
    0, 0, 0, 0, 0)

home_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
print(f"Message interval ACK:  {home_msg}")

#Read local position data
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
    32, #Code for local position message
    1e6, #Sample period (us)
    0, 0, 0, 0, 0)

home_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
print(f"Message interval ACK:  {home_msg}")

#Set the home position to current position
print('Setting home position')
connection.mav.command_long_send(connection.target_system, connection.target_component,
                                        mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0, 1, 0, 0, 0, 0,0,0)

home_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
print(f"Home ACK:  {home_msg}")

homeMessage = connection.recv_match(type='HOME_POSITION', blocking=True, timeout=3).to_dict()
positionMessage = connection.recv_match(type = 'LOCAL_POSITION_NED', blocking = True, timeout = 3).to_dict()


#Offset the test array by the home position in NED frame 
# TEST_ARRAY += np.array([homeMessage['x'], homeMessage['y'], -homeMessage['z']])
# print(TEST_ARRAY)

#Unsure about this...
# TAKEOFF_ALTITUDE-=homeMessage['z']

#Plot the desired points 
testAx.plot(homeMessage['x'], homeMessage['y'], -homeMessage['z'], marker = '.', color = 'g', linestyle = 'none')

#Updated points 
positionLine, = testAx.plot(positionMessage['x'], positionMessage['y'], -positionMessage['z'], color = 'k', marker = '.', linestyle = 'none')
targetLine, = testAx.plot(TEST_ARRAY[0,0], TEST_ARRAY[0,1], -TEST_ARRAY[0,2], color = 'r', marker = '.', linestyle = 'none')

#Labels/legend/limits
testAx.set_xlabel('X Position [m] (North)')
testAx.set_ylabel('Y Position [m] (East)')
testAx.set_zlabel('Altitute [m]')

heightArray = -TEST_ARRAY[:,2]

testAx.set_xlim(TEST_ARRAY[:,0].min()-GRID_SPACING,  TEST_ARRAY[:,0].max()+GRID_SPACING)
testAx.set_ylim(TEST_ARRAY[:,1].min()-GRID_SPACING, TEST_ARRAY[:,1].max()+GRID_SPACING)
testAx.set_zlim(heightArray.min()-GRID_SPACING, heightArray.max()+GRID_SPACING)


testAx.legend(['Setpoints', 'Home Position', 'Current Position', 'Target Position'], bbox_to_anchor = (1,1))


#Draw the initial plot
plt.pause(0.001)


#Arm the vehicle 
if ARM_VEHICLE:
    #Arm the vehicle 
    print('Arming the vehicle')
    connection.mav.command_long_send(connection.target_system, connection.target_component,
                                            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

    arm_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    print(f"Arm ACK:  {arm_msg}")


#This can be done here, but also with the flight controller (preferred)
if SET_GUIDED_MODE:
    mode = 'GUIDED'
    print('Setting guided mode')

    # Check if mode is available
    if mode not in connection.mode_mapping():
        print('Unknown mode : {}'.format(mode))
        print('Try:', list(connection.mode_mapping().keys()))
        sys.exit(1)

    mode_id = connection.mode_mapping()[mode]

    #Send the guided mode command
    connection.mav.set_mode_send(
        connection.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)

    # guided_response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    # print(f"Guided ACK:  {guided_response}")

#Takeoff vehicle 
if TAKEOFF_VEHICLE:
    print('Sending takeoff command')
    connection.mav.command_long_send(connection.target_system, 
                                    connection.target_component,
                                    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 
                                    0,0,0,0,0,0,0, 
                                    TAKEOFF_ALTITUDE)

    takeoff_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    print(f"Takeoff ACK:  {takeoff_msg}")

    print('Waiting for takeoff')
    time.sleep(TAKEOFF_WAIT)



#Send RC override function 
# https://gist.github.com/ES-Alexander/ee1dd479dd728b7cef1bf936f9114e71#file-rc_override_example-py-L101-L105
def send_rc(mav, target, rcin1=65535, rcin2=65535, rcin3=65535, rcin4=65535,
                rcin5=65535, rcin6=65535, rcin7=65535, rcin8=65535,
                rcin9=65535, rcin10=65535, rcin11=65535, rcin12=65535,
                rcin13=65535, rcin14=65535, rcin15=65535, rcin16=65535,
                rcin17=65535, rcin18=65535, *, # keyword-only from here
                pitch=None, roll=None, throttle=None, yaw=None, forward=None,
                lateral=None, camera_pan=None, camera_tilt=None, lights1=None,
                lights2=None, video_switch=None):
        ''' Sets all 18 rc channels as specified.
        Values should be between 1100-1900, or left as 65535 to ignore.
        Can specify values:
            positionally,
            or with rcinX (X=1-18),
            or with default RC Input channel mapping names
              -> see https://ardusub.com/developers/rc-input-and-output.html
        It's possible to mix and match specifier types (although generally
          not recommended). Default channel mapping names override positional
          or rcinX specifiers.
        '''
        rc_channel_values = (
            pitch        or rcin1,
            roll         or rcin2,
            throttle     or rcin3,
            yaw          or rcin4,
            forward      or rcin5,
            lateral      or rcin6,
            camera_pan   or rcin7,
            camera_tilt  or rcin8,
            lights1      or rcin9,
            lights2      or rcin10,
            video_switch or rcin11,
            rcin12, rcin13, rcin14, rcin15, rcin16, rcin17, rcin18
        )


        mav.rc_channels_override_send(
            *target,
            *rc_channel_values
        )


def set_target_attitude(yaw):
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,np.rad2deg(yaw),25, #deg/s
        0,0,0,0,0)





recordFlag = False 

initialTime = time.time() 

if RUN_COMMANDS:
#Send the control message 
    for testPoint in TEST_ARRAY:
        print('Sending control message')

        #Update the target position on the plot
        targetLine.set_xdata(testPoint[0])
        targetLine.set_ydata(testPoint[1])
        targetLine.set_3d_properties(-testPoint[2])
        
        #Create message
        message = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(0, 
                                        connection.target_system,
                                        connection.target_component,
                                        FRAME, 
                                        int(0b110111111000), 
                                        testPoint[0],
                                        testPoint[1], 
                                        testPoint[2],
                                        0,0,0,0,0,0,0,0)

        #Send message
        connection.mav.send(message)

        #Set the target attitude in local NED frame 
        if SET_ATTITUDE:
            #Set 0 deg attitude
            set_target_attitude(0)

        print('Message sent waiting %s seconds'%WAIT_TIME)

        #Wait at setpoint 
        while True:
            print('Waiting at setpoint: %s'%testPoint, end = '\r')            
            try:
                positionMessage = connection.recv_match(type = 'LOCAL_POSITION_NED').to_dict()
         
            except:
                pass 

            # positionVec = np.array([positionMessage['x'], positionMessage['y'], positionMessage['z']])



            #Update the current position 
            positionLine.set_xdata([positionMessage['x']])
            positionLine.set_ydata([positionMessage['y']])
            positionLine.set_3d_properties([-positionMessage['z']])
        
            
            # print('Sending record command')
            # send_rc(connection.mav, (connection.target_system, connection.target_component), rcin12 = 2006)


            plt.pause(0.001)

            #If time to move on, break the loop
            if time.time()-initialTime>=WAIT_TIME:
                initialTime = time.time() 
                break



#Land the vehicle (sometimes very strong landing)
if LAND_VEHICLE:
    print('Sending land command')

    connection.mav.command_long_send(
            connection.target_system, 
            connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 
            0, 0, 0, 0, 0, 0, 0, 0
        )


    # Wait for the acknowledgment
    ack = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')



if SET_LOITER: 
    #Set to controller mode
    mode = 'LOITER'
    print('Setting loiter mode')

    mode_id = connection.mode_mapping()[mode]

    connection.mav.set_mode_send(
        connection.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)

    #Get Acknowledgement
    guided_response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    print(f"Loiter ACK:  {guided_response}")


if DISARM_VEHICLE:
    print('Disarming the vehicle')
    connection.mav.command_long_send(connection.target_system, connection.target_component,
                                            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)

    arm_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    print(f"Arm ACK:  {arm_msg}")