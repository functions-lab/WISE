

################################################################################
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

# Author: Jeanmarc Laurent Milliwave Silicon Solutions


# IMPORTS
import numpy as np                                                              # matplotlib needs numpy fucntions
import matplotlib.pyplot as plt                                                 # matplotlib for 3D display
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import time
import six


# matplotlib specific plotting delays - different for Python2.x vs. Python3.x
if six.PY2:
    # print("Setting plt_pause = 1e-3")
    plt_pause = 1e-3                                                            # matplotlib: Py2.x - delay=1e-3
else:
    # print("Setting plt_pause = 1e-1")                                           # matplotlib: Py3.x - delay=1e-1
    plt_pause = 1e-1


def display_surfplot(Vang, Hang, data, vert, hori, plot_freq=0, pangle=None):
    """ 3D surface plot with last plot iteration blocking """

    plt.ion()                                                                   # turn on plot interactive, makes graph non blocking
    fig = plt.figure(1)                                                         # plot in figure 1
    plt.clf()                                                                   # clear figure before plotting new one

    ax = plt.axes(projection='3d')                                              # 3D projection
    ax.set_xlabel('Vertical angle')                                             # label X axis as Vertical
    ax.set_ylabel('Horizontal angle')                                           # label Y axis as Horizontal
    ax.set_zlabel("Power (dB)")                                                 # label z axis as captured data
    X, Y = np.meshgrid(Vang , Hang)                                             # define X Y grid
    # print("array data is: " +str(data))                                       # for debug print captured array
    zs = np.array(data)                                                         # parse captured array
    # print("Shape X is" +str(X.shape))                                         # for debug get X Y shape
    Z = zs.reshape(X.shape)                                                     # reshape the array to X Y shape
    Z[np.isnan(Z)] = np.nanmin(Z)                                               # set all NaN values to lowest value (ignoring NaN)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=False, alpha=0.5)
    if pangle is None:
        if plot_freq != 0:
            plt.title("%0.2fGHz" % (plot_freq/1e9))
    else:
        if plot_freq != 0:
            plt.title("%0.2fGHz -- Pol=%g" % (plot_freq/1e9,pangle))
        else:
            plt.title("Pol=%g" % pangle)

    plt.draw()                                                                  # draw the surface on figure 1
    plt.pause(plt_pause)                                                             # allow time for the drawing to show on screen
    time.sleep(0.01)

    if vert < Vang[len(Vang)-1] or hori < Hang[len(Hang)-1]:                    # intermediate plot
        plt.show()

    else:                                                                       # last plot becomes blocking
        print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")
        plt.ioff()
        plt.show()                                                              # closing the plot unblock the function and go to menu
# to do : save plot picture
    return()


