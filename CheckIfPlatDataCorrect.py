import os
import pandas as pd
import numpy as np

import GatherPlatDataSet
import ModuleAgnostic as ma
import math
import pyodbc
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import ProcessCoordData
import ProcessBHLLocation
from itertools import chain
from matplotlib import pyplot as plt


def drawData():
    conn, cursor = sqlConnect()
    sql_lst, sql_conc = parseDatabaseForDataWithSectionsAndSHL(cursor)
    df = pd.read_csv("All_Data_Lat_Lon.csv", encoding="ISO-8859-1")
    pd.set_option('display.max_columns', None)
    # df_lst = df.to_numpy().tolist()
    # label_lst = df['new_code'].unique
    fig, ax = plt.subplots()
    for i in range(len(sql_lst)):
        sql_lst[i][0], sql_lst[i][1], sql_lst[i][3] = int(sql_lst[i][0]), int(sql_lst[i][1]), int(sql_lst[i][3])
        sql_lst[i][2] = translateNumberToDirection('township', str(int(sql_lst[i][2])))
        sql_lst[i][4] = translateNumberToDirection('rng', str(int(sql_lst[i][4])))
        sql_lst[i][5] = translateNumberToDirection('baseline', str(int(sql_lst[i][5])))
        if len(str(sql_lst[i][0])) == 1:
            sql_lst[i][0] = "0" + str(sql_lst[i][0])
        if len(str(sql_lst[i][1])) == 1:
            sql_lst[i][1] = "0" + str(sql_lst[i][1])
        if len(str(sql_lst[i][3])) == 1:
            sql_lst[i][3] = "0" + str(sql_lst[i][3])
        sql_conc_str = str(sql_lst[i][0]) + str(sql_lst[i][1]) + str(sql_lst[i][2]) + str(sql_lst[i][3]) + str(sql_lst[i][4]) + str(sql_lst[i][5])

        df_tester = df[df['new_code'] == sql_conc_str][['Easting', 'Northing']].to_numpy().tolist()
        shl = sql_lst[i][8:10]

        if determineIfInside(shl, df_tester):
            x, y = [q[0] for q in df_tester], [q[1] for q in df_tester]
            if max(x) - min(x) < 10000:
                a = df_tester
                b = df_tester[1:] + [df_tester[0]]
                side_parameters = [float(sql_lst[i][-4]), float(sql_lst[i][-2])]
                a = np.array(a)
                b = np.array(b)
                p = np.array(shl)
                out = lineseg_dists(p, a, b)
                out = out.tolist()
                #
                if checkSides(out, side_parameters):
                    # fig, ax = plt.subplots()
                    print(sql_conc_str)
                    ax.plot(x, y, c='red')
                    # ax.scatter(x, y, c='red')
                    ax.scatter([shl[0]], [shl[1]], c='red')
                    # ma.printLine(df_tester)
                    # print()
                    # print(a)
                    # print(b)
                    # NS_distance, EW_distance = findLocationData(d_lst[j], shl)
                    # print(int(float(label_lst[j][:2])), sql_lst[i][0])
                    # if int(float(label_lst[j][:2])) == sql_lst[i][0] and int(float(label_lst[j][2:4])) == sql_lst[i][1] and int(float(label_lst[j][5:7])) == sql_lst[i][3]:
                    # print('foo')
    plt.show()
            # print('shl', shl)



    # d, d_lst = {}, []
    # d_label, label_lst = {}, []
    # for row in df_lst:
    #     re_data = row[8:10]
    #     if row[-1] not in d:
    #         d_label[row[-1]] = []
    #         d[row[-1]] = []
    #     d[row[-1]].append(re_data)
    #     d_label[row[-1]].append(row[-1])
    # d_lst = [key for item, key in d.items()]
    # label_lst = [key for item, key in d_label.items()]
    # # label_lst = [list(set(i))[0] for i in label_lst]
    #
    # for j in range(len(d_lst)):
    #     for i in range(len(sql_lst)):
    #         shl = sql_lst[i][8:10]
    #         try:
    #             if determineIfInside(shl, d_lst[j]):
    #                 x, y = [q[0] for q in d_lst[j]], [q[1] for q in d_lst[j]]
    #                 if max(x) - min(x) < 10000:
    #                     a = d_lst[j]
    #                     b = d_lst[j][1:] + [d_lst[j][0]]
    #                     a = np.array(a)
    #                     b = np.array(b)
    #                     p = np.array(shl)
    #                     out = lineseg_dists(p, a, b)
    #                     out = out.tolist()
    #                     fig, ax = plt.subplots()
    #                     # print(out)
    #
    #                     print(min(x), max(x))
    #                     ax.plot(x, y, c='red')
    #                     ax.scatter(x, y, c='red')
    #                     ax.scatter([shl[0]], [shl[1]], c='red')
    #                     ma.printLine(d_lst[j])
    #                     # print()
    #                     # print(a)
    #                     # print(b)
    #                     # NS_distance, EW_distance = findLocationData(d_lst[j], shl)
    #                     # print(int(float(label_lst[j][:2])), sql_lst[i][0])
    #                     # if int(float(label_lst[j][:2])) == sql_lst[i][0] and int(float(label_lst[j][2:4])) == sql_lst[i][1] and int(float(label_lst[j][5:7])) == sql_lst[i][3]:
    #                     # print('foo')
    #                     plt.show()
    #         except ValueError:
    #             pass
    # # ma.printLine(conc_lst)

