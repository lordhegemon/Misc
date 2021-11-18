import copy
import os
import pandas as pd
import numpy as np
from shapely.ops import cascaded_union
from rtree import index
from shapely.geometry import mapping
import CheckIfPlatDataCorrect

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
import itertools


def renderAGRCDataDown():
    pts_all = []
    new_sides = []
    df_parsed = pd.read_csv("All_Data_Lat_Lon.csv", encoding="ISO-8859-1")
    df_parsed = df_parsed.to_numpy().tolist()

    df_parsed = rewriteDataLatLon(df_parsed)
    print("number of original points", len(df_parsed))
    pd.set_option('display.max_columns', None)
    for i in range(len(df_parsed)):
        df_parsed[i][:6], df_parsed[i][-1] = [int(j) for j in df_parsed[i][:6]], str(int(df_parsed[i][-1]))
    d = [[df_parsed[0]]]
    for i in range(1, len(df_parsed)):
        if df_parsed[i][-1] != d[-1][-1][-1]:
            d.append([])
        d[-1].append(df_parsed[i])
    df_parsed = d
    tot_runner = 0
    for i in df_parsed:
        # print("_____________________________________________")
        tot_runner += len(i)
        data_set = [r[6:8] for r in i]
        tsr_data = i[0][:6]
        data_output = findCorners(data_set)
        # for j in range(len(data_output)):
        #     data_output[j] = tsr_data + data_output[j]
        #     new_sides.append(data_output[j])
    # ma.removeDupesListOfLists(new_sides)
    # print('total points found', len(new_sides))


def sortCorners(corners_lst):
    corners_left = [i for i in corners_lst if i[-1] < 0]
    corners_right = [i for i in corners_lst if i[-1] > 0]
    corners_left = sorted(corners_left, key=lambda r: r[1])
    corners_right = sorted(corners_right, key=lambda r: r[1], reverse=True)
    corners_out = corners_left + corners_right
    return corners_out


def findSideValues(data, corner, label):
    found_data_theoretical_pts = []
    found_side_data = []
    if label == 'west':
        # xy1, xy2 = corner[0], corner[1]
        xy1, xy2 = corner[3], corner[1]
    if label == 'north':
        xy1, xy2 = corner[1], corner[2]
    if label == 'east':
        # xy1, xy2 = corner[2], corner[3]
        xy1, xy2 = corner[2], corner[0]
    if label == 'south':
        xy1, xy2 = corner[3], corner[0]
        # xy1, xy2 = corner[3], corner[1]

    x_data = [xy1[0], xy2[0]]
    y_data = [xy1[1], xy2[1]]
    min_x, max_x, min_y, max_y = min(x_data), max(x_data), min(y_data), max(y_data)
    edited_square = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]]
    found_side_data.append(xy1)
    polygon = Polygon(edited_square)
    for i in data:
        if polygon.contains(Point(i[:2])):
            found_side_data.append(i[:2])
    found_side_data.append(xy2)
    new_sides = []
    if len(found_side_data) > 5:
        for k in range(5):
            distance_lst = []
            div = k / 4
            found_pt = CheckIfPlatDataCorrect.findPointsOnLine(found_side_data[0], found_side_data[-1], div)
            found_data_theoretical_pts.append(found_pt)
            # print(found_pt)
            for l in found_side_data:
                distance_lst.append([l, ma.findSegmentLength(found_pt, l)])
            distance_lst = sorted(distance_lst, key=lambda r: r[1])
            
            # if distance_lst[0][1] != 0:
                # slope = ma.slopeFinder2(found_pt, distance_lst[0][0])
                # angle = math.degrees(math.atan(1 / slope[0]))
                # print(k, distance_lst[0], angle)
            new_sides.append(distance_lst[0][0])
    else:
        new_sides = found_side_data
    found_side_data = new_sides

    # fig, ax1 = plt.subplots()
    # # x1, y1 = [i[0] for i in found_data_theoretical_pts], [i[1] for i in found_data_theoretical_pts]
    # # x2, y2 = [i[0] for i in data], [i[1] for i in data]
    # ax1.scatter([corner[0][0]], [corner[0][1]], c='black')
    # ax1.scatter([corner[1][0]], [corner[1][1]], c='blue')
    # ax1.scatter([corner[2][0]], [corner[2][1]], c='red')
    # ax1.scatter([corner[3][0]], [corner[3][1]], c='yellow')
    # plt.show()



    return found_side_data
    # pass


