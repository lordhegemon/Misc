import utm
from ast import literal_eval
import string
import re
from tika import parser
import numpy as np
import os
import re
import matplotlib.colors as mcolors
from collections import Iterable
from glob import glob
from functools import reduce
import operator
import math
import inspect
# import ModuleAgnostic as ma

import math
import os
import numpy as np
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
    print('FUNCTION:', calframe[1][3])


def printLine(lst):
    if len(lst) != 0:
        print()
        for i in range(len(lst)):
            print(i, "\t", lst[i])
        print()


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
        if lst1[i] == lst2[i]:
            match_boos.append(True)
        else:
            match_boos.append(False)
    if False in match_boos:
        return False
    else:
        return True


def convertDecimalToDegrees(dd):
    mnt, sec = divmod(dd * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return int(deg), int(mnt), round(sec, 2)


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

    # plt.figure(0)
    # fig, ax = plt.subplots()
    # for i in sections_relative_data_all:
    x1, y1 = [k[0] for k in data_lengths], [k[1] for k in data_lengths]
    text = [k[2] for k in data_lengths]
    # for i in range(len(data_lengths)):
    #     plt.text(x1[i], y1[i], round(text[i], 2))
    # x2, y2 = [k[0] for k in data_lengths], [k[1] for k in data_lengths]
    # x3, y3 = [k[0] for k in east_side], [k[1] for k in east_side]
    # x4, y4 = [k[0] for k in south_side], [k[1] for k in south_side]
    # #     ax.plot(x1, y1, c='black')
    # ax.plot(x1, y1, c='black')
    # plt.scatter(x1, y1, c='red')
    # ax.plot(x2, y2, c='red')
    # ax.plot(x3, y3, c='blue')
    # ax.plot(x4, y4, c='yellow')
    # ax.scatter([corners[0][0]], [corners[0][1]], c='black')
    # ax.scatter([corners[1][0]], [corners[1][1]], c='red')
    # ax.scatter([corners[2][0]], [corners[2][1]], c='blue')
    # ax.scatter([corners[3][0]], [corners[3][1]], c='yellow')
    # plt.show()

    east_side = arrangeDirectionData(corners, data_lengths, 'east', centroid)
    north_side = arrangeDirectionData(corners, data_lengths, 'north', centroid)
    west_side = arrangeDirectionData(corners, data_lengths, 'west', centroid)
    south_side = arrangeDirectionData(corners, data_lengths, 'south', centroid)
    # all_data = west_side[1:] + north_side[1:] + east_side[1:] + south_side[1:]
    all_data = [west_side] + [north_side] + [east_side] + [south_side]

    # for i in west_side:
    #     if i not in all_data:
    #         all_data.append(i)
    #
    # for i in north_side:
    #     if i not in all_data:
    #         all_data.append(i)
    #
    # for i in east_side:
    #     if i not in all_data:
    #         all_data.append(i)
    #
    # for i in south_side:
    #     if i not in all_data:
    #         all_data.append(i)
    return corners, all_data


def reorganizeLstPointsWithAngle(lst, centroid):

    # lst_arrange = [i + [math.atan2(i[1] - centroid[1], i[0] - centroid[0])] for i in lst]
    lst_arrange = [i + [(math.degrees(math.atan2(centroid[1] - i[1], centroid[0] - i[0])) + 360) % 360] for i in lst]
    # degrees = [(math.degrees(math.atan2(i[1] - centroid[1], i[0] - centroid[0])) + 360) % 360 for i in lst]

    # radians = [math.atan2(i[1] - centroid[1], i[0] - centroid[0]) - math.pi/2 for i in lst]


    # lst_arrange = [i + [math.atan2(centroid[1] - i[1], centroid[0] - (i[0]) + (3 * math.pi)/2)] for i in lst]
    return lst_arrange


# def arrangeDirectionData(corner, lst, label, centroid):
#     found_data_theoretical_pts = []
#     found_side_data = []
#     new_sides = []
#     angle_lst = [i[-1] for i in lst]
#     if label == 'west':
#         xy1, xy2 = corner[0], corner[3]
#     if label == 'north':
#         xy1, xy2 = corner[3], corner[2]
#     if label == 'east':
#         xy1, xy2 = corner[2], corner[1]
#     if label == 'south':
#         xy1, xy2 = corner[1], corner[0]
#     angles = [xy1[-1], xy2[-1]]
#     found_side_data.append(xy1)
#
#     for i in lst:
#         # if label == 'west':
#         if angles[0] < angles[1]:
#             # if i[1] > max(angles) or min(angles) > i[-1]:
#             if 360 > i[-1] > max(angles) or min(angles) > i[-1] > 0:
#                 found_side_data.append(i)
#         else:
#             if max(angles) > i[-1] > min(angles):
#                 found_side_data.append(i)
#
#     found_side_data.append(xy2)
#     if angles[0] < angles[1]:
#         # fig, ax = plt.subplots()
#         north_side = [i for i in found_side_data if i[-1] > 270]
#         north_side = sorted(north_side, key=lambda r: r[-1])
#         south_side = [i for i in found_side_data if 90 > i[-1]]
#         south_side = sorted(south_side, key=lambda r: r[-1])
#         found_side_data = north_side + south_side
#         found_side_data = found_side_data[::-1]
#
#
#         # output = sorted(found_side_data, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, centroid))[::-1]))) % 360)
#
#         # found_side_data = reorganizeLstPointsWithAngle(found_side_data, centroid)
#
#
#
#         # x4, y4 = [k[0] for k in found_side_data], [k[1] for k in found_side_data]
#         # for i in range(len(found_side_data)):
#         #     ax.text(x4[i], y4[i], found_side_data[i][-1])
#         # ax.plot(x4, y4, c='red')
#         # ax.scatter(x4, y4, c='red')
#         # plt.show()
#     return found_side_data

def arrangeDirectionData(corner, lst, label, centroid):
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
    return found_side_data


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
            distance = findSegmentLength(i, j)
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
            print([lst[i]])
            pass
    return lst

    # return [list(i) for i in lst if isinstance(i, set)]


def parseAllFoldersForString(new_path, searcher_var):
    files = glob(new_path + '/**/', recursive=True)
    for i in files:
        for j in os.listdir(i):
            if searcher_var in j:
                print(j)


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

def slopeFinder2(p1, p2):
    slopeValX = p2[0] - p1[0]
    slopeValY = p2[1] - p1[1]
    try:
        slopeVal = slopeValY / slopeValX
    except ZeroDivisionError:
        slopeVal = 0
    yIntercept = p1[1] - (slopeVal * p1[0])
    return slopeVal, yIntercept
    return slopeVal


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

    # print('val', bearing, dir_val)

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
    # result = []
    # for el in lst:
    #     if hasattr(el, "__iter__") and not isinstance(el, str):
    #         result.extend(manyToOne(el))
    #     else:
    #         result.append(el)
    # return result


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


def tikaParser(file):
    parsed_data_full = parser.from_file(file, xmlContent=True)
    parsed_data_full = parsed_data_full['content']

    parsedDataLst = TemplateDataGenerate.DataGenerateNoDepth(parsed_data_full)


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
