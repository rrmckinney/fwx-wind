## %
import context
import numpy as np
import pandas as pd
from pathlib import Path
from functools import reduce
from pylab import *

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from context import data_dir, img_dir
from utils.wind import get_sonic

import warnings

warnings.filterwarnings("ignore")

########## INPUTS ########
## file on interest
wdir_correction = 180
file_dates = ["220515"]
testnum = 2
winds = [["%.2d" % i for i in range(1, 21)]]

test_dirs = [0]  # zero or one options
directions = ["N"]
slice_fd = [20, -5]

###### END INPUTS ########

### read in time stamps for tests
times = pd.read_csv(file_dates+"test"+testnum+".txt", sep="\t")

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


############## UBC Cup Anemometer Data set up ####################

for i in range(len(directions)):
    test_dir = test_dirs[i]
    direction, ubc_winds, file_date, test_dir = (
        directions[i],
        winds[i],
        file_dates[i],
        test_dirs[i],
    )
    mean_wsp, mean_wdir, wind_sens = [], [], []
    sonic_mean_wsp, sonic_mean_wdir, sonic_sens = [], [], []

    for i in range(len(ubc_winds)):
        cup_in = sorted(
            Path(str(data_dir) + f"\\WIND{ubc_winds[i]}\\").glob(f"20{file_date}*.TXT")
        )

        print(str(data_dir) + f"\\WIND{ubc_winds[i]}\\")
        print(cup_in)
        filein = str(cup_in[test_dir])
        # print(filein)
        cup_df = pd.read_csv(filein, sep="\t")
        cup_df[["wsp", "wdir"]] = cup_df[["wsp", "wdir"]].apply(pd.to_numeric)
        cup_df["wsp"] = cup_df["wsp"] * 0.44704  ## convert to m\s

        cup_df["wdir"] = cup_df["wdir"] - wdir_correction
        cup_df["wdir"][cup_df["wdir"] < 0] = cup_df["wdir"] + 360

        cup_date_range = pd.date_range(
            "20" + file_date + "T" + filein[-10:-4], periods=len(cup_df), freq="3S"
        )
        cup_df = cup_df.set_index(pd.DatetimeIndex(cup_date_range))
        sonic_dfi = sonic_df[str(cup_df.index[0]) : str(cup_df.index[-2])]

        sonic_dfi["wdir"] = sonic_dfi["wdir"] - wdir_correction
        sonic_dfi["wdir"][sonic_dfi["wdir"] < 0] = sonic_dfi["wdir"] + 360

        cup_df = cup_df.reset_index()
        sonic_dfi = sonic_dfi.reset_index()

        cup_df = cup_df.iloc[slice_fd[0] : slice_fd[1]]
        sonic_dfi = sonic_dfi.iloc[slice_fd[0] * 10 : slice_fd[1]]

        mean_wsp.append(round(cup_df["wsp"].mean(), 2))
        mean_wdir.append(round(cup_df["wdir"].mean(), 0))
        wind_sens.append(f"wind{ubc_winds[i]}")

        sonic_mean_wsp.append(round(sonic_dfi["wsp"].mean(), 2))
        sonic_mean_wdir.append(round(sonic_dfi["wdir"].mean(), 0))
        sonic_sens.append(f"sonic{ubc_winds[i]}")

    ###################### plot comparsion ##############################

    fig = plt.figure(figsize=(8, 8))  # (Width, height) in inches.
    fig.suptitle(
        f"Wind Speed and Direction averaged over 10 min period \n with anemometers sampling every 3 secs for direction test {direction}",
        y=0.9,
    )
    cmap = cm.get_cmap("tab20", len(mean_wdir))
    colors = []
    for i in range(cmap.N):
        rgba = cmap(i)
        # print(matplotlib.colors.rgb2hex(rgba))
        colors.append(matplotlib.colors.rgb2hex(rgba))
    ax = fig.add_subplot(1, 1, 1)
    color = colors[i]
    for i in range(len(mean_wdir)):
        ax.scatter(
            mean_wdir[i],
            mean_wsp[i],
            label=wind_sens[i],
            color=colors[i],
            s=50,
            zorder=10,
        )
        ax.scatter(
            sonic_mean_wdir[i],
            sonic_mean_wsp[i],
            label=sonic_sens[i],
            color=colors[i],
            s=50,
            zorder=10,
            marker="x",
        )
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.4),
        ncol=6,
        fancybox=True,
        shadow=True,
    )

    ax.set_ylabel("Mean Wind Speed \n (m s^-1)", fontsize=12)
    ax.set_xlabel("Mean Wind Direction \n (Degs)", fontsize=12)
    plt.grid(zorder=1, linestyle="dashed", lw=0.5)

    plt.savefig(
        str(img_dir) + f"\\scatter-speed-cup-v-cup-{direction}-{file_date}.png",
        dpi=300,
        bbox_inches="tight",
    )

