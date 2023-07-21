from shapely.geometry import Point, LineString
from ast import literal_eval
import string
import re
import traceback
import matplotlib.colors as mcolors
from collections import Iterable
from glob import glob
from functools import reduce
import operator
import inspect
import math
import os
import numpy as np

import ModuleAgnostic
from UIDataGather import *
from shapely.geometry.polygon import Polygon


# C:\Work\RewriteAPD>C:\Users\colto\AppData\Local\Programs\Python\Python37\Scripts\pyuic5.exe fileDialog.ui -o fileDialog.py
def writeFiles(cellLst, valuesLst, worksheet):
    for i in range(len(cellLst)):
        worksheet[cellLst[i]] = valuesLst[i]


def sortPointsInClockwisePattern(coords):
    center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
    output = sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)
    return output


def printFunctionName():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print('\nFUNCTION:', calframe[1][3])


def printLineBreak():
    print("_______________________________________________________")


def printLine(lst):
    if len(lst) != 0:
        print()
        for i in range(len(lst)):
            print(i, "\t", lst[i])
        print()


def equationDistance(x1, y1, x2, y2):
    return math.sqrt((float(x2) - float(x1)) ** 2 + (float(y2) - float(y1)) ** 2)


def removeDupesListOfLists(lst):
    dup_free = []
    dup_free_set = set()
    for x in lst:
        if tuple(x) not in dup_free_set:
            dup_free.append(x)
            dup_free_set.add(tuple(x))
    return dup_free


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


def convertAllToStrings(lst):
    for i in range(len(lst)):
        if isinstance(lst[i], list):
            for j in range(len(lst[i])):
                lst[i][j] = str(lst[i][j])
        else:
            lst[i] = str(lst[i])
    return lst


def checkListOfListsIdentical(lst1, lst2):
    match_boos = []
    for i in range(len(lst1)):
        if set(lst1[i]) == set(lst2[i]):
            # print('True')
            match_boos.append(True)
        else:
            # print('\nFalse')
            # for j in range(len(lst1[i])):
            #     print(lst1[i][j], lst2[i][j])
            match_boos.append(False)
    if False in match_boos:
        return False
    else:
        return True


def convertDecimalToDegrees(dd):
    mnt, sec = divmod(dd * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return int(deg), int(mnt), round(sec, 2)

def determineIfInside(pt, data):
    point = Point(pt[0], pt[1])
    polygon = Polygon(data)
    return polygon.contains(point)


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

    data_lengths = reorganizeLstPointsWithAngle(data_lengths, centroid)
    east_side = data_lengths[8:13]
    north_side = data_lengths[4:9]
    west_side = data_lengths[:5]
    south_side = data_lengths[12:]

    all_data = [west_side] + [north_side] + [east_side] + [south_side]

    return corners, all_data


def reorganizeLstPointsWithAngle(lst, centroid):
    lst_arrange = [i + [(math.degrees(math.atan2(centroid[1] - i[1], centroid[0] - i[0])) + 360) % 360] for i in lst]
    return lst_arrange


def arrangeDirectionData(corner, lst, label, centroid):


    found_side_data = []
    x_lst, y_lst = [i[0] for i in lst], [i[1] for i in lst]
    if label == 'west':
        xy1, xy2 = corner[0], corner[3]

    if label == 'north':
        xy1, xy2 = corner[3], corner[2]
    if label == 'east':
        xy1, xy2 = corner[2], corner[1]
    if label == 'south':
        xy1, xy2 = corner[1], corner[0]

    index1 = x_lst.index(xy1[0])
    index2 = x_lst.index(xy2[0])
    index2 = len(x_lst) if index2 == 0 else index2
    if index1 < index2:
        found_side_data_foo = lst[index1:index2+1]
    else:
        found_side_data_foo = lst[:index2+1]
    #


    angles = [xy1[-1], xy2[-1]]
    found_side_data.append(xy1)

    x_gap = abs(xy1[0] - abs(xy2[0]))
    for i in lst:
        if label == 'west':
            if 360 > i[-1] > max(angles) or min(angles) > i[-1] > 0:
                found_side_data.append(i)
        else:
            if max(angles) > i[-1] > min(angles):
                found_side_data.append(i)
    found_side_data.append(xy2)
    return found_side_data_foo


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


def checkClockwisePts(coords):
    center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
    output = sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)
    return output


