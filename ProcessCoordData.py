import openpyxl
import ModuleAgnostic
import copy
import re
import itertools
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from itertools import chain
import ProcessBHLLocation
import time


# def mainProcess(delta_north, delta_east, bhl, shl):
def mainProcess(shl_utm, bhl_utm, delta_east, delta_north, prod_index, df):
    shl_utm, bhl_utm = [float(i) for i in shl_utm], [float(i) for i in bhl_utm]
    # df = pd.read_csv("All_Data_Lat_Lon.csv", encoding="ISO-8859-1")

    offset_lst = mainProcessUTM(delta_east, delta_north, shl_utm)

    plat = findStartingPlat(df, shl_utm)

    code_lst = determineAdjacentVals(plat)

    all_pts, all_bounds_by_section, sections_all, bounded_lst = findRelevantPoints(df, shl_utm, code_lst, offset_lst)

    NS_distance_SHL, EW_distance_SHL, only_coords_lst_SHL, n_shl_ind, e_shl_ind = ProcessBHLLocation.findBHLLocation(all_bounds_by_section, shl_utm, bounded_lst)

    NS_distance_prod, EW_distance_prod, only_coords_lst, n_prod_ind, e_prod_ind = ProcessBHLLocation.findBHLLocation(all_bounds_by_section, offset_lst[prod_index], bounded_lst)


    NS_distance_BHL, EW_distance_BHL, only_coords_lst, n_bhl_ind, e_bhl_ind = ProcessBHLLocation.findBHLLocation(all_bounds_by_section, bhl_utm, bounded_lst)

    n_prod_ind, e_prod_ind, n_bhl_ind, e_bhl_ind, n_shl_ind, e_shl_ind = translateSide(n_prod_ind), translateSide(e_prod_ind), translateSide(n_bhl_ind), translateSide(e_bhl_ind), translateSide(n_shl_ind), translateSide(e_shl_ind)

    bhl_coords = [NS_distance_BHL, n_bhl_ind, EW_distance_BHL, e_bhl_ind]
    prod_coords = [NS_distance_prod, n_prod_ind, EW_distance_prod, e_prod_ind]
    shl_coords = [NS_distance_SHL, n_shl_ind, EW_distance_SHL, e_shl_ind]


    return bhl_coords, prod_coords, shl_coords, only_coords_lst, offset_lst, sections_all


def translateSide(data_pt):
    if data_pt == 0:
        return 'FSL'
    elif data_pt == 1:
        return 'FEL'
    elif data_pt == 2:
        return 'FNL'
    elif data_pt == 3:
        return 'FWL'


# generate the offset list (as modified by shl) as well as the shl in utm values
def mainProcessUTM(east_lst, north_lst, shl):
    north_lst_m, east_lst_m = [i * 0.3048 for i in north_lst], [i * 0.3048 for i in east_lst]
    offset_lst = list(zip([shl[0] + i for i in east_lst_m], [shl[1] + i for i in north_lst_m]))
    return offset_lst


def findStartingPlat(df, shl):
    df['min_distance'] = np.vectorize(equationDistance)(df['Easting'], df['Northing'], shl[0], shl[1])
    min_df = df[df['min_distance'] == df['min_distance'].min()]
    data = list(set(min_df['new_code'].to_numpy().tolist()))
    df_dict = {i: df[df['new_code'].str.contains(i)][['Easting', 'Northing']].to_numpy().tolist() for i in data}

    for i, k in df_dict.items():
        k = [tuple(j) for j in k]
        if determineIfInside(shl, k):
            return i


def equationDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def determineAdjacentVals(data):
    section, township, township_dir, range_val, range_dir, meridian = int(data[:2]), int(data[2:4]), data[4], int(data[5:7]), data[7], data[8]
    all_data_lst = processSections(section, township, township_dir, range_val, range_dir, meridian)
    all_data_lst.append([section, township, township_dir, range_val, range_dir, meridian])
    for i in all_data_lst:
        output = processSections(i[0], i[1], i[2], i[3], i[4], i[5])
        all_data_lst = all_data_lst + output
    all_data_lst = [list(t) for t in set(tuple(element) for element in all_data_lst)]
    all_data_lst = sorted(all_data_lst)
    code_lst = rewriteCode(all_data_lst)
    return code_lst


