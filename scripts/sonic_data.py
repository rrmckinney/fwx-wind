## %
from pickle import TRUE
import context
import numpy as np
import pandas as pd
from pathlib import Path
from functools import reduce
from pylab import *
import statistics
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from context import sonic_dir, img_dir, data_dir
from utils.wind import choice

import warnings

warnings.filterwarnings("ignore")

########## INPUTS ########
## Choose Inputs##
cupschoice = 2        #choose position for cups (1 or 2), sonic must be opposite
sonicchoice =  1
tests = [1,2,3]
wdir_correction = 180
############################

sonic_wsp1, sonic_wsp2,sonic_wsp3,sonic_wdir1,sonic_wdir2,sonic_wdir3,sonic_sens = [], [], [], [],[], [],[]

s = choice(sonicchoice)
for i in range(0,len(s[0])):
    
    for r in range(0,len(s[1][i])):
        for q in range(len(tests)): 

            sonic_in = sorted(
                Path(str(sonic_dir)+f"\\").glob("sonic"+str(q+1)+str(s[0][i])+str(s[1][i][r])+".TXT")
            )
            
            filein = str(sonic_in[0])
            sonic_df = pd.read_csv(filein, sep=",", names = ["time", "u","v","w","dir","t","u_eng","v_eng","wsp","wdir"])
            
            sonic_df.iloc[:,8] = sonic_df.iloc[:,8].apply(pd.to_numeric)
            sonic_df.iloc[:,9] = sonic_df.iloc[:,9].apply(pd.to_numeric)
            sonic_df.iloc[:,0] = pd.to_datetime(sonic_df.iloc[:,0], format = "%Y-%m-%d %H:%M:%S")
            
            sonic_df = sonic_df.resample('3S', on="time").mean()
            
            sonic_df = sonic_df.reset_index()
            if q+1 == 1:
                sonic_wsp1.append(sonic_df["wsp"].to_list())
                sonic_wdir1.append(sonic_df["wdir"].to_list())

            elif q+1 == 2:
                sonic_wsp2.append(sonic_df["wsp"].to_list())
                sonic_wdir2.append(sonic_df["wdir"].to_list())

            elif q+1 ==3:
                sonic_wsp3.append(sonic_df["wsp"].to_list())
                sonic_wdir3.append(sonic_df['wdir'].to_list())
        
        sonic_sens.append(f"sonic{r+1}")

print(sonic_wsp2)
def sonic_mean(q,lst):
    l = [item[q] for item in lst]
    return statistics.mean(l)

sfull = []
for v in range(70):
    s1 = round(sonic_mean(v,sonic_wsp1),2)
    sfull.append(s1)

for d in range(40):
    s2 = round(sonic_mean(d,sonic_wsp2),2)
    sfull.append(s2)

for w in range(50):
    s3 = round(sonic_mean(w,sonic_wsp3),2)
    sfull.append(s3)

sfull = pd.DataFrame(sfull)
sfull.to_csv(str(sonic_dir)+f"\\sonic_all.txt", header=None, index=None, sep=',', mode='a')


fig = plt.figure(figsize=(12, 8))  # (Width, height) in inches.
fig = plt.title(
    f"sonic time series",
    y=0.9,
)

fig, ax = plt.subplots(1, 1)

for t in range(len(sonic_wsp1)):
    ax.plot(
    sonic_wsp1[t],
    label=f"speed 1",
    color="green",

    )
    ax.plot(
        sonic_wsp2[t],
        label=f"speed 2",
        color="blue",

    )
    ax.plot(
        sonic_wsp3[t],
        label=f"speed 3",
        color="teal",

    )
ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, -0.8),
    ncol=6,
    fancybox=True,
    shadow=True,
)

ax.set_ylabel("Mean Wind Speed \n (m s^-1)", fontsize=12)
ax.set_xlabel("Time", fontsize=12)
ax.grid(zorder=1, linestyle="dashed", lw=0.5)

plt.savefig(
    str(img_dir) + f"\\sonic_test.png",
    dpi=300,
    bbox_inches="tight",
)



    