def checkSides(lst, sides):
    ns_side = []
    ew_side = []
    for r in lst:
        ns_side.append(abs(r - sides[0]))
        ew_side.append((r - sides[1]))
    if min(ns_side) < 10 and min(ew_side) < 10:
        return True
    else:
        return False


def getAngles(data1, data2, point):
    slope_lst = [GatherPlatDataSet.slopeFinder2(data1[i], data2[i]) ]
    for i in range(len(data1)):
        slope = GatherPlatDataSet.slopeFinder2(data1[i], data2[i])
        slope_lst.append(slope[0])

def lineseg_dists(p, a, b):
    """Cartesian distance from point to line segment

    Edited to support arguments as series, from:
    https://stackoverflow.com/a/54442561/11208892

    Args:
        - p: np.array of single point, shape (2,) or 2D array, shape (x, 2)
        - a: np.array of shape (x, 2)
        - b: np.array of shape (x, 2)
    """
    # normalized tangent vectors
    d_ba = b - a
    d = np.divide(d_ba, (np.hypot(d_ba[:, 0], d_ba[:, 1])
                           .reshape(-1, 1)))

    # signed parallel distance components
    # rowwise dot products of 2D vectors
    s = np.multiply(a - p, d).sum(axis=1)
    t = np.multiply(p - b, d).sum(axis=1)

    # clamped parallel distance
    h = np.maximum.reduce([s, t, np.zeros(len(s))])

    # perpendicular distance component
    # rowwise cross products of 2D vectors
    d_pa = p - a
    c = d_pa[:, 0] * d[:, 1] - d_pa[:, 1] * d[:, 0]

    return np.hypot(h, c)



def mainProcessRemoveDupes():
    df = pd.read_csv("CoordDataPlats.csv", encoding="ISO-8859-1")
    pd.set_option('display.max_columns', None)
    df_lst = df.to_numpy().tolist()
    grouped_lst, conc_unique_lst = [], []
    id_conc = [str(i[0]) + str(i[1]) + str(i[2]) + str(i[3]) + str(i[4]) + str(i[5]) for i in df_lst]
    id_conc = list(set(id_conc))
    id_conc = [[i] for i in id_conc]
    for i in range(len(id_conc)):
        for j in range(len(df_lst)):
            if str(df_lst[j][0]) + str(df_lst[j][1]) + str(df_lst[j][2]) + str(df_lst[j][3]) + str(df_lst[j][4]) + str(df_lst[j][5]) == id_conc[i][0]:
                id_conc[i].append(df_lst[j])
    for i in range(len(id_conc)):
        # if len(id_conc[i]) > 21:
        grouped_lst.append(id_conc[i][1:21])
    fig, ax = plt.subplots()
    for i in grouped_lst:
        x, y = [j[6] for j in i], [j[7] for j in i]
        ts = translateNumberToDirection('township', str(int(i[0][2])))
        rng = translateNumberToDirection('rng', str(int(i[0][4])))
        bs = translateNumberToDirection('baseline', str(int(i[0][5])))
        id = str(int(float(i[0][0]))) + " " + str(int(float(i[0][1]))) + ts + " " + str(int(float(i[0][3]))) + rng + " " + bs
        centroid = (sum(x) / len(i), sum(y) / len(i))
        ax.text(centroid[0], centroid[1], id)
        ax.plot(x, y, c='red')
    plt.show()
    grouped_lst = list(chain.from_iterable(grouped_lst))



    # saveData(grouped_lst)
