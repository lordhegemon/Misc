import utm
import pandas as pd
import numpy as np
def mainConverter():
    df = pd.read_csv("All_Data_Lat_lon.csv", encoding="ISO-8859-1")
    # df = pd.read_csv("Export_Output_Part1.csv", encoding="ISO-8859-1")
    # df2 = pd.read_csv("Export_Output_Part2.csv", encoding="ISO-8859-1")
    # pd.set_option('display.max_columns', None)
    # df['TOWNSHIP'] = df.PLSSID.str[5:7]
    # df['TOWNSHIP_DIR'] = df.PLSSID.str[8:9]
    # df['RANGE'] = df.PLSSID.str[10:12]
    # df['RANGE_DIR'] = df.PLSSID.str[13:14]
    # df['SECTION'] = df.FRSTDIVID.str[-3:-1]
    # df['BASEMERIDI'] = df.PLSSID.str[2:4]
    # df['BASEMERIDIAN'] = ['S' if x == '26' else 'U' for x in df['BASEMERIDI']]
    # df['new_code'] = [str(x) + str(y) + str(z) + str(a) + str(b) + str(c) for x, y, z, a, b, c in zip(df['SECTION'], df['TOWNSHIP'], df['TOWNSHIP_DIR'], df['RANGE'], df['RANGE_DIR'], df['BASEMERIDIAN'])]
    # df['Easting'] = df.apply(lambda x: utm.from_latlon(x['Lat'], x['Lon'])[0], axis=1)
    # df['Northing'] = df.apply(lambda x: utm.from_latlon(x['Lat'], x['Lon'])[1], axis=1)
    #
    # df2['TOWNSHIP'] = df2.PLSSID.str[5:7]
    # df2['TOWNSHIP_DIR'] = df2.PLSSID.str[8:9]
    # df2['RANGE'] = df2.PLSSID.str[10:12]
    # df2['RANGE_DIR'] = df2.PLSSID.str[13:14]
    # df2['SECTION'] = df2.FRSTDIVID.str[-3:-1]
    # df2['BASEMERIDI'] = df2.PLSSID.str[2:4]
    # df2['BASEMERIDIAN'] = ['S' if x == '26' else 'U' for x in df2['BASEMERIDI']]
    # df2['new_code'] = [str(x) + str(y) + str(z) + str(a) + str(b) + str(c) for x, y, z, a, b, c in zip(df2['SECTION'], df2['TOWNSHIP'], df2['TOWNSHIP_DIR'], df2['RANGE'], df2['RANGE_DIR'], df2['BASEMERIDIAN'])]
    # df2['Easting'] = df2.apply(lambda x: utm.from_latlon(x['Lat'], x['Lon'])[0], axis=1)
    # df2['Northing'] = df2.apply(lambda x: utm.from_latlon(x['Lat'], x['Lon'])[1], axis=1)
    #
    # df = df[['FID', 'TOWNSHIP', 'RANGE', 'SECTION', 'BASEMERIDI', 'Lat', 'Lon', 'Easting', 'Northing', 'PLSSID', 'FRSTDIVID', 'new_code']]
    # df2 = df2[['FID', 'TOWNSHIP', 'RANGE', 'SECTION', 'BASEMERIDI', 'Lat', 'Lon', 'Easting', 'Northing', 'PLSSID', 'FRSTDIVID', 'new_code']]
    # out = df.append(df2)
    # out.to_csv('All_Data_Lat_lon.csv')

    pass

def valueChange(value):

    if value == 26:
        return 'S'
    elif value == 30:
        return 'U'


mainConverter()