def flatten(lst):
    if len(lst) == 1:
        if type(lst[0]) == list:
            result = flatten(lst[0])
        else:
            result = lst

    elif type(lst[0]) == list:
        result = flatten(lst[0]) + flatten(lst[1:])

    else:
        result = [lst[0]] + flatten(lst[1:])

    return result


def convertToDecimal(data):
    data_converted = []
    for i in range(len(data)):
        if len(data[i]) > 6:
            data[i] = data[i][6:12]
            data[i][1] = float(data[i][1])
        side, deg, min, sec, dir_val = float(data[i][1]), float(data[i][2]), float(data[i][3]), float(data[i][4]), float(data[i][5])
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


# 1322.71
def pointsConverter(data):
    x, y = 0, 0
    data = reorderDecimalData(data)
    data = oneToMany(data, 4)
    # for i in range(len(data)):
    #     x, y = 0, 0
    #     x_pts.append([])
    #     y_pts.append([])
    #     for j in range(len(data[i])):
    #         x_pts[i].append(x)
    #         y_pts[i].append(y)
    #         x, y = pointLineFinder(data[i][j], x, y)
    #     x_pts[i].append(x)
    #     y_pts[i].append(y)
    # for i in range(len(x_pts)):
    #     output = list(zip(x_pts[i], y_pts[i]))
    #     output = [list(i) for i in output]
    #     new_data.append(output)
    # new_data = list(itertools.chain.from_iterable(new_data))

    output = []
    x_pts, y_pts = [], []
    x, y = 0, 0
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

def convertPtsToSides(pts, tsr_data, conc_data):
    degrees_lst = []
    dirLst = [['West-Up2', 'West-Up1', 'West-Down1', 'West-Down2'],
              ['East-Up2', 'East-Up1', 'East-Down1', 'East-Down2'],
              ['North-Left2', 'North-Left1', 'North-Right1', 'North-Right2'],
              ['South-Left2', 'South-Left1', 'South-Right1', 'South-Right2']]
    pts_west, pts_north, pts_east, pts_south = pts
    lens_w = angleAndLengths(pts_west)
    lens_n = angleAndLengths(pts_north)
    lens_e = angleAndLengths(pts_east)
    lens_s = angleAndLengths(pts_south[:-1])
    lens_w = lens_w[::-1]
    lens_s = lens_s[::-1]



    tsr_data[2] = translateDirectionToNumber('township', str(tsr_data[2])).upper()
    tsr_data[4] = translateDirectionToNumber('rng', str(tsr_data[4])).upper()
    tsr_data[5] = translateDirectionToNumber('baseline', str(tsr_data[5])).upper()
    tsr_data = [int(float(i)) for i in tsr_data]
    for i in range(len(lens_w)):
        degrees = reconvertToDegrees(lens_w[i][1], 'west')

        degrees_lst.append(tsr_data + [dirLst[0][i]] + [lens_w[i][0]] + degrees + ["T"] + [conc_data])
        # degrees_lst.append(tsr_data + [dirLst[0][i]] + [lens_w[i][0]] + degrees + ["T"] + [conc_data] + [pts[-1][-2]])
    for i in range(len(lens_e)):
        degrees = reconvertToDegrees(lens_e[i][1], 'east')
        # degrees_lst.append(tsr_data + [dirLst[1][i]] + [lens_e[i][0]] + degrees + ["T"] + [conc_data] + [pts[-1][-2]])
        degrees_lst.append(tsr_data + [dirLst[1][i]] + [lens_e[i][0]] + degrees + ["T"] + [conc_data])

    for i in range(len(lens_n)):
        degrees = reconvertToDegrees(lens_n[i][1], 'north')
        # degrees_lst.append(tsr_data + [dirLst[2][i]] + [lens_n[i][0]] + degrees + ["T"] + [conc_data] + [pts[-1][-2]])
        degrees_lst.append(tsr_data + [dirLst[2][i]] + [lens_n[i][0]] + degrees + ["T"] + [conc_data])

    for i in range(len(lens_s)):
        degrees = reconvertToDegrees(lens_s[i][1], 'south')
        # degrees_lst.append(tsr_data + [dirLst[3][i]] + [lens_s[i][0]] + degrees + ["T"] + [conc_data] + [pts[-1][-2]])
        degrees_lst.append(tsr_data + [dirLst[3][i]] + [lens_s[i][0]] + degrees + ["T"] + [conc_data])

    return degrees_lst


