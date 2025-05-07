from os import walk
import numpy as np
import pandas as pd
# import plotly.express as px
import matplotlib.pyplot as plt
import os

def draw_beam_pattern(figureIndx,theta,data,color,savePath=None,pattern="none"):
    plt.figure(figureIndx)
    # ax = fig.add_subplot(projection='polar')
    ax = plt.subplot(111,polar=True)#projection='polar')
    ax.plot(theta,data,color=color)
    ax.set_theta_offset(np.pi/2)
    ax.set_thetamin(-90)
    ax.set_thetamax(90)
    if pattern != "none":
        if pattern == "freq":
            r_range = [np.median(data)-0.05,np.median(data)+0.05]
            roundSize = 3
        elif pattern == "power":
            r_range = [np.min(data),np.max(data)]#+5]
            roundSize = 0
        else: # default
            # r_range = [np.min(data),np.max(data)]
            r_range = [-40,np.max(data)]
            roundSize = 0
        ax.set_rmin(r_range[0])
        ax.set_rmax(r_range[1])
        step = (r_range[1]-r_range[0])/2
        rticks = np.arange(r_range[0], r_range[1]+step/2, step)
        if pattern == "power":
            rticks = np.concatenate([rticks[:-1],[np.max(data)],[rticks[-1]]])
        ax.set_rticks(np.round(rticks,roundSize))
    if savePath != None:
        plt.savefig(savePath)

# get all files in a sub folder
folderPath = "../../MilliBox_plot_data/dataPlot"
dataPath = folderPath + "/data/"
figurePath = folderPath + "/figure/"
stepSize = 1
filenames = next(walk(dataPath), (None, None, []))[2]  # [] if no file
# theta_data = np.arange(-90,95,5).tolist()
DEGREE_STEP = np.pi / 180 * stepSize
theta_data = np.arange(-np.pi/2,np.pi/2 + DEGREE_STEP,DEGREE_STEP).tolist()
colorLabel = ['red','green','blue','black','brown','olive','yellow','purple']
numOfElements = [1,2,4,8,16]
# labels = ["power"]*36 +["frequency"]*36

key = input("'1' for plot each csv; '2' for plot combined csv; '3' to plot all.\n")
if key == '1':
    # read CSV
    figureIndx = 0
    for filename in filenames:
        # print(filename)
        df = pd.read_csv(dataPath+filename)
        freq = [item/1e9 for item in df.freq.tolist()] # to GHz
        power = df.power.tolist()
        power_norm = [data-max(power) for data in power]
        # freq
        draw_beam_pattern(figureIndx*5+0,theta_data,freq,savePath=figurePath+filename[:-4]+'_freq.png',pattern="freq")
        # power
        draw_beam_pattern(figureIndx*5+1,theta_data,power,savePath=figurePath+filename[:-4]+'_power.png',pattern="power")
        # normalization power - peak with 0 dB
        draw_beam_pattern(figureIndx*5+2,theta_data,power_norm,savePath=figurePath+filename[:-4]+'_power_norm.png',pattern="power_norm")

        figureIndx = figureIndx + 1
elif key == '2':
    # os.listdir()
    subfiles = os.listdir(dataPath)
    # print(subfiles)
    for filenameIndx in range(len(subfiles)):
        print(str(filenameIndx)+":"+subfiles[filenameIndx])
    key = int(input("type the indx of folder want to plot:")) - int('0')
    folderName = subfiles[key]
    dataPath = dataPath+folderName + "/"
    subfiles = os.listdir(dataPath)
    # print()
    # subfiles = next(walk(dataPath + folderName), (None, None, []))[2]
    for subfileIndx in range(len(subfiles)):
        subfile = subfiles[subfileIndx]
        filename = dataPath + subfile
        df = pd.read_csv(filename)
        freq = [item/1e9 for item in df.freq.tolist()] # to GHz
        power = df.power.tolist()
        power_norm = [data-max(power) for data in power]
        if subfile != subfiles[-1]:
            savePath_freq,savePath_powr = None, None
        else:
            savePath_freq = figurePath+subfile+'_freq.png'
            savePath_powr = figurePath+subfile+'_power.png'
        # freq
        draw_beam_pattern(0,theta_data,freq,colorLabel[subfileIndx],savePath=savePath_freq,pattern="freq")
        # power
        draw_beam_pattern(1,theta_data,power_norm,colorLabel[subfileIndx],savePath=savePath_powr,pattern="power_norm")
elif key == '3':
    subfolers_allpaam = os.listdir(dataPath)
    for filenameIndx in range(len(subfolers_allpaam)):
        print(str(filenameIndx)+":"+subfolers_allpaam[filenameIndx])
    key = int(input("type the indx of folder want to plot:")) - int('0')
    folderName = subfolers_allpaam[key]
    dataPath = dataPath+folderName + "/"
    subfolers = os.listdir(dataPath)
    print(subfolers)
    figureIndx = 0
    for subfoler in subfolers:
        dataPath_sub = dataPath+subfoler+ "/"
        subfiles = sorted(os.listdir(dataPath_sub))

        # subfiles = next(walk(dataPath + folderName), (None, None, []))[2]
        for subfileIndx in range(len(subfiles)):
            subfile = subfiles[subfileIndx]
            filename = dataPath_sub + subfile
            print(filename)
            df = pd.read_csv(filename)
            freq = [item/1e9 for item in df.freq.tolist()] # to GHz
            power = df.power.tolist()
            power_norm = [data-max(power) for data in power]
            if subfile != subfiles[-1]:
                savePath_freq,savePath_powr,savePath_powr_norm = None, None, None
            else:
                savePath_freq = figurePath+subfoler+'_freq.png'
                savePath_powr = figurePath+subfoler+'_power_abs.png'
                savePath_powr_norm = figurePath+subfoler+'_power_norm.png'
            # freq
            draw_beam_pattern(0+3*figureIndx,theta_data,freq,colorLabel[subfileIndx],savePath=savePath_freq,pattern="freq")
            # power
            draw_beam_pattern(1+3*figureIndx,theta_data,power_norm,colorLabel[subfileIndx],savePath=savePath_powr_norm,pattern="power_norm")
            # power without norm
            draw_beam_pattern(2+3*figureIndx,theta_data,power,colorLabel[subfileIndx],savePath=savePath_powr,pattern="power")
            
        figureIndx = figureIndx + 1
        # break
else:
    print("haven't implemented.")
# generate the figure
