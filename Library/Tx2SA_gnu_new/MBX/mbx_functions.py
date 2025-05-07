#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
#
# Copyright 2018 MILLIWAVE SILICON SOLUTIONS, inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# Author: Ryu Woon Jung (Leon) ROBOTIS
# Author: Jeanmarc Laurent Milliwave Silicon Solutions
#
# *********     MILLIBOX FUNCTIONS      *********
#   Gimbal registers
#   Gimbal movement control
#   Equipment selection and measurement
#   Sweep functions
#

# IMPORTS
from __future__ import division                             # division compatibility Python 2.7 and Python 3.6+
import os
import sys
import csv
import time
import six

from mbx_realtimeplot import *
import numpy as np
import matplotlib.pyplot as plt
import mbx_instrument as equip
import dynamixel_functions as dynamixel                     # Uses Dynamixel SDK library

if sys.platform == "win32":                                 # if we run windows, we can use getch from OS
    from msvcrt import getch, kbhit
else:                                                       # but if we use MACos or Linux we need to create getch()
    def getch():
        x = six.moves.input()
        if len(x) > 1:
            x = chr(0)
            print("too long")
        elif len(x) == 0:
            x = chr(13)  # enter
            print("enter")
        return x

    def kbhit():
        return False


# Register set for MX64AT
# EEPROM SPACE               ADDRESS                       SIZE     R/W    DEFAULT    DESCRIPTION
ADD_MODEL_NUMBER                 = 0                           # 	2   R      311        Model Number for MX64AT(2.0)
ADD_MODEL                        = 2                           #    4   R      -          Model Information
ADD_FW_VER                       = 6                           #    1   R      -          Firmware Version  should stay 41
ADD_MOTOR_ID                     = 7                           #    1 	RW     1          ID 	DYNAMIXEL ID set H to 1 V to 2
ADD_BAUD_RATE                    = 8                           #    1   RW     1          Communication Baud Rate 	 SET to 3 -> 1Mbps
ADD_RETURN_TIME                  = 9                           #    1   RW     250        Return Delay Time
ADD_DRIVE_MODE                   = 10                          #    1   RW     0          Drive Mode
ADD_OPERATING_MODE               = 11                          #    1   RW     3          Operating Mode
ADD_SEC_ID                       = 12                          #    1   RW     255        Secondary(Shadow) ID
ADD_PROTOCOL                     = 13                          #    1   RW     2          Protocol Version
ADD_HOME_OFFSET                  = 20                          #    4   RW     0          Homing Offset
ADD_MOVE_THRESHOLD               = 24                          #    4   RW     10         Velocity Threshold for Movement Detection
ADD_TEMP_LIMIT                   = 31                          #    1   RW     80         Temperature Limit in degree C
ADD_VOLT_MAX_LIMIT               = 32                          #    2 	RW     160        Maximum Input Voltage Limit
ADD_VOLT_MIN_LIMIT               = 34                          #    2 	RW     95         Minimum Input Voltage Limit
ADD_PWM_LIMIT                    = 36                          #    2 	RW     885        Maximum PWM Limit
ADD_MAX_CURRENT                  = 38                          #    2 	RW     1941       Maximum Current Limit
ADD_MAX_ACCEL                    = 40                          #    4 	RW     32767      Maximum Acceleration Limit
ADD_MAX_VELOCITY                 = 44                          #    4 	RW     435        Maximum Velocity Limit
ADD_MAX_POS                      = 48                          #    4 	RW     4095       Maximum Position Limit
ADD_MIN_POS                      = 52                          #    4 	RW     0          Minimum Position Limit
ADD_ERROR_INFO                   = 63                          #    1 	RW     52         Shutdown Error Information

# RAM  SPACE                 ADDRESS                       SIZE     R/W    DEFAULT    DESCRIPTION
ADD_TORQUE_ENABLE                = 64                          #    1 	RW     0          Motor Torque On/Off
ADD_LED                          = 65                          #    1 	RW     0          Status LED On/Off
ADD_STATUS                       = 68                          #    1 	RW     2          Select Types of Status Return
ADD_REG_WRITE_FLAG               = 69                          #    1 	R      0          REG_WRITE Instruction Flag
ADD_HW_ERROR                     = 70                          #    1 	R      0          Hardware Error Status
ADD_VEL_I_GAIN                   = 76                          #    2 	RW     1920       I Gain of Velocity
ADD_VEL_P_GAIN                   = 78                          #    2 	RW     100        P Gain of Velocity
ADD_POS_D_GAIN                   = 80                          #    2 	RW     0          D Gain of Position
ADD_POS_I_GAIN                   = 82                          #    2 	RW     0          I Gain of Position
ADD_POS_P_GAIN                   = 84                          #    2 	RW     850        P Gain of Position
ADD_FF_2ND_GAIN                  = 88                          #    2 	RW     0          2nd Gain of Feed-Forward
ADD_FF_1ST_GAIN                  = 90                          #    2 	RW     0          1st Gain of Feed-Forward
ADD_WATCHDOG                     = 98                          #    1 	RW     0          Dynamixel BUS Watchdog
ADD_GOAL_PWM                     = 100                         #    2 	RW     -          Target PWM Value
ADD_GOAL_CURRENT                 = 102                         #    2 	RW     -          Target Current Value
ADD_GOAL_VELOC                   = 104                         #    4 	RW     -          Target Velocity Value
ADD_ACCEL_PROFILE                = 108                         #    4 	RW     0          Acceleration Value of Profile
ADD_VELOC_PROFILE                = 112                         #    4   RW     0          Velocity Value of Profile
ADD_GOAL_POSITION                = 116                         #    4 	RW     0          Target Position
ADD_TIME_TICK                    = 120 	                       #    2 	R      -          Count Time in Millisecond
ADD_MOVING                       = 122                         #    1 	R      0          Moving 	Movement Flag
ADD_MOVING_STATUS                = 123 	                       #    1 	R      0          Detailed Information of Movement Status
ADD_PRESENT_PWM                  = 124                         #    2 	R      -          Present PWM Value
ADD_PRESENT_CURR                 = 126                         #    2 	R      -          Present Current Value
ADD_PRESENT_VELOC                = 128                         #    4 	R      -          Present Velocity Value
ADD_PRESENT_POS                  = 132 	                       #    4 	R      -          Present Position Value
ADD_VELOC_TRAJ                   = 136                         #    4 	R      -          Target Velocity Trajectory from Profile
ADD_POS_TRAJ                     = 140                         #    4 	R      -          Target Position Trajectory from Profile
ADD_PRESENT_VOLT                 = 144                         #    2 	R      -          Present Input Voltage
ADD_PRESENT_TEMP                 = 146 	                       #    1   R      -          Present Internal Temperature


# SET GLOBALS
PROTOCOL_VERSION            = 2                         # See which protocol version is used in the Dynamixel
H                           = 1                         # Horizontal Motor is ID: 1
V                           = 2                         # Vertical Motor  is ID: 2
R                           = 3                         # Reverse Vertical motor is ID: 3 in case of GIM03 gimbal
P                           = 4                         # Polarization motor is ID: 4
GIM03_MOTOR_TYPE            = 1100                      # X series motors
GIM04_MOTOR_TYPE            = 2000                      # P motor series
OPER_MODE                   = 4                         # Operating mode set to multiturn
TORQUE_ENABLE               = 1                         # Value for enabling the torque
TORQUE_DISABLE              = 0                         # Value for disabling the torque
ESC_ASCII_VALUE             = 0x1b
COMM_SUCCESS                = 0                         # Communication Success result value
COMM_TX_FAIL                = -1001                     # Communication Tx Failed
H_MOVING_THRESHOLD          = 0                         # resolution for movement detection
HP_MOVING_THRESHOLD         = 5                         # resolution for movement detection: P motor series
V_MOVING_THRESHOLD          = 0                         # resolution for movement detection
P_MOVING_THRESHOLD          = 0                         # resolution for movement detection
GIM04_RAM_ADD_OFFSET        = 448                       # RAM address offset for P motor series

H_POSITION_D_G              = 0                         # Horizontal D gain
H_POSITION_I_G              = 3000                      # Horizontal I gain
H_POSITION_P_G              = 1000                      # Horizontal P gain
H_FF1_G                     = 0                         # Horizontal feed forward gain
HP_POSITION_D_G             = 0                         # base_type 4 Horizontal D gain
HP_POSITION_I_G             = 3000                      # base_type 4 Horizontal I gain
HP_POSITION_P_G             = 3000                      # base_type 4 Horizontal P gain
HP_FF1_G                    = 0                         # base_type 4 Horizontal feed forward gain
V_POSITION_D_G              = 0                         # Vertical D gain
V_POSITION_I_G              = 3000                      # Vertical I gain
V_POSITION_P_G              = 1000                      # Vertical P gain
V_FF1_G                     = 0                         # Vertical feed forward gain
P_POSITION_D_G              = 0                         # Polarization D gain
P_POSITION_I_G              = 3000                      # Polarization I gain
P_POSITION_P_G              = 1000                      # Polarization P gain
P_FF1_G                     = 0                         # Polarization feed forward gain

MIN_VERSION                 = 41                        # Minimum version supported
MAX_VELOCITY                = 1023                      # Maximum velocity
MIN_P_VERSION               = 11                        # Minimum version supported for P Motors (GIM04)
MAX_P_VELOCITY              = 2920                      # GMI04 Base velocity
H_PROFILE_VELOCITY          = 1023                      # rotation speed
HP_PROFILE_VELOCITY         = 2920                      # rotation speed
V_PROFILE_VELOCITY          = 1023                      # rotation speed
P_PROFILE_VELOCITY          = 1023                      # rotation speed
H0                          = 2048                      # center H position relative to H Offset defined
HP0                         = 0                         # center H position relative to H Offset defined (P motor)
V0                          = 2048                      # center V position relative to V Offset defined
P0                          = 2048                      # center P position relative to P Offset defined
DRIVE_MODE                  = 3                         # slave reverse mode for GIM03 reserse vertical motor
MAX_OFFSET                  = 1044479                   # +/- 255 revolutions is the max supported offset
MAX_OFFSET_P                = 2147483647
H_RATIO                     = 5
G4_H_RATIO                  = 2
V_RATIO                     = 1
P_RATIO                     = 120/50
H_GOAL_VELOCITY             = 1023
HP_GOAL_VELOCITY            = 2920
V_GOAL_VELOCITY             = 1023
P_GOAL_VELOCITY             = 1023
X_RES                       = 4096.0                    # X series resolution
P_RES                       = 607500.0                  # P series resolution for GIM04 base
X_VELOCITY_UNIT             = 0.229                     # X series velocity unit (0.229 rev/min)
P_VELOCITY_UNIT             = 0.01                      # P series velocity unit (0.01 rev/min)
MIN_VERSION_P               = 10
V_ACCELERATION_LIMIT        = 10
HP_ACCELERATION_LIMIT       = 2500

POS_ACC_THRESH_H_G1         = 1                         # positional accuracy threshold for HIGH or VERY HIGH accuracy (1/4096)*360/5 = 0.018
POS_ACC_THRESH_H_G4         = 40                        # positional accuracy threshold for HIGH or VERY HIGH accuracy (40/607500)*360/2 = 0.012
POS_ACC_THRESH_V            = 1                         # positional accuracy threshold for HIGH or VERY HIGH accuracy
POS_ACC_THRESH_P            = 1                         # positional accuracy threshold for HIGH or VERY HIGH accuracy
OVERSHOOT_H_ANG             = 2                         # in VERY HIGH accuracy mode, overshoot in H direction by 2deg
OVERSHOOT_V_ANG             = 2                         # in VERY HIGH accuracy mode, overshoot in V direction by 2deg
OVERSHOOT_P_ANG             = 2                         # in VERY HIGH accuracy mode, overshoot in P direction by 2deg
# DEBUG_MOVING                = 1					        # flag to debug movement with extra print statements
DEBUG_MOVING                = 0					        # flag to debug movement with extra print statements

