import sqlite3
import FindSurfaceLocationsAndPlats
import pandas as pd
import numpy as np
import math
import utm
import pyodbc
import itertools
import ModuleAgnostic as ma
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import copy
import EditAGRCData


def turnIntoDB():
    conn = sqlite3.connect("C:\\Work\\RewriteAPD\\APD_Data.db")
    df_parsed_utm_latlon = pd.read_excel("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\LatLonUTM.xlsx", dtype='object')
    df_parsed_utm_latlon.to_sql("SectionDataCoordinates", conn, if_exists='replace')

    df_parsed_utm_latlon = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\CasingStrengths.csv", dtype='object')
    df_parsed_utm_latlon.to_sql("CasingStrengths", conn, if_exists='replace')

    df_parsed_utm_latlon = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\PlatGridNumbers.csv", dtype='object')
    df_parsed_utm_latlon.to_sql("GridDataLatLonUTM", conn, if_exists='replace')



def main2():
    # df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\OddballSections.csv", encoding="ISO-8859-1")
    # df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\All_Data_Lat_Lon.csv", encoding="ISO-8859-1")
    # df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\ConvertedData.csv", encoding="ISO-8859-1")
    df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\PlatAllSidesFour.csv", encoding="ISO-8859-1")


    data_test = df_parsed.to_numpy().tolist()
    new_data_file = []
    for i in data_test:
        data_init = i[:8]
        data_init[:6] = [int(r) for r in data_init[:6]]
        conc_code = addZeroesForConc(i)
        data_init[2] = int(float(translateDirectionToNumber('township', data_init[2])))

        data_init[4] = int(float(translateDirectionToNumber('rng', data_init[4])))
        data_init[5] = int(float(translateDirectionToNumber('baseline', data_init[5])))
        latlon = list(utm.to_latlon(i[6], i[7], 12, 'T'))

        line = data_init + latlon + [conc_code] + ['V.1']
        new_data_file.append(line)
    df_test = [{'Section': i[0], 'Township': int(float(i[1])), 'Township Direction': i[2], 'Range': int(float(i[3])),
                'Range Direction': i[4], 'Baseline': i[5], 'Easting': float(i[6]), 'Northing': float(i[7]), 'Latitude': float(i[8]), "Longitude": float(i[9]), 'Conc': i[10], 'Version': i[11]} for i in new_data_file]
    df = pd.DataFrame(df_test, columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', "Latitude", "Longitude", 'Conc', 'Version'])
    # df.to_csv('OddballUTMLatLon.csv', index=False)
    # df.to_csv('All_Data_Lat_Lon_UTM.csv', index=False)
    # df.to_csv('ConvertedData_Out.csv', index=False)




def addZeroesForConc(i):
    conc_code_merged = i[:6]
    conc_code_merged = [int(r) for r in conc_code_merged]
    conc_code_merged[2] = translateNumberToDirection('township', str(conc_code_merged[2]))
    conc_code_merged[4] = translateNumberToDirection('rng', str(conc_code_merged[4]))
    conc_code_merged[5] = translateNumberToDirection('baseline', str(conc_code_merged[5]))

    conc_code = [str(r) for r in conc_code_merged]
    len_lst = [len(r) for r in conc_code]
    if len_lst[0] == 1:
        conc_code[0] = "0" + str(conc_code[0])
    if len_lst[1] == 1:
        conc_code[1] = "0" + str(conc_code[1])
    if len_lst[3] == 1:
        conc_code[3] = "0" + str(conc_code[3])
    conc_code = "".join([str(q) for q in conc_code])
    return conc_code




def main():
    df_read = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\PlatSidesAll.csv", encoding="ISO-8859-1")
    df_read_test = df_read.to_numpy().tolist()
    for i in range(len(df_read_test)):
        conc_out = "".join([str(j) for j in df_read_test[i][:6]])
        df_read_test[i].append(conc_out)
    df_read_lst = ma.groupByLikeValues(df_read_test, -1)
    new_sides = coordsChecker(df_read_lst)
    # new_sides = [i[:-1] for i in new_sides]
    new_sides = ma.removeDupesListOfLists(new_sides)
    new_sides = alterAGRCData(new_sides)


    print("\n\n\n\n___________________________________________________________________________\nGO")
    added_data = []
    # df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\PlatGridNumbers.csv", encoding="ISO-8859-1")
    df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\PlatAllSidesFour.csv", encoding="ISO-8859-1")
    data_test = df_parsed.to_numpy().tolist()
    conn, cursor = sqlConnect()
    sql_lst, sql_conc = parseDatabaseForDataWithSectionsAndSHL(cursor)
    output = FindSurfaceLocationsAndPlats.matcherDF1(df_parsed, sql_lst)

    pd.set_option('display.max_columns', None)
    conc_codes_all = []
    version_number = 1
    for i in output:
        lst = FindSurfaceLocationsAndPlats.transformData2(i)
        if lst != []:
            data = lst[0]
            conc_code_merged, conc_code = reTranslateData(data[0])
            if conc_code_merged not in conc_codes_all:
                version_number = 1
            else:
                version_number += 1
            conc_codes_all.append(conc_code_merged)
            counter = 0
            for j in data:
                counter +=1
                latlon = list(utm.to_latlon(j[-3], j[-2], 12, 'T'))
                data_created = j[:-1] + latlon + [conc_code_merged] + ["V.1"]
                data_created[6] = float(data_created[6])
                data_created[7] = float(data_created[7])
                added_data.append(data_created)

    added_data = new_sides + added_data
    df_test = [{'Section': i[0], 'Township': int(float(i[1])), 'Township Direction': i[2], 'Range': int(float(i[3])),
                'Range Direction': i[4], 'Baseline': i[5], 'Easting': float(i[6]), 'Northing': float(i[7]), 'Latitude': float(i[8]), "Longitude": float(i[9]), 'Conc': i[10], 'Version': i[11]} for i in added_data]
    df = pd.DataFrame(df_test, columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', "Latitude", "Longitude", 'Conc', 'Version'])
    # df.to_csv('GridDataLatLonUTM.csv', index=False)

def alterAGRCData(lst):
    for i in range(len(lst)):
        latlon = list(utm.to_latlon(lst[i][6], lst[i][7], 12, 'T'))
        conc_code = EditAGRCData.makeConcCode(copy.deepcopy(lst[i]))
        # lst[i] = lst[i] + latlon + [conc_code] + ["AGRC V.1"]
        lst[i] = lst[i][:-1] + [conc_code] + ["AGRC V.1"] + [lst[i][:-1]]
    return lst
        # lst[i].append(conc_code)

def groupAndAssembleData(lst):
    lst_grouped = ma.groupByLikeValues(copy.deepcopy(lst), -2)
    for i in lst_grouped:
        grouped_data = ma.groupByLikeValues(copy.deepcopy(i), -1)

        if len(grouped_data) > 1:
            for j in grouped_data:
                clockwiseOrganizer(j)
        else:
            grouped_data[0]


def clockwiseOrganizer(lst):
    matched_lst = []
    lst_coords = [[i[6], i[7]] for i in lst]
    organize = EditAGRCData.checkClockwisePts(lst_coords)
    for i in organize:
        for j in lst:
            if i[0] == j[6] and i[1] == j[7]:
                matched_lst.append(j)

    for i in range(len(organize)):
        print(organize[i], matched_lst[i], lst[i])
    # print(lst[-1])
    if 'agrc' not in lst[-1][-1].lower():
        fig, ax1 = plt.subplots()
        x1, y1 = [i[6] for i in matched_lst], [i[7] for i in matched_lst]
        x2, y2 = [i[6] for i in lst], [i[7] for i in lst]
        ax1.plot(x2, y2, c='red')
        # ax1.plot(x1, y1, c='black')
        plt.show()


def coordsChecker(lst):
    tot_runner = 0
    new_sides = []
    for i in lst:
        # print(i)
        tot_runner += len(i)
        data_set = [r[6:8] for r in i]
        tsr_data = i[0][:6]
        data_x, data_y = [r[0] for r in data_set], [r[1] for r in data_set]
        if max(data_x) - min(data_x) < 10000 and max(data_y) - min(data_y) < 10000 and len(data_set) > 10:
            data_output = EditAGRCData.findCorners(data_set)
            for j in range(len(data_output)):
                data_output[j] = tsr_data + data_output[j]
                new_sides.append(data_output[j])
    return new_sides

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

def assembleDataCardinalDirections(lst):
    lst = [[i[6], i[7]] for i in lst]
    centroid = Polygon(lst).centroid
    centroid = [centroid.x, centroid.y]
    data_lengths = []
    for i in range(len(lst)):
        data_lengths.append(lst[i] + [ma.findSegmentLength(centroid, lst[i])])
    corners = EditAGRCData.cornerGeneratorProcess(data_lengths)
    data_lengths = EditAGRCData.reorganizeLstPointsWithAngle(data_lengths, centroid)
    east_side = EditAGRCData.arrangeDirectionData(corners, data_lengths, 'east')
    north_side = EditAGRCData.arrangeDirectionData(corners, data_lengths, 'north')
    west_side = EditAGRCData.arrangeDirectionData(corners, data_lengths, 'west')
    south_side = EditAGRCData.arrangeDirectionData(corners, data_lengths, 'south')
    all_data = west_side + north_side + east_side + south_side
    # if len(east_side) == 5:
    #     print('five')
    # print(east_side)
    # print(west_side)
    # if len(east_side) < 5:
    #     print("\n\nEastSide\n_____________")
    #     east_side = [list(t) for t in set(tuple(element) for element in east_side)]
    #     east_side = [[i[0], i[1]] for i in east_side]
    #     east_side = arranger(east_side, 'east')
    #     east_side = dividePoints(east_side, all_data)
    #     # east_side = arranger(east_side, 'east')
    # if len(north_side) < 5:
    #     print("\n\nNorthSide\n_____________")
    #
    #     north_side = [list(t) for t in set(tuple(element) for element in north_side)]
    #     north_side = [[i[0], i[1]] for i in north_side]
    #     north_side = arranger(north_side, 'north')
    #     north_side = dividePoints(north_side, all_data)
    #     # north_side = arranger(north_side, 'north')
    # if len(west_side) < 5:
    #     print("\n\nWestSide\n_____________")
    #     west_side = [list(t) for t in set(tuple(element) for element in west_side)]
    #     west_side = [[i[0], i[1]] for i in west_side]
    #     west_side = arranger(west_side, 'west')
    #     west_side = dividePoints(west_side, all_data)
    #     # west_side = arranger(west_side, 'west')
    # if len(south_side) < 5:
    #     print("\n\nSouthSide\n_____________")
    #     south_side = [list(t) for t in set(tuple(element) for element in south_side)]
    #     south_side = [[i[0], i[1]] for i in south_side]
    #     south_side = arranger(south_side, 'south')
    #
    #     south_side = dividePoints(south_side, all_data)

        # south_side = arranger(south_side, 'south')
    if len(south_side) < 5:
        print('length')
    if len(west_side) < 5:
        print('length')
    if len(north_side) < 5:
        print('length')
    if len(east_side) < 5:
        print('length')
    all_data = west_side + north_side + east_side + south_side

def arranger(lst, label):

    # all_data = [[i[0], i[1]] for i in lst]

    if label == 'west' or label == 'east':
        sorted_data = sorted(lst, key=lambda r: r[1], reverse=True)
        return sorted_data
    else:
        sorted_data = sorted(lst, key=lambda r: r[0])
        return sorted_data

def dividePoints(side, all_data):
    length_lst = []
    all_pts = [[],[],[],[],[]]
    all_data = [[i[0], i[1]] for i in all_data]


    for i in range(len(side)-1):
        length_lst.append(ma.findSegmentLength(side[i], side[i+1]) * 3.2808399)

    if len(side) == 2:
        for j in range(4):
            div = j / 4
            all_pts[j] = [findPointsOnLine(side[0][:2], side[1][:2], div), "P"]
        all_pts[0], all_pts[-1] = [side[0][:2],"T"], [side[1][:2], "T"]
        return all_pts

    elif len(side) == 3:
        i_lst = [0,2]
        length_lst = length_lst[::-1]
        if 1.2 > length_lst[0]/length_lst[1] > 0.8:
            for i in range(2):
                counter = i_lst[i]
                for j in range(3):
                    div = j/3
                    all_pts[counter] = [findPointsOnLine(side[i][:2], side[i+1][:2], div), "P"]
                    counter += 1
            all_pts[0], all_pts[2], all_pts[4] = [side[0][:2], "T"], [side[1][:2], "T"], [side[2][:2], "T"]
            return all_pts
        else:
            if length_lst[0] < length_lst[1]:
                # fig, ax1 = plt.subplots()
                for j in range(3):
                    div = j/3
                    all_pts[j] = [findPointsOnLine(side[0][:2], side[1][:2], div), "P"]
                all_pts[0], all_pts[3], all_pts[4] = [side[0], "T"], [side[1], "T"], [side[2], "T"]
                return all_pts
                # test_data = [i for i in all_pts if i]
                # x3, y3 = [i[0][0] for i in test_data], [i[0][1] for i in test_data]
                # x2, y2 = [i[0] for i in all_data], [i[1] for i in all_data]
                # for i in range(len(x3)):
                #     ax1.text(x3[i], y3[i], str(i))
                # ax1.scatter(x2, y2, c='red', s=150)
                # ax1.scatter(x3, y3, c='black')
                # plt.show()
            else:
                for j in range(3):
                    div = j / 3
                    all_pts[j] = [findPointsOnLine(side[0][:2], side[1][:2], div), "P"]
                # test_data = [i for i in all_pts if i]
                all_pts[0], all_pts[3], all_pts[4] = [side[0][:2], "T"], [side[1][:2], "T"], [side[2][:2], "T"]
                # used_pts = [side[0][:2]] + [side[1][:2]]
                return all_pts

    elif len(side) == 4:
        print("length 4")
        side_data = [i[:2] for i in side]
        dict_lst = dict(enumerate(ma.grouper(sorted(length_lst), 600), 1))
        dict_lst = [j for t, j in dict_lst.items()]
        long_len = min(dict_lst, key=len)
        # print(position)
        print(length_lst)
        print(long_len)
        position = length_lst.index(long_len)

        if position == 0:
            # print('pos1')
            pt1, pt2 = side_data[0], side_data[1]
            for j in range(2):
                div = j / 2
                all_pts[j] = [findPointsOnLine(pt1, pt2, div), "P"]
            all_pts[2], all_pts[3], all_pts[4] = [side[1][:2], "T"], [side[2][:2], "T"], [side[3][:2], "T"]
            return all_pts
        elif position == 2:
            # print('pos2')
            pt1, pt2 = side_data[2], side_data[3]
            for j in range(2):
                div = j / 2
                all_pts[2+j] = [findPointsOnLine(pt1, pt2, div), "P"]

            all_pts[0], all_pts[1], all_pts[4] = [side[0], "T"], [side[1], "T"], [side[3], "T"]
            return all_pts
        else:
            # print(position)
            fig, ax1 = plt.subplots()

            # test_data = [i for i in all_pts if i]
            x3, y3 = [i[0] for i in side_data], [i[1] for i in side_data]
            x2, y2 = [i[0] for i in all_data], [i[1] for i in all_data]
            for i in range(len(x3)):
                ax1.text(x3[i], y3[i], str(i))
            ax1.scatter(x2, y2, c='red', s=150)
            ax1.scatter(x3, y3, c='black')
            plt.show()


        # else:

    # elif len(side) == 4:
    #     print(4)
    # if len(side) == 3:
    #     for i in range(len(side)-1):
    #         for j in range():
    #             div = j / 3
    #             new_point = findPointsOnLine(side[i], side[i+1], div)
    #             print(new_point)
    # if len(side) == 2:
    #     for i in range(len(side)-1):
    #         for j in range(2):
    #             div = j / 2
    #             new_point = findPointsOnLine(side[i], side[i+1], div)
    #             print(new_point)



def findPointsOnLine(xy1, xy2, div):
    x, y = xy1[0] + (div * (xy2[0] - xy1[0])), xy1[1] + (div * (xy2[1] - xy1[1]))
    return [x, y]

def reTranslateData(i):
    tsr_data = i[11:]
    conc_code_merged = i[:6]

    conc_code_merged[2] = translateNumberToDirection('township', str(conc_code_merged[2]))
    conc_code_merged[4] = translateNumberToDirection('rng', str(conc_code_merged[4]))
    conc_code_merged[5] = translateNumberToDirection('baseline', str(conc_code_merged[5]))
    conc_code = [str(r) for r in conc_code_merged]
    len_lst = [len(r) for r in conc_code]
    if len_lst[0] == 1:
        conc_code[0] = "0" + str(conc_code[0])
    if len_lst[1] == 1:
        conc_code[1] = "0" + str(conc_code[1])
    if len_lst[3] == 1:
        conc_code[3] = "0" + str(conc_code[3])
    conc_code = "".join([str(q) for q in conc_code])
    # return tsr_data, conc_code, conc_code_merged
    return conc_code, conc_code_merged



def convertData(shl, data_lst, utm_data):
    utm_x = abs(shl[0] - float(utm_data[0]))
    utm_y = abs(shl[1] - float(utm_data[1]))
    data_utm = []
    for i in data_lst:
        x = i[0] + utm_x
        y = i[1] + utm_y
        data_utm.append([x, y])
    return data_utm


def parseDatabaseForDataWithSectionsAndSHL(cursor):
    execute1 = ' select Wh_sec,[Wh_Twpn],[Wh_Twpd], [Wh_RngN], [Wh_RngD], [Wh_Pm], NorthReference, iFGridConvergence, X, Y, SUBSTRING(tal.API, 0, 11) As API, [Wh_FtNS], [Wh_Ns], [Wh_FtEW], [Wh_EW]'
    execute2 = ' from [dbo].[DirectionalSurveyHeader] as dsh'
    execute3 = ' join [dbo].[tblAPDLoc] tal on SUBSTRING(tal.API, 0, 11) = dsh.APINumber'
    execute4 = " where Wh_X IS NOT NULL and Wh_Y IS NOT NULL and Wh_FtNS is not Null and Wh_FtEW is not Null and API is not Null and Wh_Ns is not Null and Wh_EW is not Null and Wh_Sec is not Null and Wh_Twpn is not Null and Wh_Twpd is not Null and Wh_RngD is not Null and Wh_RngN is not Null and Wh_Pm is not Null"

    data_lst = cursor.execute(execute1 + execute2 + execute3 + execute4)
    data_lst = fixer(data_lst)
    data_lst = [list(t) for t in set(tuple(element) for element in data_lst)]
    for i in range(len(data_lst)):
        data_lst[i] = convertAllPosibleStringsToFloats(data_lst[i])
        data_lst[i][2] = translateDirectionToNumber('township', data_lst[i][2])
        data_lst[i][4] = translateDirectionToNumber('rng', data_lst[i][4])
        data_lst[i][5] = translateDirectionToNumber('baseline', data_lst[i][5])

    data_lst1 = [i[:6] for i in data_lst]
    data_lst1 = [[int(float(data_lst1[i][j])) for j in range(len(data_lst1[i]))] for i in range(len(data_lst1))]
    data_lst2 = [int(float(i[10])) for i in data_lst]
    for i in range(len(data_lst)):
        data_lst[i][:6] = data_lst1[i]
        data_lst[i][10] = data_lst2[i]
    sql_conc = [str(i[0]) + str(i[1]) + str(i[2]) + str(i[3]) + str(i[4]) + str(i[5]) for i in data_lst]

    # for i in sql_conc:
    #     count = sql_conc.count(i)

    return data_lst, sql_conc


def fixer(lst):
    fixed_lst = []
    for row in lst:
        fixed_lst.append(list(map(str, list(row))))
    return fixed_lst


def sqlConnect():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS01;"
        "Database=UTRBDMSNET;"
        "Trusted_Connection = yes;")
    cursor = conn.cursor()
    return conn, cursor


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


def pointsConverter(data):
    x_pts, y_pts = [], []
    x, y = 0, 0
    data = reorderDecimalData(data)
    data = ma.oneToMany(data, 4)
    for i in range(len(data)):
        for j in range(len(data[i])):
            x_pts.append(x)
            y_pts.append(y)
            x, y = pointLineFinder(data[i][j], x, y)
    x_pts.append(x)
    y_pts.append(y)
    output = list(zip(x_pts, y_pts))
    output = [list(i) for i in output]

    return output


def pointLineFinder(i, x, y):
    center_x, center_y = x, y
    r, angle = i[0], i[1]
    x = center_x + (r * math.cos(math.radians(angle)))
    y = center_y + (r * math.sin(math.radians(angle)))
    return x, y


def reorderDecimalData(data):
    return [data[0], data[1], data[2], data[3], data[8], data[9], data[10], data[11], data[4], data[5], data[6], data[7], data[15], data[14], data[13], data[12]]


def translateNumberToDirection(variable, val):
    if variable == 'rng':
        if val == '2':
            return 'W'
        elif val == '1':
            return 'E'
    elif variable == 'township':
        if val == '2':
            return 'S'
        elif val == '1':
            return 'N'
    elif variable == 'baseline':
        if val == '2':
            return 'U'
        elif val == '1':
            return 'S'
    elif variable == 'alignment':
        if val == '1':
            return 'SE'
        elif val == '2':
            return 'NE'
        elif val == '3':
            return 'SW'
        elif val == '4':
            return 'NW'


def convertAllPosibleStringsToFloats(lst):
    for i in range(len(lst)):
        if isinstance(lst[i], list):
            for j in range(len(lst[i])):
                try:
                    lst[i][j] = float(lst[i][j])
                except ValueError:
                    pass
        else:
            try:
                lst[i] = float(lst[i])
            except ValueError:
                pass

    return lst


def translateDirectionToNumber(variable, val):
    if variable == 'rng':
        if val == 'W':
            return '2'
        elif val == 'E':
            return '1'
        else:
            return val
    elif variable == 'township':
        if val == 'S':
            return '2'
        elif val == 'N':
            return '1'
        else:
            return val
    elif variable == 'baseline':
        if val == 'U':
            return '2'
        elif val == 'S':
            return '1'
        else:
            return val
    elif variable == 'alignment':
        if val == 'SE':
            return '1'
        elif val == 'NE':
            return '2'
        elif val == 'SW':
            return '3'
        elif val == 'NW':
            return '4'
        else:
            return val


def findSurfaceCoordinate(data, tsr_data):
    eq_lst, data = getLineSegmentSlopeEquation(data)
    ns_lines, ns_points, ew_lines, ew_points = generateParallelLineSegmentLinesAndPoints(eq_lst, data, tsr_data)
    intersection, ns_side, ew_side = createParallelLineSegments(ns_points, ew_points, tsr_data)
    surfaceRelativeCoordinate, nsSidePts, ewSidePts = intersection, ns_side, ew_side
    return surfaceRelativeCoordinate
    # data = list(itertools.chain.from_iterable(data))
    # data = list(data for data, _ in itertools.groupby(data))
    # data = [[i[0] + surfaceRelativeCoordinate[0], i[1] + surfaceRelativeCoordinate[1]] for i in data]


def getLineSegmentSlopeEquation(data):
    # data = data[getVersionGrid1()]
    eq_lst = [ma.slopeFinder2(data[i], data[(i + 1) % len(data)]) for i in range(len(data))]
    eq_lst = list(itertools.chain.from_iterable(eq_lst))
    data = [data[:5], data[4:9], data[8:13], data[12:]]
    return ma.oneToMany(eq_lst, 4), data


def generateParallelLineSegmentLinesAndPoints(eq_lst, data, tsr_data):
    ns_dir, ew_dir = tsr_data[1], tsr_data[3]
    ns_eq = [eq_lst[4:9], eq_lst[12:]]
    ew_eq = [eq_lst[:5], eq_lst[8:13]]
    ns_lines = [ns_eq[0] if ns_dir == 'FNL' else ns_eq[1]]  # for i in ns_eq]
    ew_lines = [ew_eq[0] if ns_dir == 'FWL' else ew_eq[1]]  # for i in ew_eq]
    ns_points = data[1] if ns_dir == 'FNL' else data[3]
    ew_points = data[0] if ew_dir == 'FWL' else data[2]
    return ns_lines, ns_points, ew_lines, ew_points


def createParallelLineSegments(ns_p, ew_p, tsr_data):
    ns_d, ew_d = int(float(tsr_data[0])), int(float(tsr_data[2]))
    ns_segments = [lineSegmentCalculator(ns_p[i], ns_p[i + 1], ns_d, 'ns') for i in range(len(ns_p) - 1)]
    ew_segments = [lineSegmentCalculator(ew_p[i], ew_p[i + 1], ew_d, 'ew') for i in range(len(ew_p) - 1)]
    intersection, ns_id, ew_id, i, j = detectIntersectionParseProcess(ns_segments, ew_segments)

    return intersection, ns_id, ew_id


def detectIntersectionParseProcess(ns, ew):
    for i in range(len(ns)):
        for j in range(len(ew)):
            line_ns = LineString([Point(ns[i][0]), Point(ns[i][1])])
            line_ew = LineString([Point(ew[j][0]), Point(ew[j][1])])
            outcome = line_ns.intersection(line_ew)
            try:
                intersection = [outcome.x, outcome.y]
                return intersection, ns[i], ew[j], i, j
            except AttributeError:
                pass


def lineSegmentCalculator(xy1, xy2, direct, cardinal_dir):
    x1, y1, x2, y2 = xy1[0], xy1[1], xy2[0], xy2[1]
    r = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    data_out = []
    if r != 0:
        delta_x = (direct / r) * (xy1[1] - xy2[1])
        delta_y = (direct / r) * (xy2[0] - xy1[0])
        x3, y3 = xy1[0] - delta_x, xy1[1] - delta_y
        x4, y4 = xy2[0] - delta_x, xy2[1] - delta_y
        data_out = [[x3, y3], [x4, y4]]
    if r == 0:
        if cardinal_dir == 'ns':
            y1 = y1 + direct
            y2 = y2 + direct
        else:
            x1 = x1 + direct
            x2 = x2 + direct
        data_out = [[x1, y1], [x2, y2]]
    return data_out

#
main()
# main2()
# turnIntoDB()