def mainProcess():
    df_lst, df_conc, restricted_lst,id_conc = loadData()
    conn, cursor = sqlConnect()
    sql_lst, sql_conc = parseDatabaseForDataWithSectionsAndSHL(cursor)
    corrected_lst = findComparisonList(df_lst, df_conc, sql_lst, sql_conc, restricted_lst, id_conc)
    consolidate_lst = consolidateData(corrected_lst, df_lst)
    saveData(consolidate_lst)

def consolidateData(corrected_lst, df_lst):
    consolidate_lst = []
    for i in range(len(corrected_lst)):
        for j in range(len(df_lst)):
            if corrected_lst[i][0] == df_lst[j][0] and corrected_lst[i][1] == df_lst[j][1] and corrected_lst[i][2] == df_lst[j][2] and corrected_lst[i][3] == df_lst[j][3] and corrected_lst[i][4] == df_lst[j][4] and corrected_lst[i][5] == df_lst[j][5]:
                consolidate_lst.append(df_lst[j])
    return consolidate_lst

def findComparisonList(df_lst, df_conc, sql_lst, sql_conc, restricted_lst, id_conc):
    corrected_lst = []
    df_lst = [list(t) for t in set(tuple(element) for element in df_lst)]
    sql_lst = [list(t) for t in set(tuple(element) for element in sql_lst)]
    unique_sections, unique_sections_multiple = [], []
    for i in range(len(sql_lst)):
        shl = sql_lst[i][8:10]
        for j in range(len(restricted_lst)):
            if determineIfInside(shl, restricted_lst[j]):
                try:
                    NS_distance, EW_distance = findLocationData(restricted_lst[j], shl)
                    if int(float(id_conc[j][:2])) == sql_lst[i][0] and int(float(id_conc[j][2:4])) == sql_lst[i][1] and int(float(id_conc[j][5:7])) == sql_lst[i][3]:

                        if 1.02 > NS_distance/ sql_lst[i][-4] > .98 and 1.02 > EW_distance/ sql_lst[i][-2] > .98:
                            if sql_conc[i] in unique_sections:
                                unique_sections_multiple.append(sql_conc[i])
                            corrected_lst.append(sql_lst[i][:6])
                            unique_sections.append(sql_conc[i])
                except:
                    pass
    ma.printLine(list(set(unique_sections_multiple)))
    return corrected_lst

def findLocationData(coord_lst, well_location):
    coord_lst = ma.oneToMany(coord_lst,5)
    NS_distance, EW_distance, side_data, northing_index, easting_index = ProcessBHLLocation.findBHLLocation(coord_lst, well_location)
    return NS_distance, EW_distance