num_motors                  = 2                         # number of gimbal motors (defaults to GIM01 = 2 motors (H&V))
port_num                    = None

# placeholder values (GIM01 base) - these globals will be overwritten during initialiation if GIM04 base is found
base_type                   = 1                         # base_type = 1 for GIM01 and GIM03 and base type is 4 for GIM04 and GIM04_P
base_ratio                  = H_RATIO
base_res                    = X_RES
ram_offset                  = 0
h_zero                      = H0
base_pos_acc_thresh         = POS_ACC_THRESH_H_G1
base_vel_unit               = X_VELOCITY_UNIT
max_H_velocity              = H_PROFILE_VELOCITY
h_P                         = H_POSITION_P_G
h_I                         = H_POSITION_I_G
h_D                         = H_POSITION_D_G
h_FF1                       = H_FF1_G
base_moving_threshold       = H_MOVING_THRESHOLD


# Initialize PacketHandler Structs
#dynamixel.packetHandler()
dxl_comm_result = COMM_TX_FAIL                          # Communication result
dxl_error = 0                                           # Dynamixel error


# ============================================
# ============= GIMBAL FUNCTIONS =============
# ============================================

def write1(motor, address, value):
    """ generic function to write 1 Byte to motor register """
    dynamixel.write1ByteTxRx(port_num, PROTOCOL_VERSION, motor, address, value)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
    # else:                                                                      # debug
    #     print("Motor " + str(motor) + " write sucessful")
    return


def write2(motor, address, value):
    """ generic function to write 2 Byte to motor register """
    dynamixel.write2ByteTxRx(port_num, PROTOCOL_VERSION, motor, address, value)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
    # else:                                                                      # debug
    #     print("Motor " + str(motor) + " write sucessful")
    return


def write4(motor, address, value):
    """ generic function to write 4 Byte to motor register """
    dynamixel.write4ByteTxRx(port_num, PROTOCOL_VERSION, motor, address, value)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
    # else:                                                                      # debug
    #     print("Motor " + str(motor) + " write sucessful")
    return


def read1(motor, address):
    """ generic function to read 1 Byte from motor register """
    read = dynamixel.read1ByteTxRx(port_num, PROTOCOL_VERSION, motor, address)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
    # else:
    #     print("Motor " + str(motor) + " read sucessful")
    return read


def read2(motor, address):
    """ generic function to read 2 Byte from motor register """
    read = dynamixel.read2ByteTxRx(port_num, PROTOCOL_VERSION, motor, address)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
    # else:
    #     print("Motor " + str(motor) + " read sucessfull")
    return read


def read4(motor, address):
    """ generic function to read 4 Byte from motor register """
    read = dynamixel.read4ByteTxRx(port_num, PROTOCOL_VERSION, motor, address)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
    # else:
    #     print("Motor " + str(motor) + " read sucessful")
    return read


def close():
    """ close com port and menu """
    dynamixel.closePort(port_num)
    return


def connect(DEVICENAME, BAUDRATE):
    """ initiate communication with motors, check communication """

    port_num = dynamixel.portHandler(DEVICENAME.encode('utf-8'))                # open port
    print ("device = " + str(DEVICENAME) + "   port = " + str(port_num))

    dynamixel.packetHandler()
    if dynamixel.openPort(port_num):
        print("Succeeded to open the port (%s)!" % DEVICENAME)
    else:
        print("Failed to open the port (%s)!" % DEVICENAME)
        status_ok = False
        return status_ok

    if dynamixel.setBaudRate(port_num, BAUDRATE):                               # Set port baudrate
        print("Succeeded to set the baudrate!")
    else:
        print("Failed to change the baudrate!")
        status_ok = False
        return status_ok

    status_ok = test()                                                           # test register configuration

    return status_ok


def test():
    """ test register setting and restore to MilliBox settings """

    global num_motors
    global base_type
    global base_ratio
    global base_res
    global ram_offset
    global h_zero
    global base_pos_acc_thresh
    global base_vel_unit
    global max_H_velocity
    global h_P
    global h_I
    global h_D
    global h_FF1
    global base_moving_threshold

    status_ok = True

    print("===== Gimbal type CHECK =====")
    if read2(P, ADD_MODEL_NUMBER) >= GIM03_MOTOR_TYPE:
        num_motors = 4
        print("====> GIM04_P identified")
    elif read2(R, ADD_MODEL_NUMBER) >= GIM03_MOTOR_TYPE:                          # check if slave motor is found (GIM03)
        num_motors = 3
        print("====> GIM03/04 identified")
    elif read2(V, ADD_MODEL_NUMBER) > 0:                                        # check if V motor is found (GIM01)
        num_motors = 2
        print("====> GIM01 identified")
    elif read2(H, ADD_MODEL_NUMBER) > 0:                                        # check if H motor is found (GIM1D)
        num_motors = 1
        print("====> GIM1D identified")
    else:
        print("Failed MOTOR READBACK!!")                                        # no motors found, report error and quit
        status_ok = False
        return status_ok

    if read2(H, ADD_MODEL_NUMBER) == GIM04_MOTOR_TYPE:
        base_type = 4
        base_ratio = G4_H_RATIO
        base_res = P_RES
        ram_offset = GIM04_RAM_ADD_OFFSET
        h_zero = 0
        base_pos_acc_thresh = POS_ACC_THRESH_H_G4
        base_vel_unit = P_VELOCITY_UNIT
        max_H_velocity = HP_PROFILE_VELOCITY
        h_P = HP_POSITION_P_G
        h_I = HP_POSITION_I_G
        h_D = HP_POSITION_D_G
        h_FF1 = HP_FF1_G
        base_moving_threshold = HP_MOVING_THRESHOLD
        print("====> GIM04 Base identified")
    else:
        base_type = 1
        base_ratio = H_RATIO
        base_res = X_RES
        ram_offset = 0
        h_zero = H0
        base_pos_acc_thresh = POS_ACC_THRESH_H_G1
        base_vel_unit = X_VELOCITY_UNIT
        max_H_velocity = H_PROFILE_VELOCITY
        h_P = H_POSITION_P_G
        h_I = H_POSITION_I_G
        h_D = H_POSITION_D_G
        h_FF1 = H_FF1_G
        base_moving_threshold = H_MOVING_THRESHOLD
        print("====> GIM01 GIM03 Base identified")

    print("===== motor configuration CHECK =====")
    disable_torque(H)                                                           # access flash
    if num_motors >= 2:
        disable_torque(V)
    if num_motors >= 3:
        disable_torque(R)
    if num_motors >= 4:
        disable_torque(P)
    print("flash access set ")

    # print("======  re-instate Offsets debug only==========")
    # Hoffset = read4(H, ADD_HOME_OFFSET)
    # Voffset = read4(V, ADD_HOME_OFFSET)
    # write4(H, ADD_HOME_OFFSET, Hoffset)
    # write4(V, ADD_HOME_OFFSET, Voffset)
    # print ("H Offset is:  " +str(Hoffset)+"   V Offset is:  " +str(Voffset))

    if read4(H, ADD_MOVE_THRESHOLD) == base_moving_threshold:                      # test H moving Threshold
        print("H moving threshold OK")
    else:
        print("resetting H moving threshold")

        write4(H, ADD_MOVE_THRESHOLD, base_moving_threshold)
        print("H moving threshold set to : " + str(base_moving_threshold))

    if num_motors >= 2:
        if read4(V, ADD_MOVE_THRESHOLD) == V_MOVING_THRESHOLD:                  # test V moving Threshold
            print("V moving threshold OK")
        else:
            print("resetting V moving threshold")
            write4(V, ADD_MOVE_THRESHOLD, V_MOVING_THRESHOLD)
            print("V moving threshold set to : " + str(V_MOVING_THRESHOLD))
        if num_motors >= 4:
            if read4(P, ADD_MOVE_THRESHOLD) == P_MOVING_THRESHOLD:                  # test V moving Threshold
                print("P moving threshold OK")
            else:
                print("resetting P moving threshold")
                write4(P, ADD_MOVE_THRESHOLD, P_MOVING_THRESHOLD)
                print("P moving threshold set to : " + str(P_MOVING_THRESHOLD))

    maxvelH = read4(H, ADD_MAX_VELOCITY)                                        # test max velocity settings
    if num_motors >= 2:
        maxvelV = read4(V, ADD_MAX_VELOCITY)
        if num_motors >= 4:
            maxvelP = read4(P, ADD_MAX_VELOCITY)
        else:
            maxvelP = MAX_VELOCITY
    else:
        maxvelV = MAX_VELOCITY

    # print("max velocity H = " +str(maxvelH)+ " and V = " +str(maxvelV)+ "  and P = " +str(maxvelP))

    if maxvelH == max_H_velocity:
        print("****  Max H velocity is OK : " + str(maxvelH) + "  ****")
    else:
        print(" resetting H max velocity to :  " + str(max_H_velocity))
        write4(H, ADD_MAX_VELOCITY, max_H_velocity)

    if num_motors >= 2:
        if maxvelV == MAX_VELOCITY:
            print("****  Max V velocity is OK : " + str(maxvelV) + "  ****")
        else:
            print( " resetting V max velocity to :  " + str(MAX_VELOCITY))
            write4(V, ADD_MAX_VELOCITY, MAX_VELOCITY)
        if num_motors >= 4:
            if maxvelP == MAX_VELOCITY:
                print("****  Max P velocity is OK : " + str(maxvelP) + "  ****")
            else:
                print( " resetting P max velocity to :  " + str(MAX_VELOCITY))
                write4(P, ADD_MAX_VELOCITY, MAX_VELOCITY)

    if num_motors >= 3:                                                         # This part is to make sure that if Motors are upgraded
        opmodeR = read1(R, ADD_OPERATING_MODE)                                  # GIM03 reverse slave motors (ID:3) does not lose its slave mode
        print("operating mode R = " + str(opmodeR))                             # otherwsie it could damage the gimbal
        if opmodeR == OPER_MODE:
            print("gim03 reverse motor operating mode is OK")
        else:
            write1(R, ADD_OPERATING_MODE, OPER_MODE)
            print(" reseting reverse motor operating mode")
        drmodeR = read1(R, ADD_DRIVE_MODE)
        print("drive mode R = " + str(drmodeR))
        if drmodeR == DRIVE_MODE:
            print("gim03 reverse motor drive mode is OK")
        else:
            write1(R, ADD_DRIVE_MODE, DRIVE_MODE)
            print(" resetting reverse motor drive mode")

    opmodeH = read1(H, ADD_OPERATING_MODE)                                      # test operating mode
    if num_motors >= 2:
        opmodeV = read1(V, ADD_OPERATING_MODE)
    else:
        opmodeV = OPER_MODE

    print("operating mode H = " + str(opmodeH) + " and V = " + str(opmodeV))
    if opmodeH == OPER_MODE and opmodeV == OPER_MODE:
        print("**** Operating mode is OK ****")
    else:
        print(" resetting operating mode ")
        write1(H, ADD_OPERATING_MODE, OPER_MODE)
        if num_motors >= 2:
            write1(V, ADD_OPERATING_MODE, OPER_MODE)
        print("operating mode reset to : " + str(OPER_MODE))

    if num_motors >= 4:
        if read1(P, ADD_OPERATING_MODE)==OPER_MODE:
            print("**** Operating mode is OK ****")
        else:
            print(" resetting operating mode ")
            write1(P, ADD_OPERATING_MODE, OPER_MODE)

    print("=== setting motors dynamic parameters ===")                          # those setting should be done at every power on
    enable_torque(H)
    if num_motors >= 2:
        enable_torque(V)
    if num_motors >= 3:
        enable_torque(R)
    if num_motors >= 4:
        enable_torque(P)
    print("ram access enabled")                                                 # close access to flash and enable acces to RAM area

    print("BOOT UP MOTOR POSITION CHECK before re-alignement")                  # print motor absolute position at boot up
    getposition(0)

    write4(H, (ADD_GOAL_VELOC + ram_offset), max_H_velocity)                    # set H PID values
    # write4(H, (ADD_VELOC_PROFILE + ram_offset), H_PROFILE_VELOCITY)
    # print("H goal velocity set to :" +str(GOAL_VELOCITY))
    write2(H, (ADD_POS_D_GAIN + ram_offset), h_D)
    write2(H, (ADD_POS_P_GAIN + ram_offset), h_P)
    write2(H, (ADD_POS_I_GAIN + ram_offset), h_I)
    write2(H, (ADD_FF_1ST_GAIN+ ram_offset), h_FF1)
    print("H PID configuration set")

    if num_motors >= 2:
        write4(V, ADD_GOAL_VELOC, V_GOAL_VELOCITY)                                # set V PID values
        # write4(V, ADD_VELOC_PROFILE, V_PROFILE_VELOCITY)
        # print("V goal velocity set to :" +str(V_GOAL_VELOCITY))
        write2(V, ADD_POS_D_GAIN, V_POSITION_D_G)
        write2(V, ADD_POS_P_GAIN, V_POSITION_P_G)
        write2(V, ADD_POS_I_GAIN, V_POSITION_I_G)
        write2(V, ADD_FF_1ST_GAIN, V_FF1_G)
        print("V PID configuration set")

    if num_motors >= 4:
        write4(P, ADD_GOAL_VELOC, P_GOAL_VELOCITY)                                # set P PID values
        # write4(P, ADD_VELOC_PROFILE, P_PROFILE_VELOCITY)
        # print("P goal velocity set to :" +str(P_GOAL_VELOCITY))
        write2(P, ADD_POS_D_GAIN, P_POSITION_D_G)
        write2(P, ADD_POS_P_GAIN, P_POSITION_P_G)
        write2(P, ADD_POS_I_GAIN, P_POSITION_I_G)
        write2(P, ADD_FF_1ST_GAIN, P_FF1_G)
        print("P PID configuration set")

    print("verifying all settings")                                             # check all actual values in RAM

    print("H goal Velocity : " + str(read4(H, ADD_GOAL_VELOC + ram_offset)) + " = " + str(max_H_velocity))
    print("H position D gain : " + str(read2(H, ADD_POS_D_GAIN + ram_offset)) + " = " + str(h_D))
    print("H position P gain : " + str(read2(H, ADD_POS_P_GAIN + ram_offset)) + " = " + str(h_P))
    print("H position I gain : " + str(read2(H, ADD_POS_I_GAIN + ram_offset)) + " = " + str(h_I))
    print("H FF1 gain : " + str(read2(H, ADD_FF_1ST_GAIN + ram_offset)) + " = " + str(h_FF1))

    if num_motors >= 2:
        print("V goal Velocity : " + str(read4(V, ADD_GOAL_VELOC)) + " = " + str(V_GOAL_VELOCITY))
        print("V position D gain : " + str(read2(V, ADD_POS_D_GAIN)) + " = " + str(V_POSITION_D_G))
        print("V position P gain : " + str(read2(V, ADD_POS_P_GAIN)) + " = " + str(V_POSITION_P_G))
        print("V position I gain : " + str(read2(V, ADD_POS_I_GAIN)) + " = " + str(V_POSITION_I_G))
        print("V FF1 gain : " + str(read2(V, ADD_FF_1ST_GAIN)) + " = " + str(V_FF1_G))

    if num_motors >= 4:                                                         # fixme: set P actual PID values
        print("P goal Velocity : " + str(read4(P, ADD_GOAL_VELOC)) + " = " + str(P_GOAL_VELOCITY))
        print("P position D gain : " + str(read2(P, ADD_POS_D_GAIN)) + " = " + str(P_POSITION_D_G))
        print("P position P gain : " + str(read2(P, ADD_POS_P_GAIN)) + " = " + str(P_POSITION_P_G))
        print("P position I gain : " + str(read2(P, ADD_POS_I_GAIN)) + " = " + str(P_POSITION_I_G))
        print("P FF1 gain : " + str(read2(P, ADD_FF_1ST_GAIN)) + " = " + str(P_FF1_G))

    ### reset offset and pos at startup

    versionH = read1(H, ADD_FW_VER)
    if base_type == 4:
        if versionH < MIN_VERSION_P:                                            # make sure Firmware is up to date
            print("firmware version not supported:" + str(versionH))
        else:
            print("firmware version of motor H is OKAY ")

    if base_type == 1:
        if versionH < MIN_VERSION:                                              # make sure Firmware is up to date
            print("firmware version not supported:" + str(versionH))
        else:
            print("firmware version of motor H is OKAY ")
            if versionH > 42:                                                   # offset handling after FW 42 has changed
                realign(H)
    if num_motors >= 2:
        versionV = read1(V, ADD_FW_VER)
        if versionV < MIN_VERSION:                                              # make sure Firmware is up to date
            print("firmware version not supported")
        else:
            print("firmware version of motor V is OKAY ")
            if versionV > 42:                                                   # offset handling after FW 42 has changed
                realign(V)                                                      # we may need to re-align current position
        if num_motors >= 4:
            versionP = read1(P, ADD_FW_VER)
            if versionP < MIN_VERSION:                                          # make sure Firmware is up to date
                print("firmware version not supported")
            else:
                print("firmware version of motor P is OKAY ")
                if versionP > 42:                                               # offset handling after FW 42 has changed
                    realign(P)                                                  # we may need to re-align current position

    if num_motors >= 3:                                                         # setting an acceleration limiter on GIM03 and GIM04 Vertical motor for smoother motion
        acc_profile = read4 (V, ADD_ACCEL_PROFILE)
        if acc_profile == V_ACCELERATION_LIMIT:
            print(" Vertical acceleration profile check pass")
        else:
            write4(V, ADD_ACCEL_PROFILE, V_ACCELERATION_LIMIT)
            print(" Vertical acceleration profile set to : " + str(V_ACCELERATION_LIMIT))

    if base_type == 4:                                                          # setting an acceleration limiter on GIM04 Base for smoother motion
        H_acc_profile = read4 (H, ADD_ACCEL_PROFILE + ram_offset)
        if H_acc_profile == HP_ACCELERATION_LIMIT:
            print(" GIM04 base acceleration profile check pass")
        else:
            write4(H, ADD_ACCEL_PROFILE + ram_offset, HP_ACCELERATION_LIMIT)
            print(" GIM04 base acceleration profile set to : " + str(HP_ACCELERATION_LIMIT))

    gotoZERO("HIGH")
    return status_ok