def processSections(section, township, township_dir, range_val, range_dir, meridian):
    all_data_lst = []
    lst = platAdjacentLsts(int(section))
    sections = lst[1]
    for i in range(len(lst[1])):
        tsr_mod = lst[2][i]
        for j in range(len(sections[i])):
            sec_val = sections[i][j]
            township_new, township_dir_new = modTownship(tsr_mod[0], township, township_dir)
            range_val_new, range_dir_new = modRange(tsr_mod[1], range_val, range_dir)
            all_data_lst.append([sec_val, township_new, township_dir_new, range_val_new, range_dir_new, meridian])
    return all_data_lst


def platAdjacentLsts(index):
    lst = [[[1], [[2, 11, 12], [35, 36], [6, 7], [31]], [[0, 0], [1, 0], [0, 1], [1, 1]]],
           [[2], [[3, 10, 11, 12, 1], [34, 35, 36]], [[0, 0], [1, 0]]],
           [[3], [[4, 9, 10, 11, 2], [33, 34, 35]], [[0, 0], [1, 0]]],
           [[4], [[5, 8, 9, 10, 3], [32, 33, 34]], [[0, 0], [1, 0]]],
           [[5], [[6, 7, 8, 9, 4], [31, 32, 33]], [[0, 0], [1, 0]]],
           [[6], [[7, 5, 8], [31, 32], [1, 12], [36]], [[0, 0], [1, 0], [0, -1], [1, -1]]],
           [[7], [[6, 5, 8, 17, 18], [1, 12, 13]], [[0, 0], [0, -1]]],
           [[18], [[7, 8, 17, 19, 20], [12, 13, 14]], [[0, 0], [0, -1]]],
           [[19], [[18, 17, 20, 29, 30], [13, 14, 25]], [[0, 0], [0, -1]]],
           [[30], [[19, 20, 29, 32, 31], [14, 25, 36]], [[0, 0], [0, -1]]],
           [[31], [[30, 29, 32], [6, 5], [25, 36], [1]], [[0, 0], [-1, 0], [0, -1], [-1, -1]]],
           [[12], [[13, 14, 11, 2, 1], [18, 7, 6]], [[0, 0], [0, 1]]],
           [[13], [[24, 23, 14, 11, 12], [19, 18, 7]], [[0, 0], [0, 1]]],
           [[24], [[25, 26, 23, 14, 13], [30, 19, 18]], [[0, 0], [0, 1]]],
           [[25], [[36, 35, 26, 23, 24], [31, 30, 19]], [[0, 0], [0, 1]]],
           [[32], [[31, 30, 29, 28, 33], [6, 5, 4]], [[0, 0], [-1, 0]]],
           [[33], [[32, 29, 28, 27, 34], [5, 4, 3]], [[0, 0], [-1, 0]]],
           [[34], [[33, 28, 27, 26, 35], [4, 3, 2]], [[0, 0], [-1, 0]]],
           [[35], [[34, 27, 26, 25, 36], [2, 3, 1]], [[0, 0], [-1, 0]]],
           [[36], [[35, 26, 25], [2, 1], [31, 30], [6]], [[0, 0], [-1, 0], [0, 1], [-1, 1]]],
           [[8], [[5, 4, 9, 16, 17, 18, 7, 6]], [[0, 0]]],
           [[9], [[4, 3, 10, 15, 16, 17, 8, 5]], [[0, 0]]],
           [[10], [[3, 2, 11, 14, 15, 16, 9, 4]], [[0, 0]]],
           [[11], [[2, 1, 12, 13, 14, 15, 10, 3]], [[0, 0]]],
           [[17], [[8, 9, 16, 21, 20, 19, 18, 7]], [[0, 0]]],
           [[16], [[9, 10, 15, 22, 21, 20, 17, 8]], [[0, 0]]],
           [[15], [[10, 11, 14, 23, 22, 21, 16, 9]], [[0, 0]]],
           [[14], [[11, 12, 13, 24, 23, 22, 15, 10]], [[0, 0]]],
           [[20], [[17, 16, 21, 28, 29, 30, 19, 18]], [[0, 0]]],
           [[21], [[16, 15, 22, 27, 28, 29, 20, 17]], [[0, 0]]],
           [[22], [[15, 14, 23, 26, 27, 28, 21, 16]], [[0, 0]]],
           [[23], [[14, 13, 24, 25, 26, 27, 22, 15]], [[0, 0]]],
           [[29], [[20, 21, 28, 33, 32, 31, 30, 19]], [[0, 0]]],
           [[28], [[21, 22, 27, 34, 33, 32, 29, 20]], [[0, 0]]],
           [[27], [[22, 23, 26, 35, 34, 33, 28, 21]], [[0, 0]]],
           [[26], [[23, 24, 25, 36, 35, 34, 27, 22]], [[0, 0]]]]
    for i in lst:
        if i[0][0] == index:
            return i


