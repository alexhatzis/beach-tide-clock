import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep
import pandas as pd

def find_inflections(tideData):
    trend = "none"
    prevTideLevel = tideData.iloc[0]
    maxima = []
    minima = []
    for i in range(1, len(tideData)):
        tideLevel = tideData.iloc[i]
        if tideLevel.iloc[0] > prevTideLevel.iloc[0]:
            if trend == "down":
                #found inflection
                minima.append(i-1)#prevTideLevel.name)
            trend = "up"
        else:
            if trend == "up":
                #found inflection
                maxima.append(i-1)#)prevTideLevel.name)
            trend = "down"
        prevTideLevel = tideLevel
    return maxima, minima
        

def generate_trace(tideData):
    num_pts = len(tideData)
    x_spacing = int((num_pts - 1) // 4)

    maxima, minima = find_inflections(tideData)

    markedPts = []
    for max in maxima:
        if max >= x_spacing:
            markedPts.append(max)
    for min in minima:
        if min >= x_spacing:
            markedPts.append(min)

    x = tideData.index
    y = tideData

    fig, ax = plt.subplots()
    ax.plot(x, y, 'o', ls='-', label='tides for sg beach', markevery=markedPts)

    xticks =   [tideData.iloc[x_spacing*0].name, 
                tideData.iloc[x_spacing*1].name, 
                tideData.iloc[x_spacing*2].name, 
                tideData.iloc[x_spacing*3].name, 
                tideData.iloc[x_spacing*4].name]
    
    xlabels = []
    timefmtstring = "%H:%M"
    for i in range (0,5):
        label = tideData.iloc[x_spacing*i].name.strftime(timefmtstring)
        xlabels.append(label)
    ax.set_xticks(ticks=xticks,
                   labels=xlabels)
    

    lower_ylim = -2
    upper_ylim = 10
    ax.set_ylim(bottom=lower_ylim, top=upper_ylim)
    ax.vlines(tideData.iloc[x_spacing*1].name, lower_ylim, upper_ylim, colors='Red')

    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    plt.savefig(
        'trace_only.png',
        bbox_inches='tight',
        pad_inches=0,
        transparent=True
    )