def get_nummotors():
    """ return the number of detected motors """
    global num_motors
    return num_motors


def realign(motor):
    """ re-aligns the motor at boot-up, if needed """
    if motor == H and base_type == 4:
        resolution = P_RES
        max_off = MAX_OFFSET_P
        ram = ram_offset
        skip = 1
    else:
        resolution = X_RES
        max_off = MAX_OFFSET
        ram = 0
        skip = 0                                                                # Flag whether position at boot up need to be re-aligned

    print("checking motor : " +str(motor)+ "  position at init")                # debug
    offset = read4(motor, ADD_HOME_OFFSET)                                      # read current offset from flash
    print ("offset at init is: " +str(offset))                                  # debug
    pos = read4(motor, ADD_GOAL_POSITION + ram)                                 # read current motor position
    print("motor : "+str(motor)+"  pos at init is: "  +str(pos))                # debug
    if pos >= resolution:                                                       # if current position is more than a turn, then we need to correct this
        n = int(pos/resolution)                                                 # need to count n the number of turns added
        print ("positive compensation: " + str(n) +"  turns")                   # debug
    elif pos < 0:                                                               # or if the current position is negative, then we need to correct this
        n = int(pos/resolution) - 1                                             # we need to bring the position between 0 and 4095
        print ("negative compensation: " + str(n) +"  turns")                   # debug
    else:                                                                       # if the current position is already between 0 and 4095 we can skip the rest
        skip = 1
    if skip != 1:                                                               # if not, we need to correct the current position
        new_offset = int(offset - n*resolution)                                 # remove the extra turns that have been added by firmware, by compensating with offset
        print("number of extra turns n=  " + str(n))                            # debug
        if new_offset > max_off or new_offset < -1*max_off:                     # let's chech that our offset is not maxed out
            print ("WARNING ------ offset overun need to reset offset using menu-------")
        else:                                                                   # offset is not amxed out we can make the change in flash
            disable_torque(motor)                                               # disable motor opens the motor flash memory for update
            write4(motor, ADD_HOME_OFFSET, new_offset)                          # change offset accordingly
            enable_torque(motor)                                                # close the flash write access
            print(" motor : " + str(motor) + "  offset adjusted to : " + str(new_offset))   # debug
            offset = read4(motor, ADD_HOME_OFFSET)                        # read back to make sure the change happened
            print (" updated motor : " + str(motor) + " offset is: " + str(offset))         # record the change in log
            pos = read4(motor, ADD_GOAL_POSITION + ram)                         # read back the the current position is changed accordingly
            if 0 <= pos < resolution:
                print(" updated motor : " + str(motor) + " pos is: " + str(pos))
            else:
                print("  ERROR : the motor position is wrong ")
    else:
        print("-> no compensation needed for motor : " +str(motor))

    return


def setoffset(motor):
    """ write the new offset positions to motor eeprom """

    if motor is V:
        if num_motors >= 2:
            offset = read4(motor, ADD_HOME_OFFSET)
            print("current offset= " + str(offset))
            offset = offset - current_pos(V, 1) + V0                            # we want vertical center at 2048
            if abs(offset) <= MAX_OFFSET:
                disable_torque(V)
                write4(motor, ADD_HOME_OFFSET, offset)
                print("new offset= " + str(offset))
                offset = read4(motor, ADD_HOME_OFFSET)
                print("check new offset= " + str(offset))
            else:
                print("offset out of range, reset the offset")
            enable_torque(motor)                                                # this is the call which allow the motors to move
    elif motor is P:
        if num_motors >= 4:
            offset = read4(motor, ADD_HOME_OFFSET)
            print("current offset= " + str(offset))
            offset = offset - current_pos(P, 1) + P0                            # we want Horizontal center at P0
            if abs(offset) <= MAX_OFFSET:
                disable_torque(P)
                write4(motor, ADD_HOME_OFFSET, offset)
                print("new offset= " + str(offset))
                offset = read4(motor, ADD_HOME_OFFSET)
                print("check new offset= " + str(offset))
            else:
                print("offset out of range, reset the offset")
            enable_torque(motor)                                                # this is the call which allow the motors to move
    elif motor is H:
        offset = read4(motor, ADD_HOME_OFFSET)
        print("current offset= " + str(offset))
        offset = offset - current_pos(H, 1) + h_zero                            # we want Horizontal center at 2048
        if abs(offset) <= MAX_OFFSET:
            disable_torque(H)
            write4(motor, ADD_HOME_OFFSET, offset)
            print("new offset= " + str(offset))
            offset = read4(motor, ADD_HOME_OFFSET)
            print("check new offset= " + str(offset))
        else:
            print("offset out of range, reset the offset")
        enable_torque(motor)                                                    # this is the call which allow the motors to move
    else:
        print("error ")
    return


