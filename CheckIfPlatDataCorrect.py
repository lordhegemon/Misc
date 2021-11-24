import copy
import os
import pandas as pd
import numpy as np
from shapely.ops import cascaded_union
from rtree import index
from shapely.geometry import mapping
idx = index.Index()
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
import EditAGRCData

def rewriteDataLatLon(lst):
    bad_lst = ['2709S19ES', "2809S19ES", "1309S19ES", "0105S02EU", "0604S03EU", '1404S02EU', "1605S02EU", "0104S04WU", "1309S19ES", "1105S02EU", "1309S19ES", "0805S03EU", "0104S04WU", "1605S02EU", "0104S04WU", "1105S02EU", "0104S04WU", "1605S02EU"]
    return_lst = []
    counter = 0
    lst = [i for i in lst if i[-1] not in bad_lst]
    for i in lst:
        # if counter % 1000 == 0:
        #     print(counter)
        tsr_line = i[-1]
        # if tsr_line not in return_lst:
        section, township, township_dir, range_val, range_dir, meridian = int(tsr_line[:2]), int(tsr_line[2:4]), tsr_line[4], int(tsr_line[5:7]), tsr_line[7], tsr_line[8]
        # if section == 27 and township == 9:# and township == 9 and range == 19:
        #     print([section, township, township_dir, range_val, range_dir, meridian], [tsr_line])
        easting, northing = float(i[8]), float(i[9])
        township_dir = translateDirectionToNumber('township', township_dir)
        range_dir = translateDirectionToNumber('rng', range_dir)
        meridian = translateDirectionToNumber('baseline', meridian)
        conc = str(section) + str(township) + str(township_dir) + str(range_val) + str(range_dir) + str(meridian)

        return_lst.append([section, township, township_dir, range_val, range_dir, meridian, easting, northing, 89230983, conc])
        # else:
        #     print(tsr_line)
        # counter += 1
    return return_lst

