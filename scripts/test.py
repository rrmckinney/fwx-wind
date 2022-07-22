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

from context import data_dir, img_dir, time_dir, sonic_dir
from utils.wind import get_sonic

import warnings
########## INPUTS ########
## file on interest
wdir_correction = 180
file_dates = ["220520"]
winds = [["%.2d" % i for i in range(26,29)]]
test_dirs = [0]  # zero or one options
directions = ["280"]
slice_fd = [10, -5]
###### END INPUTS ########

warnings.filterwarnings("ignore")

# ## set path to sonic data and sort all files for date of interest
sonic_in = sorted(Path(str(data_dir) + "\\sonic\\").glob(f"{file_dates[0]}*.GILL01"))

## open reach file as a dataframe and sort in list
sonic_list = [get_sonic(str(sonic_in[i]), i, len(sonic_in)) for i in range(len(sonic_in))]

# ## merge the list of dataframes based on time
sonic_df = reduce(lambda df1, df2: pd.merge(df1, df2, how="outer"), sonic_list)

# ## index dataframe on datetime
sonic_df = sonic_df.set_index(pd.DatetimeIndex(sonic_df["index"]))

# ## delte old index
del sonic_df["index"]

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
    cup_wsp_speed1,cup_wsp_speed2,cup_wsp_speed3, cup_wdir_speed1, cup_wdir_speed2,cup_wdir_speed3, wind_sens = [], [], [],[], [], [],[]
    sonic_mean_wsp1, sonic_mean_wsp2,sonic_mean_wsp3,sonic_mean_wdir1,sonic_mean_wdir2,sonic_mean_wdir3,sonic_sens = [], [], [], [],[], [],[]
    cupspeed1, cupspeed2, cupspeed3, cupdir1, cupdir2, cupdir3, cuptime1, cuptime2, cuptime3 = [], [], [], [],[], [],[], [],[]

    for i in range(len(ubc_winds)):
        cupspeed1, cupspeed2, cupspeed3, cupdir1, cupdir2, cupdir3, cuptime1, cuptime2, cuptime3 = [], [], [], [],[], [],[], [],[]
        cup_in = sorted(
            Path(str(data_dir) + f"\\WIND{ubc_winds[i]}\\").glob(f"20{file_date}*.TXT")
        )

        #print(str(data_dir) + f"\\WIND{ubc_winds[i]}\\")
        #print(cup_in)
        filein = str(cup_in[test_dir])

        cup_df = pd.read_csv(filein, sep="\t")
        cup_df[["wsp", "wdir"]] = cup_df[["wsp", "wdir"]].apply(pd.to_numeric)
        cup_df["time"] = pd.to_datetime(cup_df["time"], format = "%H:%M:%S").dt.time
        cup_df["wsp"] = cup_df["wsp"] * 0.44704  ## convert to m\s

        cup_df["wdir"] = cup_df["wdir"] - wdir_correction
        cup_df["wdir"][cup_df["wdir"] < 0] = cup_df["wdir"] + 360
        
        time1 = pd.to_datetime(times.iloc[i,0])
        time2 = pd.to_datetime(times.iloc[i,1])
        time3 = pd.to_datetime(times.iloc[i,2])
        
        #print(time1, time2,time3)
        
        speedtime1 = (time2-time1).seconds
        speedtime2 = speedtime1 + (time3-time2).seconds
        
        seconds = []
        for r in range(len(cup_df.index)):
            secondsnew = (cup_df["time"][r].hour*60+cup_df["time"][r].minute)*60+cup_df["time"][r].second
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
        
        print(time1,time2,time3)
        
        cup_date_range1 = pd.date_range(
            "20" + file_date + "T" + str(time1.strftime("%H:%M:%S")), periods=len(cups1), freq="3S"
        )
        cup_date_range2 = pd.date_range(
            "20" + file_date + "T" + str(time2.strftime("%H:%M:%S")),periods=len(cups2), freq="3S"
        )
        cup_date_range3 = pd.date_range(
            "20" + file_date + "T" + str(time3.strftime("%H:%M:%S")), periods=len(cups3), freq="3S"
        )
        
        cups1 = cups1.set_index(pd.DatetimeIndex(cup_date_range1))
        cups2 = cups2.set_index(pd.DatetimeIndex(cup_date_range2))
        cups3 = cups3.set_index(pd.DatetimeIndex(cup_date_range3))

        sonic1 = sonic_df[str(cups1.index[0]) : str(cups1.index[-1])]
        cups1 = cups1.reset_index()
        
        sonic1["wdir"] = sonic1["wdir"] - wdir_correction
        sonic1["wdir"][sonic1["wdir"] < 0] = sonic1["wdir"] + 360

        sonic2 = sonic_df[str(cups2.index[0]) : str(cups2.index[-1])]
        cups2 = cups2.reset_index()

        sonic2["wdir"] = sonic2["wdir"] - wdir_correction
        sonic2["wdir"][sonic2["wdir"] < 0] = sonic2["wdir"] + 360

        sonic3 = sonic_df[str(cups3.index[0]) : str(cups3.index[-1])]
        cups3 = cups3.reset_index()
  
        sonic3["wdir"] = sonic3["wdir"] - wdir_correction
        sonic3["wdir"][sonic3["wdir"] < -1] = sonic3["wdir"] + 360
        
        sonic1 = sonic1.reset_index()
        sonic2 = sonic2.reset_index()
        sonic3 = sonic3.reset_index()
        #print(str(sonic1.index[-2]), str(cups1.index[-2]), len(cups1.index))

        # cups1 = cups1.iloc[slice_fd[0] : slice_fd[1]]
        # cups2 = cups2.iloc[slice_fd[0] : slice_fd[1]]
        # cups3 = cups3.iloc[slice_fd[0] : slice_fd[1]]
        
        sonic1 = sonic1.iloc[slice_fd[0] *40 : slice_fd[1]]
        sonic2 = sonic2.iloc[slice_fd[0] *40 : slice_fd[1]]
        sonic3 = sonic3.iloc[slice_fd[0] *40 : slice_fd[1]]
    
        cup_wsp_speed1.append(round(cups1["wsp"].mean(),2))
        cup_wsp_speed2.append(round(cups2["wsp"].mean(),2))
        cup_wsp_speed3.append(round(cups3["wsp"].mean(),2))

        cup_wdir_speed1.append(round(cups1["wdir"].mean(),0))
        cup_wdir_speed2.append(round(cups2["wdir"].mean(),0))
        cup_wdir_speed3.append(round(cups3["wdir"].mean(),0))
        wind_sens.append(f"wind{ubc_winds[i]}")

        sonic_mean_wsp1.append(round(sonic1["wsp"].mean(), 2))
        sonic_mean_wsp2.append(round(sonic2["wsp"].mean(), 2))
        sonic_mean_wsp3.append(round(sonic3["wsp"].mean(), 2))

        sonic_mean_wdir1.append(round(sonic1["wdir"].mean(), 0))
        sonic_mean_wdir2.append(round(sonic2["wdir"].mean(), 0))
        sonic_mean_wdir3.append(round(sonic3["wdir"].mean(), 0))
        sonic_sens.append(f"sonic{ubc_winds[i]}")
        
        # #print(sonic1, sonic2, sonic3)
        
        sonic1.to_csv(str(sonic_dir)+f"\\sonic1{file_date}{ubc_winds[i]}.txt", header=None, index=None, sep=',', mode='a')
        sonic2.to_csv(str(sonic_dir)+f"\\sonic2{file_date}{ubc_winds[i]}.txt", header=None, index=None, sep=',', mode='a')
        sonic3.to_csv(str(sonic_dir)+f"\\sonic3{file_date}{ubc_winds[i]}.txt", header=None, index=None, sep=',', mode='a')
        
        # print(sonic3)

