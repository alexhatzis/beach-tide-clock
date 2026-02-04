import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep

def find_inflections(tideData):
    trend = "none"

def generate_trace(tideData):
    num_pts = len(tideData)
    x_spacing = int((num_pts - 1) // 4)

    x = tideData.index
    y = tideData

    fig, ax = plt.subplots()
    ax.plot(x, y, label='tides for sg beach')

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