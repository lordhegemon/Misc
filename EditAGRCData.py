import copy
import os
import pandas as pd
import numpy as np
from shapely.ops import cascaded_union
from rtree import index
from shapely.geometry import mapping
# import CheckIfPlatDataCorrect

import GatherPlatDataSet
import ModuleAgnostic as ma
import math
import pyodbc
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import ProcessCoordData
import ProcessBHLLocation
from itertools import chain
from matplotlib import pyplot as plt
import itertools
from functools import reduce
import operator


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
    counter = 0
    for i in df_parsed:

        tot_runner += len(i)
        data_set = [r[6:8] for r in i]
        tsr_data = i[0][:6]
        data_x, data_y = [r[0] for r in data_set], [r[1] for r in data_set]
        if max(data_x) - min(data_x) < 10000 and max(data_y) - min(data_y) < 10000 and len(data_set) > 10:
            data_output = findCorners(data_set)
            for j in range(len(data_output)):
                data_output[j] = tsr_data + data_output[j]
                new_sides.append(data_output[j])

        counter += 1

    new_sides = ma.removeDupesListOfLists(new_sides)
    # ma.printLine(new_sides)
    # print('new sides')
    saveData(new_sides)
    # print('done')


def saveData(lst):
    # lst = [i[:8] for i in lst]
    df = pd.DataFrame(columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', 'Direction', 'ConcCode', 'AGRC Version'])
    counter = 0

    df_test = [{'Section': i[0], 'Township': int(float(i[1])), 'Township Direction': i[2], 'Range': int(float(i[3])),
                'Range Direction': i[4], 'Baseline': i[5], 'Easting': i[6], 'Northing': i[7], 'Direction': i[8], 'ConcCode': makeConcCode(i), 'AGRC Version': 'AGRC V.1'} for i in lst]
    df = pd.DataFrame(df_test, columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', 'Direction', 'ConcCode', 'AGRC Version'])
    test_data = df.to_numpy().tolist()
    # ma.printLine(test_data)
    fig, ax1 = plt.subplots()
    for i in test_data:
        if i[-2] == "3637S04WS":
            ax1.scatter([i[6]], [i[7]], c='red', s=25)
            print(i)
    # print(df)
    # print(df)
    # for i in lst:
    #     if counter % 1000 == 0:
    #         print(counter)
    #     new_row = {'Section': i[0],
    #                'Township': int(float(i[1])),
    #                'Township Direction': i[2],
    #                'Range': int(float(i[3])),
    #                'Range Direction': i[4],
    #                'Baseline': i[5],
    #                'Easting': i[6],
    #                'Northing': i[7],
    #                'ConcCode': makeConcCode(i),
    #                'AGRC Version': 'AGRC V.1'}
    #     df = df.append(new_row, ignore_index=True)
    #     counter += 1
    # df.to_csv('OddballSections.csv', index=False)
    # df.to_csv('PlatSidesAll.csv', index=False)
    plt.show()

def makeConcCode(data):
    data[0] = int(float(data[0]))
    data[1] = int(float(data[1]))
    data[2] = translateNumberToDirection('township', str(data[2]))
    data[3] = int(float(data[3]))
    data[4] = translateNumberToDirection('rng', str(data[4]))
    data[5] = translateNumberToDirection('baseline', str(data[5]))
    if len(str(data[0])) == 1:
        data[0] = "0" + str(data[0])
    if len(str(data[1])) == 1:
        data[1] = "0" + str(data[1])
    if len(str(data[3])) == 1:
        data[3] = "0" + str(data[3])
    for j in range(len(data)):
        data[j] = str(data[j])
    output = "".join(data[:6])

    return output


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
        xy1, xy2 = corner[0], corner[3]
    if label == 'north':
        xy1, xy2 = corner[3], corner[2]
    if label == 'east':
        xy1, xy2 = corner[2], corner[1]
    if label == 'south':
        xy1, xy2 = corner[1], corner[0]

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
            found_pt = findPointsOnLine(found_side_data[0], found_side_data[-1], div)
            found_data_theoretical_pts.append(found_pt)

            for l in found_side_data:
                distance_lst.append([l, ma.findSegmentLength(found_pt, l)])
            distance_lst = sorted(distance_lst, key=lambda r: r[1])

            # if distance_lst[0][1] != 0:
            #     slope = ma.slopeFinder2(found_pt, distance_lst[0][0])
            #     angle = math.degrees(math.atan(1 / slope[0]))

            new_sides.append(distance_lst[0][0])
    else:
        new_sides = found_side_data
    found_side_data = new_sides

    return found_side_data
    # pass

def findPointsOnLine(xy1, xy2, div):
    x, y = xy1[0] + (div * (xy2[0] - xy1[0])), xy1[1] + (div * (xy2[1] - xy1[1]))
    return [x, y]
    # return x,y

def checkClockwisePts(coords):
    center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
    output = sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)
    return output


def checkForPointsTooCloseToCorners(lst, centroid, o_lst, counter_def):
    colors = ["blue", "red", "yellow", "black"]
    counter = 0
    pass_counter = 0
    lst_poly = Polygon(lst)

    while counter != 3:
        lst_sorted_by_distance = copy.deepcopy(sorted(lst, key=lambda r: r[2]))[::-1]
        corners = lst_sorted_by_distance[:4]
        corners = checkClockwisePts(corners)
        counter = 0
        for i, j in zip(corners, corners[1:]):
            if 50 > ma.findSegmentLength(i[:2], j[:2]) > 0:
                sorted_data = sorted([i, j], key=lambda r: r[2], reverse=True)
                lst = [i for i in lst if i[2] != sorted_data[1][2]]
            else:
                counter += 1
        pass_counter += 1
        # if pass_counter == 10:
            # fig, ax1 = plt.subplots()
            # x1, y1 = [i[0] for i in corners], [i[1] for i in corners]
            # x2, y2 = [i[0] for i in lst], [i[1] for i in lst]
            # ax1.scatter(x1, y1, c='blue')
            # ax1.scatter(x2, y2, c='black', s=5)
            # plt.show()
    lst = sorted(lst, key=lambda r: r[2], reverse=True)

    corners = lst[:4]
    corners = checkClockwisePts(corners)

    corner_arrange = [i + [(math.degrees(math.atan2(centroid[1] - i[1], centroid[0] - i[0])) + 360) % 360] for i in corners]
    corners = sorted(corner_arrange, key=lambda r: r[-1])
    return corners, lst


def reorganizeLstPointsWithAngle(lst, centroid):
    lst_arrange = [i + [(math.degrees(math.atan2(centroid[1] - i[1], centroid[0] - i[0])) + 360) % 360] for i in lst]
    return lst_arrange


def arrangeDirectionData(corner, lst, label):
    found_data_theoretical_pts = []
    found_side_data = []
    new_sides = []
    if label == 'west':
        xy1, xy2 = corner[0], corner[3]
    if label == 'north':
        xy1, xy2 = corner[3], corner[2]
    if label == 'east':
        xy1, xy2 = corner[2], corner[1]
    if label == 'south':
        xy1, xy2 = corner[1], corner[0]
    angles = [xy1[-1], xy2[-1]]
    found_side_data.append(xy1)
    for i in lst:
        if label == 'west':
            if 360 > i[-1] > max(angles) or min(angles) > i[-1] > 0:
                found_side_data.append(i)
        else:
            if max(angles) > i[-1] > min(angles):
                found_side_data.append(i)
    found_side_data.append(xy2)
    if len(found_side_data) > 5:
        for k in range(5):
            distance_lst = []
            div = k / 4
            found_pt = findPointsOnLine(found_side_data[0], found_side_data[-1], div)
            found_data_theoretical_pts.append(found_pt)
            for l in found_side_data:
                distance_lst.append([l, ma.findSegmentLength(found_pt, l)])
            distance_lst = sorted(distance_lst, key=lambda r: r[1])
            new_sides.append(distance_lst[0][0])
    else:
        new_sides = found_side_data
    found_side_data = new_sides

    return found_side_data


def findNewLengthAndAngle(xy1, xy2, label, found_side_data):
    line = ma.findSegmentLength(xy1, xy2)
    angle = (math.degrees(math.atan2(xy1[1] - xy2[1], xy1[0] - xy2[0])) + 360) % 360
    changeAngles(label, angle, found_side_data)


def translateNumberToDirection(variable, val):
    try:
        val = str(int(val))
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
    except:
        pass


def changeAngles(label, angle, found_side_data):
    if label.lower() == 'west':
        if 360 > angle > 220:
            pass
            # print(angle, abs(360 - (angle - 90)))
        elif 150 > angle > 50:
            pass
            # print(angle, abs(angle - 90))
        else:
            if angle != 0:
                fig, ax1 = plt.subplots()
                x1, y1 = [i[0] for i in found_side_data], [i[1] for i in found_side_data]
                ax1.scatter(x1, y1, c='black')
                ax1.set_aspect('equal', adjustable='box')
                plt.show()
    # if 'west' in data[i][0].lower():
    #     if dir_val in [4, 1]:
    #         decVal = 90 + dec_val_base
    #     else:
    #         decVal = 90 - dec_val_base
    # if 'east' in data[i][0].lower():
    #     if dir_val in [4, 1]:
    #         decVal = 270 + dec_val_base
    #     else:
    #         decVal = 270 - dec_val_base
    # if 'north' in data[i][0].lower():
    #     if dir_val in [3, 2]:
    #         decVal = 360 - (270 + dec_val_base)
    #     else:
    #         decVal = 270 + dec_val_base
    # if 'south' in data[i][0].lower():
    #     if dir_val in [4, 1]:
    #         decVal = 90 + dec_val_base
    #     else:
    #         decVal = 360 - (90 + dec_val_base)

def cornerGeneratorProcess(data_lengths):
    centroid = Polygon(data_lengths).centroid
    centroid = [centroid.x, centroid.y]
    lst_poly = Polygon(data_lengths)
    bounds = lst_poly.bounds
    bounds_lst = organizeBoundsToPoints(bounds)
    corners = determinePointProximity(bounds_lst, data_lengths)
    corners = checkClockwisePts(corners)
    corner_arrange = [i + [(math.degrees(math.atan2(centroid[1] - i[1], centroid[0] - i[0])) + 360) % 360] for i in corners]
    corners = sorted(corner_arrange, key=lambda r: r[-1])
    return corners



def organizeBoundsToPoints(bounds):
    nw = [bounds[0], bounds[3]]
    ne = [bounds[2], bounds[3]]
    sw = [bounds[0], bounds[1]]
    se = [bounds[2], bounds[1]]
    return nw, ne, sw, se


def determinePointProximity(bounds, lst):
    distance_lst = []
    for i in bounds:
        min_distance = 9999999
        dist_pt = []
        for j in lst:
            distance = ma.findSegmentLength(i, j)
            if distance < min_distance:
                min_distance = distance
                dist_pt = j
        distance_lst.append(dist_pt)
    return distance_lst


def findCorners(lst):

    try:
        lst = checkClockwisePts(lst)
    except TypeError:
        print(lst)

    data_lengths = []

    centroid = Polygon(lst).centroid
    centroid = [centroid.x, centroid.y]
    # print(centroid)
    for i in range(len(lst)):
        # output = GatherPlatDataSet.slopeFinder2(centroid, lst[i])
        data_lengths.append(lst[i] + [ma.findSegmentLength(centroid, lst[i])])

    # corners = cornerGeneratorProcess(data_lengths)

    # lst_poly = Polygon(data_lengths)
    # bounds = lst_poly.bounds
    # bounds_lst = organizeBoundsToPoints(bounds)
    # corners = determinePointProximity(bounds_lst, data_lengths)
    # corners = checkClockwisePts(corners)
    # corner_arrange = [i + [(math.degrees(math.atan2(centroid[1] - i[1], centroid[0] - i[0])) + 360) % 360] for i in corners]
    # corners = sorted(corner_arrange, key=lambda r: r[-1])

    # if counter == 0:
    #     print(1, corners)
    # # corners, data_lengths = checkForPointsTooCloseToCorners(data_lengths, centroid, lst, counter)
    # if counter == 0:
    #     print(2, corners)
    # ma.printLine(data_lengths)
    corners = cornerGeneratorProcess(data_lengths)
    data_lengths = reorganizeLstPointsWithAngle(data_lengths, centroid)
    east_side = arrangeDirectionData(corners, data_lengths, 'east')
    north_side = arrangeDirectionData(corners, data_lengths, 'north')
    west_side = arrangeDirectionData(corners, data_lengths, 'west')
    south_side = arrangeDirectionData(corners, data_lengths, 'south')
    west_side = [i[:2] + ["WEST"] for i in west_side]
    east_side = [i[:2] + ["EAST"] for i in east_side]
    north_side = [i[:2] + ["NORTH"] for i in north_side]
    south_side = [i[:2] + ["SOUTH"] for i in south_side]


    # all_data = west_side[1:] + north_side[1:] + east_side[1:] + south_side[1:]
    all_data = west_side + north_side + east_side + south_side
    # ma.printLine(all_data)

    # fig, ax1 = plt.subplots()
    # # # x1, y1 = [i[0] for i in found_data_theoretical_pts], [i[1] for i in found_data_theoretical_pts]
    # # # x2, y2 = [i[0] for i in data], [i[1] for i in data]
    # x1, y1 = [i[0] for i in east_side], [i[1] for i in east_side]
    # x2, y2 = [i[0] for i in north_side], [i[1] for i in north_side]
    # x3, y3 = [i[0] for i in west_side], [i[1] for i in west_side]
    # x4, y4 = [i[0] for i in south_side], [i[1] for i in south_side]
    # ax1.scatter(x1, y1, c='black')
    # ax1.scatter(x2, y2, c='blue')
    # ax1.scatter(x3, y3, c='red')
    # ax1.scatter(x4, y4, c='yellow')
    # plt.show()
    # east_side = findSideValues(lst, corners, 'east')
    # north_side = findSideValues(lst, corners, 'north')
    # west_side = findSideValues(lst, corners, 'west')
    # south_side = findSideValues(lst, corners, 'south')

    # for xy1, xy2 in zip(lst, lst[1:]):
    #     output = GatherPlatDataSet.slopeFinder2(xy1, xy2)
    #     data_group.append([math.degrees(math.atan(1/output[0]))] + xy1)
    # output_data = [[data_group[0]]]
    # ns_lst, ew_lst = [], []
    # lst_test = [[]]
    # for xy1, xy2 in zip(data_group, data_group[1:]):
    #     diff_val = abs(xy1[0] - xy2[0])

    #
    # for i in range(len(data_group)):
    #     if abs(data_group[i][0]) > 45:
    #         ns_lst.append(data_group[i][1:])
    #     else:
    #         ew_lst.append(data_group[i][1:])

    # ns_1, ns_2 = [i[0] for i in ns_lst], [i[1] for i in ns_lst]
    # ew_1, ew_2 = [i[0] for i in ew_lst], [i[1] for i in ew_lst]
    # data_ew = dict(enumerate(ma.grouper(sorted(ew_1), 100), 1))
    # output_data_ew = [j for i, j in data_ew.items()]

    #
    # data_ns = dict(enumerate(ma.grouper(sorted(ns_2), 100), 1))
    # output_data_ns = [j for i, j in data_ns.items()]

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

    # if counter == 442:
    #     fig, ax1 = plt.subplots()
    #     # x1, y1 = [i[0] for i in east_side], [i[1] for i in east_side]
    #     # x2, y2 = [i[0] for i in north_side], [i[1] for i in north_side]
    #     # x3, y3 = [i[0] for i in west_side], [i[1] for i in west_side]
    #     # x4, y4 = [i[0] for i in south_side], [i[1] for i in south_side]
    #     x1, y1 = [corners[0][0]], [corners[0][1]]
    #     x2, y2 = [corners[1][0]], [corners[1][1]]
    #     x3, y3 = [corners[2][0]], [corners[2][1]]
    #     x4, y4 = [corners[3][0]], [corners[3][1]]
    #     x5, y5 = [i[0] for i in bounds_lst], [i[1] for i in bounds_lst]
    #     x6, y6 = [i[0] for i in all_data], [i[1] for i in all_data]
    #     ax1.scatter(x1, y1, c='black')  # east
    #     ax1.scatter(x2, y2, c='blue')  # north
    #     ax1.scatter(x3, y3, c='red')  # west
    #     ax1.scatter(x4, y4, c='yellow')  # south
    #     ax1.scatter(x5, y5, c='grey', s=5)
    #     ax1.scatter(x6, y6, c='red', s = 1)
    #     plt.show()

    return all_data


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
        township_dir = translateDirectionToNumber('township', township_dir)
        range_dir = translateDirectionToNumber('rng', range_dir)
        meridian = translateDirectionToNumber('baseline', meridian)
        conc = str(section) + str(township) + str(township_dir) + str(range_val) + str(range_dir) + str(meridian)

        return_lst.append([section, township, township_dir, range_val, range_dir, meridian, easting, northing, 89230983, conc])
    return return_lst

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


# renderAGRCDataDown()