def resetoffset():
    """ reset the offset position in case it reach the maximum number of turns 255 """
    disable_torque(H)
    offseth = read4(H, ADD_HOME_OFFSET)
    print("current H offset= " + str(offseth))
    write4(H, ADD_HOME_OFFSET, 0)
    enable_torque(H)
    print("*** offset reset done on H")
    if num_motors >= 2:
        disable_torque(V)
        offsetv = read4(V, ADD_HOME_OFFSET)
        print("current V offset= " + str(offsetv))
        write4(V, ADD_HOME_OFFSET, 0)
        enable_torque(V)
        print("*** offset reset done on V")
        if num_motors >= 4:
            disable_torque(P)
            offsetp = read4(P, ADD_HOME_OFFSET)
            print("current P offset= " + str(offsetp))
            write4(P, ADD_HOME_OFFSET, 0)
            enable_torque(P)
            print("*** offset reset done on P")


def changerate(rate):
    """ change all motors communication baud rate, this is used for MACos which does not support 1Mbps """
    disable_torque(H)
    write1(H, ADD_BAUD_RATE, rate)
    enable_torque(H)
    if num_motors >= 2:
        disable_torque(V)
        write1(V, ADD_BAUD_RATE, rate)
        enable_torque(V)
        if num_motors >= 3:
            disable_torque(R)
            write1(R, ADD_BAUD_RATE, rate)
            enable_torque(R)
            if num_motors >= 4:
                disable_torque(P)
                write1(P, ADD_BAUD_RATE, rate)
                enable_torque(P)
    print("*** rate changed, port is closed, set BAUDRATE global in mbx.py accordingly")
    print("*** restart mbx.py with correct baud rate")
    sys.exit()
    return


def enable_torque(motor):
    """ allow motor to move and block eeprom register access """
    if motor <= num_motors:
        if motor == H:
            if read1(motor, (ADD_TORQUE_ENABLE + ram_offset)) == TORQUE_ENABLE:
                print("torque for motor : " + str(motor) + " is already enabled")
            else:
                write1(motor, (ADD_TORQUE_ENABLE + ram_offset), TORQUE_ENABLE)
                print("torque now enabled for motor" + str(motor))
        elif motor > H:
            if read1(motor, ADD_TORQUE_ENABLE) == TORQUE_ENABLE:
                print("torque for motor : " + str(motor) + " is already enabled")
            else:
                write1(motor, ADD_TORQUE_ENABLE, TORQUE_ENABLE)
                print("torque now enabled for motor" + str(motor))
    else:
        print("WARNING: Attempting to enable torque on Motor %d that does not exist" % motor)
    return


def disable_torque(motor):
    """ stop motor from being moved and allow eeprom register access """
    if motor <= num_motors:
        if motor == H:
            if read1(motor, (ADD_TORQUE_ENABLE + ram_offset)) == TORQUE_DISABLE:
                print("torque for motor : " + str(motor) + " is already disabled")
            else:
                write1(motor, (ADD_TORQUE_ENABLE + ram_offset), TORQUE_DISABLE)
                print("torque now disabled for motor" + str(motor))
        elif motor > H:
            if read1(motor, ADD_TORQUE_ENABLE) == TORQUE_DISABLE:
                print("torque for motor : " + str(motor) + " is already disabled")
            else:
                write1(motor, ADD_TORQUE_ENABLE, TORQUE_DISABLE)
                print("torque now disabled for motor" + str(motor))
    else:
        print("WARNING: Attempting to disable torque on Motor %d that does not exist" % motor)
    return


def get_velocity():
    """ print motor RPM value """
    global base_ratio
    global ram_offset
    global base_vel_unit
    global V_GOAL_VELOCITY
    global P_GOAL_VELOCITY
    global X_VELOCITY_UNIT

    # print("base_type = %g" % base_type)
    # print("base_ratio = %g" % base_ratio)
    # print("ram_offset = %g" % ram_offset)
    # print("base_vel_unit = %g" % base_vel_unit)

    H_velocity = base_vel_unit * read4(H, (ADD_VELOC_PROFILE + ram_offset)) / base_ratio    # read the current motor H velocity setting and convert to rpm
    print("horizontal velocity is set to = " + str(H_velocity) + " rpm")

    if num_motors >= 2:
        V_velocity = X_VELOCITY_UNIT * read4(V, ADD_VELOC_PROFILE)/V_RATIO                  # read the current motor V velocity setting and convert to rpm
        print("vertical velocity is set to = " + str(V_velocity) + " rpm")
    else:
        V_velocity = V_GOAL_VELOCITY

    if num_motors >= 4:
        P_velocity = X_VELOCITY_UNIT * read4(P, ADD_VELOC_PROFILE)/P_RATIO                  # read the current motor P velocity setting and convert to rpm
        print("polarization velocity is set to = " + str(P_velocity) + " rpm")
    else:
        P_velocity = P_GOAL_VELOCITY

    return H_velocity, V_velocity, P_velocity


def set_velocity(h_vel=0, v_vel=0, p_vel=0):
    """ change rotation speed of the motors """
    global base_ratio
    global ram_offset
    global base_vel_unit
    global max_H_velocity
    global V_GOAL_VELOCITY
    global P_GOAL_VELOCITY
    global X_VELOCITY_UNIT

    # print("base_ratio = %g" % base_ratio)
    # print("ram_offset = %g" % ram_offset)
    # print("base_vel_unit = %g" % base_vel_unit)
    # print("max_H_velocity = %g" % max_H_velocity)

    if h_vel == 0:                                                              # if user set 0 then default max speed is used
        H_vel = max_H_velocity
    else:
        H_vel = int(round(h_vel*base_ratio/base_vel_unit))                      # convert horizontal velocity to actual register value
        if H_vel > max_H_velocity:                                              # can't exceed max speed
            H_vel = max_H_velocity
            print("clamping to maximum possible velocity for H motor")
        if H_vel < 1:                                                           # can't be less than min speed
            H_vel = 1
            print("clamping to minimum possible velocity for H motor")
    write4(H, ADD_VELOC_PROFILE + ram_offset, H_vel)                            # program register value in RAM

    if num_motors >= 2:
        if v_vel == 0:                                                          # if user set 0 then default max speed is used
            V_vel = V_GOAL_VELOCITY
        else:
            V_vel = int(round(v_vel*V_RATIO/X_VELOCITY_UNIT))                   # convert vertical velocity to actual register value
            if V_vel > V_GOAL_VELOCITY:                                         # can't exceed max speed
                V_vel = V_GOAL_VELOCITY
                print("clamping to maximum possible velocity for V motor")
            if V_vel < 1:                                                       # can't be less than min speed
                V_vel = 1
                print("clamping to minimum possible velocity for V motor")
        write4(V, ADD_VELOC_PROFILE, V_vel)                                     # program register value in RAM

    if num_motors >= 4:
        if p_vel == 0:                                                          # if user set 0 then default max speed is used
            P_vel = P_GOAL_VELOCITY
        else:
            P_vel = int(round(p_vel*P_RATIO/X_VELOCITY_UNIT))                   # convert vertical velocity to actual register value
            if P_vel > P_GOAL_VELOCITY:                                         # can't exceed max speed
                P_vel = P_GOAL_VELOCITY
                print("clamping to maximum possible velocity for P motor")
            if P_vel < 1:                                                       # can't be less than min speed
                P_vel = 1
                print("clamping to minimum possible velocity for P motor")
        write4(P, ADD_VELOC_PROFILE, P_vel)

    get_velocity()                                                              # check the values by reading back the registers

    return


# ===========================================
# ============= GIMBAL MOVEMENT =============
# ===========================================

def convertangletopos(motor, angle):
    """ convert angle in degree to motor position """
    if motor is V:
        pos = int(round((angle*X_RES*V_RATIO)/360.0))+V0                        # Vertical motor is in direct drive
    elif motor is H:
        pos = int(round((angle*base_res*base_ratio)/360.0))+h_zero              # Horizontal motor has an additional 5x gear ratio in gimbal
    elif motor is P:
        pos = int(round(angle*X_RES*P_RATIO)/360.0)+P0                          # Pol motor has an additional 3x gear ratio in gimbal
    else:
        print("position error")
    return pos


def convertpostoangle(motor, pos):
    """ convert reported motor position to absolute angle """
    if motor is V:
        angle = ((pos-V0)*360.0/(X_RES*V_RATIO))                                # Vertical motor is in direct drive
    elif motor is H:
        angle = ((pos-h_zero)*360.0/(base_res*base_ratio))                      # Horizontal motor has an additional 5x gear ratio in gimbal
    elif motor is P:
        angle = ((pos-P0)*360.0/(X_RES*P_RATIO))                                # Pol motor has an additional 2.4x (120/50) gear ratio in gimbal
    else:
        print("position error")
    return angle


def current_pos(motor, log):
    """ read the absolute current position of the motor """
    # this function can be called while the motor is moving
    # if a settled position is desired, use wait_stop_moving() before calling this function
    if motor <= num_motors:
        if motor == H:
            curpos = read4(motor, ADD_PRESENT_POS + ram_offset)
            offset = read4(motor, ADD_HOME_OFFSET)
        else:
            curpos = read4(motor, ADD_PRESENT_POS)
            offset = read4(motor, ADD_HOME_OFFSET)
        if log == 0:
            cur_angle = convertpostoangle(motor, curpos)
            print("Current position for motor " + str(motor) + "  is =  " + str(cur_angle) + " degree, Position is : " + str(curpos) + "steps,  Offset is : " + str(offset))
    else:
        curpos = convertangletopos(motor, 0)
    return curpos


def goal_pos(motor, log):
    """ read the absolute goal position of the motor """
    if motor <= num_motors:
        if motor == H:
            cur_goal_pos = read4(motor, ADD_GOAL_POSITION + ram_offset)
            offset = read4(motor, ADD_HOME_OFFSET)
        else:
            cur_goal_pos = read4(motor, ADD_GOAL_POSITION)
            offset = read4(motor, ADD_HOME_OFFSET)
    else:
        cur_goal_pos = convertangletopos(motor, 0)
        offset = 0

    goal_angle = convertpostoangle(motor, cur_goal_pos)
    if log == 0:
        print("Current goal position for motor " + str(motor) + "  is =  " + str(goal_angle) + " degree, Position is : " + str(cur_goal_pos) + "steps,  Offset is : " + str(offset))
    return cur_goal_pos


def getposition(log=0):
    """ get absolute H V position """
    hpos = current_pos(H, log)
    vpos = current_pos(V, log)
    ppos = current_pos(P, log)
    return hpos, vpos, ppos