def angleAndLengths(lst):
    alLst = []
    for i in range(len(lst) - 1):
        pt1, pt2 = Point(lst[i]), Point(lst[i + 1])
        angle = (math.degrees(math.atan2(lst[i][1] - lst[i + 1][1], lst[i][0] - lst[i + 1][0])) + 360) % 360
        d = round(pt1.distance(pt2),2)
        alLst.append([d, angle])
    return alLst

def reconvertToDegrees(decVal, data):
    if data == 'west':
        decimal_value = abs(decVal - 270)
        if decVal < 270:
            dir_val = 3
        else:
            dir_val = 4
        deg_val = convertDecimalToDegrees(decimal_value)
    if data == 'east':# or data == 'west':
        decimal_value = abs(90 - decVal)
        if decVal < 90:
            dir_val = 3
        else:
            dir_val = 4
        deg_val = convertDecimalToDegrees(decimal_value)
    if data == 'north':# or data == 'south':
        if decVal < 180:
            decimal_value = abs(90 - decVal)
            dir_val = 4
        else:
            decimal_value = 90 - abs(180 - decVal)
            dir_val = 3
        deg_val = convertDecimalToDegrees(decimal_value)
    if data == 'south':
        data_360 = math.isclose(360, decVal, abs_tol=50)
        data_0 = math.isclose(0, decVal, abs_tol=50)
        if data_360 and not data_0:
            decimal_value = abs(decVal - 270)
            dir_val = 4
        if not data_360 and data_0:
            decimal_value = abs(90-decVal)
            dir_val = 3
        deg_val = convertDecimalToDegrees(decimal_value)
    return list(deg_val) + [dir_val]

def changeAngles(label, angle, found_side_data):
    if label.lower() == 'west':
        if 360 > angle > 220:
            pass
        elif 150 > angle > 50:
            pass


def reassemble(lst):
    w_lst, n_lst, e_lst, s_lst = lst
    w_lst = [tuple(i) for i in w_lst]
    n_lst = [tuple(i) for i in n_lst]
    e_lst = [tuple(i) for i in e_lst]
    s_lst = [tuple(i) for i in s_lst]

    west_north_connector_pt = w_lst[-1]
    n_lst = [[i[0] + west_north_connector_pt[0], i[1] + west_north_connector_pt[1]] for i in n_lst]
    west_south_connector_pt = s_lst[-1]
    s_lst = [[i[0] - west_south_connector_pt[0], i[1] - west_south_connector_pt[1]] for i in s_lst]

    north_east_connector_pt = n_lst[-1]
    e_lst = [[i[0] + north_east_connector_pt[0], i[1] + north_east_connector_pt[1]] for i in e_lst]

    w_lst = [tuple(i) for i in w_lst]
    n_lst = [tuple(i) for i in n_lst]
    e_lst = [tuple(i) for i in e_lst]
    s_lst = [tuple(i) for i in s_lst]


def pointLineFinder(i, x, y):
    center_x, center_y = x, y
    r, angle = i[0], i[1]
    x = center_x + (r * math.cos(math.radians(angle)))
    y = center_y + (r * math.sin(math.radians(angle)))
    return x, y


def reorderDecimalData(data):
    return [data[3], data[2], data[1], data[0], data[8], data[9], data[10], data[11], data[4], data[5], data[6], data[7], data[15], data[14], data[13], data[12]]
    # return [data[0], data[1], data[2], data[3], data[8], data[9], data[10], data[11], data[4], data[5], data[6], data[7], data[15], data[14], data[13], data[12]]


def convertFromPointsToRelativeSides(lst):
    corners, all_data = cornerGeneratorProcess(lst)


# def checkIfTwoListOfListsAreIdentical(lst1, lst2):

# def sortOutListsRecursion(lst, new_lst):
#     for i in range(len(lst)):
#         if not isinstance(lst[i], list):
#             new_lst = new_lst + lst