def modTownship(tsr_val, tsr_base, tsr_direction):
    if tsr_val == 0:
        return tsr_base, tsr_direction
    else:
        if tsr_direction == 'N':
            if tsr_val == -1:
                tsr_base -= 1
            elif tsr_val == 1:
                tsr_base += 1
        elif tsr_direction == 'S':
            if tsr_val == -1:
                tsr_base += 1
            elif tsr_val == 1:
                tsr_base -= 1
        if tsr_direction == 'N' and tsr_base == 0:
            tsr_direction, tsr_base = 'S', 1
        elif tsr_direction == 'S' and tsr_base == 0:
            tsr_direction, tsr_base = 'N', 1
        return tsr_base, tsr_direction


def modRange(tsr_val, tsr_base, tsr_direction):
    if tsr_val == 0:
        return tsr_base, tsr_direction
    else:
        if tsr_direction == 'W':
            if tsr_val == -1:
                tsr_base += 1
            elif tsr_val == 1:
                tsr_base -= 1
        elif tsr_direction == 'E':
            if tsr_val == -1:
                tsr_base -= 1
            elif tsr_val == 1:
                tsr_base += 1

        if tsr_direction == 'E' and tsr_base == 0:
            tsr_direction, tsr_base = 'W', 1
        elif tsr_direction == 'W' and tsr_base == 0:
            tsr_direction, tsr_base = 'E', 1
        return tsr_base, tsr_direction


def rewriteCode(lst):
    new_lst = []
    lst = sorted(lst)
    for i in lst:
        section, township, township_dir, range_val, range_dir, meridian = str(i[0]), str(i[1]), i[2], str(i[3]), i[4], i[5]
        if len(section) == 1:
            section = "0" + section
        if len(township) == 1:
            township = "0" + township
        if len(range_val) == 1:
            range_val = "0" + range_val
        fullLine = section + township + township_dir + range_val + range_dir + meridian
        new_lst.append(fullLine)
    return new_lst


def findRelevantPoints(df, shl, code_lst, offset_lst):
    sections_all, all_points, pts_all, test_combo_section, test_id, test_all = [], [], [], [], [], []
    all_points, sections_all, test_combo_section = findRelevantPointsGetComboLists(df, code_lst, offset_lst)
    test_lst = []
    for i in range(len(test_combo_section)):
        test_lst.append([])
        test_lst[-1].append([test_combo_section[i][0]])
        for k in range(len(test_combo_section[i][1])):
            test_lst[-1].append(list(test_combo_section[i][1][k]))
    sections_all, all_points = testFinder(test_combo_section)  # for i in code_lst:

    for i in range(len(all_points)):
        all_points[i], south_bounds, east_bounds, north_bounds, west_bounds = getPlatBounds(all_points[i])
        pts_all.append([south_bounds, east_bounds, north_bounds, west_bounds])

    test_lst = list(k for k, _ in itertools.groupby(test_lst))
    all_points_flattened = [list(t) for t in set(tuple(element) for element in list(chain.from_iterable(all_points)))]

    return all_points_flattened, test_lst, sections_all, pts_all


def findRelevantPointsGetComboLists(df, code_lst, offset_lst):
    all_points, sections_all, test_combo_section = [], [], []
    data_val = list(zip(df['Easting'].tolist(), df['Northing'].tolist(), df['new_code'].tolist()))
    for i in code_lst:
        df_lst = [(n[0], n[1]) for n in data_val if i in n[2]]
        data_set = [i for i in df_lst if i]
        for j in offset_lst:
            if determineIfInside(j, data_set):
                sections_all.append(i)
                test_combo_section.append([i, data_set])
            all_points.append(data_set)
    return all_points, sections_all, test_combo_section