# def renderAGRCDataDown():
#     pts_all = []
#     new_sides = []
#     df_parsed = pd.read_csv("All_Data_Lat_Lon.csv", encoding="ISO-8859-1")
#     df_parsed = df_parsed.to_numpy().tolist()
#
#     df_parsed = rewriteDataLatLon(df_parsed)
#     print("number of original points", len(df_parsed))
#     pd.set_option('display.max_columns', None)
#     for i in range(len(df_parsed)):
#         df_parsed[i][:6], df_parsed[i][-1] = [int(j) for j in df_parsed[i][:6]], str(int(df_parsed[i][-1]))
#     d = [[df_parsed[0]]]
#     for i in range(1, len(df_parsed)):
#         if df_parsed[i][-1] != d[-1][-1][-1]:
#             d.append([])
#         d[-1].append(df_parsed[i])
#     df_parsed = d
#     tot_runner = 0
#     counter_true = 0
#     counter_edited = 0
#     id_unique = []
#     counter_unedited = 0
#     for i in df_parsed:
#         # print("_____________________________________________")
#         tot_runner += len(i)
#         data_set = [r[6:8] for r in i]
#         tsr_data = i[0][:6]
#         # boundaries_all, south_bounds, east_bounds, north_bounds, west_bounds = ProcessCoordData.getPlatBounds(data_set)
#         # tot_lengths = len(south_bounds)+ len(east_bounds)+ len(north_bounds)+ len(west_bounds)
#         # if tot_lengths > 40:
#         data_output = findCorners(data_set)
#         for j in range(len(data_output)):
#             data_output[j] = tsr_data + data_output[j]
#             new_sides.append(data_output[j])
#             # graph_data(data_set, north_bounds, south_bounds, east_bounds, west_bounds)
#         # # print()
#         # # print(len(data_set))
#         # # print(len(south_bounds), len(east_bounds), len(north_bounds), len(west_bounds), len(south_bounds)+ len(east_bounds)+ len(north_bounds)+ len(west_bounds))
#         # pts_all.append([south_bounds, east_bounds, north_bounds, west_bounds])
#         # for j in pts_all[-1]:
#         #     if len(j) > 5:
#         #         counter_true += len(j)
#         #         # counter = 0
#         #         # print(len(j))
#         #         for k in range(5):
#         #             counter_edited +=1
#         #             # counter_true += 1
#         #             distance_lst = []
#         #             div = k / 4
#         #             found_pt = findPointsOnLine(j[0], j[-1], div)
#         #             for l in j:
#         #                 distance_lst.append([l, ma.findSegmentLength(found_pt, l)])
#         #             distance_lst = sorted(distance_lst, key=lambda r: r[1])
#         #             new_sides.append(tsr_data + distance_lst[0][0])
#         #         # print(len(j), counter)
#         #     else:
#         #         for k in j:
#         #             counter_unedited += 1
#         #             # counter_true += 1
#         #             new_sides.append(tsr_data + k)
#     ma.removeDupesListOfLists(new_sides)
#     # print('original points beginning', tot_runner)
#     # print('number of original points', counter_true)
#     # print('number of points edited down', counter_edited)
#     # print('already five length points', counter_unedited)
#     # print('total points inferred', counter_edited + counter_unedited)
#     print('total points found', len(new_sides))
#     # ma.printLine(new_sides)
#
#
# def sortCorners(corners_lst):
#     corners_left = [i for i in corners_lst if i[-1] < 0]
#     corners_right = [i for i in corners_lst if i[-1] > 0]
#     # ma.printLine(corners_left)
#     # ma.printLine(corners_right)
#     corners_left = sorted(corners_left, key=lambda r: r[1])
#     corners_right = sorted(corners_right, key=lambda r: r[1], reverse=True)
#     corners_out = corners_left + corners_right
#     return corners_out
#
# def findSideValues(data, corner, label):
#     found_side_data = []
#     if label == 'west':
#         xy1, xy2 = corner[0], corner[1]
#     if label == 'north':
#         xy1, xy2 = corner[1], corner[2]
#     if label == 'east':
#         xy1, xy2 = corner[2], corner[3]
#     if label == 'south':
#         xy1, xy2 = corner[3], corner[1]
#
#     x_data = [xy1[0], xy2[0]]
#     y_data = [xy1[1], xy2[1]]
#     min_x, max_x, min_y, max_y = min(x_data), max(x_data), min(y_data), max(y_data)
#     edited_square = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]]
#     found_side_data.append(xy1)
#     polygon = Polygon(edited_square)
#     for i in data:
#         if polygon.contains(Point(i[:2])):
#             found_side_data.append(i[:2])
#     found_side_data.append(xy2)
#
#     # ma.printLine(found_side_data)
#
#     new_sides = []
#     if len(found_side_data) > 5:
#         for k in range(5):
#             distance_lst = []
#             div = k / 4
#             found_pt = findPointsOnLine(found_side_data[0], found_side_data[-1], div)
#             for l in found_side_data:
#                 distance_lst.append([l, ma.findSegmentLength(found_pt, l)])
#             distance_lst = sorted(distance_lst, key=lambda r: r[1])
#             new_sides.append(distance_lst[0][0])
#     else:
#         new_sides = found_side_data
#     found_side_data = new_sides
#     # ma.printLine(found_side_data)
#
#     return found_side_data
#     pass
#
# def findCorners(lst):
#     data_lengths = []
#     centroid = Polygon(lst).centroid
#     centroid = [centroid.x, centroid.y]
#     for i in range(len(lst)):
#         # data_lengths.append(lst[i] + [ma.findSegmentLength(centroid, lst[i])])
#         output = GatherPlatDataSet.slopeFinder2(centroid, lst[i])
#         data_lengths.append(lst[i] + [ma.findSegmentLength(centroid, lst[i])] + [math.degrees(math.atan(1/output[0]))])
#         # data_lengths = ma.findSegmentLength(centroid, lst[i])
#     data_lengths = sorted(data_lengths, key=lambda r: r[2])
#     corners = data_lengths[-4:]
#     corners = sortCorners(corners)
#     corners = [i[:2] for i in corners]
#     east_side = findSideValues(lst, corners, 'east')
#     north_side = findSideValues(lst, corners, 'north')
#     west_side = findSideValues(lst, corners, 'west')
#     south_side = findSideValues(lst, corners, 'south')
#     ma.printLine(south_side)
#     # fig, ax1 = plt.subplots()
#     # x1, y1 = [i[0] for i in lst], [i[1] for i in lst]
#     # x2, y2 = [i[0] for i in sides_data], [i[1] for i in sides_data]
#     # ax1.scatter(x1, y1, c='black')
#     # ax1.fill(x2, y2, c='blue')
#     # plt.show()
#
#
#
#     # ma.printLine(corners)
#     # for xy1, xy2 in zip(lst, lst[1:]):
#     #     output = GatherPlatDataSet.slopeFinder2(xy1, xy2)
#     #     data_group.append([math.degrees(math.atan(1/output[0]))] + xy1)
#     # output_data = [[data_group[0]]]
#     # ns_lst, ew_lst = [], []
#     # lst_test = [[]]
#     # for xy1, xy2 in zip(data_group, data_group[1:]):
#     #     diff_val = abs(xy1[0] - xy2[0])
#     #     print(diff_val)
#     #
#     # for i in range(len(data_group)):
#     #     if abs(data_group[i][0]) > 45:
#     #         ns_lst.append(data_group[i][1:])
#     #     else:
#     #         ew_lst.append(data_group[i][1:])
#     # ma.printLine(ns_lst)
#     # ma.printLine(ew_lst)
#     # ns_1, ns_2 = [i[0] for i in ns_lst], [i[1] for i in ns_lst]
#     # ew_1, ew_2 = [i[0] for i in ew_lst], [i[1] for i in ew_lst]
#     # print(min(ns_1), max(ns_1),max(ns_1)-min(ns_1) )
#     # print(min(ns_2), max(ns_2),max(ns_2)-min(ns_2))
#     # data_ew = dict(enumerate(ma.grouper(sorted(ew_1), 100), 1))
#     # output_data_ew = [j for i, j in data_ew.items()]
#     # print(output_data_ew)
#     #
#     # data_ns = dict(enumerate(ma.grouper(sorted(ns_2), 100), 1))
#     # output_data_ns = [j for i, j in data_ns.items()]
#     # print(output_data_ns)
#     # for i in range(1, len(data_group)):
#     #     diff = abs(data_group[i][0] - output_data[-1][-1][0])
#     #     if diff > 45:
#     #         output_data.append([])
#     #     output_data[-1].append(data_group[i])
#     #     if abs(data_group[i][0] - output_data[-1][-1][0]) > 45:
#     #         output_data.append([])
#     #     output_data[-1].append(data_group)
#     # all_data = west_side[1:] + north_side[1:] + east_side[1:] + south_side[1:]
#     all_data = west_side + north_side + east_side + south_side
#     # all_data = ma.removeDupesListOfLists(all_data)
#     fig, ax1 = plt.subplots()
#     x1, y1 = [i[0] for i in all_data], [i[1] for i in all_data]
#     x2, y2 = [i[0] for i in lst], [i[1] for i in lst]
#     ax1.scatter(x1, y1, c='black')
#     ax1.scatter(x2, y2, c='blue')
#     plt.show()
#     print(len(lst), len(all_data))
#     return all_data
#
# def graph_data(lst_all, n_data, s_data, e_data, w_data):
#     colors = ["black", "#E69F00", "#56B4E9", "#56B4E9", '#0072B2', '#D55E00', '#CC79A7']
#     fig, ax1 = plt.subplots()
#     x1, y1 = [i[0] for i in lst_all], [i[1] for i in lst_all]
#     x2, y2 = [i[0] for i in n_data], [i[1] for i in n_data]
#     x3, y3 = [i[0] for i in s_data], [i[1] for i in s_data]
#     x4, y4 = [i[0] for i in e_data], [i[1] for i in e_data]
#     x5, y5 = [i[0] for i in w_data], [i[1] for i in w_data]
#     ax1.scatter(x1, y1, c=colors[0])
#     # ax1.plot(x2, y2, c=colors[1])
#     # ax1.plot(x3, y3, c=colors[2])
#     # ax1.plot(x4, y4, c=colors[3])
#     # ax1.plot(x5, y5, c=colors[4])
#     plt.show()

