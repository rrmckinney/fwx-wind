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

from context import data_dir, img_dir, time_dir
from utils.wind import get_sonic

import warnings
########## INPUTS ########
## file on interest
wdir_correction = 180
file_dates = ["220516"]
testnum = 2
winds = [["%.2d" % i for i in range(21, 29)]]

test_dirs = [0]  # zero or one options
directions = ["N"]
slice_fd = [5, -5]
###### END INPUTS ########

warnings.filterwarnings("ignore")

# ## set path to sonic data and sort all files for date of interest
sonic_in = sorted(Path(str(data_dir) + "\\sonic\\").glob(f"{file_dates[0]}*.GILL01"))

# ## open reach file as a dataframe and sort in list
sonic_list = [get_sonic(str(filein)) for filein in sonic_in]

# ## merge the list of dataframes based on time
sonic_df = reduce(lambda df1, df2: pd.merge(df1, df2, how="outer"), sonic_list)

# ## index dataframe on datetime
sonic_df = sonic_df.set_index(pd.DatetimeIndex(sonic_df["index"]))

# ## delte old index
del sonic_df["index"]

sonic_df["wdir"] = sonic_df["wdir"] - wdir_correction
sonic_df["wdir"][sonic_df["wdir"] < 0] = sonic_df["wdir"] + 360

times_in = Path(str(time_dir)+"\\"+str(file_dates[0])+".txt", sep="\t")
times = pd.read_csv(times_in)
times = times. apply(pd.to_datetime)