def display_multilineplot(Vang, Hang, data, vert, hori, plot_freq=0, pangle=None):
    """ multiple line plot with last plot iteration blocking """

    plt.ion()                                                                   # turn on plot interactive, makes graph non blocking
    fig = plt.figure(1)                                                         # plot in figure 1
    plt.clf()                                                                   # clear figure before plotting new one

    curVIdx = max(np.where(Vang == vert)[0])                                    # find the index for the current vertical angle
    curHIdx = max(np.where(Hang == hori)[0])                                    # find the index for the current horizontal angle

    X = Hang                                                                    # plot individual slices vs. H angle
    zs = np.array(data)                                                         # parse captured array
    Z = zs.reshape(len(Hang),len(Vang))                                         # reshape the array to X Y shape

    plt.clf()                                                                   # clear current figure; replot from scratch
    plt.plot(X,Z,color='0.6',marker='.',linestyle='-')                          # plot all of the curves in GRAY
    plt.xlabel('Horizontal angle')
    plt.ylabel("Power (dB)")
    if pangle is None:
        if plot_freq == 0:
            plt.title("(H,V)=(%g,%g):   Power = %0.2fdBm" % (hori,vert,Z[curHIdx][curVIdx]))    # display current point in title
        else:
            plt.title("%0.2fGHz\n(H,V)=(%g,%g):   Power = %0.2fdBm" % (plot_freq/1e9,hori,vert,Z[curHIdx][curVIdx]))    # display current point in title
    else:
        if plot_freq == 0:
            plt.title("Pol=%g\n(H,V)=(%g,%g):   Power = %0.2fdBm" % (pangle,hori,vert,Z[curHIdx][curVIdx]))  # display current point in title
        else:
            plt.title("%0.2fGHz -- Pol=%g\n(H,V)=(%g,%g):   Power = %0.2fdBm" % (plot_freq/1e9,pangle,hori,vert,Z[curHIdx][curVIdx]))  # display current point in title
    plt.grid(True)                                                              # turn on grid

    if vert < Vang[len(Vang)-1] or hori < Hang[len(Hang)-1]:                    # intermediate plot
        plt.plot(X, Z[:, curVIdx], 'r.-',linewidth=3)                           # plot the current curve in RED
        plt.draw()                                                              # draw the plot
        plt.pause(plt_pause)                                                         # allow time for the drawing to show on screen
        time.sleep(0.01)                                                        #
        plt.show()

    else:                                                                       # last plot becomes blocking
        print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")

        hmaxidx = np.where(Z == np.amax(Z))[0][0]                               # find H angle for peak power
        vmaxidx = np.where(Z == np.amax(Z))[1][0]                               # find V angle for peak power
        if pangle is None:
            if plot_freq == 0:
                plt.title("Peak @ (H,V)=(%g,%g):   Power = %0.2fdBm" % (Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
            else:
                plt.title("%0.2fGHz\nPeak @ (H,V)=(%g,%g):   Power = %0.2fdBm" % (plot_freq/1e9,Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
        else:
            if plot_freq == 0:
                plt.title("Pol=%g\nPeak @ (H,V,P)=(%g,%g):   Power = %0.2fdBm" % (pangle,Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
            else:
                plt.title("%0.2fGHz -- Pol=%g\nPeak @ (H,V)=(%g,%g):   Power = %0.2fdBm" % (plot_freq/1e9,pangle,Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
        plt.plot(Hang[hmaxidx],Z[hmaxidx][vmaxidx],'ro')                        # plot the location of the peak
        plt.draw()                                                              # draw the plot
        plt.pause(plt_pause)                                                         # allow time for the drawing to show on screen
        time.sleep(0.01)                                                        #

        plt.ioff()
        plt.show()                                                              # closing the plot unblock the function and go to menu

# to do : save plot picture
    return()


def display_1dplot(dir, Vang, Hang, data, vert, hori, plot_freq=0, block_final=True, pangle=None):
    """ single line plot with last plot iteration blocking """

    plt.ion()                                                                   # turn on plot interactive, makes graph non blocking
    fig = plt.figure(1)                                                         # plot in figure 1
    plt.clf()                                                                   # clear figure before plotting new one

    curVIdx = max(np.where(Vang == vert)[0])                                    # find the index for the current vertical angle
    curHIdx = max(np.where(Hang == hori)[0])                                    # find the index for the current horizontal angle

    Z = np.array(data)                                                          # parse captured array

    if dir == "H":
        plt.plot(Hang,Z,color='0.6',marker='.',linestyle='-')                   # plot the curve in GRAY
        plt.xlabel('Horizontal angle')
        if pangle is None:
            if plot_freq == 0:
                plt.title("(H,V)=(%g,%g):   Power = %0.2f dBm" % (hori, vert, Z[curHIdx]))                              # display current point in title
            else:
                plt.title("%0.2fGHz\n(H,V)=(%g,%g):   Power = %0.2f dBm" % (plot_freq/1e9, hori, vert, Z[curHIdx]))   # display current point in title
        else:
            if plot_freq == 0:
                plt.title("Pol=%g\n(H,V)=(%g,%g):   Power = %0.2f dBm" % (pangle, hori, vert, Z[curHIdx]))                              # display current point in title
            else:
                plt.title("%0.2fGHz -- Pol=%g\n(H,V)=(%g,%g):   Power = %0.2f dBm" % (plot_freq/1e9, pangle, hori, vert, Z[curHIdx]))   # display current point in title
    elif dir == "V":
        plt.plot(Vang,Z,color='0.6',marker='.',linestyle='-')                   # plot the curve in GRAY
        plt.xlabel('Vertical angle')
        if pangle is None:
            if plot_freq == 0:
                plt.title("(H,V)=(%g,%g):   Power = %0.2f dBm" % (hori, vert, Z[curHIdx]))                              # display current point in title
            else:
                plt.title("%0.2fGHz\n(H,V)=(%g,%g):   Power = %0.2f dBm" % (plot_freq/1e9, hori, vert, Z[curHIdx]))   # display current point in title
        else:
            if plot_freq == 0:
                plt.title("Pol=%g\n(H,V)=(%g,%g):   Power = %0.2f dBm" % (pangle, hori, vert, Z[curHIdx]))                              # display current point in title
            else:
                plt.title("%0.2fGHz -- Pol=%g\n(H,V)=(%g,%g):   Power = %0.2f dBm" % (plot_freq/1e9, pangle, hori, vert, Z[curHIdx]))   # display current point in title

    plt.ylabel("Power (dB)")
    plt.grid(True)                                                              # turn grid on
    plt.draw()                                                                  # draw the surface on figure 1
    plt.pause(plt_pause)                                                             # allow time for the drawing to show on screen
    time.sleep(0.01)

    if vert < Vang[len(Vang)-1] or hori < Hang[len(Hang)-1]:                    # intermediate plot
        plt.show()

    else:                                                                       # last plot becomes blocking
        maxidx = np.where(Z == np.amax(Z))[0][0]                                # find angle for peak power
        if dir == "H":
            hmaxidx = maxidx
            vmaxidx = 0
            plt.plot(Hang[hmaxidx], Z[hmaxidx], 'ro')                           # plot the location of the peak
        elif dir == "V":
            vmaxidx = maxidx
            hmaxidx = 0
            plt.plot(Vang[vmaxidx], Z[vmaxidx], 'ro')                           # plot the location of the peak
        if pangle is None:
            if plot_freq == 0:
                plt.title("Peak @ (H,V)=(%g,%g):   Power = %0.2f dBm" % (Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
            else:
                plt.title("%0.2fGHz\nPeak @ (H,V)=(%g,%g):   Power = %0.2f dBm" % (plot_freq/1e9, Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
        else:
            if plot_freq == 0:
                plt.title("Pol=%g\nPeak @ (H,V)=(%g,%g):   Power = %0.2f dBm" % (pangle,Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location
            else:
                plt.title("%0.2fGHz -- Pol=%g\nPeak @ (H,V)=(%g,%g):   Power = %0.2f dBm" % (plot_freq/1e9, pangle, Hang[hmaxidx],Vang[vmaxidx],np.amax(Z)))  # print the peak power and location

        if block_final:
            print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")

            plt.ioff()
            plt.show()                                                              # closing the plot unblock the function and go to menu

# to do : save plot picture
    return()


def display_hvplot(Vang, Hang, dataV, dataH, blocking, plot_freq=0, block_final=True, pangle=None):
    """ line plot for E- and H-plane with last plot iteration blocking """

    plt.ion()                                                                   # turn on plot interactive, makes graph non blocking
    fig = plt.figure(1)                                                         # plot in figure 1
    plt.clf()                                                                   # clear figure before plotting new one

    ZV = np.array(dataV)                                                        # parse captured array
    ZH = np.array(dataH)                                                        # parse captured array

    plt.plot(Hang,ZH,color='0.6',marker='.',linestyle='-')                      # plot H sweep in GRAY
    plt.plot(Vang,ZV,color='r',marker='.',linestyle='-')                        # plot V sweep in RED
    plt.xlabel('angle [deg]')
    plt.legend(['H sweep','V sweep'])
    if pangle is None:
        if plot_freq != 0:
            plt.title("%0.2fGHz" % (plot_freq/1e9))
    else:
        if plot_freq != 0:
            plt.title("%0.2fGHz -- Pol=%g" % (plot_freq/1e9,pangle))
        else:
            plt.title("Pol=%g" % (pangle))


    plt.ylabel("Power (dB)")
    plt.grid(True)                                                              # turn on grid
    plt.draw()                                                                  # draw the surface on figure 1
    plt.pause(plt_pause)                                                             # allow time for the drawing to show on screen
    time.sleep(0.01)

    if not blocking:                                                            # intermediate plot
        plt.show()

    else:                                                                       # last plot becomes blocking
        if block_final:
            print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")

            plt.ioff()
            plt.show()                                                              # closing the plot unblock the function and go to menu

# to do : save plot picture
    return()


def display_3d_ant_pattern(gain, phi, theta, plot_range, step, plot_freq=0, pangle=None):
    """ 3d radiation pattern plot based on SPHERICAL COORDINATES
    this function will plot all of the power with a total dynamic range of plot_range
    the values that will plot are from [max(gain)-plot_range ... max(gain)]
    all other points are set to minimum """

    plt.ion()                                                                   # turn on plot interactive, makes graph non blocking
    fig = plt.figure(1, figsize=(8,6))                                          # plot in figure 1, make default size larger (8" x 6")
    plt.clf()                                                                   # clear figure before plotting new one

    ax = plt.axes(projection='3d')                                              # 3D projection
    ax.set_aspect('auto')                                                       # fixme: 3d axis do not support "equal"
    ax.margins(x=0, y=-0.25)                                                    # reduce margins to make plot larger

    color_scale = 10.0
    color_max = color_scale * plot_range                                        # color_max = dynamic_range to plot * color_scale
    gain_max = np.ceil(np.nanmax(gain))                                         # determine the max(gain)
    c = color_scale*(gain - gain_max + plot_range)                              # re-scale everything based on max(gain)
    c[c < 0] = 0                                                                # all small values forced to 0

    y, z = np.meshgrid(np.linspace(-color_max,color_max,3),np.linspace(-color_max,color_max,3))     # color_max is also the maximum spherical magnitude
    x = np.zeros(y.size)
    x = x.reshape(y.shape)
    ax.plot_wireframe(x,y,z,color='black')                                      # plot reference DUT on YZ-plane (x=0) with black wireframe

    x = c * np.sin(theta) * np.cos(phi)                                         # convert (gain,phi,theta) to (x,y,z)
    y = c * np.sin(theta) * np.sin(phi)                                         #
    z = c * np.cos(theta)                                                       #

    stride = int(max(1,6/int(step)))                                            # if step<4, skip some data points for faster plotting
    surf = ax.plot_surface(x,y,z,facecolors=cm.jet(c/color_max),shade=False,rstride=stride, cstride=stride, antialiased=False,
                    linewidth=0.01, alpha=0.85)                                 # plot semi-transparent with color proportional to gain
    surf.set_edgecolors('k')                                                    # display black edges
    mag = 1.3                                                                   # zoom in on image for nice size
    ax.set_xlim([-color_max/mag,color_max/mag])
    ax.set_ylim([-color_max/mag,color_max/mag])
    ax.set_zlim([-color_max/mag,color_max/mag])
    ax.view_init(elev=15, azim=-15)                                             # set default camera angle
    plt.axis('off')
    if pangle is None:
        if plot_freq == 0:
            ax.set_title('3D radiation pattern')
        else:
            ax.set_title('%0.2fGHz\n\n3D radiation pattern' % (plot_freq/1e9))
    else:
        if plot_freq == 0:
            ax.set_title('Pol=%g\n\n3D radiation pattern' % (pangle))
        else:
            ax.set_title('%0.2fGHz -- Pol=%g\n\n3D radiation pattern' % (plot_freq/1e9,pangle))

    sm = plt.cm.ScalarMappable(cmap="jet", norm=plt.Normalize(vmin=gain_max-plot_range, vmax=gain_max))     # set range of colorbar to dynamic range
    sm.set_array([])
    plt.colorbar(sm)                                                            # display colorbar

    plt.draw()                                                                  # draw the plot
    plt.pause(plt_pause)                                                             # allow time for the drawing to show on screen
    time.sleep(0.01)                                                            #
    plt.show()

# to do : save plot picture
    return()


def display_millibox3d_ant_pattern(Vang, Hang, data, vert, hori, step, plot_freq=0, block_final=True, pangle=None):
    """ 3d radiation pattern plot based on MILLIBOX COORDINATES
    plot radiation pattern based on the gimbal (H,V)(deg) coordinates - dynamic range to plot is 50dB
    NOTE:
        H has same sign as phi
        V has same sign as theta but is offset by 90deg (i.e., V=0 -> theta=90) """

    V, H = np.meshgrid(Vang, Hang)                                              # format the data vs. H and V
    #print("V is "  +str(V)+ "and H is " +str(V)  )
    gain = np.array(data)
    gain = gain.reshape(V.shape)                                                # reshape the data

    plot_range = 50                                                             # dynamic range is set to 50dB default
    display_3d_ant_pattern(gain, H*np.pi/180, (90+V)*np.pi/180, plot_range, step, plot_freq, pangle)   # translate from (H,V)(deg) to (phi,theta)(rad)

    if vert < Vang[len(Vang)-1] or hori < Hang[len(Hang)-1]:                    # intermediate plot
        plt.show()

    else:                                                                       # last plot becomes blocking
        if block_final:
            print("-----------CLOSE PLOT GRAPHIC TO RETURN TO MENU-----------------")

            plt.ioff()
            plt.show()                                                              # closing the plot unblock the function and go to menu

# to do : save plot picture
    return()