#             # new_lst.append(lst)
#         else:
#             # new_lst.append([])
#             sortOutListsRecursion(lst[i], new_lst)
#     # new_lst = [i for i in new_lst if i]

#     return new_lst

# def checkDataTypes(lst, data_lst):
#     for i in range(len(lst)):
#         if not isinstance(lst[i], list):
#             data_lst.extend([findDataType(lst[i])])
#         else:
#             data_lst.append([])
#             checkDataTypes(lst[i], data_lst[-1])
#     data_lst = [i for i in data_lst if i]
#     return data_lst

def get_type(input_data):
    try:
        return type(literal_eval(input_data))
    except (ValueError, SyntaxError):
        return str


def convertSetsToList(lst):
    for i in range(len(lst)):
        if isinstance(lst[i], set):
            pass
        elif isinstance(lst[i], list):
            convertSetsToList(lst[i])
        elif not isinstance(lst[i], list) and not isinstance(lst[i], set):
            # print([lst[i]])
            pass
    return lst

    # return [list(i) for i in lst if isinstance(i, set)]


def parseAllFoldersForString(new_path, searcher_var):
    files = glob(new_path + '/**/', recursive=True)
    for i in files:
        for j in os.listdir(i):
            if searcher_var in j:
                print(j)


def groupByLikeValues(lst, index):
    d = {}
    for row in lst:
        if row[index] not in d:
            d[row[index]] = []
        d[row[index]].append(row)
    d_lst = [j for i, j in d.items()]
    return d_lst


def reorderListByStringOrder(order_lst, lst, index):
    adjusted_lst = []
    for j in range(len(order_lst)):
        for i in range(len(lst)):

            if order_lst[j] == lst[i][index]:
                adjusted_lst.append(lst[i])
    return adjusted_lst


def dataGather(lst):
    data = lst.replace("\n", " ").replace("†", "").lower().strip().replace(",", "")
    data = re.sub(r'[^0-9. ]+', '', data).strip()
    data_lst = data.split(" ")
    data_lst = [i for i in data_lst if i]
    if len(data_lst) > 1 or data_lst == []:
        return []
    elif len(data_lst[0]) * 2 < len(lst):
        return []
    else:
        return data_lst


def findAllNumbers(data):
    re_finder = re.sub(r'[^0-9. ]+', '', data).strip().split()
    re_data = [float(i) for i in re_finder]
    return re_data


def printFormattedLine(lst):
    for row in lst:
        for col in row:
            print("{:10.2f}".format(col), end=" ")
        print("")


def getColors():
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color))),
                     name)
                    for name, color in mcolors.CSS4_COLORS.items())
    names = [name for hsv, name in by_hsv]
    return names


def isNotDigit(str):
    lstStringAll = list(string.printable)
    lstStringDigit = list(string.digits)
    lstStringRelevant = [x for x in lstStringAll if x not in lstStringDigit]
    lstStringRelevant.remove(".")
    strLst = list(str)
    count = 0
    for i in strLst:
        if i in lstStringRelevant:
            count += 1

    if count != 0:
        return True
    else:
        return False


def isNumericValue(str):
    lstStringDigit = list(string.digits)
    lstStringDigit.append('.')
    strLst = list(str)
    count = 0
    for i in strLst:
        if i not in lstStringDigit:
            count += 1
    if count != 0:
        return False
    else:
        return True


def lineIntersectionPt(m1, m2, b1, b2):
    xi = (b1 - b2) / (m2 - m1)
    yi = m1 * xi + b1
    return [xi, yi]


def slopeFinder(p1, p2):
    slopeValX, slopeValY = p2[0] - p1[0], p2[1] - p1[1]
    try:
        slopeVal = slopeValY / slopeValX
    except ZeroDivisionError:
        slopeVal = 0
    yIntercept = p1[1] - (slopeVal * p1[0])
    return slopeVal, yIntercept


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
    return val