def compareGISDataToParsed(df):
    df_parsed = pd.read_csv("AllGrids.csv", encoding="ISO-8859-1")
    df_parsed = df_parsed.to_numpy().tolist()
    high_prob_lst, mid_prob_lst = [], []
    # df_parsed = ma.oneToMany(df_parsed, )
    for i in range(len(df_parsed)):
        df_parsed[i][:6], df_parsed[i][-1] = [int(j) for j in df_parsed[i][:6]], str(int(df_parsed[i][-1]))
    d = [[df_parsed[0]]]
    for i in range(1, len(df_parsed)):
        if df_parsed[i][-1] != d[-1][-1][-1]:
            d.append([])
        d[-1].append(df_parsed[i])
    df_parsed = d

    for i in range(len(df_parsed)):
        df_parsed_coords = [j[6:8] for j in df_parsed[i]]
        df_parsed[i][0][0], df_parsed[i][0][1], df_parsed[i][0][3] = int(df_parsed[i][0][0]), int(df_parsed[i][0][1]), int(df_parsed[i][0][3])
        # many_pts_conc = int(float(str(df_parsed[i][0]) + str(df_parsed[i][1]) + str(df_parsed[i][2]) + str(df_parsed[i][3]) + str(df_parsed[i][4]) + str(df_parsed[i][5])))
        sql_string_indexes = [int(df_parsed[i][0][0]), int(df_parsed[i][0][1]), int(df_parsed[i][0][2]), int(df_parsed[i][0][3]), int(df_parsed[i][0][4]), int(df_parsed[i][0][5])]
        sql_string_indexes = copy.deepcopy(sql_string_indexes)
        df_parsed[i][0][2] = translateNumberToDirection('township', str(int(df_parsed[i][0][2])))
        df_parsed[i][0][4] = translateNumberToDirection('rng', str(int(df_parsed[i][0][4])))
        df_parsed[i][0][5] = translateNumberToDirection('baseline', str(int(df_parsed[i][0][5])))
        df_parsed[i][0] = [str(r) for r in df_parsed[i][0]]
        len_lst = [len(r) for r in df_parsed[i][0][:6]]
        if len_lst[0] == 1:
            df_parsed[i][0][0] = "0" + str(df_parsed[i][0][0])
        if len_lst[1] == 1:
            df_parsed[i][0][1] = "0" + str(df_parsed[i][0][1])
        if len_lst[3] == 1:
            df_parsed[i][0][3] = "0" + str(df_parsed[i][0][3])
        sql_conc_str = str(df_parsed[i][0][0]) + str(df_parsed[i][0][1]) + str(df_parsed[i][0][2]) + str(df_parsed[i][0][3]) + str(df_parsed[i][0][4]) + str(df_parsed[i][0][5])
        # sql_string_indexes = [str(df_parsed[i][0][0]), str(df_parsed[i][0][1]), str(df_parsed[i][0][2]), str(df_parsed[i][0][3]), str(df_parsed[i][0][4]), str(df_parsed[i][0][5])]
        df_tester = df[df['new_code'] == sql_conc_str][['Easting', 'Northing']].to_numpy().tolist()
        # print("\n______________________________________________________________\n", sql_conc_str)
        high_prob, mid_prob = compareDirect(df_tester, df_parsed_coords)
        if high_prob:
            high_prob = [sql_string_indexes + r for r in high_prob]
            high_prob_lst.append(high_prob)
        if mid_prob:
            mid_prob = [sql_string_indexes + r for r in mid_prob]
            mid_prob_lst.append(mid_prob)
    high_prob_lst = [i for i in high_prob_lst if i]
    mid_prob_lst = [i for i in mid_prob_lst if i]
    print(len(high_prob_lst), len(mid_prob_lst))
    pd.set_option('display.max_columns', None)


