import pandas as pd
import numpy as np
import math
import ModuleAgnostic as ma
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon


def main():
    df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\PlatSidesAll.csv", encoding="ISO-8859-1")
    data = df_parsed.to_numpy().tolist()
    conc_lst = []
    d = {}
    pd.set_option('display.max_columns', None)
    for i in data:
        if i[9] not in d:
            d[i[9]] = []
        d[i[9]].append(i)
    dict_lst = [j for t, j in d.items()]
    for i in dict_lst:
        # if i[0][-3] == '3637S04WS':
        # print("\n\n", i[0][-3], "\n___________________________________")
        conc_lst = conc_lst + processEachSection(i)
    conc_lst = [i for i in conc_lst if i]
    # ma.printLine(conc_lst)
    df_test = [{'Section': i[0], 'Township': int(float(i[1])), 'Township Direction': i[2], 'Range': int(float(i[3])),
                'Range Direction': i[4], 'Baseline': i[5], 'Side': i[6], 'Length': i[7], 'Degrees': i[8], 'Minutes': i[9], 'Seconds': i[10], 'Direction': i[11], 'North Reference':i[12], 'Conc': i[13], 'Version':i[14]} for i in conc_lst]
    # ma.printLine(df_test)
    df = pd.DataFrame(df_test, columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Side', 'Length', 'Degrees', 'Minutes', 'Seconds', 'Direction', 'North Reference', 'Conc', 'Version'])
    # print(df)
    df.to_csv('PlatSides.csv', index=False)

def addMissingPts(lst):
    if len(lst) != 5:
        missing_num = 5 - len(lst)
        for i in range(missing_num):
            lst.append(lst[-1])
    return lst


def processEachSection(data):
    dirLst = [['West-Up2', 'West-Up1', 'West-Down1', 'West-Down2'],
              ['East-Up2', 'East-Up1', 'East-Down1', 'East-Down2'],
              ['North-Left2', 'North-Left1', 'North-Right1', 'North-Right2'],
              ['South-Left2', 'South-Left1', 'South-Right1', 'South-Right2']]
    tsr_data = data[0][:6]
    other_data = data[0][9:-1]
    # new_sides = ma.removeDupesListOfLists(new_sides)
    if len(data) <= 20:

        d = {}
        degrees_lst = []
        for i in data:
            if i[8] not in d:
                d[i[8]] = []
            d[i[8]].append(i[6:9])
        dict_lst = [j for t, j in d.items()]

        pts_west = [i[:2] for i in dict_lst[0]][::-1]
        pts_north = [i[:2] for i in dict_lst[1]]
        pts_east = [i[:2] for i in dict_lst[2]]
        pts_south = [i[:2] for i in dict_lst[3]][::-1]

        pts_west = addMissingPts(pts_west)
        pts_north = addMissingPts(pts_north)
        pts_east = addMissingPts(pts_east)
        pts_south = addMissingPts(pts_south)

        data_pts_base = [i[6:8] for i in data]
        data_pts_base = sizeDown(data_pts_base)


        lens_w = angleAndLengths(pts_west)
        lens_n = angleAndLengths(pts_north)
        lens_e = angleAndLengths(pts_east)
        lens_s = angleAndLengths(pts_south)
        conc_lst = [str(i) for i in tsr_data]
        conc_lst = "".join(conc_lst)

        lens_w = lens_w[::-1]




        for i in range(len(lens_w)):
            degrees = reconvertToDegrees(lens_w[i][1], 'west')
            conc_lst_dir = conc_lst + dirLst[0][i]
            degrees_lst.append(tsr_data + [dirLst[0][i]] + [lens_w[i][0]] + degrees + ["T"] + [conc_lst_dir] + [data[-1][-2]])
        for i in range(len(lens_e)):
            degrees = reconvertToDegrees(lens_e[i][1], 'east')
            conc_lst_dir = conc_lst + dirLst[1][i]
            degrees_lst.append(tsr_data + [dirLst[1][i]] + [lens_e[i][0]] + degrees + ["T"] + [conc_lst_dir] + [data[-1][-2]])
        for i in range(len(lens_n)):
            degrees = reconvertToDegrees(lens_n[i][1], 'north')
            conc_lst_dir = conc_lst + dirLst[2][i]
            degrees_lst.append(tsr_data + [dirLst[2][i]] + [lens_n[i][0]] + degrees + ["T"] + [conc_lst_dir] + [data[-1][-2]])
        for i in range(len(lens_s)):
            degrees = reconvertToDegrees(lens_s[i][1], 'south')
            conc_lst_dir = conc_lst + dirLst[3][i]
            degrees_lst.append(tsr_data + [dirLst[3][i]] + [lens_s[i][0]] + degrees + ["T"] + [conc_lst_dir] + [data[-1][-2]])
        # conv = convertToDecimal(degrees_lst)
        # conv = pointsConverter(conv)
        return degrees_lst
        # ma.printLine(degrees_lst)
        # fig, ax1 = plt.subplots()
        # x1, y1 = [i[0] for i in pts_west], [i[1] for i in pts_west]
        # x2, y2 = [i[0] for i in pts_north], [i[1] for i in pts_north]
        # x3, y3 = [i[0] for i in pts_east], [i[1] for i in pts_east]
        # x4, y4 = [i[0] for i in pts_south], [i[1] for i in pts_south]
        # x5, y5 = [i[0] for i in conv], [i[1] for i in conv]
        # x6, y6 = [i[0] for i in data_pts_base], [i[1] for i in data_pts_base]
        # ax1.scatter(x5, y5, c='red', s = 25)
        # ax1.plot(x6, y6, c='black')
        # ax1.scatter(x6, y6, c='black', s=10)
        # ax1.scatter(x1, y1, c='black')
        # ax1.scatter(x2, y2, c='red')
        # ax1.scatter(x3, y3, c='blue')
        # ax1.scatter(x4, y4, c='yellow')
        # plt.show()
    return []

def sizeDown(lst):
    resize_x, resize_y = lst[0][0], lst[0][1]
    lst = [[i[0]-resize_x, i[1]-resize_y] for i in lst]
    lst = [[i[0]  * 3.2808399, i[1] * 3.2808399] for i in lst]
    return lst

def angleAndLengths(lst):
    alLst = []
    for i in range(len(lst) - 1):
        pt1, pt2 = Point(lst[i]), Point(lst[i + 1])
        angle = (math.degrees(math.atan2(lst[i][1] - lst[i + 1][1], lst[i][0] - lst[i + 1][0])) + 360) % 360
        d = round(pt1.distance(pt2) * 3.2808399,2)
        alLst.append([d, angle])
    return alLst


def reconvertToDegrees(decVal, data):
    dir_val = -1
    # if data == 'west' or data == 'east':
    #     print(decVal)
    #     if decVal < 270:
    #         dir_val = 2
    #     else:
    #         dir_val = 4
    #     decimal_value = abs(270 - decVal)
    #     # print(decVal)
    #     # print(decimal_value)
    #     deg_val = list(ma.convertDecimalToDegrees(decimal_value))
    #     # print(deg_val)
    if data == 'east' or data == 'west':
        decimal_value = abs(90 - decVal)
        if decVal < 90:
            dir_val = 2
        else:
            dir_val = 4

        deg_val = ma.convertDecimalToDegrees(decimal_value)
    if data == 'north' or data == 'south':

        if decVal < 180:
            decimal_value = abs(90 - decVal)
            dir_val = 4
        else:
            decimal_value = 90 - abs(180 - decVal)
            dir_val = 2
        deg_val = ma.convertDecimalToDegrees(decimal_value)

    # if data == 'south':
    #     if 360 > decVal > 330:
    #         dir_val = 4
    #         decimal_value = abs(270 - decVal)
    #     else:
    #         decimal_value = abs(90-decVal)
    #         dir_val = 2

    #     if 270 > decVal > 90:
    #         decimal_value = 90 - abs(180 - decVal)
    #     else:
    #         decimal_value = decVal
    #     # if decVal > 180 and o_data < 180 or decVal < 180 and o_data > 180:
    #     #     dir_val = self.alterDirection('south', dir_val)
    #     deg_val = ma.convertDecimalToDegrees(decimal_value)

    # data[8:12] = list(deg_val) + [dir_val]
    return list(deg_val) + [dir_val]
    # return data

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

    #
    # # pts = [j[6:8] for j in data]
    # # pts = ma.removeDupesListOfLists(pts)
    # # pts.append(pts[0])
    # # for i in dict_lst:
    # #     pts = [j[:2] for j in i]
    # corners, data = ma.cornerGeneratorProcess(pts)


main()