def azimuthToBearing(azi_val):
    if 90 > azi_val > 0:
        bearing = azi_val
        dir_val = 2
    elif 180 > azi_val > 90:
        bearing = 180 - azi_val
        dir_val = 1
    elif 270 > azi_val > 180:
        bearing = azi_val - 180
        dir_val = 3
    else:
        bearing = 360 - azi_val
        dir_val = 4

    # if 90 > azi_val > 0:
    #     bearing = azi_val
    #     dir_val = 2
    # elif 180 > azi_val > 90:
    #     bearing = 180 - azi_val
    #     dir_val = 1
    # elif 270 > azi_val > 180:
    #     bearing = azi_val - 180
    #     dir_val = 3
    # else:
    #     bearing = 360 - azi_val
    #     dir_val = 4
    # bearing = abs(bearing - 90)


    return bearing, dir_val


def bearingToAzimuth(bearing, direction):
    pass


def checkOccurences(str, valuesLst):
    # ()
    rejectedLst = ['UT', 'KOP', 'IDENTIFICATION', 'Operator', 'Wellbore', 'HLD', 'County', 'Project', 'EOB',
                   "interpolated", "County", 'Project:', 'Reference:', 'NAD83', 'HLD',
                   "minimum", "database", "company", "reference", "Calculation", "Well", "Federal"]
    booVal = None
    valueCount = 0
    for j in rejectedLst:
        try:
            if j.lower() in str.lower():
                booVal = False
        except AttributeError:
            if j in str:
                booVal = False
    if booVal is not False:
        for i in valuesLst:
            try:
                if i.lower() in str.lower():
                    valueCount += 1
            except AttributeError:
                if i in str:
                    valueCount += 1
    if valueCount > 0:
        booVal = True
    if booVal is None:
        booVal = False
    return booVal


def oneToMany(lst, number):
    count = -1
    outLst = []
    for i in range(len(lst)):
        if i % number == 0:
            outLst.append([])
            count += 1
        outLst[count].append(lst[i])
    return outLst


def manyToOne(lst):
    return list(manyToOneParse(lst))


def manyToOneParse(lst):
    for item in lst:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in manyToOne(item):
                yield x
        else:
            yield item


def removeInvalidDegreesAzimuth(lst):
    newLst = []
    for i in range(len(lst)):
        if lst[i][1] < 110 and lst[i][2] < 366 and lst[i][0] < 30000:
            newLst.append(lst[i])
    return newLst


def removeDuplicatesMany(lst):
    emptyLst = []
    emptyLstFull = []
    for i in range(len(lst)):
        if lst[i][0] not in emptyLst:
            emptyLstFull.append(lst[i])
            emptyLst.append(lst[i][0])
    return emptyLstFull


def testPrint():
    print('foo')


# def tikaParser(file):
#     parsed_data_full = parser.from_file(file, xmlContent=True)
#     parsed_data_full = parsed_data_full['content']
#
#     parsedDataLst = TemplateDataGenerate.DataGenerateNoDepth(parsed_data_full)


#     pageDataLst = [[]]
#     pageCounter = 0
#     pagesLst = [0]
#     for i in range(len(parsedDataLst)):
#         # search for occurnces of the mentioned strings and replace them with an empty space
#         parsedDataLst[i] = parsedDataLst[i].replace('<div class="page"><p />', " ").replace('<p>', ' ').replace('</p>', ' ')
#
#         # add the datalist row to the relative list for that page
#         pageDataLst[pageCounter].append(parsedDataLst[i])
#
#         # create a new list(page) when the following occurs
#         if parsedDataLst[i] == "</div>" and parsedDataLst[i + 1] == '<div class="page"><p />':
#             pagesLst.append(pageCounter + 1)
#             pageCounter += 1
#             pageDataLst.append([])
#
#     return pageDataLst, pagesLst
#

def cluster(data, maxgap):
    '''Arrange data into groups where successive elements
       differ by no more than *maxgap*

        >>> cluster([1, 6, 9, 100, 102, 105, 109, 134, 139], maxgap=10)
        [[1, 6, 9], [100, 102, 105, 109], [134, 139]]

        >>> cluster([1, 6, 9, 99, 100, 102, 105, 134, 139, 141], maxgap=10)
        [[1, 6, 9], [99, 100, 102, 105], [134, 139, 141]]

    '''
    data.sort()
    groups = [[data[0]]]
    for x in data[1:]:
        if abs(x - groups[-1][-1]) <= maxgap:
            groups[-1].append(x)
        else:
            groups.append([x])
    return groups