def compareDirect(lst1, lst2):
    high_prob = []
    mid_prob = []
    output = EditAGRCData.findCorners(lst1)

    lst1 = ProcessCoordData.getPlatBounds(lst1)[1:]
    lst1 = list(chain.from_iterable(lst1))
    new_points_1, new_points_2 = [], []
    dup_free1, dup_free2 = [], []
    colors = ["black", "#E69F00", "#56B4E9", "#56B4E9", '#0072B2', '#D55E00', '#CC79A7']
    # for r in range(1):
    new_pts_side = []
    for xy1, xy2 in zip(lst1, lst1[1:]):
        new_points_1.append(xy1)
        for i in range(1, 100):
            div = i / 100
            new_points_1.append(findPointsOnLine(xy1, xy2, div))
            new_pts_side.append(findPointsOnLine(xy1, xy2, div))
    for xy1, xy2 in zip(lst2, lst2[1:]):
        new_points_2.append(xy1)
        for i in range(1, 100):
            div = i / 100
            new_points_2.append(findPointsOnLine(xy1, xy2, div))
            new_points_2.append(findPointsOnLine(xy1, xy2, div))

    for x in new_points_1:
        if x not in dup_free1:
            dup_free1.append(x)

    for x in new_points_2:
        if x not in dup_free2:
            dup_free2.append(x)
    new_points_1, new_points_2 = dup_free1, dup_free2

    poly_1 = Polygon(new_points_1).buffer(1.5)
    poly_2 = Polygon(new_points_2).buffer(1.5)
    area_poly_1 = poly_1.area
    area_poly_2 = poly_2.area
    output_diff = poly_1.difference(poly_2)
    output_diff2 = poly_2.difference(poly_1)
    total_area = poly_1.intersection(poly_2).area
    counter = 0
    total_diff, total_diff2 = 0, 0

    if output_diff.geom_type == 'MultiPolygon':
        for i in output_diff:
            total_diff += i.area
    else:
        total_diff += output_diff.area
    if output_diff2.geom_type == 'MultiPolygon':
        for i in output_diff2:
            total_diff2 += i.area
    else:
        total_diff2 += output_diff2.area
        # point_i = list(zip(*i.exterior.coords.xy))
        # point_i = [list(j) for j in point_i]
        # x1, y1 = [i[0] for i in point_i], [i[1] for i in point_i]
        # ax1.plot(x1, y1, c=colors[counter])

        # counter += 1

    overlap1 = round((total_area / area_poly_1) * 100, 3)
    overlap2 = round((total_area / area_poly_2) * 100, 3)
    overlap_avg = round((overlap1 + overlap2) / 2, 3)
    if 101 > overlap_avg > 99:
        # if 102 > overlap1 > 98 and 102 > overlap2 > 98:
        # print('total_diff1', total_diff)
        # print('total_diff2', total_diff2)
        # print('total area', total_area)
        # print('total difference avg', overlap_avg)


        high_prob = lst2
    if 103 > overlap_avg > 97:
        fig, ax1 = plt.subplots()
        x1, y1 = [i[0] for i in new_points_1], [i[1] for i in new_points_1]
        x2, y2 = [i[0] for i in new_points_2], [i[1] for i in new_points_2]
        ax1.plot(x1, y1, c='#B42F32')
        ax1.plot(x2, y2, c='#878D92')
        # plt.show()
        mid_prob = lst2

    return high_prob, mid_prob


