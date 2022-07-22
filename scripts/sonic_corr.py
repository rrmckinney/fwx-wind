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

from context import sonic_dir, img_dir
from utils.wind import get_sonic

import warnings
########## INPUTS ########

sonic6_220513_1 = pd.read_csv(str(sonic_dir)+f"\\sonic1220513wind06.txt", sep=",")
sonic6_220513_2 = pd.read_csv(str(sonic_dir)+f"\\sonic2220513wind06.txt", sep=",")
sonic6_220513_3 = pd.read_csv(str(sonic_dir)+f"\\sonic3220513wind06.txt", sep=",")

sonic20_220513_1 = pd.read_csv(str(sonic_dir)+f"\\sonic1220513wind20.txt", sep=",")
sonic20_220513_2 = pd.read_csv(str(sonic_dir)+f"\\sonic2220513wind20.txt", sep=",")
sonic20_220513_3 = pd.read_csv(str(sonic_dir)+f"\\sonic3220513wind20.txt", sep=",")

mean1_diff6, mean1_diff20, mean2_diff6, mean2_diff20, mean3_diff6, mean3_diff20 = [], [],[],[],[],[] 
sonic06diff1, sonic06diff2,sonic06diff3 =  {}, {},{}
sonic20diff1, sonic20diff2,sonic20diff3 =  {}, {},{}

for i in range(0,6):
    print(i)
    sonic1, sonic2, sonic3 = {},{},{}
    sonic1 = pd.read_csv(str(sonic_dir)+f"\\sonic1220512wind{i}.txt", sep=",")
    sonic2 = pd.read_csv(str(sonic_dir)+f"\\sonic2220512wind{i}.txt", sep=",")
    sonic3 = pd.read_csv(str(sonic_dir)+f"\\sonic3220512wind{i}.txt", sep=",")

    sonic06diff1['wind'+str(i)]  = sonic6_220513_1.iloc[:,8] - sonic1.iloc[:,8]
    sonic06diff2['wind'+str(i)]  = sonic6_220513_2.iloc[:,8] - sonic2.iloc[:,8]
    sonic06diff3['wind'+str(i)]  = sonic6_220513_3.iloc[:,8] - sonic3.iloc[:,8]

    sonic20diff1['wind'+str(i)] = sonic20_220513_1.iloc[:,8] - sonic1.iloc[:,8]
    sonic20diff2['wind'+str(i)] = sonic20_220513_2.iloc[:,8] - sonic2.iloc[:,8]
    sonic20diff3['wind'+str(i)] = sonic20_220513_3.iloc[:,8] - sonic3.iloc[:,8]

    mean1_diff6.append((round(sonic06diff1['wind'+str(i)].mean(), 2)))
    mean2_diff6.append((round(sonic06diff2['wind'+str(i)].mean(), 2)))
    mean3_diff6.append((round(sonic06diff3['wind'+str(i)].mean(), 2)))

    mean1_diff20.append((round(sonic20diff1['wind'+str(i)].mean(), 2)))
    mean2_diff20.append((round(sonic20diff2['wind'+str(i)].mean(), 2)))
    mean3_diff20.append((round(sonic20diff3['wind'+str(i)].mean(), 2)))


fig = plt.figure(figsize=(8, 8))  # (Width, height) in inches.
fig.suptitle(
    f"Sonic Position 1 - Position 2",
    y=0.9,
)

ax = fig.add_subplot(1, 1, 1)

# ax.plot(sonic20diff1['wind1'], label="Speed1", color="blue")
# ax.plot(sonic20diff2['wind1'], label="Speed2", color="green")
# ax.plot(sonic20diff3['wind1'], label="Speed3", color="teal")
ax.plot(mean1_diff6,marker='o', label="Speed1", color="blue")
ax.plot(mean2_diff6,marker='o', label="Speed2", color="green")
ax.plot(mean3_diff6,marker='o', label="Speed3", color="purple")
ax.plot(mean1_diff20,marker='o', label="Speed1", color="red")
ax.plot(mean2_diff20,marker='o', label="Speed2", color="orange")
ax.plot(mean3_diff20,marker='o', label="Speed3", color="yellow")
ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, -0.),
    ncol=6,
    fancybox=True,
    shadow=True,
)
plt.savefig(
    str(img_dir) + f"\\sonicdiffall.png",
    dpi=300,
    bbox_inches="tight",
)

# sonic20_220512_1 = cup_df = pd.read_csv(str(sonic_dir)+f"\\sonic1220512wind20.txt", sep=",")
# sonic20_220512_2 = cup_df = pd.read_csv(str(sonic_dir)+f"\\sonic2220512wind20.txt", sep=",")
# sonic20_220512_3 = cup_df = pd.read_csv(str(sonic_dir)+f"\\sonic3220512wind20.txt", sep=",")

#sonic06 = pd.sonicFrame({"time":sonic6_220513.iloc[0],"wsp":sonic06diff})
#sonic20 = pd.sonicFrame({"time":sonic20_220513.iloc[0],"wsp":sonic20diff})
# print(sonic20diff1, sonic20diff2, sonic20diff3)
# print(sonic06diff1, sonic06diff2, sonic06diff3)

# ax.plot([sonic06diff1[i] for i in range(0,2250, 100)], marker='o', linestyle=':', label="Speed1", color = "blue")
# ax.plot([sonic06diff2[i] for i in range(0,2250,100)],marker='o', linestyle=':', label="Speed2", color = "green")
# ax.plot([sonic06diff3[i] for i in range(0,2250,100)],marker='o', linestyle=':', label="Speed3", color = "teal")
