#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2020 MILLIWAVE SILICON SOLUTIONS, inc.

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

# Author: Chinh Doan Milliwave Silicon Solutions

import os
import sys
import csv
import six
from mbx_realtimeplot import *

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


def mbx_plot(DISPLAY_TEST_MENU=False):                                          # plotting menu
    """ main menu for MilliBox plotting from file """

    dataDir = 'C:\\SWMilliBox\\MilliBox_plot_data\\'                            # default data directory
    path = ['', dataDir, dataDir+'sample_data\\']                               # search path order

    while True:
        print("")
        print("************* PLOTTING MAIN MENU *********************")
        print("**************** USE KEYBOARD ************************")
        print("* Press <ESC> or <q> to quit plot menu")
        print("* press <a> for Line Plot - 1D sweep")
        print("* press <b> for Line Plot - HV sweep")
        print("* press <c> for Surface Plot - 2D sweep")
        print("* press <d> for Multi-Line Slice Plot - 2D sweep")
        print("* press <e> for 3D Radiation Pattern Plot - 2D sweep")
        print("******************************************************")
        if DISPLAY_TEST_MENU:
            print("**********************  TEST MENU  **********************")
            print("* press <Shift-1> for 1D line plot of sample 1D sweep")
            print("* press <Shift-2> for HV line plot of sample HV sweep")
            print("* press <Shift-3> for surface plot of sample 2D sweep")
            print("* press <Shift-4> for multi-line slice plot of sample 2D sweep")
            print("* press <Shift-5> for 3D radiation pattern plot of sample 2D sweep")
            print("*********************************************************")
            print("* press <Shift-6> for 1D line plot of sample 1D sweep (VNA)")
            print("* press <Shift-7> for HV line plot of sample HV sweep (VNA)")
            print("* press <Shift-8> for surface plot of sample 2D sweep (VNA)")
            print("* press <Shift-9> for multi-line slice plot of sample 2D sweep (VNA)")
            print("* press <Shift-0> for 3D radiation pattern plot of sample 2D sweep (VNA)")
            print("*********************************************************")

        pressedkey = ord(getch().lower())
        loadfile = ''

        if pressedkey == 27 or pressedkey == ord("q"):                          # esc or "q": quit
            print("exit called bye bye!")
            return

        print(chr(pressedkey))

        if pressedkey-ord("a") in range(ord("e")-ord("a")+1):                   # valid option chosen, enter filename
            print("")
            loadfile = six.moves.input("Filename to plot or [ENTER] to cancel: ")
            print("")

        ####################################################
        #  Special TEST modes - to plot pre-defined files  #
        ####################################################

        if pressedkey == ord("!"):                                              # Shift-1: test mode / 1D plot for stored file
            loadfile = 'mbx_capture_1d_H_example.csv'
            pressedkey = ord("a")
        if pressedkey == ord("@"):                                              # Shift-2: test mode / HV plot for stored file
            loadfile = 'mbx_capture_HV_example.csv'
            pressedkey = ord("b")
        if pressedkey == ord("#"):                                              # Shift-3: test mode / surface plot for stored file
            loadfile = 'mbx_capture_2d_full_sweep_example.csv'
            pressedkey = ord("c")
        if pressedkey == ord("$"):                                              # Shift-4: test mode / multi-line plot for stored file
            loadfile = 'mbx_capture_2d_full_sweep_example.csv'
            pressedkey = ord("d")
        if pressedkey == ord("%"):                                              # Shift-5: test mode / radiation pattern for stored file
            loadfile = 'mbx_capture_2d_full_sweep_example.csv'
            pressedkey = ord("e")
        if pressedkey == ord("^"):                                              # Shift-6: test mode / 1D plot for stored VNA file
            loadfile = 'mbx_capture_1d_H_VNA_example.csv'
            pressedkey = ord("a")
        if pressedkey == ord("&"):                                              # Shift-7: test mode / HV plot for stored VNA file
            loadfile = 'mbx_capture_HV_VNA_example.csv'
            pressedkey = ord("b")
        if pressedkey == ord("*"):                                              # Shift-8: test mode / surface plot for stored VNA file
            loadfile = 'mbx_capture_2d_full_sweep_VNA_example.csv'
            pressedkey = ord("c")
        if pressedkey == ord("("):                                              # Shift-9: test mode / multi-line plot for stored VNA file
            loadfile = 'mbx_capture_2d_full_sweep_VNA_example.csv'
            pressedkey = ord("d")
        if pressedkey == ord(")"):                                              # Shift-0: test mode / radiation pattern for stored VNA file
            loadfile = 'mbx_capture_2d_full_sweep_VNA_example.csv'
            pressedkey = ord("e")

        if pressedkey - ord("a") in range(ord("e") - ord("a") + 1):             # valid plot option chosen

            filefound = False
            for pathdir in path:                                                # search through the path in order
                if not filefound:                                               # if file hasn't been found
                    fullfile = pathdir + loadfile                               # append the path to the filename
                    if os.path.isfile(fullfile):
                        filefound = True                                        # found = True
                        loadfile = fullfile                                     # set loadfile with absolute path

            if not filefound:                                                   # if no file found
                if loadfile != '':
                    print("*** ERROR: File %s does not exist! ***" % loadfile)  # if file does not exist, exit routine
                continue
            else:
                print("Plotting file: %s" % loadfile)                           # display filename with full path

            data = []                                                           # format data and plot
            csvplot = open(loadfile, 'r')                                       # open CSV file for read
            capture = csv.reader(csvplot, lineterminator='\n')                  # set line terminator to newline only (no carriage return)
            first = True
            freqList = []
            for row in capture:                                                 # cycle through one row at a time
                if first:                                                       # parse the header to get freq list
                    if row[4] != "P":
                        polFile = False
                        for x in range(len(row)-4):
                            freqList.append(float(row[4+x]))
                    else:
                        polFile = True
                        for x in range(len(row)-6):
                            freqList.append(float(row[6+x]))
                    first = False
                else:
                    data.append(row)                                            # append each row to data

            if len(freqList) > 1:
                freqIdx = [0, int(round(len(freqList)/2)), len(freqList) - 1]   # pick first, mid, last freqs for VNA
                # fixme: expand with more flexibility later
            else:
                freqIdx = [0]

            if pressedkey == ord("a"):                                          # line plot
                for idx in freqIdx:
                    Vangle = []                                                 # initialize the V angle sweep
                    Hangle = []                                                 # initialize the H angle sweep
                    heatmap = []                                                # initialize the sweep data

                    for x in range(len(data)):
                        Vangle.append(float(data[x][0]))                        # append the V angle
                        Hangle.append(float(data[x][2]))                        # append the H angle
                        if not polFile:
                            heatmap.append(float(data[x][4+idx]))                   # append the H data
                        else:
                            heatmap.append(float(data[x][6+idx]))

                    Vangle = np.unique(Vangle)                                  # compute unique V angles
                    Hangle = np.unique(Hangle)                                  # compute unique H angles

                    if len(Vangle) == 1:
                        direction = 'H'                                         # if # V angles=1 -> dir = H
                    elif len(Hangle) == 1:
                        direction = 'V'                                         # if # H angles=1 -> dir = V
                    else:
                        print("*** ERROR: Incorrect data format ***")           # if H>1 and V>1 -> wrong format (2D)
                        continue

                    vert = np.max(Vangle)                                       # set "current point" to last point
                    hori = np.max(Hangle)

                    if polFile:
                        pangle = float(data[0][4])
                    else:
                        pangle = None

                    display_1dplot(direction, Vangle, Hangle, heatmap, vert, hori, plot_freq=freqList[idx], pangle=pangle)   # plot data

            if pressedkey == ord("b"):                                          # HV plot
                for idx in freqIdx:
                    Vangle = []                                                 # initialize the V angle sweep
                    Hangle = []                                                 # initialize the H angle sweep
                    heatmapV = []                                               # initialize the V sweep data
                    heatmapH = []                                               # initialize the H sweep data

                    Hsweep = True                                               # CSV file starts with H data
                    for x in range(len(data)):
                        if Hsweep and (float(data[x][0]) != 0.0):               # check until first time V angle <> 0
                            Hsweep = False
                        if Hsweep:                                              # if H sweep
                            Hangle.append(float(data[x][2]))                    # append the H angle
                            if not polFile:
                                heatmapH.append(float(data[x][4+idx]))              # append the H data
                            else:
                                heatmapH.append(float(data[x][6+idx]))          # append the H data
                        else:                                                   # if V sweep
                            Vangle.append(float(data[x][0]))                    # append the V angle
                            if not polFile:
                                heatmapV.append(float(data[x][4+idx]))          # append the V data
                            else:
                                heatmapV.append(float(data[x][6+idx]))          # append the V data
                    if len(Hangle) <= 1 or len(Vangle) <= 1 or len(Vangle) != len(np.unique(Vangle)):   # sanity check for HV data validity
                        print("*** ERROR: Incorrect data format ***")
                        continue

                    if polFile:
                        pangle = float(data[0][4])
                    else:
                        pangle = None

                    blocking = 1
                    display_hvplot(Vangle, Hangle, heatmapV, heatmapH, blocking, plot_freq=freqList[idx], pangle=pangle)   # plot data

            if chr(pressedkey) in ['c', 'd', 'e']:                              # 2D data
                for idx in freqIdx:
                    Vangle = []                                                 # initialize the V angle sweep
                    Hangle = []                                                 # initialize the H angle sweep
                    heatmap = []                                                # initialize the captured data

                    for x in range(len(data)):
                        Vangle.append(float(data[x][0]))                        # append the V angle
                        Hangle.append(float(data[x][2]))                        # append the H angle
                        if not polFile:
                            heatmap.append(float(data[x][4+idx]))                   # append the captured data
                        else:
                            heatmap.append(float(data[x][6+idx]))                   # append the captured data

                    Vangle = np.unique(Vangle)                                  # compute unique V angles
                    Hangle = np.unique(Hangle)                                  # compute unique H angles

                    if len(Vangle)*len(Hangle) != len(heatmap) or len(Vangle) <= 1 or len(Hangle) <= 1:     # sanity check for 2D data validity
                        print("*** ERROR: Incorrect data format ***")
                        continue

                    heatmap = np.array(heatmap).reshape(len(Vangle), len(Hangle)).transpose().tolist()      # reshape data

                    vert = np.max(Vangle)                                       # set "current point" to last point
                    hori = np.max(Hangle)
                    step = np.max(np.diff(Hangle))                              # compute the step size

                    if polFile:
                        pangle = float(data[0][4])
                    else:
                        pangle = None

                    if pressedkey == ord('c'):
                        display_surfplot(Vangle, Hangle, heatmap, vert, hori, plot_freq=freqList[idx], pangle=pangle)          # 3D surface plot
                    elif pressedkey == ord('d'):
                        display_multilineplot(Vangle, Hangle, heatmap, vert, hori, plot_freq=freqList[idx], pangle=pangle)     # multi-line slice plot
                    elif pressedkey == ord('e'):
                        display_millibox3d_ant_pattern(Vangle, Hangle, heatmap, vert, hori, step, plot_freq=freqList[idx], pangle=pangle)  # 3D radiation pattern plot

            print("")


if __name__ == "__main__":
    mbx_plot()
