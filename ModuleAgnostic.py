import string
import re
from tika import parser
import numpy as np
import os
import re
import matplotlib.colors as mcolors
import random
import matplotlib.pyplot as plt
from itertools import chain
import statistics as st


# C:\Work\RewriteAPD>C:\Users\colto\AppData\Local\Programs\Python\Python37\Scripts\pyuic5.exe fileDialog.ui -o fileDialog.py
def writeFiles(cellLst, valuesLst, worksheet):
    for i in range(len(cellLst)):
        worksheet[cellLst[i]] = valuesLst[i]


def printLine(lst):
    # if len(lst) == 0:
    #     print("Print Failed - list length is zero")
    if len(lst) != 0:
        print()
        for i in range(len(lst)):
            print(i, "\t", lst[i])
        print()


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


def graphData(lst):
    colors = getColors()

    grouper_x, grouper_y = [], []
    for r in range(len(lst)):
        grouper_x.append([])
        grouper_y.append([])
        for s in range(len(lst[r])):
            x_data = st.mean([lst[r][s][0], lst[r][s][2]])
            y_data = st.mean([lst[r][s][1], lst[r][s][3]])
            grouper_x[r].append(x_data)
            grouper_y[r].append(y_data)
    colors_used = random.choices(colors, k=len(grouper_x))

    fig, ax = plt.subplots()

    all_x = list(chain.from_iterable(grouper_x))
    # plt.axhline(y=boundary, color='red', linestyle='--')
    for r in range(len(grouper_x)):
        plot_x, plot_y = grouper_x[r], grouper_y[r]
        print(plot_x)
        ax.scatter(plot_x, plot_y, c=colors_used[r])

        for s in range(len(grouper_x[r])):
            try:
                ax.text(plot_x[s], plot_y[s], lst[r][s][-1])
            except TypeError:
                pass
    plt.xlim([0, 650])
    plt.ylim([0, 900])
    plt.show()


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
    result = []
    for el in lst:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(manyToOne(el))
        else:
            result.append(el)
    return result


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


def findAntiCol(dataLst, pagesLst):
    colPages = []
    # transform each line into a string
    for i in range(len(dataLst)):
        dataLst[i] = [str(dataLst[i][j]) for j in range(len(dataLst[i]))]
    # search for occurences of 'anticollision' and mark which pages it occurs on
    for i in range(len(dataLst)):
        for j in range(len(dataLst[i])):
            reAntiCol = re.match(r"\b{}\b".format('anticollision'), dataLst[i][j], re.IGNORECASE)
            if reAntiCol is not None:
                colPages.append(i)
    # delete the pages containing anticollision
    for i in reversed(range(len(colPages))):
        dataLst[colPages[i]] = []
        # del pagesLst[colPages[i]]

    # convert all lines into lists
    for i in range(len(dataLst)):
        dataLst[i] = [dataLst[i][j].split(" ") for j in range(len(dataLst[i]))]

    return dataLst, pagesLst


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
    # for root, subdirectories, files in os.walk(r"F:"):
    #     for subdirectory in subdirectories:
    #         print(os.path.join(root, subdirectory))
    # for file in files:
    #     print(os.path.join(root, file))

    for subdir, dirs, files in os.walk(r"C:\Google Drive"):
        #     if 'garry' in subdir:
        #         print('gar', subdir)
        for name in files:
            if text.lower() in name.lower():  # or '.mp4' in file or '.rm' in file:
                print(os.path.join(subdir, name))


def findSegmentLength(xy1, xy2):
    return np.sqrt((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2)
