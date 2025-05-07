#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
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

# Author: Jeanmarc Laurent Milliwave Silicon Solutions


from __future__ import division                             # division compatibility Python 2.7 and Python 3.6+
import sys
import six
if sys.platform == "win32":                                 # if we run windows, we can use getch from OS
    from msvcrt import getch
else:                                                       # but if we use MACos or Linux we need to create getch()
    def getch():
        x = six.moves.input()
        if len(x) > 1:
            x = chr(0)
            print("too long")
        elif len(x) == 0:
            x = chr(13)     # enter
            print("enter")
        return x
from mbx_functions import *
from mbx_plot import *
import mbx_instrument as equip
import mbx_test_config as config
import pickle

from os import path


H                           = 1                             # Horizontal Motor is ID: 1
V                           = 2                             # Vertical Motor  is ID: 2
R                           = 3                             # Gimbal 3 has a Motor ID: 3 which is a mirror of Motor 2
P                           = 4                             # Gimbal 4 can have a 4th motor for polirization
BAUDRATE                    = 1000000                       # for windows and Linux set to 1000000 for MACOs change BAUDRATE to 57600 and set the motor baudrate accordingly
DEVICENAME                  = "COM3"                        # Check which port is being used on your controller
                                                            # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
MAN_STEP                    = 11.25                         # Initial step size used during manual alignment 128*(360/4096)
ACCURACY                    = "HIGH"                        # set to STANDARD, HIGH, or VERY HIGH for gimbal positional accuracy
DISPLAY_TEST_MENU           = False                         # set to True to display special TEST menu
RELEASE_VER                 = 21.1                          # software release version


print("")
print("MilliBox Software Release: %0.1f" % (RELEASE_VER))   # display SW release version
print("Python Version: " + sys.version)                     # display Python version

if connect(DEVICENAME, BAUDRATE):                           # initiate connection with motors, check communication and register settings
    print("Device connected")
    set_velocity()                                          # initialize velocity using default (max) on all motors
else:
    print("Press any key to terminate...")                  # terminate if error communicating with motor
    getch()
    quit()

num_motors = get_nummotors()
wait_stop_moving(ACCURACY)
print("Found %d motor(s)" % num_motors)
print("Gimbal accuracy setting = %s" % ACCURACY)

print("++++++++++++++++ MilliBox Gimbal is ready  +++++++++++++++")
print("")

# load instrument setup information from previous run
print("choose \'1\' for 44 GHz microwave analyzer, '2' for 9 GHz MA.")
device_selected = ord(getch())
if device_selected == ord("1"):
    meas_fname = "C:\\SWMilliBox\\MBX\\python\\meas_setup_44GHz"
elif device_selected == ord("2"):
    meas_fname = "C:\\SWMilliBox\\MBX\\python\\meas_setup_9GHz"
else:
    print("other keys taken, use default 44 GHz Microwave analyzer...")
    meas_fname = "C:\\SWMilliBox\\MBX\\python\\meas_setup_44GHz"

if not path.isfile(meas_fname):
    meas_mode = "NONE"                                      # if meas_setup file does not exist, default to NONE / SIMULATION
    addr = ["SIMULATION"]                                   # addr is list of VISA addresses
    data = (meas_mode, addr)
    fileObject = open(meas_fname, 'wb')
    pickle.dump(data, fileObject)                           # store the tuple in the file
    fileObject.close()                                      # close the file
    print("measurement mode saved to file")                 # use previous measurement mode on next run
else:
    data = pickle.load(open(meas_fname, "rb"))              # load the previous measurement mode and addr
    if isinstance(data, tuple):                             # check if data is a tuple
        meas_mode = data[0]
        addr = data[1]                                      # addr is list of VISA addresses
    else:
        meas_mode = "NONE"
        addr = ["SIMULATION"]

