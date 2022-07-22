## %
from pickle import TRUE
import context
import numpy as np
import pandas as pd
from pathlib import Path
from functools import reduce
from pylab import *

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from context import sonic_dir, img_dir, data_dir
from utils.wind import choice

import warnings

warnings.filterwarnings("ignore")

########## INPUTS ########
## Choose Inputs##
cupschoice = 1        #choose position for cups (1 or 2), sonic must be opposite
sonicchoice =  2
tests = [1,2,3]
wdir_correction = 180
############################

cup_wsp_speed1,cup_wsp_speed2,cup_wsp_speed3, cup_wdir_speed1, cup_wdir_speed2,cup_wdir_speed3, wind_sens = [], [], [],[], [], [],[]
sonic_mean_wsp1, sonic_mean_wsp2,sonic_mean_wsp3,sonic_mean_wdir1,sonic_mean_wdir2,sonic_mean_wdir3,sonic_sens = [], [], [], [],[], [],[]
cupspeed1, cupspeed2, cupspeed3, cupdir1, cupdir2, cupdir3, cuptime1, cuptime2, cuptime3 = [], [], [], [],[], [],[], [],[]

c = choice(cupschoice)


for i in range(0,len(c[0])):

    times_in = Path(str(data_dir)+"_20"+str(c[0][i])+"\\"+"time\\"+str(c[0][i])+".txt", sep="\t")
    times = pd.read_csv(times_in)
    times = times. apply(pd.to_datetime)
    
    for r in range(0,len(c[1][i])):

        cupspeed1, cupspeed2, cupspeed3, cupdir1, cupdir2, cupdir3, cuptime1, cuptime2, cuptime3 = [], [], [], [],[], [],[], [],[]
        cup_in = sorted(
            Path(str(data_dir) +"_20"+str(c[0][i])+ f"\\WIND{c[1][i][r]}\\").glob(f"20{c[0][i]}*.TXT")
        )
        
        #print(str(data_dir) + f"\\WIND{ubc_winds[i]}\\")
        #print(cup_in)
        
        filein = str(cup_in[0])

        cup_df = pd.read_csv(filein, sep="\t")
        cup_df[["wsp", "wdir"]] = cup_df[["wsp", "wdir"]].apply(pd.to_numeric)
        cup_df["time"] = pd.to_datetime(cup_df["time"], format = "%H:%M:%S").dt.time
        cup_df["wsp"] = cup_df["wsp"] * 0.44704  ## convert to m\s

        cup_df["wdir"] = cup_df["wdir"] - wdir_correction
        cup_df["wdir"][cup_df["wdir"] < 0] = cup_df["wdir"] + 360
        
        time1 = pd.to_datetime(times.iloc[r,0])
        time2 = pd.to_datetime(times.iloc[r,1])
        time3 = pd.to_datetime(times.iloc[r,2])
        
        #print(time1, time2,time3)
        
        speedtime1 = (time2-time1).seconds
        speedtime2 = speedtime1 + (time3-time2).seconds
        
        seconds = []
        for m in range(len(cup_df.index)):
            secondsnew = (cup_df["time"][m].hour*60+cup_df["time"][m].minute)*60+cup_df["time"][m].second
            seconds.append(secondsnew)
        seconds = pd.DataFrame(seconds)

        for x in range(len(cup_df)):
            if seconds.iloc[x,0] < speedtime1:
                cupspeed1.append(cup_df["wsp"][x])
                cupdir1.append(cup_df["wdir"][x])
                cuptime1.append(cup_df["time"][x])
            elif (seconds.iloc[x,0] > speedtime1 and seconds.iloc[x,0] < speedtime2):
                cupspeed2.append(cup_df["wsp"][x])
                cupdir2.append(cup_df["wdir"][x])
                cuptime2.append(cup_df["time"][x])
            elif seconds.iloc[x,0] > speedtime2:
                cupspeed3.append(cup_df["wsp"][x])
                cupdir3.append(cup_df["wdir"][x])
                cuptime3.append(cup_df["time"][x])

            cups1 = pd.DataFrame({"time":cuptime1,"wsp": cupspeed1,"wdir":cupdir1})
            cups2 = pd.DataFrame({"time":cuptime2,"wsp": cupspeed2,"wdir":cupdir2})
            cups3 = pd.DataFrame({"time":cuptime3,"wsp": cupspeed3,"wdir":cupdir3})
        
        cup_wsp_speed1.append(round(cups1["wsp"].mean(),3))
        cup_wsp_speed2.append(round(cups2["wsp"].mean(),3))
        cup_wsp_speed3.append(round(cups3["wsp"].mean(),3))

        cup_wdir_speed1.append(round(cups1["wdir"].mean(),0))
        cup_wdir_speed2.append(round(cups2["wdir"].mean(),0))
        cup_wdir_speed3.append(round(cups3["wdir"].mean(),0))
        wind_sens.append(f"wind{r+1}")