def wait_stop_moving(accuracy="HIGH", debug=DEBUG_MOVING):
    """ wait until all motors are not moving """
    global ram_offset
    global base_pos_acc_thresh
    global POS_ACC_THRESH_V
    global POS_ACC_THRESH_P

    INIT_DELAY = 0.15                                                           # delay before any register is read (to avoid ismoving reporting incorrectly)
    LOOP_DELAY = 0.05                                                           # delay in while loop polling status

    if debug:
        print("wait_stop_moving() called...")

    time.sleep(INIT_DELAY)

    if accuracy == "HIGH" or accuracy == "VERY HIGH":
        goalH = read4(H,ADD_GOAL_POSITION + ram_offset)                         # read H goal position
        if num_motors >= 2:
            goalV = read4(V,ADD_GOAL_POSITION)                                  # read V goal position
            if num_motors >= 4:
                goalP = read4(P,ADD_GOAL_POSITION)                              # read P goal position

    # wait until motor H reports not MOVING (based on velocity)
    ismovingH = True
    while ismovingH:
        ismovingH = (read1(H, ADD_MOVING + ram_offset) > 0)                     # check H MOVING register
        if debug:
            print("H is moving = %d" % ismovingH)
        if ismovingH:
            time.sleep(LOOP_DELAY)                                              # delay before polling again

    # wait until motor H reaches goal position (based on target and current position)
    if accuracy == "HIGH" or accuracy == "VERY HIGH":
        not_reachedH = True
        while not_reachedH:                                                     # for higher accuracy, loop until (pres_pos - goal) <= threshold
            pres_posH = read4(H, ADD_PRESENT_POS + ram_offset)
            if debug:
                print("H goal position / present / error = %d / %d / %d" % (goalH, pres_posH, goalH - pres_posH))
            not_reachedH = (abs(pres_posH - goalH) > base_pos_acc_thresh)
            if not_reachedH:
                time.sleep(LOOP_DELAY)                                          # delay before polling again

    if num_motors >= 2:                                                         # if we are not GIM1D
        # wait until motor V reports not MOVING (based on velocity)
        ismovingV = True
        while ismovingV:
            ismovingV = (read1(V, ADD_MOVING) > 0)                              # check V MOVING register
            if debug:
                print("V is moving = %d" % ismovingV)
            if ismovingV:
                time.sleep(LOOP_DELAY)                                          # delay before polling again

        # wait until motor V reaches goal position (based on target and current position)
        if accuracy == "HIGH" or accuracy == "VERY HIGH":
            not_reachedV = True
            while not_reachedV:                                                 # for higher accuracy, loop until (pres_pos - goal) <= threshold
                pres_posV = read4(V, ADD_PRESENT_POS)
                if debug:
                    print("V goal position / present / error = %d / %d / %d" % (goalV, pres_posV, goalV - pres_posV))
                not_reachedV = (abs(pres_posV - goalV) > POS_ACC_THRESH_V)
                if not_reachedV:
                    time.sleep(LOOP_DELAY)                                      # delay before polling again

    if num_motors >= 4:                                                         # if we are a GIM04
        # wait until motor P reports not MOVING (based on velocity)
        ismovingP = 1
        while ismovingP:
            ismovingP = (read1(P, ADD_MOVING) > 0)                              # check P MOVING register
            if debug:
                print("P is moving = %d" % ismovingP)
            if ismovingP:
                time.sleep(LOOP_DELAY)                                          # delay before polling again

        # wait until motor P reaches goal position (based on target and current position)
        if accuracy == "HIGH" or accuracy == "VERY HIGH":
            not_reachedP = True
            while not_reachedP:                                                 # for higher accuracy, loop until (pres_pos - goal) <= threshold
                pres_posP = read4(P, ADD_PRESENT_POS)
                if debug:
                    print("P goal position / present / error = %d / %d / %d" % (goalP, pres_posP, goalP - pres_posP))
                not_reachedP = (abs(pres_posP - goalP) > POS_ACC_THRESH_P)
                if not_reachedP:
                    time.sleep(LOOP_DELAY)                                      # delay before polling again

    return


def move(motor, step, accuracy="HIGH"):
    """ Move motor position to a new position relative to current one (and check for boundary limits) """
    global OVERSHOOT_H_ANG, OVERSHOOT_V_ANG, OVERSHOOT_P_ANG

    overshoot_H = convertangletopos(H, OVERSHOOT_H_ANG) - convertangletopos(H, 0)     # convert step angle to motor position step
    overshoot_V = convertangletopos(V, OVERSHOOT_V_ANG) - convertangletopos(V, 0)     # convert step angle to motor position step
    overshoot_P = convertangletopos(P, OVERSHOOT_P_ANG) - convertangletopos(P, 0)     # convert step angle to motor position step

    step_pos = convertangletopos(motor, step) - convertangletopos(motor, 0)     # convert step angle to motor position step

    cur_goal_pos = goal_pos(motor, 1)                                           # read the current goal position
    if motor is V:
        if num_motors >= 2:
            if abs(step_pos) < 1:                                               # check step size is not lower than resolution (360/4096)
                print("step is too small for this motor, increase step size, to move")
            else:                                                               # prevent loop around on V
                if (step_pos + cur_goal_pos)> X_RES/2+V0 or (step_pos + cur_goal_pos) < -1*X_RES/2+V0:
                    print ("limit up   " +str(X_RES/2+V0))
                    print ("limit down " +str(-1*X_RES/2+V0))
                    print ("target     "  +str(step_pos + cur_goal_pos))
                    print("please go back on V out of range")
                else:
                    pos=(step_pos + cur_goal_pos)
                    print("motor vertical target position =  " + str(pos))
                    angle=convertpostoangle(V, pos)
                    print("target vertical angle =  " + str(angle))
                    if accuracy == "VERY HIGH":
                        write4(motor, ADD_GOAL_POSITION, pos - overshoot_V)     # overshoot goal V position first
                        wait_stop_moving(accuracy)
                    write4(motor, ADD_GOAL_POSITION, pos)                       # go to final goal V position
                    wait_stop_moving(accuracy)                                  # wait for motor to stop moving
        else:
            if step != 0:
                print("WARNING: Trying to move V motor, but motor not detected")

    elif motor is H:
        if abs(step_pos) < 1:                                                   # check step size is not lower than resolution (360/(4096*5))
            print("step is too small for this motor, increase step size, to move")
        else:                                                                   # prevent loop around on H
            if (step_pos + cur_goal_pos) > (base_res*base_ratio)/2+h_zero or (step_pos + cur_goal_pos) < (-1*base_res*base_ratio)/2+h_zero:
                print("please go back on H out of range")
            else:
                pos = (step_pos + cur_goal_pos)
                print("Motor horizontal target position =  " + str(pos))
                angle = convertpostoangle(H, pos)
                print("Target horizontal angle =  " + str(angle))
                if accuracy == "VERY HIGH":
                    write4(motor, ADD_GOAL_POSITION + ram_offset, pos - overshoot_H)         # overshoot goal H position first
                    wait_stop_moving(accuracy)                                  # wait for motor to stop moving
                write4(motor, ADD_GOAL_POSITION + ram_offset, pos)              # go to final goal H position
                wait_stop_moving(accuracy)                                      # wait for motor to stop moving

    elif motor is P:
        if num_motors >= 4:
            if abs(step_pos) < 1:                                               # check step size is not lower than resolution (360/4096)
                print("step is too small for this motor, increase step size, to move")
            else:                                                               # prevent loop around on V
                if (step_pos + cur_goal_pos)> X_RES*P_RATIO/2+P0 or (step_pos + cur_goal_pos) < -1*X_RES*P_RATIO/2+P0:
                    print("please go back on P out of range")
                else:
                    pos=(step_pos + cur_goal_pos)
                    print("motor Polarization target position =  " + str(pos))
                    angle=convertpostoangle(P, pos)
                    print("target vertical angle =  " + str(angle))
                    if accuracy == "VERY HIGH":
                        write4(motor, ADD_GOAL_POSITION, pos - overshoot_P)     # overshoot goal V position first
                        wait_stop_moving(accuracy)
                    write4(motor, ADD_GOAL_POSITION, pos)                       # go to final goal V position
                    wait_stop_moving(accuracy)                                  # wait for motor to stop moving
        else:
            if step != 0:
                print("WARNING: Trying to move P motor, but motor not detected")

    else:
        print(" Warning motor selection is wrong")

    return


def jump_H(hpos):
    """ makes H motor move to a given absolute position
    does not wait for motor to stop moving before returning """
    write4(H, ADD_GOAL_POSITION + ram_offset, int(hpos))                        # move to H goal position
    return


def jump_V(vpos):
    """ makes V motor move to a given absolute position
    does not wait for motor to stop moving before returning """
    if num_motors >= 2:
        write4(V, ADD_GOAL_POSITION, int(vpos))                                 # move to V goal position if motor exists
    else:
        if convertpostoangle(V, vpos) != 0:                                     # if V motor does not exist, and try to move to non-zero angle, print WARNING
            print("WARNING: Trying to move Motor V that does not exist")
    return


def jump_P(ppos):
    """ makes P motor move to a given absolute position
    does not wait for motor to stop moving before returning """
    if num_motors >= 4:
        write4(P, ADD_GOAL_POSITION, int(ppos))                                 # move to P goal position if motor exists
    else:
        if convertpostoangle(P, ppos) != 0:                                     # if P motor does not exist, and try to move to non-zero angle, print WARNING
            print("WARNING: Trying to move Motor P that does not exist")
    return


def jump_angle_H(hang, accuracy="HIGH"):
    """ makes H motor move to a given absolute angle """
    global OVERSHOOT_H_ANG
    h_pos = convertangletopos(H, hang)                                          # calculate H goal position

    if accuracy == "VERY HIGH":
        overshoot_H = convertangletopos(H, OVERSHOOT_H_ANG) - convertangletopos(H, 0)  # convert overshoot angle to motor position step
        jump_H(int(h_pos) - overshoot_H)                                        # for very high accuracy, overshoot H goal position first
        wait_stop_moving(accuracy)                                              # wait for motor to stop moving

    jump_H(h_pos)                                                               # move to H goal position
    wait_stop_moving(accuracy)                                                  # wait for motor to stop moving
    return


def jump_angle_V(vang, accuracy="HIGH"):
    """ makes V motor move to a given absolute angle """
    global OVERSHOOT_V_ANG
    v_pos = convertangletopos(V, vang)                                          # calculate V goal position

    if num_motors >= 2:
        if accuracy == "VERY HIGH":
            overshoot_V = convertangletopos(V, OVERSHOOT_V_ANG) - convertangletopos(V, 0)  # convert overshoot angle to motor position step
            jump_V(int(v_pos) - overshoot_V)                                    # for very high accuracy, overshoot V goal position first
            wait_stop_moving(accuracy)                                          # wait for motor to stop moving

        jump_V(v_pos)                                                           # move to V goal position if motor exists
        wait_stop_moving(accuracy)                                              # wait for motor to stop moving
    else:
        if vang != 0:                                                           # if V motor does not exist, and try to move to non-zero angle, print WARNING
            print("WARNING: Trying to move Motor V that does not exist")

    return


def jump_angle_P(pang, accuracy="HIGH"):
    """ makes P motor move to a given absolute angle """
    global OVERSHOOT_P_ANG
    p_pos = convertangletopos(P, pang)                                          # calculate P goal position

    if num_motors >= 4:
        if accuracy == "VERY HIGH":
            overshoot_P = convertangletopos(P, OVERSHOOT_P_ANG) - convertangletopos(P, 0)  # convert overshoot angle to motor position step
            jump_P(int(p_pos) - overshoot_P)                                    # for very high accuracy, overshoot P goal position first
            wait_stop_moving(accuracy)                                          # wait for motor to stop moving

        jump_P(p_pos)                                                           # move to P goal position if motor exists
        wait_stop_moving(accuracy)                                              # wait for motor to stop moving
    else:
        if pang != 0:                                                           # if P motor does not exist, and try to move to non-zero angle, print WARNING
            print("WARNING: Trying to move Motor P that does not exist")

    return


def jump_angle(hang, vang, pang, accuracy="HIGH"):
    """ makes all motors move to a given absolute angle """
    global OVERSHOOT_H_ANG, OVERSHOOT_V_ANG, OVERSHOOT_P_ANG

    h_pos = convertangletopos(H, hang)                                                  # calculate H goal position
    overshoot_H = convertangletopos(H, OVERSHOOT_H_ANG) - convertangletopos(H, 0)       # convert overshoot angle to motor position step

    if num_motors >= 2:
        v_pos = convertangletopos(V, vang)                                              # calculate V goal position
        overshoot_V = convertangletopos(V, OVERSHOOT_V_ANG) - convertangletopos(V, 0)   # convert overshoot angle to motor position step

    if num_motors >= 4:
        p_pos = convertangletopos(P, pang)                                              # calculate P goal position
        overshoot_P = convertangletopos(P, OVERSHOOT_P_ANG) - convertangletopos(P, 0)   # convert overshoot angle to motor position step

    if accuracy == "VERY HIGH":
        jump_H(int(h_pos) - overshoot_H)                                        # for very high accuracy, overshoot H goal position first
        if num_motors >= 2:
            jump_V(int(v_pos) - overshoot_V)                                    # for very high accuracy, overshoot V goal position first
            if num_motors >= 4:
                jump_P(int(p_pos) - overshoot_P)                                # for very high accuracy, overshoot V goal position first
        wait_stop_moving(accuracy)                                              # wait for all motors to stop moving

    jump_H(int(h_pos))                                                          # for very high accuracy, overshoot H goal position first
    if num_motors >= 2:
        jump_V(int(v_pos))                                                          # for very high accuracy, overshoot V goal position first
        if num_motors >= 4:
            jump_P(int(p_pos))                                                          # for very high accuracy, overshoot P goal position first
    wait_stop_moving(accuracy)                                                  # wait for all motors to stop moving

    return


