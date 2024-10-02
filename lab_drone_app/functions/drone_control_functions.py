import socket
import struct 
import numpy as np 
import io 
from scipy import signal 
from PyQt5.QtCore import QThread, pyqtSignal
import dataclasses 

from pymavlink import mavutil
from pymavlink.quaternion import QuaternionBase
import sys 
import time 
import math 
import numpy as np 
import matplotlib.pyplot as plt 
import pymavlink.dialects.v20.all as dialect



class DroneController(QThread):
    def __init__(self):


    def connect(self):
        # Create the connection
        connection = mavutil.mavlink_connection("/dev/ttyUSB0", baud=57600)



    def create_array(self):
    # def plot_drone_position(self):
    # def send_record_command(self):



# @dataclass 
# class ControllerSettings:
    # self.