for i in range(len(directions)):
    test_dir = test_dirs[i]
    direction, ubc_winds, file_date, test_dir = (
    directions[i],
    winds[i],
    file_dates[i],
    test_dirs[i],
    )
    mean_wsp_speed1,mean_wsp_speed2,mean_wsp_speed3, mean_wdir_speed1, mean_wdir_speed2,mean_wdir_speed3, wind_sens = [], [], [],[], [], [],[]
    sonic_mean_wsp1,  sonic_mean_wsp2,  sonic_mean_wsp3,sonic_mean_wdir1,sonic_mean_wdir2, sonic_mean_wdir3, sonic_sens = [], [], [], [],[], [],[]
    cupspeed1, cupspeed2, cupspeed3, cupdir1, cupdir2, cupdir3, cuptime1, cuptime2, cuptime3 = [], [], [], [],[], [],[], [],[]
    sp1diff, sp2diff, sp3diff = [],[],[]

    for i in range(len(ubc_winds)):
        cup_in = sorted(
            Path(str(data_dir) + f"\\WIND{ubc_winds[i]}\\").glob(f"20{file_date}*.TXT")
        )

        #print(str(data_dir) + f"\\WIND{ubc_winds[i]}\\")
        #print(cup_in)
        filein = str(cup_in[test_dir])
        # print(filein)
        cup_df = pd.read_csv(filein, sep="\t")
        cup_df[["wsp", "wdir"]] = cup_df[["wsp", "wdir"]].apply(pd.to_numeric)
        cup_df["time"] = pd.to_datetime(cup_df["time"], format = "%H:%M:%S").dt.time
        cup_df["wsp"] = cup_df["wsp"] * 0.44704  ## convert to m\s

        cup_df["wdir"] = cup_df["wdir"] - wdir_correction
        cup_df["wdir"][cup_df["wdir"] < 0] = cup_df["wdir"] + 360
        wind_sens.append(f"wind{ubc_winds[i]}")
        sonic_sens.append(f"sonic{ubc_winds[i]}")

        time1 = pd.to_datetime(times.iloc[i,0])
        time2 = pd.to_datetime(times.iloc[i,1])
        time3 = pd.to_datetime(times.iloc[i,2])
        
        print(time1, time2,time3)
        
        speedtime1 = (time2-time1).seconds
        speedtime2 = speedtime1 + (time3-time2).seconds
        
        seconds = []
        for i in range(len(cup_df.index)):
            secondsnew = (cup_df["time"][i].hour*60+cup_df["time"][i].minute)*60+cup_df["time"][i].second
            seconds.append(secondsnew)
        seconds = pd.DataFrame(seconds)
                

        for i in range(len(cup_df)):
            if seconds.iloc[i,0] < speedtime1:
                cupspeed1.append(cup_df["wsp"][i])
                cupdir1.append(cup_df["wdir"][i])
                cuptime1.append(cup_df["time"][i])
            elif seconds.iloc[i,0] > speedtime1 and seconds.iloc[i,0] < speedtime2:
                cupspeed2.append(cup_df["wsp"][i])
                cupdir2.append(cup_df["wdir"][i])
                cuptime2.append(cup_df["time"][i])
            else:
                cupspeed3.append(cup_df["wsp"][i])
                cupdir3.append(cup_df["wdir"][i])
                cuptime3.append(cup_df["time"][i])

        cups1 = pd.DataFrame({"time":cuptime1,"wsp": cupspeed1,"wdir":cupdir1})
        cups2 = pd.DataFrame({"time":cuptime2,"wsp": cupspeed2,"wdir":cupdir2})
        cups3 = pd.DataFrame({"time":cuptime3,"wsp": cupspeed3,"wdir":cupdir3})
        
        cup_date_range1 = pd.date_range(
            "20" + file_date + "T" + str(time1.strftime("%H:%M:%S")), periods=len(cups1), freq="3S"
        )
        cup_date_range2 = pd.date_range(
            "20" + file_date + "T" + str(time2.strftime("%H:%M:%S")), periods=len(cups2), freq="3S"
        )
        cup_date_range3 = pd.date_range(
            "20" + file_date + "T" + str(time3.strftime("%H:%M:%S")), periods=len(cups3), freq="3S"
        )

        cups1 = cups1.set_index(pd.DatetimeIndex(cup_date_range1))
        cups2 = cups2.set_index(pd.DatetimeIndex(cup_date_range2))
        cups3 = cups3.set_index(pd.DatetimeIndex(cup_date_range3))
  
        sonic1 = sonic_df[str(cups1.index[0]) : str(cups1.index[-1])]
        sonic2 = sonic_df[str(cups2.index[0]) : str(cups2.index[-1])]
        sonic3 = sonic_df[str(cups3.index[0]) : str(cups3.index[-1])]

        cups1 = cups1.reset_index()
        sonic1 = sonic1.reset_index()
        cups2 = cups2.reset_index()
        sonic2 = sonic2.reset_index()
        cups3 = cups3.reset_index()
        sonic3 = sonic3.reset_index()

        cups1 = cups1.iloc[slice_fd[0] : slice_fd[1]]
        cups2 = cups2.iloc[slice_fd[0] : slice_fd[1]]
        cups3 = cups3.iloc[slice_fd[0] : slice_fd[1]]
        
        sonic1 = sonic1.iloc[slice_fd[0] *10  : slice_fd[1]]
        sonic2 = sonic2.iloc[slice_fd[0] *10 : slice_fd[1]]
        sonic3 = sonic3.iloc[slice_fd[0] *10 : slice_fd[1]]
       
        sp1diff.append(round(sonic1["wsp"].mean() - cups1["wsp"].mean(),2))
        sp2diff.append(round(sonic2["wsp"].mean() - cups2["wsp"].mean(),2))
        sp3diff.append(round(sonic3["wsp"].mean() - cups3["wsp"].mean(),2))

    fig = plt.figure(figsize=(12, 8))  # (Width, height) in inches.
    fig.suptitle(
    f"Sonic - Cup Mean Wind Speed for direction test {direction}",
    y=0.9,
    )
    cmap = cm.get_cmap("tab20", 3)
    colors = []
    for i in range(cmap.N):
        rgba = cmap(i)
        # print(matplotlib.colors.rgb2hex(rgba))
        colors.append(matplotlib.colors.rgb2hex(rgba))

    ax = fig.add_subplot(1, 1, 1)
    color = colors[i]
    print(sp1diff, sp2diff, sp3diff)
    for x in range(8):
        ax.scatter(
            wind_sens[x],
            sp1diff[x],
            label="Speed 1",
            color="red",
            s=50,
            #zorder=10
        )
        ax.scatter(
            wind_sens[x],
            sp2diff[x],
            label="Speed 2",
            color="green",
            s=50,
            #zorder=10
        )
        ax.scatter(
            wind_sens[x],
            sp3diff[x],
            label= "Speed 3",
            color="blue",
            s=50,
            #zorder=10
        )

    ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, -0.6),
    ncol=6,
    fancybox=True,
    shadow=True,
    )

    ax.set_ylabel("Mean Wind Speed Difference \n (m s^-1)", fontsize=12)
    ax.set_xlabel("Cup Sensor ID", fontsize=12)
    ax.grid(zorder=1, linestyle="dashed", lw=0.5)

    plt.savefig(
    str(img_dir) + f"\\scatter-speed-diff-{direction}-{file_date}.png",
    dpi=300,
    bbox_inches="tight",
    )



    