def check_move(h_target, v_target, p_target):                                   # check that the move values are in range
    """ check the move is doable """
    ok = 1
    if (abs(h_target) > 180) or \
            ((v_target is not None) and (abs(v_target) > 180)) or \
            ((p_target is not None) and (abs(p_target) > 180)):
        ok = 0
    # else:
    #     print("---->  target values okay")
    return ok


def gim_move(h_target, v_target, p_target, accuracy="HIGH"):                    # move H and V motors to any H,V position in space
    """ make a direct move and measure the move time """
    t0 = time.time()                                                            # record start time
    if check_move(h_target, v_target, p_target) == 1:
        jump_angle(h_target, v_target, p_target, accuracy)                      # do the move
    else:
        print(" ERROR: move location out of valid range")
    t1 = time.time()                                                            # record stop time
    travel_time = (t1 - t0)                                                     # measure travel time
    print(" travel time was : %0.3f seconds" % travel_time)                     # print travel time


def gotoZERO(accuracy="HIGH"):
    """ makes all motors go home """
    print("going to zero position")
    jump_angle(0, 0, 0, accuracy)
    return


# ===========================================================
# ============= MEASUREMENT EQUIPMENT FUNCTIONS =============
# ===========================================================

def select_meas_mode(cur_mode="UNDEFINED"):
    """ select if using SA, SG+SA, or VNA """
    print("\nCurrent measurement mode = %s\n" % cur_mode)
    print("************* MEASUREMENT SETUP *************")
    print("* press <0> for No Instrument")
    print("* press <1> for Spectrum Analyzer only")
    print("* press <2> for SigGen + Spectrum Analyzer")
    print("* press <3> for VNA")
    print("* press <ESC> for no change")
    print("*********************************************")
    valid = False
    while not valid:
        pressedkey = ord(getch())
        if pressedkey == ord('0'):
            meas_mode = "NONE"
            print("NO EQUIPMENT mode selected")
            valid = True
        elif pressedkey == ord('1'):
            meas_mode = 'SA'
            print("Spectrum Analyzer mode selected")
            valid = True
        elif pressedkey == ord('2'):
            meas_mode = 'SG+SA'
            print("Sig Gen + Spectrum Analyzer mode selected")
            valid = True
        elif pressedkey == ord('3'):
            meas_mode = 'VNA'
            print("VNA mode selected")
            valid = True
        elif pressedkey == 27:
            meas_mode = cur_mode
            if meas_mode != "UNDEFINED":
                valid = True
            else:
                print("Must select a valid measurement mode")
    return meas_mode


def select_visa_addr(orig_addr="SIMULATION"):
    """ displays list of connected VISA instruments and selects one """
    print("")
    print("************** INSTRUMENT LIST **************")
    resources = equip.list_resources()                                          # find list of potential instruments
    resources = [x for x in resources if str(x).find('ASRL') == -1]             # only keep resources without "ASRL" in name
    resources.insert(0, 'MANUAL ENTRY (%s)' % orig_addr)                        # pre-pend "MANUAL ENTRY" to the list - used to type in a socket address
    resources.insert(0, 'SIMULATION')                                           # pre-pend "SIMULATION" to the list - used if no instrument connected

    for x in range(0, len(resources), 1):                                       # list all the resources
        if orig_addr == resources[x]:
            print("  >>> %3d) %s" % (x+1, resources[x]))                        # show which equipment is currently selected
        else:
            print("      %3d) %s" % (x+1, resources[x]))
    print("*********************************************")
    print("")

    done = False
    while not done:
        selection = int(input_num("Select instrument or enter <0> for no change: "))
        if selection in range(len(resources)+1):
            if selection == 0:
                new_addr = orig_addr
                done = True
            elif selection == 2:                                                # manual entry
                new_addr = str(six.moves.input("Enter equipment VISA address: "))
                done = True
            else:
                new_addr = str(resources[selection-1])                          # set the name of the GPIB resource, convert from unicode to string
                done = True
        else:
            print("Invalid selection. Please try again")

    print ("")
    print("Measurement instrument selected (addr): %s" % (new_addr))

    return new_addr


def visa(orig_meas_mode, inst):
    """ list all potential VISA instruments connected, select and initialize for measurement """

    orig_addr = inst.addr
    inst.close_instrument()

    meas_mode = select_meas_mode(orig_meas_mode)

    # Spectrum Analyzer mode
    if meas_mode == "SA":
        if orig_meas_mode != meas_mode:
            orig_addr = ["SIMULATION"]                                          # if previous was not SA, set default to SIMULATION

        print("Select Spectrum Analyzer VISA address")
        new_addr = [select_visa_addr(orig_addr[0])]                             # select Spectrum Analyzer

        inst = equip.inst_setup(meas_mode, new_addr)                            # initialize equipment

    # SigGen + SpecAnalyzer mode
    elif meas_mode == "SG+SA":
        if orig_meas_mode != meas_mode:
            orig_addr = ["SIMULATION", "SIMULATION"]                            # if previous was not SG+SA, set default to SIMULATION

        print("\n\nSelect SIG GEN VISA address")
        sg_addr = select_visa_addr(orig_addr[0])                                # select Sig Gen
        print("\n\nSelect SPECTRUM ANALYZER VISA address")
        sa_addr = select_visa_addr(orig_addr[1])                                # select Spectrum Analyzer
        new_addr = [sg_addr, sa_addr]

        inst = equip.inst_setup(meas_mode, new_addr)                            # initialize equipment

    # VNA mode
    elif meas_mode == "VNA":
        if orig_meas_mode != meas_mode:
            orig_addr = ["SIMULATION"]                                          # if previous was not VNA, set default to SIMULATION

        print("Select VNA VISA address")
        new_addr = [select_visa_addr(orig_addr[0])]                             # select VNA

        inst = equip.inst_setup(meas_mode, new_addr)                            # initialize equipment

    # NONE or undefined mode
    else:
        inst = equip.inst_setup(meas_mode, ["SIMULATION"])                      # initialize SIMULATION mode

    if inst.port_open:                                                          # if instrument is open
        print("initializing equipment")
        inst.init_meas()                                                        # initialize instrument for measurement

    return meas_mode, inst


def get_power(inst):
    """ return measured power at a given gimbal (H,V) position or compute value if no instrument connected """

    # readback power from instrument
    if inst.port_open:
        if inst.inst_type.find("SA") > -1:
            inst.set_marker_peak(1)                                             # set the marker to the peak get_power
            val = [round(float(inst.get_marker(1)),2)]                          # readback marker 1 if connected to an instrument
            freq = [float(inst.get_marker_freq(1))]                             # readback marker 1 freq
        elif inst.inst_type.find("VNA") > -1:
            inst.single_trigger()                                               # single trigger and hold
            val, phase = inst.get_s_dbphase()                                   # readback S21
            val = [round(x,2) for x in val]                                     # round values to 2 digits
            freq = inst.get_freq_list()                                         # readback frequency list
            # inst.cont_trigger()

    # compute simulated power level based on (H,V) position
    else:                                                                       # compute DUMMY value based on gimbal position if not connected to instrument
        print("simulated")
        hori_ang = convertpostoangle(H,current_pos(H,1))
        vert_ang = convertpostoangle(V,current_pos(V,1))
        val = [round(((vert_ang ** 2 + 0.6 * hori_ang ** 2) * (-1 / 300.0)),2)] # DUMMY val, when instrument is not connected
        freq = [28.0e9]

    return val, freq


# =================================================
# ============= SWEEP CHECK FUNCTIONS =============
# =================================================

def input_num(prompt, default=None):
    """ prompt for a number and wait until a valid number is returned """
    ok = False
    while not ok:
        s = six.moves.input(prompt)                                                       # display prompt and wait for input, does not crash on empty string six make it 2.x and 3.x compatible
        if len(s) == 0:
            s = str(default)
        try:
            x = float(s)
            ok = True
        except ValueError:
            print ("\n*** ERROR: Please enter a valid number ***\n")
    return x


def check_plot(minh, maxh, minv, maxv, step, pola=None):
    """ check that user plot values are valid """
    ok = 1
    if (minh < -180) or (minv < -180):
        ok = 0
    if (maxh > 180) or (maxv > 180):
        ok = 0
    if (maxh-minh) < 0:
        ok = 0
    if (maxv-minv) < 0:
        ok = 0
    if step > (maxh-minh):
        ok = 0
    if step > (maxv-minv):
        ok = 0
    if step <= 0:
        ok = 0
    if pola is not None:
        if (pola > 180) or (pola < -180):
            ok = 0
    return ok


def check_plot_1d(dir, minh, maxh, minv, maxv, step, pola=None):
    """ check that user plot values are valid for 1D sweep """
    ok = 1
    if (minh < -180) or (minv < -180):
        ok = 0
    if (maxh > 180) or (maxv > 180):
        ok = 0
    if (maxh-minh) < 0:
        ok = 0
    if (maxv-minv) < 0:
        ok = 0
    if dir == "H" and step > (maxh-minh):
        ok = 0
    if dir == "V" and step > (maxv-minv):
        ok = 0
    if step <= 0:
        ok = 0
    if pola is not None:
        if (pola > 180) or (pola < -180):
            ok = 0
    return ok


def check_abort():
    """ check if <ESC> was pressed to abort measurement sweep """
    keypressed = chr(ord(getch()))
    if keypressed == chr(27):
        print("")
        print("Are you sure you want to ABORT? [Y/N]")
        while keypressed not in ['Y', 'N']:
            keypressed = chr(ord(getch().upper()))
        if keypressed == 'Y':
            print("*** ABORTING ***")
            print("")
    else:
        keypressed = ''
    return keypressed == 'Y'


# =================================================
# ================ SWEEP FUNCTIONS ================
# =================================================