def findPolygonDifference(lst, shape):
    # fig, ax1 = plt.subplots()
    poly = Polygon(shape)
    contain_yes, contain_no = [], []
    for i in lst:
        if poly.contains(Point(i)):
            contain_yes.append(i)
        else:
            contain_no.append(i)
    poly_all = Polygon(poly).area
    poly_yes = Polygon(contain_yes).area
    poly_no = Polygon(contain_no).area

    area_diff = abs(poly_yes - poly_all)
    x1, y1 = [i[0] for i in contain_yes], [i[1] for i in contain_yes]
    x2, y2 = [i[0] for i in contain_no], [i[1] for i in contain_no]
    x3, y3 = [i[0] for i in lst], [i[1] for i in lst]
    x4, y4 = [i[0] for i in shape], [i[1] for i in shape]

    # ax1.plot(x2, y2, c='black')
    # ax1.plot(x3, y3, c="#E69F00")
    # ax1.plot(x4, y4, c='#0072B2')
    # ax1.fill(x1, y1, c='#B42F32', alpha = .8)
    # plt.show()
    return contain_yes


def findPointsOnLine(xy1, xy2, div):
    x, y = xy1[0] + (div * (xy2[0] - xy1[0])), xy1[1] + (div * (xy2[1] - xy1[1]))
    return [x, y]
    # return x,y