def saveData(lst):
    df = pd.DataFrame(columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', 'API'])
    for i in lst:
        new_row = {'Section': i[0],
                   'Township': int(float(i[1])),
                   'Township Direction': i[2],
                   'Range': int(float(i[3])),
                   'Range Direction': i[4],
                   'Baseline': i[5],
                   'Easting': i[6],
                   'Northing': i[7],
                   'API': i[8]}
        df = df.append(new_row, ignore_index=True)
    df.to_csv('UTMDataEdited.csv', index=False)
# [2722322,3322322,3122222,132122,3022222,23922111,1632222,932222,3022112,21922111,3632122,3652622,15722211,2732422,92622011,2222322,1732112,2522322,16722211,2522122,7922111,3322322,3422422,4922111,36722011,16722211,2532522,1632222,2632422,2622322,1922222,932222,2622222,3022222,21922111,1332522,3522422,2332122,15722011]
def loadData():
    df = pd.read_csv("CoordDataPlatsGrid2.csv", encoding="ISO-8859-1")
    pd.set_option('display.max_columns', None)
    df_lst = df.to_numpy().tolist()
    for i in range(len(df_lst)):
        print(i, df_lst[i])
        df_lst[i] = convertAllPosibleStringsToFloats(df_lst[i])
        df_lst[i][0], df_lst[i][1], df_lst[i][3] = int(df_lst[i][0]), int(df_lst[i][1]), int(df_lst[i][3])
        df_lst[i][2] = translateNumberToDirection('township', str(int(df_lst[i][2])))
        df_lst[i][4] = translateNumberToDirection('rng', str(int(df_lst[i][4])))
        df_lst[i][5] = translateNumberToDirection('baseline', str(int(df_lst[i][5])))
        if len(str(df_lst[i][0])) == 1:
            df_lst[i][0] = "0" + str(df_lst[i][0])
        if len(str(df_lst[i][1])) == 1:
            df_lst[i][1] = "0" + str(df_lst[i][1])
        if len(str(df_lst[i][3])) == 1:
            df_lst[i][3] = "0" + str(df_lst[i][3])

    id_conc = [str(i[0]) + str(i[1]) + str(i[2]) + str(i[3]) + str(i[4]) + str(i[5]) for i in df_lst]

    for i in range(len(df_lst)):
        print(i, df_lst[i])
        df_lst[i] = convertAllPosibleStringsToFloats(df_lst[i])
        df_lst[i][2] = translateDirectionToNumber('township', df_lst[i][2])
        df_lst[i][4] = translateDirectionToNumber('rng', df_lst[i][4])
        df_lst[i][5] = translateDirectionToNumber('baseline', df_lst[i][5])

    df_lst1 = [i[:6] for i in df_lst]
    df_lst1 = [[int(float(df_lst1[i][j])) for j in range(len(df_lst1[i]))] for i in range(len(df_lst1))]
    df_lst2 = [int(float(i[-1])) for i in df_lst]

    for i in range(len(df_lst)):
        df_lst[i][:6] = df_lst1[i]
        df_lst[i][-1] = df_lst2[i]

    df_conc = [str(i[0]) + str(i[1]) + str(i[2]) + str(i[3]) + str(i[4]) + str(i[5]) for i in df_lst]


    bounded_lst, restricted_lst = [], list(set(id_conc))

    restricted_lst = [[i] for i in restricted_lst]

    for i in range(len(df_lst)):
        bounded_lst.append([id_conc[i], df_lst[i][6], df_lst[i][7]])

    for i in range(len(bounded_lst)):
        for j in range(len(restricted_lst)):
            if restricted_lst[j][0] == bounded_lst[i][0]:
                restricted_lst[j].append(bounded_lst[i][1:])
    restricted_lst_pts, restricted_lst_id = [i[1:] for i in restricted_lst], [i[0] for i in restricted_lst]

    return df_lst, df_conc, restricted_lst_pts, restricted_lst_id

def determineIfInside(shl, data):
    point = Point(shl[0], shl[1])
    polygon = Polygon(data)
    return polygon.contains(point)

def sqlConnect():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS;"
        "Database=UTRBDMSNET;"
        "Trusted_Connection = yes;")
    cursor = conn.cursor()
    return conn, cursor

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
    #     print('count', count)

    return data_lst, sql_conc

def fixer(lst):
    fixed_lst = []
    for row in lst:
        fixed_lst.append(list(map(str, list(row))))
    return fixed_lst

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

def testFinder(test_combo_section):
    test_id, test_all = [], []
    for i in range(len(test_combo_section)):
        if test_combo_section[i][0] not in test_id:
            test_id.append(test_combo_section[i][0])
            test_all.append(test_combo_section[i][1])
    return test_id, test_all

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



drawData()