# print(sonic_mean_wsp1, cup_wsp_speed1)
# print(sonic_mean_wsp2, cup_wsp_speed2)
# print(sonic_mean_wsp3, cup_wsp_speed3)

# fig = plt.figure(figsize=(12, 8))  # (Width, height) in inches.
# fig = plt.title(
#     f"Wind Speed and Direction averaged over 10 min period \n with anemometers sampling every 3 secs for direction test {direction}",
#     y=0.9,
# )
# cmap = cm.get_cmap("tab20", len(sonic_mean_wdir1))
# colors = []
# for i in range(cmap.N):
#     rgba = cmap(i)
#     # print(matplotlib.colors.rgb2hex(rgba))
#     colors.append(matplotlib.colors.rgb2hex(rgba))

# fig, ax = plt.subplots(1, 3)

# ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# ax[2].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# color = colors[i]
# for i in range(len(sonic_mean_wdir1)):
#     ax[0].scatter(
#         cup_wdir_speed1[i],
#         cup_wsp_speed1[i],
#         label=wind_sens[i],
#         color=colors[i],
#         s=50,
#         zorder=10,
#     )
#     ax[0].scatter(
#         sonic_mean_wdir1[i],
#         sonic_mean_wsp1[i],
#         label=sonic_sens[i],
#         color=colors[i],
#         s=50,
#         zorder=10,
#         marker="x",
#     )
#     ax[1].scatter(
#         cup_wdir_speed2[i],
#         cup_wsp_speed2[i],
#         label=wind_sens[i],
#         color=colors[i],
#         s=50,
#         zorder=10,
#     )
#     ax[1].scatter(
#         sonic_mean_wdir2[i],
#         sonic_mean_wsp2[i],
#         label=sonic_sens[i],
#         color=colors[i],
#         s=50,
#         zorder=10,
#         marker="x",
#     )
#     ax[2].scatter(
#         cup_wdir_speed3[i],
#         cup_wsp_speed3[i],
#         label=wind_sens[i],
#         color=colors[i],
#         s=50,
#         zorder=10,
#     )
#     ax[2].scatter(
#         sonic_mean_wdir3[i],
#         sonic_mean_wsp3[i],
#         label=sonic_sens[i],
#         color=colors[i],
#         s=50,
#         zorder=10,
#         marker="x",
#     )
# ax[1].legend(
#     loc="lower center",
#     bbox_to_anchor=(0.5, -0.6),
#     ncol=6,
#     fancybox=True,
#     shadow=True,
# )

# ax[0].set_ylabel("Mean Wind Speed \n (m s^-1)", fontsize=12)
# ax[1].set_xlabel("Mean Wind Direction \n (Degs)", fontsize=12)
# ax[0].grid(zorder=1, linestyle="dashed", lw=0.5)
# ax[1].grid(zorder=1, linestyle="dashed", lw=0.5)
# ax[2].grid(zorder=1, linestyle="dashed", lw=0.5)
# ax[0].set_title("High Speed")
# ax[1].set_title("Medium Speed")
# ax[2].set_title("Low Speed")

# plt.subplots_adjust(left=0.1,
#                     bottom=0.1, 
#                     right=0.9, 
#                     top=0.9, 
#                     wspace=0.4, 
#                     hspace=0.4)

# plt.savefig(
#     str(img_dir) + f"\\scatter-{direction}-{file_date}.png",
#     dpi=300,
#     bbox_inches="tight",
# )



    


