import context
import numpy as np
import pandas as pd

def choice(choose):
    if choose == 1:
        ## Position 1 ##
        dates = ["220512","220519", "220520"]
        sensors = [ ["%.2d" % i for i in range(1,21)], 
                    ["%.2d" % i for i in range(21,26)], 
                    ["%.2d" % i for i in range(26,29)]]

        direction = ["350"]
        return dates, sensors, direction

    elif choose ==2:
        ## Position 2 ##
        dates = ["220515","220516"]
        sensors = [["%.2d" % i for i in range(1,21)], 
                    ["%.2d" % i for i in range(21,29)]]
        direction = ["280"]
        return dates, sensors, direction


def gettime(time_of_int):
    """
    input
        str in decimal hours
    returns
        HH:mm:ss.SSS string for time on int
    """
    hour = int(time_of_int)
    minute = (time_of_int * 60) % 60
    seconds = (time_of_int * 3600) % 60
    decisecond = (time_of_int * 36000) % 60
    datetime_of_int = "%d:%02d:%02d.%d" % (hour, minute, seconds, decisecond)
    return datetime_of_int


def get_sonic(filein, i, length):

    ## open and set headers for sonic dataframe
    header = [
        "ID",
        "U_eng",
        "V_eng",
        "W",
        "units",
        "sos",
        "internal temp",
        "ind1",
        "ind2",
    ]
    print(filein)
    sonic_df = pd.read_csv(filein, names=header, encoding_errors='ignore')
    file_date = filein[-15:-7]
    ## parse datetime from timestampe in file name
    decimal_end_hour = float(int(file_date[-2:]) / 4)
    decimal_end_deciseconds = decimal_end_hour * 60 * 60 / 0.1  # decimal end hour
    decimal_start_hour = (
        (decimal_end_deciseconds - len(sonic_df)) / 60 / 60 * 0.1
    )  # decimal start hour

    end_hour = gettime(decimal_end_hour)
    start_hour = gettime(decimal_start_hour)
    # print(f"start time {start_hour}")
    # print(f"end time {end_hour}")

    ## define stat and end date time for pandas
    start_datetime = (
        f"20{file_date[:2]}-{file_date[2:4]}-{file_date[4:6]}-T{start_hour}"
    )
    end_datetime = f"20{file_date[:2]}-{file_date[2:4]}-{file_date[4:6]}-T{end_hour}"

    ## create dataetime array and set as dataframe index
    sonic_date_range = pd.date_range(
        start_datetime, end_datetime, periods=len(sonic_df)
    )
    if i == length-1:
        # start_offest = pd.Timestamp(start_hour[2:])
        diff =  sonic_date_range[-1] - sonic_date_range[0] 
        diff =  pd.Timedelta(minutes=30) - diff
        sonic_date_range = sonic_date_range - diff
        # print(diff)
        # print(sonic_date_range[-1])
    else:
        pass
    # sonic_date_range = sonic_date_range + diff

    sonic_df = sonic_df.set_index(pd.DatetimeIndex(sonic_date_range))
    sonic_df = sonic_df.dropna()
    del sonic_df["ID"]
    del sonic_df["units"]
    del sonic_df["ind1"]
    del sonic_df["ind2"]
    sonic_df["U_eng"] = sonic_df["U_eng"].replace("+", "")
    sonic_df["V_eng"] = sonic_df["V_eng"].replace("+", "")
    sonic_df["W"] = sonic_df["W"].replace("+", "")
    sonic_df = sonic_df.apply(pd.to_numeric)  # convert all columns of DataFrame

    ## convert u and v to wind speed and direction
    sonic_df["U_eng"][(sonic_df["U_eng"] > 20) | (sonic_df["U_eng"] < -20)] = sonic_df[
        "U_eng"
    ].mean()
    sonic_df["V_eng"][(sonic_df["V_eng"] > 20) | (sonic_df["V_eng"] < -20)] = sonic_df[
        "V_eng"
    ].mean()

    sonic_df["U"] = sonic_df["V_eng"] * -1
    sonic_df["V"] = sonic_df["U_eng"]
    # wsp = np.sqrt((sonic_df["U"] ** 2) + (sonic_df["V"] ** 2))
    wsp = ((sonic_df["U"] ** 2) + (sonic_df["V"] ** 2)) ** 0.5

    sonic_df["wsp"] = wsp
    # wdir = ((180 / np.pi) * np.arctan2(sonic_df["U"], sonic_df["V"]))
    wdir = 180 + ((180 / np.pi) * np.arctan2(sonic_df["U"], sonic_df["V"]))
    # wdir[wdir <= 0] = wdir + 360
    sonic_df["wdir"] = wdir

    sonic_df = sonic_df.reset_index()
    return sonic_df