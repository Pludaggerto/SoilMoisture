import os
import pandas as pd
import logging

import matplotlib
from matplotlib import pyplot as plt 
from matplotlib import colors

plt.rc('font',family='Times New Roman') 

def main():
    
    root = r"C:\Campbellsci\PC400"
    figFolder = set_folder(root, "fig")

    RT_Data_568  = os.path.join(root, "CR1000XSeries_568_RT_Data.dat")
    Day_Data_568 = os.path.join(root, "CR1000XSeries_568_Day_Data.dat")
    TenMin_Data_568 = os.path.join(root, "CR1000XSeries_568_TenMin_Data.dat")

    RT_Data_567  = os.path.join(root, "CR1000XSeries_567_RT_Data.dat")
    Day_Data_567 = os.path.join(root, "CR1000XSeries_567_Day_Data.dat")
    TenMin_Data_567 = os.path.join(root, "CR1000XSeries_567_TenMin_Data.dat")

    log = logging.getLogger()
    handler = logging.StreamHandler()
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    TenMin   = read_data(TenMin_Data_568)
    Day      = read_data(Day_Data_568)
    # RealTime = read_data(RT_Data_568)
    plot_single_object(TenMin, figFolder, "568_10min")
    plot_single_object(Day, figFolder, "568_1day")

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

def plot_single_object(df, path, types):
    ys = df.columns[1:]

    for y in ys:
        try:
            fig = plt.figure(figsize=(9, 6))
            ax = fig.add_subplot(111)

            df_temp = df[df[y] != "NAN"]
            df_temp[y]=df_temp[y].astype(float)
            ax = df_temp.plot(x = 'TIMESTAMP(TS)', y = y, ax = ax)
            if ("/" in y):
                index = y.find("/")
                yName = y[:index] + "_" + y[index + 1:]
            else:
                yName = y
            plt.savefig(os.path.join(path, types + "_" + yName))
        except:
            logging.info("error in" + y)

if __name__ == '__main__':
    main()