def grouper(iterable, val):
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= val:

            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group

def grouper2(iterable, val):
    groups = []
    current_group = []
    for item in iterable:
        if current_group and item - current_group[-1] > val:
            groups.append(current_group)
            current_group = []
        current_group.append(item)
    if current_group:
        groups.append(current_group)
    return groups

def grouper3(iterable, val):
    groups = []
    current_group = []
    indices = []
    current_indices = []
    prev_item = None
    for i, item in enumerate(iterable):
        if prev_item is not None and item - prev_item > val:
        #if current_group and item - current_group[-1] > val:
            if current_group:
                    groups.append(current_group)
                    indices.append(current_indices)
            current_group = []
            current_indices = []
        current_group.append(item)
        current_indices.append(i)
        prev_item = item
    if current_group:
        groups.append(current_group)
        indices.append(current_indices)
    return groups, indices


# def grouper3(iterable, threshold):
#     group = []
#     indices = []
#     for i, item in enumerate(iterable):
#         if not group or item - group[-1] <= threshold:
#             group.append(item)
#             indices.append(i)
#         else:
#             yield group, indices
#             group = [item]
#             indices = [i]
#     if group:
#         yield group, indices



def polyfit(x, degree):
    y = list(range(len(x)))
    results = {}

    coeffs = np.polyfit(x, y, degree)

    # Polynomial Coefficients
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)  # or [p(z) for z in x]
    ybar = np.sum(y) / len(y)  # or sum(y)/len(y)
    ssreg = np.sum((yhat - ybar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot

    return results


def reTranslateData(i):
    conc_code_merged = i[:6]
    conc_code_merged[2] = translateNumberToDirection('township', str(conc_code_merged[2])).upper()
    conc_code_merged[4] = translateNumberToDirection('rng', str(conc_code_merged[4])).upper()
    conc_code_merged[5] = translateNumberToDirection('baseline', str(conc_code_merged[5])).upper()
    conc_code = [str(r) for r in conc_code_merged]
    len_lst = [len(r) for r in conc_code]
    if len_lst[0] == 1:
        conc_code[0] = "0" + str(int(float(conc_code[0])))
    if len_lst[1] == 1:
        conc_code[1] = "0" + str(int(float(conc_code[1])))
    if len_lst[3] == 1:
        conc_code[3] = "0" + str(int(float(conc_code[3])))
    conc_code = "".join([str(q) for q in conc_code])
    # return tsr_data, conc_code,
    return conc_code


def translateNumberToDirection(variable, val):
    if variable == 'rng':
        if val == '2':
            return 'W'
        elif val == '1':
            return 'E'
        else:
            return val
    elif variable == 'township':
        if val == '2':
            return 'S'
        elif val == '1':
            return 'N'
        else:
            return val
    elif variable == 'baseline':
        if val == '2':
            return 'U'
        elif val == '1':
            return 'S'
        else:
            return val
    elif variable == 'alignment':
        if val == '1':
            return 'SE'
        elif val == '2':
            return 'NE'
        elif val == '3':
            return 'SW'
        elif val == '4':
            return 'NW'
        else:
            return val


def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(e[2]))
    exception_list.extend(traceback.format_exception_only(e[0], e[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str


def polyfit2(x, y, degree):
    results = {}

    coeffs = np.polyfit(x, y, degree)

    # Polynomial Coefficients
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)  # or [p(z) for z in x]
    ybar = np.sum(y) / len(y)  # or sum(y)/len(y)
    ssreg = np.sum((yhat - ybar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot

    return results


def searcher(dir, text):
    for subdir, dirs, files in os.walk(r"C:\Google Drive"):
        #     if 'garry' in subdir:
        #         print('gar', subdir)
        for name in files:
            if text.lower() in name.lower():  # or '.mp4' in file or '.rm' in file:
                print(os.path.join(subdir, name))


def findSegmentLength(xy1, xy2):
    return np.sqrt((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2)


def matchAndRemergeLists(original_lst, new_lst, index):
    matched_lst = []
    for i in original_lst:
        if i[index] in new_lst:
            matched_lst.append(i)
    return matched_lst
