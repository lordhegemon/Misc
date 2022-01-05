import ModuleAgnostic as ma
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import ProcessCoordData
import ProcessBHLLocation
from itertools import chain
from matplotlib import pyplot as plt
import math
import pandas as pd
import numpy as np
import sqlite3


def convertAnglesToBearing(data_set):
    conn = sqlite3.connect("C:\\Work\\RewriteAPD\\APD_Data.db")
    string_sql = 'select * from BearingConverter'
    df = pd.read_sql(string_sql, conn, index_col='index')
    for i in range(len(data_set)):
        dec_val, deg_val = converter(data_set[i], df)
        print(dec_val, deg_val, data_set[i])

def converter(val, df):

    val_floor, val_ceil = math.floor(val), math.ceil(val)
    found_df = df[df["Degrees (MPL)"].between(val_floor, val_ceil, inclusive='both')].to_numpy().tolist()
    distances = [val - found_df[0][0], found_df[1][0] - val]
    if found_df[0][2] > found_df[1][2]:
        data = found_df[0][2] - distances[0]
        return data, ma.convertDecimalToDegrees(data)
    else:
        data = found_df[0][2] + distances[0]
        return data, ma.convertDecimalToDegrees(data)


def convertAnglesToBearing2(data_set):
    # grid_data = [[1, 7, 2, 19, 1, 1, 'West-Up2', 1401.17, 2, 24, 4, 1, 'G', '1721911West-Up2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'West-Up1', 1401.17, 2, 24, 4, 1, 'G', '1721911West-Up1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'West-Down1', 1368.6, 2, 24, 25, 1, 'G', '1721911West-Down1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'West-Down2', 1368.6, 2, 24, 25, 1, 'G', '1721911West-Down2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'East-Up2', 1387.21, 1, 47, 26, 1, 'G', '1721911East-Up2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'East-Up1', 1387.21, 1, 47, 26, 1, 'G', '1721911East-Up1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'East-Down1', 1342, 1, 18, 36, 1, 'G', '1721911East-Down1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'East-Down2', 1342, 1, 18, 36, 1, 'G', '1721911East-Down2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'North-Left2', 1343.95, 88, 50, 57, 2, 'G', '1721911North-Left2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'North-Left1', 1343.95, 88, 50, 57, 2, 'G', '1721911North-Left1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'North-Right1', 1343.9, 88, 52, 3, 2, 'G', '1721911North-Right1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'North-Right2', 1344.08, 88, 51, 9, 2, 'G', '1721911North-Right2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'South-Left2', 1326.06, 88, 0, 35, 3, 'G', '1721911South-Left2', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'South-Left1', 1326.74, 87, 58, 16, 3, 'G', '1721911South-Left1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'South-Right1', 1325.35, 88, 1, 7, 3, 'G', '1721911South-Right1', 'V.1'],
    #              [1, 7, 2, 19, 1, 1, 'South-Right2', 1315.62, 87, 57, 25, 3, 'G', '1721911South-Right2', 'V.1']]
    df = pd.read_excel("C:\\Work\\RewriteAPD\\Datasets\\AngleToBearing.xlsx", dtype='object')
    # conn = sqlite3.connect("C:\\Work\\RewriteAPD\\APD_Data.db")
    # df = pd.read_excel("C:\\Work\\RewriteAPD\\Datasets\\AngleToBearing.xlsx", dtype='object')
    # df = pd.read_excel("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\LatLonUTM.xlsx", dtype='object')
    # df.to_sql("BearingConverter", conn, if_exists='replace')
    # val = 187.78
    # data_test_vals = [271.31, 1.1475000000000364, 182.04305555555555]
    # output = convertToDecimal(grid_data)
    # for i in range(len(output)):
    #     convertBack(output[i][1], df, grid_data[i])
    # print()
    for i in range(len(data_set)):
        converter(data_set[i], df)

def convertBack(val, df, grid_data):
    ma.printFunctionName()
    print('value', val)
    val_floor, val_ceil = math.floor(val), math.ceil(val)
    print(val_floor, val_ceil)
    found_df = df[df["Degrees (MPL)"].between(val_floor, val_ceil, inclusive='both')].to_numpy().tolist()
    distances = [val - found_df[0][0], found_df[1][0] - val]
    deg, min, sec = grid_data[2], grid_data[3], grid_data[4]
    dec_val_base = (deg + min / 60 + sec / 3600)
    if found_df[0][2] > found_df[1][2]:
        print(grid_data,ma.convertDecimalToDegrees(dec_val_base), found_df[0][-1])
        print(found_df[0][2] - distances[0], dec_val_base)
    else:
        print(grid_data, ma.convertDecimalToDegrees(dec_val_base), found_df[0][-1])
        print(found_df[0][2] + distances[0], dec_val_base)

def converter2(val, df):
    ma.printFunctionName()
    val_floor, val_ceil = math.floor(val), math.ceil(val)
    found_df = df[df["Degrees (MPL)"].between(val_floor, val_ceil, inclusive='both')].to_numpy().tolist()
    distances = [val - found_df[0][0], found_df[1][0] - val]
    if found_df[0][2] > found_df[1][2]:
        data = found_df[0][2] - distances[0]
        return data, ma.convertDecimalToDegrees(data)
        # print(data, ma.convertDecimalToDegrees(data))
    else:
        data = found_df[0][2] + distances[0]
        return data, ma.convertDecimalToDegrees(data)
        # print(data, ma.convertDecimalToDegrees(data))
        # print(data, ma.convertDecimalToDegrees(data))
    # print("end")
def convertToDecimal(data):
    data_converted = []
    for i in range(len(data)):
        data[i] = data[i][6:12]
        data[i][1] = float(data[i][1])
        side, deg, min, sec, dir_val = data[i][1], data[i][2], data[i][3], data[i][4], data[i][5]
        dec_val_base = (deg + min / 60 + sec / 3600)
        if 'west' in data[i][0].lower():
            if dir_val in [4, 1]:
                decVal = 90 + dec_val_base
            else:
                decVal = 90 - dec_val_base
        if 'east' in data[i][0].lower():
            if dir_val in [4, 1]:
                decVal = 270 + dec_val_base
            else:
                decVal = 270 - dec_val_base
        if 'north' in data[i][0].lower():
            if dir_val in [3, 2]:
                decVal = 360 - (270 + dec_val_base)
            else:
                decVal = 270 + dec_val_base
        if 'south' in data[i][0].lower():
            if dir_val in [4, 1]:
                decVal = 90 + dec_val_base
            else:
                decVal = 360 - (90 + dec_val_base)
        data_converted.append([side, decVal])
    return data_converted

convertAnglesToBearing([271.31, 1.1475000000000364, 182.04305555555555])
