import logging
import os

import pandas as pd

class Reader(object):

    def __init__(self, fileName, dataType = "cehui"):
        """Read the received data"""
        logging.info("Reading " + fileName)
        self.fileName = fileName
        self.dataType = dataType

        # 测绘学院土壤湿度计的格式
        if dataType == "cehui":   

            with open(fileName, 'r') as File:

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
                # Actual depth 
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

            with open(fileName, 'r') as File:
                lines = File.readlines()

            temp = fileName[:-4] + "_tmp.dat"
            with open(fileName[:-4] + "_tmp.dat", "w") as File:
                lines = [varTotals + "\n"] + lines[4:]
                File.writelines(lines)

        if dataType == "tumu":
            self.fileName = fileName
            with open(fileName, 'r', encoding = "utf-8") as File:
                lines = []
                line = File.readline()
                lines.append(line)
                counts = 1
                while line:
                    if counts >= 4:
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

            with open(fileName, 'r', encoding = "utf-8") as File:
                lines = File.readlines()

            temp = fileName[:-4] + "_tmp.dat"
            with open(fileName[:-4] + "_tmp.dat", "w", encoding = "utf-8") as File:
                lines = [varTotals + "\n"] + lines[4:]
                File.writelines(lines)

        self.data = pd.read_csv(temp)
        os.remove(temp)

    def __del__(self):
        return 

    def to_csv(self, name = "", cols = [], write = True):

        if cols == []:
            data = self.data
        else:
            data = self.data[cols]

        if write:
            if name == "":
                data.to_csv(self.fileName[:-4] + "_filter.csv", index = False)
            else:
                data.to_csv(name, index = False)

        return data

    def read_VWC(self):

        if self.dataType == "cehui":
            cols = ["TIMESTAMP(TS)", "VWC_5cm_Avg(m^3/m^3)", "VWC_10cm_Avg(m^3/m^3)", "VWC_30cm_Avg(m^3/m^3)", "VWC_50cm_Avg(m^3/m^3)", "VWC_70cm_Avg(m^3/m^3)"]
            name = self.fileName[:-4] + "_VMC.csv"
        
        if self.dataType == "tumu":
            cols = ["TIMESTAMP(TS)", "Soil_05cm_VWC_Avg(m³/m³)", "Soil_10cm_VWC_Avg(m³/m³)", "Soil_20cm_VWC_Avg(m³/m³)", "Soil_40cm_VWC_Avg(m³/m³)"]
            name = self.fileName[:-4] + "_VMC.csv"

        self.to_csv(name, cols)