def millibox_1dsweep(dir, minh, maxh, minv, maxv, step, pangle, plot, tag, inst, accuracy="HIGH", meas_delay=0, plot_freq=0):
    """ 1D sweep - capture, plot and save the data """

    # print ("millibox_1dsweep: pangle = ", pangle)
    t0 = time.time()                                                            # get the start time for routine
    timeStr = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())                # get day and time to build unique file names
    outdir = 'C:\\SWMilliBox\\MilliBox_plot_data'                               # outdir is C:\SWMilliBox\MilliBox_plot_data
    if not os.path.isdir(outdir):                                               # check if directory exists
        print("*** Creating output directory MilliBox_plot_data ***")
        os.mkdir(outdir)                                                        # create directory if it doesn't exist
    filename = outdir + '\\mbx_capture_' + timeStr +'_1d_'+dir+'_' + tag + '.csv'  # format CSV filename
    print(" Plot data is saved in file : " +str(filename))                      # tell user filename
    csvplot = open(filename, 'w', buffering=1)                                  # open CSV file for write
    capture = csv.writer(csvplot, lineterminator='\n')                          # set line terminator to newline only (no carraige return)

    val, freq = get_power(inst)                                                 # query the frequency points

    if num_motors >= 4:
        capture.writerow(['V', 'actual_V', 'H', 'actual_H', 'P', 'actual_P'] + freq)    # write the column headers to file (include pol)
    else:
        # capture.writerow(['V', 'actual_V', 'H', 'actual_H'] + freq)             # write the column headers to file
        capture.writerow(['V', 'actual_V', 'H', 'actual_H','freq','power'])             # write the column headers to file
    freqIdx = np.abs(np.array(freq) - plot_freq).argmin()                       # find index for value that is closest to plot_freq
    print("\n**** Plotting frequency = %0.3fGHz ****\n" % (freq[freqIdx]/1.0e9))

    num = int(np.floor((maxv-minv)/step))                                       # map of vertical angle iteration
    Vangle = np.linspace(minv,minv+num*step,num+1)                              # [min:step:max] with endpoints inclusive
    num = int(np.floor((maxh-minh)/step))                                       # map of horizontal angle iteration
    Hangle = np.linspace(minh,minh+num*step,num+1)                              # [min:step:max] with endpoints inclusive
    print(" x: V range is = " + str(Vangle))                                    # log tracker
    print(" y: H range is = " + str(Hangle))                                    # log tracker
    if num_motors >= 4:
        print(" p: Polarization position is = " + str(pangle))
        jump_angle_P(pangle, accuracy)

    inst.fix_status()                                                           # check and run calibration, if needed

    if dir == "H":
        heatmap = [np.nan for x in Hangle]                                      # Initialize heatmap array with all point = NaN
        i = 0
        vert = min(Vangle)                                                      # vert angle is fixed during sweep
        jump_angle_V(vert, accuracy)                                            # jump to vert angle
        for hori in Hangle:                                                     # loop for horizontal motion

            if kbhit():                                                         # check if key pressed
                if check_abort():                                               # check if <ESC> pressed
                    gotoZERO(accuracy)                                          # go to home and abort
                    csvplot.close()
                    if six.PY2:
                        plt.close('all')                                        # automatically close plot for Py2.x
                    else:
                        print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
                        plt.ioff()
                        plt.show(block=True)                                    # manually close plot for Py3.x
                    return

            jump_angle_H(hori,accuracy)                                         # move to H position

            time.sleep(meas_delay)                                              # optional delay after movement before measuring
            val, freq = get_power(inst)                                         # #####################  this is where you get the value from measurement ####################

            actual_H = convertpostoangle(H, current_pos(H, 1))                  # record actual absolute position moto H reached
            actual_V = convertpostoangle(V, current_pos(V, 1))                  # record actual absolute position moto V reached

            if num_motors >= 4:
                actual_P = convertpostoangle(P, current_pos(P, 1))
                if len(val) == 1:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))
                else:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))

                entry = [vert, actual_V,  hori, actual_H, pangle, actual_P] + freq + val                     # record a new plot entry

            else:
                if len(val) == 1:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,val[freqIdx]))
                else:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,val[freqIdx]))

                entry = [vert, actual_V,  hori, actual_H] + freq + val                     # record a new plot entry

            capture.writerow(entry)                                             # commit to CSV file
            heatmap[i] = val[freqIdx]                                           # append heatmap with actual captured val
            i += 1                                                              # update counter

            if hori == Hangle[-1]:                                              # last point
                if inst.inst_type == "VNA":
                    inst.cont_trigger()                                         # enable continuous trigger
                gotoZERO(accuracy)                                              # go to (0,0)
                csvplot.close()                                                 # close the CSV file
                print("## THE PLOT WAS SAVED IN FILE :  " + str(filename) + "    ##")  # tell user where to find CSV file
                t1 = time.time()
                print("*** Elapsed time = %0.1f sec ***" % (t1 - t0))
            if plot == 1:
                display_1dplot(dir,Vangle,Hangle,heatmap,vert,hori,plot_freq=freq[freqIdx],pangle=pangle)   # update the line plot after each data point

    elif dir == "V":
        heatmap = [np.nan for x in Vangle]                                      # Initialize heatmap array with all point = NaN
        i = 0
        hori = min(Hangle)                                                      # hori angle is fixed during sweep
        jump_angle_H(hori, accuracy)                                            # jump to hori angle
        for vert in Vangle:                                                     # loop for vertical motion

            if kbhit():                                                         # check if key pressed
                if check_abort():                                               # check if <ESC> pressed
                    gotoZERO(accuracy)                                          # go to home and abort
                    csvplot.close()
                    if six.PY2:
                        plt.close('all')                                        # automatically close plot for Py2.x
                    else:
                        print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
                        plt.ioff()
                        plt.show(block=True)                                    # manually close plot for Py3.x
                    return

            jump_angle_V(vert, accuracy)                                        # move to V position

            time.sleep(meas_delay)                                              # optional delay after movement before measuring
            val, freq = get_power(inst)                                         # #####################  this is where you get the value from measurement ####################

            actual_H = convertpostoangle(H, current_pos(H, 1))                  # record actual absolute position moto H reached
            actual_V = convertpostoangle(V, current_pos(V, 1))                  # record actual absolute position moto V reached

            if num_motors >= 4:
                actual_P = convertpostoangle(P, current_pos(P, 1))
                if len(val) == 1:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))
                else:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))

                entry = [vert, actual_V,  hori, actual_H, pangle, actual_P] + freq + val                     # record a new plot entry

            else:
                if len(val) == 1:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,val[freqIdx]))
                else:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,val[freqIdx]))

                entry = [vert, actual_V,  hori, actual_H] + freq + val                     # record a new plot entry

            capture.writerow(entry)                                             # commit to CSV file
            heatmap[i] = val[freqIdx]                                           # append heatmap with actual captured val
            i += 1                                                              # update counter

            if vert == Vangle[-1]:                                              # last point
                if inst.inst_type == "VNA":
                    inst.cont_trigger()                                         # enable continuous trigger
                gotoZERO(accuracy)                                              # go to (0,0)
                csvplot.close()                                                 # close the CSV file
                print("## THE PLOT WAS SAVED IN FILE :  " + str(filename) + "    ##")  # tell user where to find CSV file
                t1 = time.time()
                print("*** Elapsed time = %0.1f sec ***" % (t1 - t0))           # display elapsed time
            if plot == 1:
                display_1dplot(dir,Vangle,Hangle,heatmap,vert,hori,plot_freq=freq[freqIdx],pangle=pangle)     # update the line plot after each data point

    return


def millibox_hvsweep(min, max, step, pangle, plot, tag, inst, accuracy="HIGH", meas_delay=0, plot_freq=0):
    """ 1D sweep in H and V planes - capture, plot and save the data """

    t0 = time.time()                                                            # get the start time for routine
    timeStr = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())                # get day and time to build unique file names
    outdir = 'C:\\SWMilliBox\\MilliBox_plot_data'                               # outdir is C:\SWMilliBox\MilliBox_plot_data
    if not os.path.isdir(outdir):                                               # check if directory exists
        print("*** Creating output directory MilliBox_plot_data ***")
        os.mkdir(outdir)                                                        # create directory if it doesn't exist
    filename = outdir + '\\mbx_capture_' + timeStr +'_hv_'+ tag +'.csv'         # format CSV filename
    print(" Plot data is saved in file : " +str(filename))                      # tell user filename
    csvplot = open(filename, 'w', buffering=1)                                  # open CSV file for write
    capture = csv.writer(csvplot, lineterminator='\n')                          # set line terminator to newline only (no carraige return)

    val, freq = get_power(inst)                                                 # query the frequency points

    if num_motors >= 4:
        capture.writerow(['V', 'actual_V', 'H', 'actual_H', 'P', 'actual_P'] + freq)    # write the column headers to file (include pol)
    else:
        capture.writerow(['V', 'actual_V', 'H', 'actual_H'] + freq)             # write the column headers to file
    freqIdx = np.abs(np.array(freq) - plot_freq).argmin()                       # find index for value that is closest to plot_freq
    print("\n**** Plotting frequency = %0.3fGHz ****\n" % (freq[freqIdx]/1.0e9))

    num = int(np.floor((max-min)/step))                                         # map of vertical angle iteration
    Vangle = np.linspace(min,min+num*step,num+1)                                # [min:step:max] with endpoints inclusive
    num = int(np.floor((max-min)/step))                                         # map of horizontal angle iteration
    Hangle = np.linspace(min,min+num*step,num+1)                                # [min:step:max] with endpoints inclusive
    print(" x: V range is = " + str(Vangle))                                    # log tracker
    print(" y: H range is = " + str(Hangle))                                    # log tracker
    if num_motors >= 4:
        print(" p: Polarization position is = " + str(pangle))
        jump_angle_P(pangle, accuracy)                                          # make the polarization move

    heatmapV = [np.nan for x in Vangle]                                         # Initialize heatmap array with all point = NaN
    heatmapH = [np.nan for x in Hangle]                                         # Initialize heatmap array with all point = NaN

    i = 0
    vert = 0                                                                    # Hsweep with vert=0
    jump_angle_V(vert, accuracy)                                                # jump to vert angle

    inst.fix_status()                                                           # check and run calibration, if needed

    for hori in Hangle:                                                         # loop for horizontal motion

        if kbhit():                                                             # check if key pressed
            if check_abort():                                                   # check if <ESC> pressed
                gotoZERO(accuracy)                                              # go to home and abort
                csvplot.close()
                if six.PY2:
                    plt.close('all')                                            # automatically close plot for Py2.x
                else:
                    print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
                    plt.ioff()
                    plt.show(block=True)                                        # manually close plot for Py3.x
                return

        jump_angle_H(hori,accuracy)                                             # make the move

        time.sleep(meas_delay)                                                  # optional delay after movement before measuring
        val, freq = get_power(inst)                                             # #####################  this is where you get the value from measurement ####################

        actual_H = convertpostoangle(H, current_pos(H, 1))                      # record actual absolute position moto H reached
        actual_V = convertpostoangle(V, current_pos(V, 1))                      # record actual absolute position moto V reached
        if num_motors >= 4:
            actual_P = convertpostoangle(P, current_pos(P, 1))
            if len(val) == 1:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))
            else:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))

            entry = [vert, actual_V,  hori, actual_H, pangle, actual_P] + val                     # record a new plot entry

        else:
            if len(val) == 1:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,val[freqIdx]))
            else:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,val[freqIdx]))

            entry = [vert, actual_V,  hori, actual_H] + val                     # record a new plot entry

        capture.writerow(entry)                                                 # commit to CSV file

        heatmapH[i] = val[freqIdx]                                              # append heatmap with actual captured val
        i += 1                                                                  # update counter
        if hori == Hangle[-1]:
            if num_motors >= 4:
                jump_angle(0, 0, pangle, accuracy)                              # go to (0,0,pol) after last point
            else:
                gotoZERO(accuracy)                                              # go to (0,0) after last point

        if plot == 1:
            blocking = 0                                                        # set interactive (non-blocking) plot
            display_hvplot(Vangle,Hangle,heatmapV,heatmapH,blocking,plot_freq=freq[freqIdx],pangle=pangle)    # update the line plot after each data point

    i = 0
    hori = 0                                                                    # Vsweep with hori=0
    jump_angle_H(hori, accuracy)                                                # jump to hori angle

    inst.fix_status()                                                           # check and run calibration, if needed

    for vert in Vangle:                                                         # loop for vertical motion

        if kbhit():                                                             # check if key pressed
            if check_abort():                                                   # check if <ESC> pressed
                gotoZERO(accuracy)                                              # go to home and abort
                csvplot.close()
                if six.PY2:
                    plt.close('all')                                            # automatically close plot for Py2.x
                else:
                    print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
                    plt.ioff()
                    plt.show(block=True)                                        # manually close plot for Py3.x
                return

        jump_angle_V(vert,accuracy)                                             # make the move

        time.sleep(meas_delay)                                                  # optional delay after movement before measuring
        val, freq = get_power(inst)                                             # #####################  this is where you get the value from measurement ####################

        actual_H = convertpostoangle(H, current_pos(H, 1))                      # record actual absolute position moto H reached
        actual_V = convertpostoangle(V, current_pos(V, 1))                      # record actual absolute position moto V reached
        if num_motors >= 4:
            actual_P = convertpostoangle(P, current_pos(P, 1))
            if len(val) == 1:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))
            else:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))

            entry = [vert, actual_V,  hori, actual_H, pangle, actual_P] + val                     # record a new plot entry

        else:
            if len(val) == 1:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,val[freqIdx]))
            else:
                print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,val[freqIdx]))

            entry = [vert, actual_V,  hori, actual_H] + val                     # record a new plot entry
        capture.writerow(entry)                                                 # commit to CSV file

        heatmapV[i] = val[freqIdx]                                              # append heatmap with actual captured val
        i += 1                                                                  # update counter

        if vert == Vangle[-1]:                                                  # last point
            if inst.inst_type == "VNA":
                inst.cont_trigger()                                             # enable continuous trigger
            gotoZERO(accuracy)                                                  # go to (0,0)
            t1 = time.time()
            print("*** Elapsed time = %0.1f sec ***" % (t1 - t0))               # display elapsed time
        if plot == 1:
            blocking = 0                                                        # set interactive (non-blocking) plot
            display_hvplot(Vangle,Hangle,heatmapV,heatmapH,blocking,plot_freq=freq[freqIdx],pangle=pangle)    # update the line plot after each data point

    csvplot.close()                                                             # close the CSV file
    print("## THE PLOT WAS SAVED IN FILE :  " +str(filename) + "    ##")        # tell user where to find CSV file

    if plot == 1:
        blocking = 1
        display_hvplot(Vangle,Hangle,heatmapV,heatmapH,blocking,plot_freq=freq[freqIdx],pangle=pangle)        # re-plot data as blocking
    return()