def findCorners(lst):
    data_lengths = []
    centroid = Polygon(lst).centroid
    centroid = [centroid.x, centroid.y]
    for i in range(len(lst)):
        # data_lengths.append(lst[i] + [ma.findSegmentLength(centroid, lst[i])])
        output = GatherPlatDataSet.slopeFinder2(centroid, lst[i])
        data_lengths.append(lst[i] + [ma.findSegmentLength(centroid, lst[i])] + [math.degrees(math.atan(1 / output[0]))])
        # data_lengths = ma.findSegmentLength(centroid, lst[i])
    data_lengths = sorted(data_lengths, key=lambda r: r[2])
    corners = data_lengths[-4:]
    corners = sortCorners(corners)
    corners = [i[:2] for i in corners]
    east_side = findSideValues(lst, corners, 'east')
    north_side = findSideValues(lst, corners, 'north')
    west_side = findSideValues(lst, corners, 'west')
    south_side = findSideValues(lst, corners, 'south')

    # fig, ax1 = plt.subplots()
    # x1, y1 = [i[0] for i in lst], [i[1] for i in lst]
    # x2, y2 = [i[0] for i in sides_data], [i[1] for i in sides_data]
    # ax1.scatter(x1, y1, c='black')
    # ax1.fill(x2, y2, c='blue')
    # plt.show()

    # ma.printLine(corners)
    # for xy1, xy2 in zip(lst, lst[1:]):
    #     output = GatherPlatDataSet.slopeFinder2(xy1, xy2)
    #     data_group.append([math.degrees(math.atan(1/output[0]))] + xy1)
    # output_data = [[data_group[0]]]
    # ns_lst, ew_lst = [], []
    # lst_test = [[]]
    # for xy1, xy2 in zip(data_group, data_group[1:]):
    #     diff_val = abs(xy1[0] - xy2[0])
    #     print(diff_val)
    #
    # for i in range(len(data_group)):
    #     if abs(data_group[i][0]) > 45:
    #         ns_lst.append(data_group[i][1:])
    #     else:
    #         ew_lst.append(data_group[i][1:])
    # ma.printLine(ns_lst)
    # ma.printLine(ew_lst)
    # ns_1, ns_2 = [i[0] for i in ns_lst], [i[1] for i in ns_lst]
    # ew_1, ew_2 = [i[0] for i in ew_lst], [i[1] for i in ew_lst]
    # print(min(ns_1), max(ns_1),max(ns_1)-min(ns_1) )
    # print(min(ns_2), max(ns_2),max(ns_2)-min(ns_2))
    # data_ew = dict(enumerate(ma.grouper(sorted(ew_1), 100), 1))
    # output_data_ew = [j for i, j in data_ew.items()]
    # print(output_data_ew)
    #
    # data_ns = dict(enumerate(ma.grouper(sorted(ns_2), 100), 1))
    # output_data_ns = [j for i, j in data_ns.items()]
    # print(output_data_ns)
    # for i in range(1, len(data_group)):
    #     diff = abs(data_group[i][0] - output_data[-1][-1][0])
    #     if diff > 45:
    #         output_data.append([])
    #     output_data[-1].append(data_group[i])
    #     if abs(data_group[i][0] - output_data[-1][-1][0]) > 45:
    #         output_data.append([])
    #     output_data[-1].append(data_group)
    # all_data = west_side[1:] + north_side[1:] + east_side[1:] + south_side[1:]
    # all_data = west_side + north_side + east_side + south_side
    # all_data = ma.removeDupesListOfLists(all_data)
    fig, ax1 = plt.subplots()
    x1, y1 = [i[0] for i in east_side], [i[1] for i in east_side]
    x2, y2 = [i[0] for i in north_side], [i[1] for i in north_side]
    x3, y3 = [i[0] for i in west_side], [i[1] for i in west_side]
    x4, y4 = [i[0] for i in south_side], [i[1] for i in south_side]
    x5, y5 = [i[0] for i in lst], [i[1] for i in lst]
    ax1.scatter(x1, y1, c='black') #east
    ax1.scatter(x2, y2, c='blue') # north
    ax1.scatter(x3, y3, c='red') #west
    ax1.scatter(x4, y4, c='yellow') #south
    ax1.scatter(x5, y5, c='grey', s = 5)
    plt.show()
    # print(len(lst), len(all_data))
    # return all_data


def graph_data(lst_all, n_data, s_data, e_data, w_data):
    colors = ["black", "#E69F00", "#56B4E9", "#56B4E9", '#0072B2', '#D55E00', '#CC79A7']
    fig, ax1 = plt.subplots()
    x1, y1 = [i[0] for i in lst_all], [i[1] for i in lst_all]
    x2, y2 = [i[0] for i in n_data], [i[1] for i in n_data]
    x3, y3 = [i[0] for i in s_data], [i[1] for i in s_data]
    x4, y4 = [i[0] for i in e_data], [i[1] for i in e_data]
    x5, y5 = [i[0] for i in w_data], [i[1] for i in w_data]
    ax1.scatter(x1, y1, c=colors[0])
    # ax1.plot(x2, y2, c=colors[1])
    # ax1.plot(x3, y3, c=colors[2])
    # ax1.plot(x4, y4, c=colors[3])
    # ax1.plot(x5, y5, c=colors[4])
    # plt.show()


def rewriteDataLatLon(lst):
    bad_lst = ['2709S19ES', "2809S19ES", "1309S19ES", "0105S02EU", "0604S03EU", '1404S02EU', "1605S02EU", "0104S04WU", "1309S19ES", "1105S02EU", "1309S19ES", "0805S03EU", "0104S04WU", "1605S02EU", "0104S04WU", "1105S02EU", "0104S04WU", "1605S02EU"]
    return_lst = []
    counter = 0
    lst = [i for i in lst if i[-1] not in bad_lst]
    for i in lst:
        tsr_line = i[-1]
        section, township, township_dir, range_val, range_dir, meridian = int(tsr_line[:2]), int(tsr_line[2:4]), tsr_line[4], int(tsr_line[5:7]), tsr_line[7], tsr_line[8]
        easting, northing = float(i[8]), float(i[9])
        township_dir = CheckIfPlatDataCorrect.translateDirectionToNumber('township', township_dir)
        range_dir = CheckIfPlatDataCorrect.translateDirectionToNumber('rng', range_dir)
        meridian = CheckIfPlatDataCorrect.translateDirectionToNumber('baseline', meridian)
        conc = str(section) + str(township) + str(township_dir) + str(range_val) + str(range_dir) + str(meridian)

        return_lst.append([section, township, township_dir, range_val, range_dir, meridian, easting, northing, 89230983, conc])
    return return_lst


renderAGRCDataDown()