# initalize VISA instrument control or set to use SIMULATION mode
inst = equip.inst_setup(meas_mode, addr)
inst.init_meas()
# set rbw
print("manuel set freq span 10MHz and rbw 150kHz.")
inst.set_span(10e6)
inst.set_rbw(150000)

print("\n\n******* Measurement Mode = %s *******" % meas_mode)

while True:
    hang = convertpostoangle(H, current_pos(H, 1))
    vang = convertpostoangle(V, current_pos(V, 1))
    pang = convertpostoangle(P, current_pos(P, 1))
    print("")
    print("**************************************************")
    print("*")
    print("*       Mode: %s" % meas_mode)
    print("* Instrument: %s" % inst.addr)
    print("*   Accuracy: %s" % ACCURACY)
    if num_motors >= 4:
        print("*   Position: (%0.2f, %0.2f, %0.2f)" % (hang, vang, pang))
    elif num_motors >= 2:
        print("*   Position: (%0.2f, %0.2f)" % (hang, vang))
    else:
        print("*   Position: (%0.2f)" % hang)
    print("*")
    print("************* MAIN MENU **************************")
    print("************ USE KEYBOARD ************************")
    print("* Press <ESC> or <q> to close ports and quit!")
    if num_motors >= 2:
        print("* use <arrow keys> or <ijkl> to align DUT with laser guide")
    else:
        print("* use <arrow keys> or <jl> to align DUT with laser guide")
    if num_motors >= 4:
        print("* use <[> or <]> to adjust polarization angle")
    print("* use <a> to reduce step size for finer alignment resolution")
    print("* use <s> to increase step size for coarser alignment resolution")
    if num_motors >= 4:
        print("* press <ENTER> key to store H0 V0 P0 position")
        print("* press <h> to go home to last saved H0 V0 P0 home position")
    elif num_motors >= 2:
        print("* press <ENTER> key to store H0 V0 position")
        print("* press <h> to go home to last saved H0 V0 home position")
    else:
        print("* press <ENTER> key to store H0 position")
        print("* press <h> to go home to last saved H0 home position")
    print("* press <g> to print current position")
    if num_motors >= 2:
        print("* press <d> to start default plot H -90 90 V -90 90 Step 15deg ")     # 2D sweep for GIM01 or GIM03 or GIM04
    else:
        print("* press <d> to start default plot H -180 180 Step 10deg")             # single axis sweep for GIM1D
    print("* press <e> to cycle through accuracy setting")
    print("* press <c> to start accuracy position check menu ")
    print("* press <r> to test motor register configuration ")
    print("* press <v> to open the velocity setting menu")
    print("* press <m> to open the direct move travel menu")
    print("* press <b> to change motor baudrate configuration ")
    print("* press <w> to reset offset for home position ")
    print("* press <y> to set measurement mode (VNA/SG+SA/SA/NONE) and set equipment VISA address")
    print("* press <f> to force instrument re-initialization")
    print("* press <x> to get current power measurement")
    print("* press <p> to plot from file")
    print("* press <1> to start a 1-D sweep")
    print("* press <0> to start a -90 to 90 degree benchmark 1-D sweep")
    if num_motors >= 2:                                                         # 2D sweep options available for GIM01 and GIM03
        print("* press <2> to start a 2-D sweep")
        print("* press <3> to start a 1-D sweep in E-plane and H-plane")
    print("*********************************************************")
    if DISPLAY_TEST_MENU:
        print("**********************  TEST MENU  **********************")
        print("* press <Shift-1> to show Gimbal platform")
        print("* press <Shift-2> to test Gimbal full range of motion")
        if num_motors >= 2:
            print("* press <Shift-3> to run a full Gimbal sweep H -180 180 V -180 180 Step 20deg")   # full 2D sweep for GIM01 or GIM03
        else:
            print("* press <Shift-3> to run a full Gimbal sweep H -180 180 Step 5deg")               # full single axis sweep for GIM1D
        if num_motors >= 4:
            print("* press <Shift-4> to test range of X-pol")                   # X-pol rotation for GIM04x
        print("* press <Shift-5> to test Gimbal position settling accuracy")
        print("*********************************************************")

    pressedkey = ord(getch())

    if pressedkey == 224:                                                       # check for arrow keys
        nextkey = ord(getch())
        if nextkey == 72:                                                       # up -> map to "i" for vertical up move
            pressedkey = ord("i")
        elif nextkey == 80:                                                     # down -> map to "k" for vertical down move
            pressedkey = ord("k")
        elif nextkey == 75:                                                     # left -> map to "j" for horizontal left move
            pressedkey = ord("j")
        elif nextkey == 77:                                                     # right -> map to "l" for horizontal right move
            pressedkey = ord("l")

    if pressedkey == ord("i"):                                                  # "i":  vertical up move
        if num_motors >= 2:
            print("up")
            move(V, MAN_STEP, ACCURACY)

    elif pressedkey == ord("k"):                                                # "k": vertical down move
        if num_motors >= 2:
            print("down")
            move(V, MAN_STEP * -1, ACCURACY)

    elif pressedkey == ord("j"):                                                # "j": horizontal left move
        print("left")
        move(H, MAN_STEP * -1, ACCURACY)

    elif pressedkey == ord("l"):                                                # "l": horizontal right move
        print("right")
        move(H, MAN_STEP, ACCURACY)

    elif pressedkey == ord("["):                                                # "[": polarization left
        if num_motors >= 4:
            print("polarization left")
            move(P, MAN_STEP*-1, ACCURACY)

    elif pressedkey == ord("]"):                                                # "]": polarization right
        if num_motors >= 4:
            print("polarization right")
            move(P, MAN_STEP, ACCURACY)

    elif pressedkey == 27 or pressedkey == ord("q"):                            # esc or "q": close port
        gotoZERO(ACCURACY)                                                      # park Gimbal home upon exiting controller

        print("")
        print("Disable TORQUE on motors? [Y/N]")
        key = None                                                              # block on space bar
        while key not in ['Y', 'N']:
            key = chr(ord(getch().upper()))
            if key == 'Y':
                print("disabling torque on all motors")
                disable_torque(H)
                if num_motors >= 2:
                    disable_torque(V)
                # if num_motors >= 3:
                #     disable_torque(R)
                if num_motors >= 4:
                    disable_torque(P)

        print("")
        print("exit called bye bye!")
        inst.close_instrument()                                                 # close all instruments
        exit()

    elif pressedkey == ord("r"):                                                # r: register test program
        print(" check and program gimbal registers")
        test()

    elif pressedkey == ord("h"):                                                # h: go home
        print("0")
        print("go to 0 position")
        gim_move(0, 0, 0, ACCURACY)                                             # move to (0,0,0) and prints move time

    elif pressedkey == ord("a"):                                                # a: reduce step size by half
        print("a")
        MAN_STEP=MAN_STEP/2
        print("step size is now: " +str(MAN_STEP))

    elif pressedkey == ord("s"):                                                # s: increase step size by two
        print("s")
        MAN_STEP=MAN_STEP*2
        print("step size is now: " +str(MAN_STEP))

    elif pressedkey == ord("e"):                                                # e: cycle through accuracy setting
        print("e")
        if ACCURACY == "STANDARD":
            ACCURACY = "HIGH"
        elif ACCURACY == "HIGH":
            ACCURACY = "VERY HIGH"
        elif ACCURACY == "VERY HIGH":
            ACCURACY = "STANDARD"
        print("Gimbal accuracy setting = %s" % ACCURACY)

    elif pressedkey == ord("v"):                                                # v: set velocity
        print("this menu sets rotation velocity")                               # initiates velocity menu
        get_velocity()                                                          # print current velocity settings
        H_VEL = float(input_num("Enter your desired rotation velocity for H in RPM (enter 0 for default): "))
        if num_motors >= 2:
            V_VEL = float(input_num("Enter your desired rotation velocity for V in RPM: (enter 0 for default): "))
        else:
            V_VEL = 0
        if num_motors >= 4:
            P_VEL = float(input_num("Enter your desired rotation velocity for P in RPM: (enter 0 for default): "))
        else:
            P_VEL = 0
        set_velocity(H_VEL, V_VEL, P_VEL)

    elif pressedkey == ord("m"):                                                # m: move to H V menu
        H_TARGET = float(input_num("Enter targeted angle in horizontal plane in degree: "))
        if num_motors >= 2:
            V_TARGET = float(input_num("Enter targeted angle in vertical plane in degree: "))
        else:
            V_TARGET = None
        if num_motors >= 4:
            P_TARGET = float(input_num("Enter targeted angle in polarization plane in degree: "))
        else:
            P_TARGET = None

        if check_move(H_TARGET, V_TARGET, P_TARGET) == 1:
            print("## Please make sure everything is ready to start measurement ##")# warning
            print("#####      Automatic motion of MilliBox will start!!       ####")
            print("##   Press SPACE BAR when all is ready to start plotting     ##")
            key = None
            while key != 32:                                                # wait for space bar
                key = ord(getch())
                if key == 32:
                    gim_move(H_TARGET, V_TARGET, P_TARGET, ACCURACY)                      # make the move

    elif pressedkey == ord("d"):                                                # d: run default plot
        print("d")
        gotoZERO(ACCURACY)                                                      # make sure millibox is reset to (0,0)
        print("## Please make sure everything is ready to start measurement ##")# warning
        print("#####      Automatic motion of MilliBox will start!!       ####")
        print("##   Press SPACE BAR when all is ready to start plotting     ##")
        if sys.platform == "win32":                                             # if we run windows, we can abort with <ESC>
            print("##   Press ESC to abort                                      ##")
        key = None                                                              # block on space bar
        while key != 32:
            key = ord(getch())
            if key == 32:
                if num_motors >= 4:
                    millibox_2dsweep(-90, 90, -90, 90, 15, 0, 1, 'default', inst, ACCURACY)         # start default 2d sweep
                elif num_motors >= 2:
                    millibox_2dsweep(-90, 90, -90, 90, 15, None, 1, 'default', inst, ACCURACY)      # start default 2d sweep
                else:
                    millibox_1dsweep('H', -180, 180, 0, 0, 10, None, 1, 'default', inst, ACCURACY)  # start default 1d sweep

    elif pressedkey == ord("w"):                                                # w: reset the offset for home position.
        print(" WARNING you need to have the gimbal close to its home position to proceed")
        print("press any key to go back to main menu and SPACE BAR to proceed with Offset reset")
        key = ord(getch())
        if key == 32:
            resetoffset()
        else:
            print("back top menu")

    elif pressedkey == ord("b"):                                                # b: change baudrate
        print("### This menu changes the motor communication baudrate ####")
        print("### proceed with caution as you may loose communication with motors ####")
        print("### the baudrate set in the motors and the baudrate in mbx.py global settings have to match ####")
        BRATE = int(input_num("Enter (1) for 57600 kbps, enter (3) for 1 MBps, any other number to exit: "))
        if (BRATE == 1) or (BRATE == 3):
            changerate(BRATE)

    elif pressedkey == ord("g"):                                                # g: get motors current position
        print("g")
        getposition()

    elif pressedkey == 13:                                                      # ENTER: write current position as (0,0) position
        setoffset(H)
        if num_motors >= 2:
            setoffset(V)
            if num_motors >= 4:
                setoffset(P)
        gotoZERO(ACCURACY)
        print("this position is now HOME position")                             # in absolute this is V= 0 H= 0 P=0

    elif pressedkey == ord("y"):                                                # list and select VISA instrument
        (meas_mode, inst) = visa(meas_mode, inst)
        fileObject = open(meas_fname, 'wb')
        data = (meas_mode, inst.addr)
        pickle.dump(data, fileObject)                                           # store the value in the file
        fileObject.close()                                                      # close the file
        print("measurement mode and equipment saved to file")                   # use measurement mode on next run

    elif pressedkey == ord("f"):                                                # force instrument re-initialization
        print("\nresetting instruments\n")
        if inst.port_open:
            inst.init_meas()

    elif pressedkey == ord("x"):                                                # readback motor position and power level
        print("x")
        wait_stop_moving(ACCURACY)

        if num_motors >= 4:
            print("power at (H,V,P) = (%0.1f,%0.1f,%0.1f):" % (convertpostoangle(H,current_pos(H,1)),convertpostoangle(V,current_pos(V,1)),convertpostoangle(P,current_pos(P,1))))
        elif num_motors >= 2:
            print("power at (H,V) = (%0.1f,%0.1f):" % (convertpostoangle(H,current_pos(H,1)),convertpostoangle(V,current_pos(V,1))))
        else:
            print("power at (H) = (%0.1f):" % (convertpostoangle(H,current_pos(H,1))))

        val, freq = get_power(inst)
        # print(val[0],freq[1])
        for i in range(len(val)):
            print("%7.2fGHz : %7.2f" % (freq[i]/1e9,val[i]))

        if meas_mode == "VNA" and inst.port_open:
            print("Setting continuous trigger")
            inst.cont_trigger()                                                 # set to cont sweep after power measurement

    elif pressedkey == ord("p"):                                                # plot from file
        print("p")
        mbx_plot(DISPLAY_TEST_MENU)

    # only benchmark for PAAM board testing
    elif pressedkey == ord("0"):                                                # 0: start 1-D sweep menu
        gotoZERO(ACCURACY)
        print("\n\n************ 1-D Single Direction Sweep ************\n")
        print("Plot display options:")
        print("  0 - no interactive plot")                                      # no graphic - save data to CSV file only
        print("  1 - interactive plot")                                         # line plot
        print("")
        # PLOT = -1
        # while PLOT not in [0,1]:
        #     PLOT = int(input_num("Select the plot display option: "))
        PLOT = 1
        print("")

        MINH = MAXH = MINV = MAXV = POLA = 0
        STEP = 10
        DIR = 'H'
        while check_plot_1d(DIR, MINH, MAXH, MINV, MAXV, STEP, POLA) == 0:      # loop until valid data is entered
            if num_motors >= 2:
                print("<H>orizontal or <V>ertical sweep?")
                DIR = None
                while DIR not in ['H', 'V']:
                    DIR = chr(ord(getch().upper()))
            else:
                DIR = "H"
            if DIR == "H":
                if num_motors >= 2:
                    MINV = float(input_num("Enter your FIXED angle in vertical plane in degree: "))
                else:
                    MINV = 0.0
                MAXV = MINV
                # MINH = float(input_num("Enter your start angle in horizontal plane in degree: "))
                # MAXH = float(input_num("Enter your last angle in horizontal plane in degree: "))
                # STEP = float(input_num("Enter your step size in degree : "))          # capture user entries for H sweep
                MINH = -90
                MAXH = 90
                STEP = 1 #float(input_num("Enter your step size in degree : "))          # capture user entries for H sweep
                if num_motors >= 4:
                    POLA = float(input_num("Enter your polarization position in degree : "))
                else:
                    POLA = None
            elif DIR == "V":
                MINH = float(input_num("Enter your FIXED angle in horizontal plane in degree: "))
                MAXH = MINH
                MINV = float(input_num("Enter your start angle in vertical plane in degree: "))
                MAXV = float(input_num("Enter your last angle in vertical plane in degree: "))
                STEP = float(input_num("Enter your step size in degree : "))          # capture user entries for V sweep
                if num_motors >= 4:
                    POLA = float(input_num("Enter your polarization position in degree : "))
                else:
                    POLA = None
            if check_plot_1d(DIR, MINH, MAXH, MINV, MAXV, STEP, POLA) == 0:
                print("\n\n#####################################################################")
                print("##    ERROR :  THOSE VALUES CAN'T PLOT, Please try other values    ##")
                print("#####################################################################\n\n")

        print("")
        tag = six.moves.input("Enter a tag to append to filename (e.g 'n2' for 2 elements enabled): ")
        print("")

        config.millibox_1dsweep_wrapper(DIR, MINH, MAXH, MINV, MAXV, STEP, POLA, PLOT, tag, inst, ACCURACY)   # start plot with user inputs

    elif pressedkey == ord("1"):                                                # 1: start 1-D sweep menu
        gotoZERO(ACCURACY)
        print("\n\n************ 1-D Single Direction Sweep ************\n")
        print("Plot display options:")
        print("  0 - no interactive plot")                                      # no graphic - save data to CSV file only
        print("  1 - interactive plot")                                         # line plot
        print("")
        PLOT = -1
        while PLOT not in [0,1]:
            PLOT = int(input_num("Select the plot display option: "))
        print("")

        MINH = MAXH = MINV = MAXV = POLA = 0
        STEP = 10
        DIR = 'H'
        while check_plot_1d(DIR, MINH, MAXH, MINV, MAXV, STEP, POLA) == 0:      # loop until valid data is entered
            if num_motors >= 2:
                print("<H>orizontal or <V>ertical sweep?")
                DIR = None
                while DIR not in ['H', 'V']:
                    DIR = chr(ord(getch().upper()))
            else:
                DIR = "H"
            if DIR == "H":
                if num_motors >= 2:
                    MINV = float(input_num("Enter your FIXED angle in vertical plane in degree: "))
                else:
                    MINV = 0.0
                MAXV = MINV
                MINH = float(input_num("Enter your start angle in horizontal plane in degree: "))
                MAXH = float(input_num("Enter your last angle in horizontal plane in degree: "))
                STEP = float(input_num("Enter your step size in degree : "))          # capture user entries for H sweep
                if num_motors >= 4:
                    POLA = float(input_num("Enter your polarization position in degree : "))
                else:
                    POLA = None
            elif DIR == "V":
                MINH = float(input_num("Enter your FIXED angle in horizontal plane in degree: "))
                MAXH = MINH
                MINV = float(input_num("Enter your start angle in vertical plane in degree: "))
                MAXV = float(input_num("Enter your last angle in vertical plane in degree: "))
                STEP = float(input_num("Enter your step size in degree : "))          # capture user entries for V sweep
                if num_motors >= 4:
                    POLA = float(input_num("Enter your polarization position in degree : "))
                else:
                    POLA = None
            if check_plot_1d(DIR, MINH, MAXH, MINV, MAXV, STEP, POLA) == 0:
                print("\n\n#####################################################################")
                print("##    ERROR :  THOSE VALUES CAN'T PLOT, Please try other values    ##")
                print("#####################################################################\n\n")

        print("")
        tag = six.moves.input("Enter a tag to append to filename or [ENTER] for no tag: ")
        print("")

        config.millibox_1dsweep_wrapper(DIR, MINH, MAXH, MINV, MAXV, STEP, POLA, PLOT, tag, inst, ACCURACY)   # start plot with user inputs

    elif (pressedkey == ord("2")) and num_motors >= 2:                          # 2: start 2-D sweep menu
        gotoZERO(ACCURACY)
        print("This is your zero position: center of the plot")
        print("\n\n************ 2-Axis Sweep ************\n")
        print("Plot display options:")
        print("  0 - no interactive plot display")                              # no graphic - save data to CSV file only
        print("  1 - 3d surface plot")                                          # 3D surface plot + 3D radiation pattern
        print("  2 - multi-trace line plot")                                    # multi-trace line plot + 3D radiation pattern
        print("  3 - 3d radiation pattern ONLY")                                # 3D radiation pattern only
        print("")
        PLOT = -1
        while PLOT not in [0,1,2,3]:
            PLOT = int(input_num("Select the plot display option: "))
        print("")

        MINH = MAXH = MINV = MAXV = POLA = 0
        STEP = 10
        while check_plot(MINH, MAXH, MINV, MAXV, STEP, POLA) == 0:              # loop until valid data is entered
            MINH = float(input_num("Enter your start angle in horizontal plane in degree: "))
            MAXH = float(input_num("Enter your last angle in horizontal plane in degree: "))
            MINV = float(input_num("Enter your start angle in vertical plane in degree: "))
            MAXV = float(input_num("Enter your last angle in vertical plane in degree: "))
            STEP = float(input_num("Enter your step size in degree : "))              # capture user entries
            if num_motors >= 4:
                POLA = float(input_num("Enter your polarization position in degree : "))
            else:
                POLA = None

            if check_plot(MINH, MAXH, MINV, MAXV, STEP, POLA) == 0:
                print("\n\n#####################################################################")
                print("##    ERROR :  THOSE VALUES CAN'T PLOT, Please try other values    ##")
                print("#####################################################################\n\n")

        print("")
        tag = six.moves.input("Enter a tag to append to filename or [ENTER] for no tag: ")
        print("")

        config.millibox_2dsweep_wrapper(MINH, MAXH, MINV, MAXV, STEP, POLA, PLOT, tag, inst, ACCURACY)  # start plot with user inputs

    elif pressedkey == ord("3") and num_motors >= 2:                            # 3: start 1-D plot menu for E- and H-plane
        gotoZERO(ACCURACY)
        print("\n\n************ 1-D Single Direction Sweep in E-plane and H-plane ************\n")
        print("Plot display options:")
        print("  0 - no interactive plot")                                      # no graphic - save data to CSV file only
        print("  1 - interactive plot")                                         # line plot
        print("")
        PLOT = -1
        while PLOT not in [0,1]:
            PLOT = int(input_num("Select the plot display option: "))
        print("")

        MIN = MAX = POLA = 0
        STEP = 10
        while check_plot(MIN, MAX, MIN, MAX, STEP, POLA) == 0:
            MIN = float(input_num("Enter your start angle in degree: "))
            MAX = float(input_num("Enter your last angle in degree: "))
            STEP = float(input_num("Enter your step size in degree : "))              # capture user entries
            if num_motors >= 4:
                POLA = float(input_num("Enter your polarization position in degree : "))
            else:
                POLA = None
            if check_plot(MIN, MAX, MIN, MAX, STEP, POLA) == 0:
                print("\n\n#####################################################################")
                print("##    ERROR :  THOSE VALUES CAN'T PLOT, Please try other values    ##")
                print("#####################################################################\n\n")

        print("")
        tag = six.moves.input("Enter a tag to append to filename or [ENTER] for no tag: ")
        print("")

        config.millibox_hvsweep_wrapper(MIN, MAX, STEP, POLA, PLOT, tag, inst, ACCURACY)  # start plot with user inputs

    elif pressedkey == ord("c"):                                                # c: start accuracy plot menu
        gotoZERO(ACCURACY)
        print("This is your zero position: center of the plot")
        check_ok = 0
        while check_ok == 0:
            MINH = float(input_num("Enter your start angle in horizontal plane in degree: "))
            MAXH = float(input_num("Enter your last angle in horizontal plane in degree: "))
            if num_motors >= 2:
                MINV = float(input_num("Enter your start angle in vertical plane in degree: "))
                MAXV = float(input_num("Enter your last angle in vertical plane in degree: "))
            else:
                MINV = MAXV = 0
            STEP = float(input_num("Enter your step size in degree : "))        # capture user entries
            if num_motors >= 2:
                check_ok = check_plot(MINH, MAXH, MINV, MAXV, STEP)
            else:
                check_ok = check_plot_1d('H', MINH, MAXH, MINV, MAXV, STEP)
            if check_ok == 1:
                print("## Please make sure everything is ready to start measurement ##")# warning
                print("#####      Automatic motion of MilliBox will start!!       ####")
                print("##   Press SPACE BAR when all is ready to start plotting     ##")
                if sys.platform == "win32":                                     # if we run windows, we can abort with <ESC>
                    print("##   Press ESC to abort                                      ##")
                key = None
                while key != 32:                                                # wait for space bar
                    key = ord(getch())
                    if key == 32:
                        milliboxacc(MINH, MAXH, MINV, MAXV, STEP, ACCURACY)     # start position accuracy check with user inputs
            else:
                print("\n\n#####################################################################")
                print("##    ERROR :  THOSE VALUES CAN'T PLOT, Please try other values    ##")
                print("#####################################################################\n\n")

    # test modes
    elif pressedkey == ord("!"):                                                # Shift-1: test mode, move to -110deg angle to show platform
        jump_angle(-110, 0, 0)
    elif pressedkey == ord("@"):                                                # Shift-2: test mode, demonstrate range of gimbal
        gotoZERO()
        jump_angle_H(-180)
        jump_angle_H(180)
        jump_angle_H(0)
        if num_motors >= 2:
            jump_angle_V(-180)
            jump_angle_V(180)
            jump_angle_V(0)
            if num_motors >= 4:
                jump_angle_P(0)
                jump_angle_P(-90)
                jump_angle_P(0)
        gotoZERO()
    elif pressedkey == ord("#"):                                                # Shift-3: test mode, full sweep -180 180 -180 180 20
        gotoZERO(ACCURACY)                                                      # make sure millibox is reset to (0,0)
        print("## Please make sure everything is ready to start measurement ##")# warning
        print("#####      Automatic motion of MilliBox will start!!       ####")
        print("##   Press SPACE BAR when all is ready to start plotting     ##")
        if sys.platform == "win32":                                             # if we run windows, we can abort with <ESC>
            print("##   Press ESC to abort                                      ##")
        key = None                                                              # block on space bar
        while key != 32:
            key = ord(getch())
            if key == 32:
                if num_motors >= 4:
                    millibox_2dsweep(-180, 180, -180, 180, 20, 0, 1, 'full', inst, ACCURACY)   # start full 2d sweep
                elif num_motors >= 2:
                    millibox_2dsweep(-180, 180, -180, 180, 20, None, 1, 'full', inst, ACCURACY)   # start full 2d sweep
                else:
                    millibox_1dsweep('H', -180, 180, 0, 0, 5, None, 1, 'full', inst, ACCURACY)    # start full 1d sweep

    elif pressedkey == ord("$"):                                                # Shift-4: test mode, x-pol demonstration
        if num_motors >= 4:
            jump_angle(-60, 0, 0)
            jump_angle_P(0)
            jump_angle_P(-180)                                                  # clockwise 180deg rotation
            time.sleep(1)
            jump_angle_P(0)
            time.sleep(1)
            jump_angle_P(-180)                                                  # clockwise 180deg rotation
            time.sleep(1)
            jump_angle_P(0)

    elif pressedkey == ord("%"):                                                # Shift-5: test mode, check move accuracy settling
        gotoZERO(ACCURACY)
        jump_angle_H(-180, ACCURACY)
        jump_angle_H(180, ACCURACY)
        jump_angle_H(0, ACCURACY)
        if num_motors >= 2:
            jump_angle_V(-180, ACCURACY)
            jump_angle_V(180, ACCURACY)
            jump_angle_V(0, ACCURACY)
            if num_motors >= 4:
                jump_angle_P(0, ACCURACY)
                jump_angle_P(-90, ACCURACY)
                jump_angle_P(0, ACCURACY)
        gotoZERO(ACCURACY)