def millibox_2dsweep(minh, maxh, minv, maxv, step, pangle, plot, tag, inst, accuracy="HIGH", meas_delay=0, plot_freq=0):
    """ 2D sweep - capture, plot and save the data """

    t0 = time.time()                                                            # get the start time for routine
    timeStr = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())                # get day and time to build unique file names
    outdir = 'C:\\SWMilliBox\\MilliBox_plot_data'                               # outdir is C:\SWMilliBox\MilliBox_plot_data
    if not os.path.isdir(outdir):                                               # check if directory exists
        print("*** Creating output directory MilliBox_plot_data ***")
        os.mkdir(outdir)                                                        # create directory if it doesn't exist
    filename = outdir + '\\mbx_capture_' + timeStr +'_2d_' + tag + '.csv'       # format CSV filename
    print(" Plot data is save in file : " +str(filename))                       # tell user filename
    csvplot = open(filename, 'w', buffering=1)                                  # open CSV file for write
    capture = csv.writer(csvplot, lineterminator='\n')                          # set line terminator to newline only (no carraige return)

    val, freq = get_power(inst)                                                 # query the frequency points

    if num_motors >= 4:
        capture.writerow(['V', 'actual_V', 'H', 'actual_H', 'P', 'actual_P'] + freq)    # write the column headers to file (include pol)
    else:
        capture.writerow(['V', 'actual_V', 'H', 'actual_H'] + freq)             # write the column headers to file
    freqIdx = np.abs(np.array(freq) - plot_freq).argmin()                       # find index for value that is closest to plot_freq
    print("\n**** Plotting frequency = %0.3fGHz ****\n" % (freq[freqIdx]/1.0e9))

    num = int(np.floor((maxv-minv)/step))                                       # map of vertical angle iteration
    Vangle = np.linspace(minv,minv+num*step,num+1)                              # [min:step:max] with endpoints inclusive
    num = int(np.floor((maxh-minh)/step))                                       # map of horizontal angle iteration
    Hangle = np.linspace(minh,minh+num*step,num+1)                              # [min:step:max] with endpoints inclusive

    heatmap = [[np.nan for x in Vangle] for y in Hangle]                        # Initialize heamap array  with x is V, y is H with all point = NaN
    print(" x: V range is = "  +str(Vangle))                                    # log tracker
    print(" y: H range is = " +str(Hangle))                                     # log tracker
    i = j = 0                                                                   # init loop counters
    if num_motors >= 4:                                                         # if GIM04
        jump_angle_P(pangle, accuracy)                                          # move P to target position
    for vert in Vangle:                                                         # loop for vertical motion
        jump_angle_V(vert, accuracy)                                            # make the vertical move

        inst.fix_status()                                                       # check and run calibration, if needed

        for hori in Hangle:                                                     # loop for horizontal motion

            if kbhit():
                if check_abort():
                    gotoZERO(accuracy)
                    csvplot.close()
                    if six.PY2:
                        plt.close('all')                                        # automatically close plot for Py2.x
                    else:
                        print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
                        plt.ioff()
                        plt.show(block=True)                                    # manually close plot for Py3.x
                    return

            jump_angle_H(hori, accuracy)                                        # make the horizontal move

            time.sleep(meas_delay)                                              # optional delay after movement before measuring
            val, freq = get_power(inst)                                         # #####################  this is where you get the value from measurement ####################

            actual_H = convertpostoangle(H, current_pos(H, 1))                  # record actual absolute position moto H reached
            actual_V = convertpostoangle(V, current_pos(V, 1))                  # record actual absolute position moto V reached
            if num_motors >= 4:
                actual_P = convertpostoangle(P, current_pos(P, 1))                  # record actual absolute position moto V reached
                if len(val) == 1:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))
                else:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| P=%+8.3f| actual_P=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,pangle,actual_P,val[freqIdx]))
                entry = [vert, actual_V,  hori, actual_H, pangle, actual_P] + val                     # record a new plot entry
                capture.writerow(entry)                                             # commit to CSV file
            else:
                if len(val) == 1:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=%0.2f" % (vert,actual_V,hori,actual_H,val[freqIdx]))
                else:
                    print("capture: V=%+8.3f| actual_V=%+8.3f| H=%+8.3f| actual_H=%+8.3f| VALUE=[ ... %0.2f ... ]" % (vert,actual_V,hori,actual_H,val[freqIdx]))

                entry = [vert, actual_V,  hori, actual_H] + val                     # record a new plot entry
                capture.writerow(entry)                                             # commit to CSV file

            heatmap[i][j] = val[freqIdx]                                        # append heatmap with actual captured val
            i += 1                                                              # update H counter

            if vert == Vangle[-1] and hori == Hangle[-1]:                       # last point
                if inst.inst_type == "VNA":
                    inst.cont_trigger()                                         # enable continuous trigger
                gotoZERO(accuracy)                                              # go to (0,0)
                csvplot.close()                                                 # close the CSV file
                print("## THE PLOT WAS SAVED IN FILE :  " + str(filename) + "    ##")  # tell user where to find CSV file
                t1 = time.time()
                print("*** Elapsed time = %0.1f sec ***" % (t1 - t0))           # display elapsed time

            if plot == 2:                                                       # plot multi-line plot after each data point
                display_multilineplot(Vangle, Hangle, heatmap, vert, hori, plot_freq=freq[freqIdx], pangle=pangle)
        j += 1                                                                  # update V counter
        i = 0                                                                   # reset H counter

        if plot == 1:                                                           # interactive plot is not recommended for large plot, as it takes too much CPU resource
            display_surfplot(Vangle, Hangle, heatmap, vert, hori, plot_freq=freq[freqIdx], pangle=pangle)  # pass all values for interactive plot, last slice call to plot will be blocking here
        print("")

    if plot > 0:
        display_millibox3d_ant_pattern(Vangle, Hangle, heatmap, vert, hori, step, plot_freq=freq[freqIdx], pangle=pangle)  # display 3D radiation pattern plot

    return()


def milliboxacc(minh, maxh, minv, maxv, step, accuracy="HIGH"):
    """ capture position accuracy data, and save the data """

    t0 = time.time()                                                            # get the start time for routine
    timeStr = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())                # get day and time to build unique file names
    outdir = 'C:\\SWMilliBox\\MilliBox_plot_data'                               # outdir is C:\SWMilliBox\MilliBox_plot_data
    if not os.path.isdir(outdir):                                               # check if directory exists
        print("*** Creating output directory MilliBox_plot_data ***")
        os.mkdir(outdir)                                                        # create directory if it doesn't exist
    filename = outdir + '\\mbx_accuracy_' + timeStr +'.csv'                     # format CSV filename
    print(" accuracy data is saved in file : " +str(filename))                  # tell user filename

    csvplot = open(filename, 'w', buffering=1)                                  # open CSV file for write
    capture = csv.writer(csvplot, lineterminator='\n')                          # set line terminator to newline only (no carraige return)
    capture.writerow(['V', 'Vquant', 'actual_V', 'H', 'Hquant', 'actual_H', 'Verr', 'Herr', 'Vtoterr', 'Htoterr'])        # write the column headers to file

    spanah = maxh - minh                                                        # calculate horizontal span in degree
    spanav = maxv - minv                                                        # calculate vertical span in degree

    num = int(np.floor((maxv-minv)/step))                                       # map of vertical angle iteration
    Vangle = np.linspace(minv,minv+num*step,num+1)                              # [min:step:max] with endpoints inclusive
    num = int(np.floor((maxh-minh)/step))                                       # map of horizontal angle iteration
    Hangle = np.linspace(minh,minh+num*step,num+1)                              # [min:step:max] with endpoints inclusive
    print(" x: V range is = " + str(Vangle))                                    # log tracker
    print(" y: H range is = " + str(Hangle))                                    # log tracker

    for vert in Vangle:                                                         # loop for vertical motion
        print ("")
        jump_angle_V(vert, accuracy)                                            # jump to vert position
        for hori in Hangle:                                                     # loop for horizontal motion

            if kbhit():
                if check_abort():
                    gotoZERO(accuracy)
                    csvplot.close()
                    if six.PY2:
                        plt.close('all')                                        # automatically close plot for Py2.x
                    else:
                        print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
                        plt.ioff()
                        plt.show(block=True)                                    # manually close plot for Py3.x
                    return

            jump_angle_H(hori, accuracy)                                        # make the move
            hquant = convertpostoangle(H,round(convertangletopos(H,hori)))      # compute the quantized H target angle
            vquant = convertpostoangle(V,round(convertangletopos(V,vert)))      # compute the quantized V target angle
            actual_H = convertpostoangle(H, current_pos(H, 1))
            actual_V = convertpostoangle(V, current_pos(V, 1))
            herr = actual_H - hquant                                            # error between actual and quantized
            verr = actual_V - vquant
            htoterr = actual_H - hori                                           # error between actual and target
            vtoterr = actual_V - vert
            entry = (vert, vquant, actual_V, hori, hquant, actual_H, verr, herr, vtoterr, htoterr)  # record a new plot entry
            print("capture: V=%+7.2f|V_quant=%+7.2f|actual_V=%+7.2f|H=%+7.2f|Hquant=%+7.2f|actual_H=%+7.2f|verr=%+7.2f|herr=%+7.2f|vtoterr=%+7.2f|htoterr=%+7.2f" % entry)
            capture.writerow(list(entry))                                       # commit to CSV file

    csvplot.close()
    print("## THE PLOT WAS SAVED IN FILE :  " +str(filename) + "    ##")        # tell user where to find CSV file
    gotoZERO(accuracy)                                                          # always return to 0,0 when plot is done
    t1 = time.time()
    print("*** Elapsed time = %0.1f sec ***" % (t1-t0))                         # display elapsed time

    return
