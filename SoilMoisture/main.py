import logging
import os

import pandas as pd
from Reader import Reader

def main():
    root = r"D:\SoilMoisture\data\土木湿度计"
    Reader(os.path.join(root, "CR1000XSeries_Daily_2023_05_22_16_29_57.dat"), "tumu").read_VWC()

if __name__ == '__main__':
    main()
    