s = choice(sonicchoice)
for i in range(0,len(s[0])):
    
    for r in range(0,len(s[1][i])):
        for q in range(len(tests)): 
            print(str(sonic_dir)+f"\\"+"sonic"+str(q+1)+str(s[0][i])+"wind"+str(s[1][i][r]))

            sonic_in = sorted(
                Path(str(sonic_dir)+f"\\").glob("sonic"+str(q+1)+str(s[0][i])+str(s[1][i][r])+".TXT")
            )
            print(f"wind{s[1][i][r]}")
           
            print(sonic_in)
            filein = str(sonic_in[0])
            sonic_df = pd.read_csv(filein, sep=",")
            sonic_df.iloc[:,8] = sonic_df.iloc[:,8].apply(pd.to_numeric)
            sonic_df.iloc[:,9] = sonic_df.iloc[:,9].apply(pd.to_numeric)
            sonic_df.iloc[:,0] = pd.to_datetime(sonic_df.iloc[:,0], format = "%Y-%m-%d %H:%M:%S").dt.time

            if q+1 == 1:
                sonic_mean_wsp1.append(round(sonic_df.iloc[:,8].mean(), 3))
                sonic_mean_wdir1.append(round(sonic_df.iloc[:,9].mean(), 0))

            elif q+1 == 2:
                sonic_mean_wsp2.append(round(sonic_df.iloc[:,8].mean(), 3))
                sonic_mean_wdir2.append(round(sonic_df.iloc[:,9].mean(), 0))

            elif q+1 ==3:
                sonic_mean_wsp3.append(round(sonic_df.iloc[:,8].mean(), 3))
                sonic_mean_wdir3.append(round(sonic_df.iloc[:,9].mean(), 0))

        sonic_sens.append(f"sonic{r+1}")

labs = l = [i for i in range(1,29)]


print(len(sonic_mean_wsp3))
fig = plt.figure(figsize=(12, 8))  # (Width, height) in inches.
fig = plt.title(
    f"Position 2 for Cups",
    y=0.9,
)
cmap = cm.get_cmap("jet", len(sonic_mean_wdir1))
colors = []
for i in range(cmap.N):
    rgba = cmap(i)
    # print(matplotlib.colors.rgb2hex(rgba))
    colors.append(matplotlib.colors.rgb2hex(rgba))

fig, ax = plt.subplots(1, 3)

ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax[2].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
color = colors[i]
for i in range(len(sonic_mean_wdir1)):
    ax[0].scatter(
        cup_wdir_speed1[i],
        cup_wsp_speed1[i],
        label=f"wind{labs[i]}",
        color=colors[i],
        s=50,
        zorder=10,
    )
    ax[0].scatter(
        sonic_mean_wdir1[i],
        sonic_mean_wsp1[i],
        label=f"sonic{labs[i]}",
        color=colors[i],
        s=50,
        zorder=10,
        marker="x",
    )
    ax[1].scatter(
        cup_wdir_speed2[i],
        cup_wsp_speed2[i],
        label=f"wind{labs[i]}",
        color=colors[i],
        s=50,
        zorder=10,
    )
    ax[1].scatter(
        sonic_mean_wdir2[i],
        sonic_mean_wsp2[i],
        label=f"sonic{labs[i]}",
        color=colors[i],
        s=50,
        zorder=10,
        marker="x",
    )
    ax[2].scatter(
        cup_wdir_speed3[i],
        cup_wsp_speed3[i],
        label=f"wind{labs[i]}",
        color=colors[i],
        s=50,
        zorder=10,
    )
    ax[2].scatter(
        sonic_mean_wdir3[i],
        sonic_mean_wsp3[i],
        label=f"sonic{labs[i]}",
        color=colors[i],
        s=50,
        zorder=10,
        marker="x",
    )
ax[1].legend(
    loc="lower center",
    bbox_to_anchor=(0.5, -0.8),
    ncol=6,
    fancybox=True,
    shadow=True,
)

ax[0].set_ylabel("Mean Wind Speed \n (m s^-1)", fontsize=12)
ax[1].set_xlabel("Mean Wind Direction \n (Degs)", fontsize=12)
ax[0].grid(zorder=1, linestyle="dashed", lw=0.5)
ax[1].grid(zorder=1, linestyle="dashed", lw=0.5)
ax[2].grid(zorder=1, linestyle="dashed", lw=0.5)
ax[0].set_title("High Speed")
ax[1].set_title("Medium Speed")
ax[2].set_title("Low Speed")

plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

plt.savefig(
    str(img_dir) + f"\\position1-scatter.png",
    dpi=300,
    bbox_inches="tight",
)



    