def testFinder(test_combo_section):
    test_id, test_all = [], []
    for i in range(len(test_combo_section)):
        if test_combo_section[i][0] not in test_id:
            test_id.append(test_combo_section[i][0])
            test_all.append(test_combo_section[i][1])
    return test_id, test_all


def determineIfInside(shl, data):
    point = Point(shl[0], shl[1])
    polygon = Polygon(data)
    return polygon.contains(point)


def getPlatBounds(data_set):
    data_setX, data_setY = [p[0] for p in data_set], [p[1] for p in data_set]
    # print('data', data_setX)
    x_output, y_output = dict(enumerate(ModuleAgnostic.grouper(sorted(data_setX), 300), 1)), dict(enumerate(ModuleAgnostic.grouper(sorted(data_setY), 300), 1))
    x_output, y_output = [j for i, j in x_output.items()], [j for i, j in y_output.items()]

    xBounds, yBounds = boundaryFinder(x_output, y_output, data_set)
    south_bounds, north_bounds, west_bounds, east_bounds = yBounds[0], yBounds[1], xBounds[0], xBounds[1]
    south_bounds = sorted(boundsParser(south_bounds, 0, 'S'), key=lambda x: x[0])
    north_bounds = list(reversed(sorted(boundsParser(north_bounds, 0, 'N'), key=lambda x: x[0])))
    west_bounds = list(reversed(sorted(boundsParser(west_bounds, 1, 'W'), key=lambda x: x[0])))
    east_bounds = sorted(boundsParser(east_bounds, 1, 'E'), key=lambda x: x[1])

    boundaries_all = south_bounds + east_bounds + north_bounds + west_bounds

    return boundaries_all, south_bounds, east_bounds, north_bounds, west_bounds


def boundsParser(lst, target, dir):
    lst_org = copy.deepcopy(lst)
    lst_group = [float(i[target]) for i in lst]
    output_dict = dict(enumerate(ModuleAgnostic.grouper(sorted(lst_group), 10), 1))
    output_data = [j for i, j in output_dict.items()]
    for i in range(len(output_data)):
        if len(output_data[i]) > 1 and len(lst_group) != len(output_data[0]):
            found_data = findPresentData(output_data[i], lst_org, target)

            if dir == 'S':
                data = [p[1] for p in found_data]
                bad_data = min(data)
                lst = [k for k in lst if k[1] != bad_data]
            elif dir == 'N':
                data = [p[1] for p in found_data]
                bad_data = max(data)
                lst = [k for k in lst if k[1] != bad_data]

            elif dir == 'W':
                data = [p[0] for p in found_data]
                bad_data = max(data)
                lst = [k for k in lst if k[0] != bad_data]

            elif dir == 'E':
                data = [p[0] for p in found_data]
                bad_data = min(data)
                lst = [k for k in lst if k[0] != bad_data]

    return lst


def findPresentData(val_lst, all_lst, target):
    found_data = []
    for i in val_lst:
        for j in all_lst:
            if i == j[target]:
                found_data.append(j)
    return found_data


def boundaryFinder(x_output, y_output, coord):
    xBounds, yBounds = [x_output[0], x_output[-1]], [y_output[0], y_output[-1]]
    for i in range(len(xBounds)):
        for j in range(len(xBounds[i])):
            for k in coord:
                if xBounds[i][j] == k[0]:
                    xBounds[i][j] = k
    for i in range(len(yBounds)):
        for j in range(len(yBounds[i])):
            for k in coord:
                if yBounds[i][j] == k[1]:
                    yBounds[i][j] = k
    for i in range(len(xBounds)):
        xBounds[i] = [list(t) for t in set(tuple(element) for element in xBounds[i])]
    for i in range(len(yBounds)):
        yBounds[i] = [list(t) for t in set(tuple(element) for element in yBounds[i])]
    return xBounds, yBounds


def grapher(x, y):
    pass
    # fig = plt.figure()
    # ax = plt.axes(projection=None)
    # ax.set_yticks(np.arange(min(y), max(y) + 1000, 1000))
    # ax.set_xticks(np.arange(min(x), max(x) + 1000, 1000))
    # ax.set_xlabel("Easting")
    # ax.set_ylabel("Northing")
    # ax.scatter(x, y, c='red')
    # plt.tight_layout()
    # plt.show()
