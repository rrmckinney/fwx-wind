## %
import context
import numpy as np
import pandas as pd
from pathlib import Path
from functools import reduce
from pylab import *
from sklearn import linear_model, feature_selection
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from context import data_dir, img_dir, sonic_dir
from utils.wind import get_sonic, choice

import warnings

warnings.filterwarnings("ignore")
## Choose posiion of interest ##

########## INPUTS ########
wdir_correction = 180
test_dirs = [0]  # zero or one options
slice_fd = [20, -5]

#Files of Interest
cup_choice = 2    #choose position for cups (1 or 2), sonic must be opposite
sonic_choice = 1
###### END INPUTS ########

df_wsp = pd.DataFrame()
df_wdir = pd.DataFrame()

#### Get all sonic data ####
sonic_in = sorted(Path(str(sonic_dir)).glob(f"sonic_all_{sonic_choice}.txt"))
filein = str(sonic_in[0])
sonic_in = pd.read_csv(filein)
sonic_in = sonic_in.reset_index()
############## UBC Cup Anemometer Data set up ####################

c = choice(cup_choice)
wind_rs = []
sens = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16",
"17","18","19","20","21","22","23","24","25","26","27","28"]

for i in range(len(c[0])):
    wind_sens,sonic_sens = [], []
    for r in range(0,len(c[1][i])):
       
        cup_in = sorted(
            Path(str(data_dir) +"_20"+str(c[0][i])+ f"\\WIND{c[1][i][r]}\\").glob(f"20{c[0][i]}*.TXT")
        )

        print(str(data_dir) + f"\\WIND{c[1][i][r]}\\")
        print(cup_in)
        filein = str(cup_in[0])
        # print(filein)
        cup_df = pd.read_csv(filein, sep="\t")
        cup_df[["wsp", "wdir"]] = cup_df[["wsp", "wdir"]].apply(pd.to_numeric)
        cup_df["wsp"] = cup_df["wsp"] * 0.44704  ## convert to m\s

        cup_df["wdir"] = cup_df["wdir"] - wdir_correction
        cup_df["wdir"][cup_df["wdir"] < 0] = cup_df["wdir"] + 360
        
        # cup_date_range = pd.date_range(
        #     "20" + c[0][i] + "T" + filein[-10:-4], periods=len(cup_df), freq="3S"
        # )
        # cup_df = cup_df.set_index(pd.DatetimeIndex(cup_date_range))

        cup_df = cup_df.iloc[slice_fd[0] : slice_fd[1]]

        df_wsp[f"wind{c[1][i][r]}"] = cup_df["wsp"]

        df_wdir["wind{c[1][i][r]}"] = cup_df["wdir"]

        wind_sens.append(f"wind{c[1][i][r]}")


# ### Pearson correlation
# Solve Pearson correlation prior to linear regression
for u in range(0,28):
    wind_r = round(df_wsp[f"wind{sens[u]}"].corr(sonic_in.iloc[:,0]), 4)
    wind_rs.append(wind_r)
    print(f"Pearson correlation for (ubc_wind{sens[u]},sonic) = {wind_r}")

# ## Scatter plots
# Make scatter plots of the data points for each pm sensor and plot the linear regression line in the scatter plots.

# %%
ny = len(sens) // 2
nx = len(sens) - ny
cmap = cm.get_cmap("jet", len(sens))
colors = []
for i in range(cmap.N):
    rgba = cmap(i)
    #print(matplotlib.colors.rgb2hex(rgba))
    colors.append(matplotlib.colors.rgb2hex(rgba))
color = colors[i]

# fig = plt.figure(figsize=(nx * 5, ny * 5))  # (Width, height) in inches.
# for i in range(len(sens)):
#     ax = fig.add_subplot(ny, nx, i + 1)
#     sns.regplot(x=df_wsp[f"wind{sens[i]}"].dropna(), y=sonic_in.iloc[0:len(df_wsp[f"wind{sens[i]}"].dropna()),0], color=colors[i])
#     ax.set_title(f"(wind{sens[i]},sonic) $r$ = {wind_rs[i]}")
#     ax.set_ylabel(r"Sonic Wind Speed ($\frac{m}{s}$)", fontsize=14)
#     ax.set_xlabel(r"Cup Wind Speed ($\frac{m}{s}$)", fontsize=14)
#     ax.tick_params(axis="both", which="major", labelsize=13)
#     ax.xaxis.grid(color="gray", linestyle="dashed")
#     ax.yaxis.grid(color="gray", linestyle="dashed")
# fig.tight_layout()

def make_mlr(i):
    X = df_wsp[f"wind{sens[i]}"].dropna().values[:, np.newaxis]
    y = sonic_in.iloc[0:len(df_wsp[f"wind{sens[i]}"].dropna()),1].values
    lm_MLR = linear_model.LinearRegression()
    model = lm_MLR.fit(X, y)
    ypred_MLR = lm_MLR.predict(X)  # y predicted by MLR
    intercept_MLR = lm_MLR.intercept_  # intercept predicted by MLR
    coef_MLR = lm_MLR.coef_  # regression coefficients in MLR model
    R2_MLR = lm_MLR.score(X, y)  # R-squared value from MLR model

    # print("MLR results:")
    # print(f"a0 = {intercept_MLR}")

    coeff = {"a0": intercept_MLR}
    for j in range(len(coef_MLR)):
        coeff.update({f"a{j+1}": coef_MLR[j]})
        # print(f"a{j+1} = {coef_MLR[j]}")
    if len(coeff) > 2:
        raise ValueError("This is a linear model, code only does single")
    else:
        pass
    ax = fig.add_subplot(7, 4, i + 1)
    ax.set_ylabel(r"Cup Wind Speed ($\frac{m}{s}$)", fontsize=14)
    ax.set_xlabel(r"Sonic Wind Speed ($\frac{m}{s}$)", fontsize=14)
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.xaxis.grid(color="gray", linestyle="dashed")
    ax.yaxis.grid(color="gray", linestyle="dashed")
    sns.regplot(x=y, y=ypred_MLR, color=colors[i])
    # print(coeff)
    # print(coef_MLR)

    ax.set_title(
        f"UBC-WIND-{sens[i]}  MLR "
        + r"$R^{2}$"
        + f"= {round(R2_MLR,4)} \n y = {round(coeff['a0'],4)} + {round(coeff['a1'],4)}x"
    )
    return

fig = plt.figure(figsize=(7* 5, 4 * 5))  # (Width, height) in inches.
for i in range(len(sens)):
    make_mlr(i)
fig.tight_layout()
fig.savefig(str(img_dir) + f"//position2-mlr.png", dpi=250, bbox_inches="tight")