def drawData():
    conn, cursor = sqlConnect()
    len_lst = []
    sql_lst, sql_conc = parseDatabaseForDataWithSectionsAndSHL(cursor)
    df = pd.read_csv("All_Data_Lat_Lon.csv", encoding="ISO-8859-1")
    # df = pd.read_csv("LatLonEdited.csv", encoding="ISO-8859-1")
    compareGISDataToParsed(df)
    pd.set_option('display.max_columns', None)
    # many_pts_lst, conc_many_lst, conc_bad = [], [642312, 142422, 27921911, 1652212, 1152212, 28921911, 1442212, 13921911, 152212, 852312], [2542222, 652312, 3142212, 3642422, 2632222, 4922111, 3342622, 1822322, 3242622, 30722311, 2342212, 3442622, 722322, 22921511, 15921511, 31922111, 5822011,
    #                                                                                                                                         1922322, 752312, 30722011, 3042212, 2532222, 8822011, 3532422, 242422, 2442212, 1342212, 552212, 1842312, 13821611, 642312]
    # # many_pts_lst, conc_many_lst, conc_bad = [], [], []
    fig, ax = plt.subplots()

    len_lst = sorted(len_lst, key=lambda r: r[0])

    # saveData(many_pts_lst)

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
    slope_lst = [GatherPlatDataSet.slopeFinder2(data1[i], data2[i])]
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
    df = pd.read_csv("UTMTrueData.csv", encoding="ISO-8859-1")
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
        if len(id_conc[i]) > 21:
            grouped_lst.append(id_conc[i][1:21])
    # fig, ax = plt.subplots()
    for i in grouped_lst:
        x, y = [j[6] for j in i], [j[7] for j in i]
        ts = translateNumberToDirection('township', str(int(i[0][2])))
        rng = translateNumberToDirection('rng', str(int(i[0][4])))
        bs = translateNumberToDirection('baseline', str(int(i[0][5])))
        id = str(int(float(i[0][0]))) + " " + str(int(float(i[0][1]))) + ts + " " + str(int(float(i[0][3]))) + rng + " " + bs
        centroid = (sum(x) / len(i), sum(y) / len(i))
        # ax.text(centroid[0], centroid[1], id)
        # ax.plot(x, y, c='red')
    # plt.show()
    grouped_lst = list(chain.from_iterable(grouped_lst))
    saveData(grouped_lst)


def mainProcess():
    df_lst, df_conc, restricted_lst, id_conc = loadData()
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

                        if 1.02 > NS_distance / sql_lst[i][-4] > .98 and 1.02 > EW_distance / sql_lst[i][-2] > .98:
                            if sql_conc[i] in unique_sections:
                                unique_sections_multiple.append(sql_conc[i])
                            corrected_lst.append(sql_lst[i][:6])
                            unique_sections.append(sql_conc[i])
                except:
                    pass
    return corrected_lst


def findLocationData(coord_lst, well_location):
    coord_lst = ma.oneToMany(coord_lst, 5)
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
    # df.to_csv('OddballSections.csv', index=False)
    df.to_csv('TrueSections.csv', index=False)


# [2722322,3322322,3122222,132122,3022222,23922111,1632222,932222,3022112,21922111,3632122,3652622,15722211,2732422,92622011,2222322,1732112,2522322,16722211,2522122,7922111,3322322,3422422,4922111,36722011,16722211,2532522,1632222,2632422,2622322,1922222,932222,2622222,3022222,21922111,1332522,3522422,2332122,15722011]
def loadData():
    df = pd.read_csv("CoordDataPlatsGrid2.csv", encoding="ISO-8859-1")
    pd.set_option('display.max_columns', None)
    df_lst = df.to_numpy().tolist()
    for i in range(len(df_lst)):
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
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS01;"
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


# mainProcessRemoveDupes()
drawData()
# renderAGRCDataDown()