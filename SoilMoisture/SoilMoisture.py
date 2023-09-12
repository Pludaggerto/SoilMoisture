import os
import pandas as pd
import logging

import matplotlib
from matplotlib import pyplot as plt 
from matplotlib import colors

import datetime

plt.rc('font',family='Times New Roman') 

def main():
    
    root = r"C:\Campbellsci\PC400"
    figFolder = set_folder(root, "fig")

    RT_Data_568     = os.path.join(root, "CR1000XSeries_568_RT_Data.dat")
    Day_Data_568    = os.path.join(root, "CR1000XSeries_568_Day_Data.dat")
    TenMin_Data_568 = os.path.join(root, "CR1000XSeries_568_TenMin_Data.dat")

    RT_Data_567     = os.path.join(root, "CR1000XSeries_567_RT_Data.dat")
    Day_Data_567    = os.path.join(root, "CR1000XSeries_567_Day_Data.dat")
    TenMin_Data_567 = os.path.join(root, "CR1000XSeries_567_TenMin_Data.dat")

    log = logging.getLogger()
    handler = logging.StreamHandler()
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    TenMin   = read_data(TenMin_Data_568)
    Day      = read_data(Day_Data_568)
    RealTime = read_data(RT_Data_568)

    for y in Day.columns:
        if "TMn" in y or "TMx" in y:
            Day[y] = Day[y].apply(date_to_num)

    Day['TIMESTAMP(TS)']    = pd.to_datetime(Day['TIMESTAMP(TS)']   , format='%Y-%m-%d %H:%M:%S')
    TenMin['TIMESTAMP(TS)'] = pd.to_datetime(TenMin['TIMESTAMP(TS)'], format='%Y-%m-%d %H:%M:%S')

    plot_single_object(TenMin, figFolder, "568_10min")
    plot_single_object(Day, figFolder, "568_1day")
    plot_VWC(TenMin, figFolder, "568_10min")
    plot_temperature_compare(Day, figFolder, "568_1day")
    plot_depth_temperature(Day, figFolder, "568_10min")
    plot_water_time(Day, figFolder, "568_1day")
    for i in range(1, 30):
        plot_one_day(TenMin, figFolder, 2022, 10, i)

def read_data(filename):
    logging.info("Reading " + filename)
    with open(filename, 'r') as File:
        lines = []
        line = File.readline()
        lines.append(line)
        counts = 1
        while line:
            if counts >= 5:
                break
            line = File.readline()
            lines.append(line)
            counts += 1

    varNames = lines[1][:-2].split(",")
    varNames = [var[1:-1] for var in varNames]
    varUnits = lines[2][:-2].split(",")
    varUnits = [var[1:-1] for var in varUnits]
    varTotals = ""

    for i in range(len(varNames)):
        # Actual depth in station 568
        if "100cm" in varNames[i]:
            index = varNames[i].find("100cm")
            varNames[i] = varNames[i][:index] + "70cm" + varNames[i][index+5:]
        # Actual unit of rainfall
        if "Rain_To" in varNames[i]:
            varUnits[i] = "mm"
        varTotal = varNames[i] + "(" + varUnits[i] + ")"
        if i == 0:
            varTotals = varTotal
        else:
            varTotals = varTotals + "," + varTotal


    with open(filename, 'r') as File:
        lines = File.readlines()

    temp = filename[:-4] + "_tmp.dat"
    with open(filename[:-4] + "_tmp.dat", "w") as File:
        lines = [varTotals + "\n"] + lines[4:]
        File.writelines(lines)

    df = pd.read_csv(temp)
    # os.remove(temp)
    return df

def set_folder(folder, name):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def filter_and_get_name(df, y):

    if ("/" in y):
        index = y.find("/")
        yName = y[:index] + "_" + y[index + 1:]
    else:
        yName = y

    try:
        df_temp = df[df[y] != "NAN"]
        df_temp[y]=df_temp[y].astype(float)
        return df_temp, yName
    except:
        return df, yName

def plot_single_object(df, path, types):

    path = set_folder(path, types)
    ys = df.columns[1:]
    
    for y in ys:

        df_temp, yName = filter_and_get_name(df, y)

        try:
            if "TMn" in y or "TMx" in y:

                fig = plt.figure(figsize=(12, 9))
                ax = fig.add_subplot(111)
                ax = df_temp.plot(x = 'TIMESTAMP(TS)', y = y, ax = ax, kind = "scatter")
                ax.tick_params(axis='x', labelrotation= -30)

                index = y.find("(")
                yLabel = y[:index] + "(h)"

                ax.set_title(types, fontsize = 26)
                ax.set_xlabel("time", fontsize = 20)
                ax.set_ylabel(yLabel, fontsize = 22)

                plt.yticks(fontsize = 20)
                plt.xticks(fontsize = 22)
                
                plt.grid(alpha = 0.5)
                plt.savefig(os.path.join(path, yLabel), dpi = 300)

            else:

                df_temp, yName = filter_and_get_name(df, y)
                df_temp = df_temp.set_index('TIMESTAMP(TS)')
                fig = plt.figure(figsize=(12, 9))
                ax = fig.add_subplot(111)
                ax = df_temp.plot(y = y, ax = ax, fontsize=14)
                

                ax.set_title(types, fontsize = 26)
                ax.set_xlabel("time", fontsize = 22)
                ax.set_ylabel(y, fontsize = 22)

                plt.yticks(fontsize = 22)
                ax.tick_params(axis='x',which='minor',labelsize =18)
                plt.legend(fontsize = 24)
                plt.savefig(os.path.join(path, yName), dpi = 300)

        except:
            logging.info("error in "  + y) 

def plot_VWC(df, path, types, subtitle = ""):
    """
    10 mins data
    """
    path = set_folder(path, types)
    names = ['TIMESTAMP(TS)', "VWC_5cm(m^3/m^3)", 'VWC_10cm(m^3/m^3)', 'VWC_30cm(m^3/m^3)', 'VWC_50cm(m^3/m^3)', 'VWC_70cm(m^3/m^3)']
    for name in names:
        df, _ = filter_and_get_name(df, name)
    df_plot = df[names]
    df_plot = df_plot.set_index('TIMESTAMP(TS)')
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    ax = df_plot.plot(ax = ax, fontsize=14)
    ax.set_title("VWC " + subtitle, fontsize = 22)
    ax.set_xlabel("time", fontsize = 20)
    ax.set_ylabel("VWC", fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.xticks(fontsize = 20)
    plt.legend(fontsize = 24)
    ax.tick_params(axis='x',which='minor',labelsize =18)
    plt.savefig(os.path.join(path, "VMC_total"), dpi = 300)

    return None

def plot_temperature_compare(df, path, types):
    """
    1 day data
    """
    path = set_folder(path, types)
    names = ['TIMESTAMP(TS)', 'Air_T_Avg(deg C)', 'Air_T_Max(deg C)', 'Air_T_Min(deg C)']
    for name in names:
        df, _ = filter_and_get_name(df, name)
    df_plot = df[names]

    df_plot['TIMESTAMP(TS)'] = pd.to_datetime(df_plot['TIMESTAMP(TS)'], format='%Y-%m-%d %H:%M:%S')
    df_plot = df_plot.set_index('TIMESTAMP(TS)')

    df_station = pd.read_excel(r"C:\Users\lwx\source\repos\SoilMoisture\SoilMoisture\zhuhai.xlsx")
    df_station = df_station[["date", "station_max", "station_min"]]
    df_station['date']=pd.to_datetime(df_station['date'], format='%Y-%m-%d')
    df_station = df_station.set_index("date")

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    df_total = df_station.join(df_plot)
    ax = df_total.plot(ax = ax, fontsize=20)
    ax.set_title("Temperature", fontsize = 22)
    ax.set_xlabel("time", fontsize = 20)
    ax.set_ylabel("temperature", fontsize = 20)
    ax.tick_params(axis='x',which='minor',labelsize =18)
    plt.yticks(fontsize = 20)
    plt.xticks(fontsize = 20)
    plt.legend(fontsize = 20)
    plt.savefig(os.path.join(path, "Temperature"), dpi = 300)

    return None

def plot_depth_temperature(df, path, types):
    """
    1 day data
    """
    path = set_folder(path, types)
    names = ['TIMESTAMP(TS)', "TSoil_5cm_Avg(deg C)", 'TSoil_10cm_Avg(deg C)', 'TSoil_30cm_Avg(deg C)', 
             'TSoil_50cm_Avg(deg C)', 'TSoil_70cm_Avg(deg C)']
    for name in names:
        df, _ = filter_and_get_name(df, name)
    df_plot = df[names]

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    ax = df_plot.plot(x = 'TIMESTAMP(TS)', ax = ax, fontsize=14)
    ax.set_title("Temperature_Soil", fontsize = 26)
    ax.set_xlabel("time", fontsize = 20)
    ax.set_ylabel("Temperature", fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.xticks(fontsize = 20)
    plt.legend(fontsize = 24)
    ax.tick_params(axis='x',which='minor',labelsize =18)
    ax.tick_params(axis='x', labelrotation= -10)
    plt.savefig(os.path.join(path, "Temperature_oil"), dpi = 300)

def plot_depth_temperature_tenmin(df, path, types, subtitles = ""):
    """
    1 day data
    """
    path = set_folder(path, types)
    names = ['TIMESTAMP(TS)', "TSoil_5cm(deg C)", 'TSoil_10cm(deg C)', 'TSoil_30cm(deg C)', 
             'TSoil_50cm(deg C)', 'TSoil_70cm(deg C)']
    for name in names:
        df, _ = filter_and_get_name(df, name)
    df_plot = df[names]

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    ax = df_plot.plot(x = 'TIMESTAMP(TS)', ax = ax, fontsize=14)
    ax.set_title("Soil Temperature" + " " + subtitles, fontsize = 26)
    ax.set_xlabel("time", fontsize = 20)
    ax.set_ylabel("Temperature", fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.xticks(fontsize = 20)
    ax.tick_params(axis='x',which='minor',labelsize =18)
    plt.legend(fontsize = 24)

    plt.savefig(os.path.join(path, "Temperature_oil"), dpi = 300)


def date_to_num(dateStr):
    time24 = dateStr.split(" ")[-1].split(":")
    timeNum = float(time24[0]) + float(time24[1]) / 60 + float(time24[2]) / 3600
    return timeNum

def plot_water_time(df, path, types):
    """
    1 day 
    """
   
    path = set_folder(path, types)
    names = ['TIMESTAMP(TS)', "VWC_5cm_TMx(m^3/m^3)", 'VWC_10cm_TMx(m^3/m^3)', 
             'VWC_30cm_TMx(m^3/m^3)', 'VWC_50cm_TMx(m^3/m^3)', 'VWC_70cm_TMx(m^3/m^3)']

    ys = ["VWC_5cm_TMx(m^3/m^3)", 'VWC_10cm_TMx(m^3/m^3)', 
          'VWC_30cm_TMx(m^3/m^3)', 'VWC_50cm_TMx(m^3/m^3)', 'VWC_70cm_TMx(m^3/m^3)']

    for y in ys:
        try:
            df, _ = filter_and_get_name(df, y)
        except:
            logging.info("None")

    df_plot = df[names]
    df_plot.columns = ['TIMESTAMP(TS)', "VWC_5cm_TMx(h)", 'VWC_10cm_TMx(h)', 
                       'VWC_30cm_TMx(h)', 'VWC_50cm_TMx(h)', 'VWC_70cm_TMx(h)']

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    
    #ax = df_plot.plot(x = 'TIMESTAMP(TS)', y = "VWC_5cm_TMx(h)", ax = ax, fontsize=14, kind = "scatter")
    #ax = df_plot.plot(x = 'TIMESTAMP(TS)', y = "VWC_10cm_TMx(h)", ax = ax, fontsize=14, kind = "scatter")
    #ax = df_plot.plot(x = 'TIMESTAMP(TS)', y = "VWC_30cm_TMx(h)", ax = ax, fontsize=14, kind = "scatter")
    #ax = df_plot.plot(x = 'TIMESTAMP(TS)', y = "VWC_50cm_TMx(h)", ax = ax, fontsize=14, kind = "scatter")
    #ax = df_plot.plot(x = 'TIMESTAMP(TS)', y = "VWC_70cm_TMx(h)", ax = ax, fontsize=14, kind = "scatter")

    ax.plot_date(df_plot['TIMESTAMP(TS)'], df_plot["VWC_5cm_TMx(h)"],  c = "red", label = "VWC_5cm_TMx(h)")
    ax.plot_date(df_plot['TIMESTAMP(TS)'], df_plot["VWC_10cm_TMx(h)"], c = "green", label = "VWC_10cm_TMx(h)")
    ax.plot_date(df_plot['TIMESTAMP(TS)'], df_plot["VWC_30cm_TMx(h)"], c = "black", label = "VWC_30cm_TMx(h)")
    ax.plot_date(df_plot['TIMESTAMP(TS)'], df_plot["VWC_50cm_TMx(h)"], c = "orange", label = "VWC_50cm_TMx(h)")
    ax.plot_date(df_plot['TIMESTAMP(TS)'], df_plot["VWC_70cm_TMx(h)"], c = "cyan", label = "VWC_70cm_TMx(h)")
    ax.tick_params(axis='x',which='minor',labelsize =18)
    ax.set_title("Water Content", fontsize = 26)
    ax.set_xlabel("time", fontsize = 20)
    ax.set_ylabel("VMC(h)", fontsize = 20)

    plt.yticks(fontsize = 20)
    plt.xticks(fontsize = 20)
    plt.legend(fontsize = 24)

    plt.savefig(os.path.join(path, "water_content_compare.jpg"), dpi = 300)

def plot_one_day(df, path, year, month, day):
   low = datetime.datetime(year, month, day)
   high = datetime.timedelta(1) + low
   df = df[(df['TIMESTAMP(TS)'] > low) & (df['TIMESTAMP(TS)'] < high)]
   types = str(year) + "_" + str(month) + "_" + str(day)
   plot_single_object(df, path, types)
   plot_depth_temperature_tenmin(df, path, types, types)
   plot_VWC(df, path, types, types)

def compare_data():
    return
   
if __name__ == '__main__':
    main()