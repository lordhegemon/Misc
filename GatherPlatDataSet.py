import ModuleAgnostic
import ModuleAgnostic as ma
import math
import copy
import itertools
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
import ProcessBHLLocation


def drawGraphic(data, dir_lst):
    data_converted = sideDataToDecimalAzimuth(dir_lst, data)

    dir_lst_flatten = ma.manyToOne(dir_lst)
    # dir_lst_flatten = ma.manyToOne(dir_lst)
    # new_data = [i[7:12] for i in data]
    # new_data = [[float(j) for j in i] for i in new_data]
    # new_data = [[data[i][6]] + new_data[i] for i in range(len(new_data))]
    # data_converted = convertDirections(new_data, dir_lst_flatten)
    #
    coordLst = getCoordsLst(data_converted, [0.0, 0.0])
    eqLst, coordLst, cornersLst = linesMain(coordLst, dir_lst_flatten)
    return coordLst


def sideDataToDecimalAzimuth(dir_lst, data):
    dir_lst_flatten = ma.manyToOne(dir_lst)
    new_data = [i[7:12] for i in data]
    new_data = [[float(j) for j in i] for i in new_data]
    new_data = [[data[i][6]] + new_data[i] for i in range(len(new_data))]
    data_converted = convertDirections(new_data, dir_lst_flatten)
    return data_converted


def gatherValData(data, dir_lst):
    dir_lst_flatten = ma.manyToOne(dir_lst)
    new_data = [i[7:12] for i in data]
    new_data = [[float(j) for j in i] for i in new_data]
    new_data = [[data[i][6]] + new_data[i] for i in range(len(new_data))]
    data_converted = convertDirections(new_data, dir_lst_flatten)
    return dir_lst_flatten, new_data


def convertDirections(new_data, dir_lst):
    # dir_lst_flatten = ma.manyToOne(dir_lst)
    data_converted = []
    for i in range(len(dir_lst)):
        side, deg, min, sec, dir_val = new_data[i][1], new_data[i][2], new_data[i][3], new_data[i][4], new_data[i][5]
        if i > 8:
            if dir_val == 4 or dir_val == 1:
                decVal = 180 - (deg + min / 60 + sec / 3600)
            else:
                decVal = (deg + min / 60 + sec / 3600)
        else:
            if dir_val == 4 or dir_val == 1:
                decVal = 180 - (deg + min / 60 + sec / 3600)
            else:
                decVal = 180 + (deg + min / 60 + sec / 3600)
        data_converted.append([side, decVal])

    data_converted = [data_converted[12], data_converted[13], data_converted[14], data_converted[15],
                      data_converted[7], data_converted[6], data_converted[5], data_converted[4],
                      data_converted[11], data_converted[10], data_converted[9], data_converted[8],
                      data_converted[0], data_converted[1], data_converted[2], data_converted[3]]
    return data_converted


def getCoordsLst(valsLstMod, coord):
    coordLst = [[coord], [], [], []]
    yVals = [0.0]
    xVals = [0.0]
    for i in range(0, len(valsLstMod)):
        if i < 4:
            coord = equationSolveForEndPoint(valsLstMod[i][1], valsLstMod[i][0], coord)
            coordLst[0].append(coord)
            xVals.append(coord[0])
            yVals.append(coord[1])
        if 7 >= i >= 3:
            if i == 3:
                coordLst[1].append(coord[:])
            else:
                coord = equationSolveForEndPoint(valsLstMod[i][1], valsLstMod[i][0], coord)
                coordLst[1].append(coord)
            xVals.append(coord[0])
            yVals.append(coord[1])
        if 11 >= i >= 7:
            if i == 7:
                coordLst[2].append(coord[:])
            else:
                coord = equationSolveForEndPoint(valsLstMod[i][1], -valsLstMod[i][0], coord)
                coordLst[2].append(coord)
            xVals.append(coord[0])
            yVals.append(coord[1])

        if i >= 11:
            if i == 11:
                coordLst[3].append(coord[:])
            else:
                coord = equationSolveForEndPoint(valsLstMod[i][1], -valsLstMod[i][0], coord)
                coordLst[3].append(coord)
            xVals.append(coord[0])
            yVals.append(coord[1])
    coordLst1 = coordLst[:]

    return coordLst1


def offsetValsToPositive(xVals, yVals, coordLst):
    adjustX = min(xVals)
    adjustY = min(yVals)
    newCLst = copy.deepcopy(coordLst)

    if adjustX < 0:
        for i in range(len(newCLst)):
            for j in range(len(newCLst[i])):
                newCLst[i][j][0] = newCLst[i][j][0] + abs(adjustX)

    if adjustY < 0:
        for i in range(len(newCLst)):
            for j in range(len(newCLst[i])):
                newCLst[i][j][1] = newCLst[i][j][1] + abs(adjustY)

    return newCLst, abs(adjustX), abs(adjustY)


# solves for the connecting point at the end of the line
def equationSolveForEndPoint(alpha, h, coord):
    if alpha < 90:
        newAlph = 90 - alpha

    if 95 > alpha >= 90:
        newAlph = 90 - alpha

    if alpha >= 180:
        newAlph = 90 - (alpha - 180)

    if 175 < alpha < 180:
        newAlph = 90 - (alpha - 180)

    h = float(h)
    x = coord[0]
    y = coord[1]
    x2 = x + (h * math.cos(math.radians(newAlph)))
    y2 = y + (h * math.sin(math.radians(newAlph)))

    return [x2, y2]


def linesMain(coordLst, dirLst):
    newCoordLst = copy.deepcopy(coordLst)
    slopeLst = getSlope(coordLst)
    yIntLst = getYIntercept(coordLst, slopeLst)
    eqLst = [(slopeLst[i], yIntLst[i], dirLst[i]) for i in range(len(slopeLst))]
    coordLst1, cornersLst = connectAllCorners(slopeLst, yIntLst, coordLst)
    return eqLst, newCoordLst, cornersLst


def getYIntercept(coordLst, slopeLst):
    yIntLst = []
    count = 0
    for i in range(len(coordLst)):
        for j in range(len(coordLst[i]) - 1):
            x = coordLst[i][j][0]
            y = coordLst[i][j][1]
            m = slopeLst[count]

            yIntLst.append(y - (m * x))

            count += 1
    return yIntLst


def getSlope(coordLst):
    slopeLst1 = [[slopeFinder(i, j, coordLst) for j in range(len(coordLst[i]) - 1)] for i in range(len(coordLst))]
    slopeLst = [j for sub in slopeLst1 for j in sub]
    return slopeLst


def slopeFinder(i, j, coordLst):
    slopeValX = coordLst[i][j + 1][0] - coordLst[i][j][0]
    slopeValY = coordLst[i][j + 1][1] - coordLst[i][j][1]
    try:
        slopeVal = slopeValY / slopeValX
    except ZeroDivisionError:

        slopeVal = 0

    return slopeVal


def connectAllCorners(slopeLst, yIntLst, cLst):
    cnL = []
    # find the specific values for each corner and then create a sequential list of those coordinates
    corner11, corner12 = cLst[0][0], cLst[3][4]
    corner21, corner22 = cLst[0][4], cLst[1][0]
    corner31, corner32 = cLst[1][4], cLst[2][0]
    corner41, corner42 = cLst[2][4], cLst[3][0]
    cornersLst = [[corner11, corner12, 'SW'], [corner21, corner22, "SE"], [corner31, corner32, "NE"], [corner41, corner42, "NW"]]
    cnL.append([0, 0, 3, 4])
    cnL.append([0, 4, 1, 0])
    cnL.append([1, 4, 2, 0])
    cnL.append([2, 4, 3, 0])

    vals = [[0, 15], [3, 4], [7, 8], [11, 12]]
    sc = [[corner11, corner12], [corner21, corner22], [corner31, corner32], [corner41, corner42]]

    for i in range(4):
        # if the corner values are the same, ignore it
        if sc[i][0] == sc[i][1]:
            pass
        # if the corner values are not the same, find where the lines would intercept, and change the corners to that point
        else:
            # find the intercept between the two lines and change the value accordinly
            m1, m2 = slopeLst[vals[i][0]], slopeLst[vals[i][1]]
            y1, y2 = yIntLst[vals[i][0]], yIntLst[vals[i][1]]
            xy = getLineIntercept(m1, m2, y1, y2)
            for j in range(len(cLst)):
                for k in range(len(cLst[j])):
                    if cLst[j][k] == sc[i][0]:
                        cLst[j][k] = xy
                    if cLst[j][k] == sc[i][1]:
                        cLst[j][k] = xy
            cLst[cnL[i][0]][cnL[i][1]] = xy
            cLst[cnL[i][2]][cnL[i][3]] = xy

    corner11, corner12 = cLst[0][0], cLst[3][4]
    corner21, corner22 = cLst[0][4], cLst[1][0]
    corner31, corner32 = cLst[1][4], cLst[2][0]
    corner41, corner42 = cLst[2][4], cLst[3][0]
    cornersLst = [[corner11, corner12, 'SW'], [corner21, corner22, "SE"], [corner31, corner32, "NE"], [corner41, corner42, "NW"]]

    return cLst, cornersLst


# check for where the two lines intercept at
def getLineIntercept(m1, m2, b1, b2):
    if (m2 - m1) != 0:
        x = (b1 - b2) / (m2 - m1)
    else:
        x = (b1 - b2) / 1
    y = m1 * x + b1
    return [x, y]


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
    elif variable == 'township':
        if val == 'S':
            return '2'
        elif val == 'N':
            return '1'
    elif variable == 'baseline':
        if val == 'U':
            return '2'
        elif val == 'S':
            return '1'
    elif variable == 'alignment':
        if val == 'SE':
            return '1'
        elif val == 'NE':
            return '2'
        elif val == 'SW':
            return '3'
        elif val == 'NW':
            return '4'


def sectionsData(sections_all):
    new_lst = []
    for i in sections_all:
        new_lst.append([str(int(float(i[:2]))), str(int(float(i[2:4]))), i[4:5].replace("S", "2").replace("N", "1"), str(int(float(i[5:7]))), i[7:8].replace("W", '2').replace("E", '1'), i[8:].replace('U', '2').replace("S", "1")])
    return new_lst


def drawFullGraphic(wellPath, all_vals_lst, converted_plats, tsr_data, sections_lst):
    coordLst = converted_plats[0]
    dirLst = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    try:
        int(float(tsr_data[0][1]))
        quad_tsr = [int(float(tsr_data[0][1])), tsr_data[0][2], int(float(tsr_data[0][3])), tsr_data[0][4]]
    except ValueError:
        tsr_graphic = tsr_data[0][1].split()
        quad_tsr = [int(float(tsr_graphic[0])), tsr_graphic[1], int(float(tsr_graphic[2])), tsr_graphic[3]]
        # tsr_graphic = tsr_data[0][2].split()
    # quad_tsr = [int(float(tsr_data[0][1])), tsr_data[0][2], int(float(tsr_data[0][3])), tsr_data[0][4]]

    surfaceCoord, xMin, xMax, yMin, yMax = getQuad(converted_plats[0], quad_tsr)

    wellPath = getModifiedWellPath(surfaceCoord, wellPath)
    counter = 0
    valsLstTot = all_vals_lst[0]
    if len(coordLst) == 4:
        coordLst = list(itertools.chain.from_iterable(coordLst))
    allCoords = [coordLst]
    while len(wellPath) > 0:
        direction, wellPath = getDirections(xMin, xMax, yMin, yMax, wellPath)
        if direction == 'Null':
            return allCoords
        coordLst, all_vals_lst[counter] = getNewCoords(direction, coordLst, all_vals_lst, all_vals_lst[counter])
        xMin, xMax, yMin, yMax = getXMinMax(coordLst)
        valsLstTot.append(all_vals_lst[counter])
        allCoords.append(coordLst)
        counter += 1

    return allCoords


def getXMinMax(coordLst):
    xMinlst = [coordLst[i][0] for i in range(len(coordLst))]
    yMinlst = [coordLst[i][1] for i in range(len(coordLst))]
    xMin, xMax = min(xMinlst), max(xMinlst)
    yMin, yMax = min(yMinlst), max(yMinlst)
    return xMin, xMax, yMin, yMax


def getQuad(coordLst, surfaceLoc):
    count = 0
    for i in range(len(coordLst)):
        for j in range(len(coordLst[i])):
            count += 1
    vertDir, vertDirVal = surfaceLoc[0], surfaceLoc[1]
    horDir, horDirVal = surfaceLoc[2], surfaceLoc[3]
    if vertDirVal == 0:
        vertDirVal = 1
    if horDirVal == 0:
        horDirVal = 1
    quadVert, quadHor, lineVert, lineHor, lineVertOtherValues, lineHorOtherValues = defineEWNSSideID(vertDirVal, horDirVal, coordLst)

    yMin, yMax = min(lineHor), max(lineHor)
    xMin, xMax = min(lineVert), max(lineVert)

    vert, hor, adjPointsVert, adjPointsHor = findLineSegmentID(lineHor, lineVert, horDir, vertDir, horDirVal, vertDirVal, xMax, yMax, lineHorOtherValues, lineVertOtherValues)

    mX, bXNeg, bXPos = testSolvingStuffX(adjPointsHor, vertDir)
    mY, bYNeg, bYPos = testSolvingStuffY(adjPointsVert, horDir)

    surfaceCoord = findAllTheIntersectionsBetweenLines(mX, mY, bXNeg, bXPos, bYNeg, bYPos, vertDirVal, vertDir, horDirVal, horDir, lineHor, lineVert, coordLst)

    return surfaceCoord, xMin, xMax, yMin, yMax


def defineEWNSSideID(NSDirVal, EWDirVal, coordLst):
    if NSDirVal == "FSL":
        quadValNS = 0
        lineVert = coordLst[0][0][0], coordLst[0][1][0], coordLst[0][2][0], coordLst[0][3][0], coordLst[0][4][0]
        lineVertOtherValues = coordLst[0][0][1], coordLst[0][1][1], coordLst[0][2][1], coordLst[0][3][1], coordLst[0][4][1]
    else:
        quadValNS = 2
        lineVert = coordLst[2][0][0], coordLst[2][1][0], coordLst[2][2][0], coordLst[2][3][0], coordLst[2][4][0]
        lineVertOtherValues = coordLst[2][0][1], coordLst[2][1][1], coordLst[2][2][1], coordLst[2][3][1], coordLst[2][4][1]
    if EWDirVal == "FEL":
        quadValEW = 1
        lineHor = coordLst[1][0][1], coordLst[1][1][1], coordLst[1][2][1], coordLst[1][3][1], coordLst[1][4][1]
        lineHorOtherValues = coordLst[1][0][0], coordLst[1][1][0], coordLst[1][2][0], coordLst[1][3][0], coordLst[1][4][0]
    else:
        quadValEW = 3
        lineHor = coordLst[3][0][1], coordLst[3][1][1], coordLst[3][2][1], coordLst[3][3][1], coordLst[3][4][1]
        lineHorOtherValues = coordLst[3][0][0], coordLst[3][1][0], coordLst[3][2][0], coordLst[3][3][0], coordLst[3][4][0]
    return quadValNS, quadValEW, lineVert, lineHor, lineVertOtherValues, lineHorOtherValues


def find_proximalSegments(midPoint_coord_lst, quadVert, quadHor, s_loc):
    lst_x, lst_y = midPoint_coord_lst[quadHor], midPoint_coord_lst[quadVert]
    val_x, x_index = 100000, -1
    val_y, y_index = 100000, -1
    for i in range(len(lst_x)):

        val_x_solved = equationDistance(s_loc[0], lst_x[i][0], s_loc[1], lst_x[i][1])

        if val_x_solved < val_x:
            val_x = val_x_solved
            x_index = i

    for i in range(len(lst_y)):
        val_y_solved = equationDistance(s_loc[0], lst_y[i][0], s_loc[1], lst_y[i][1])
        if val_y_solved < val_y:
            val_y = val_y_solved
            y_index = i


def findLineSegmentID(lineVert, lineHor, x, y, horDirVal, vertDirVal, xMax, yMax, lineVertOtherValues, lineHorOtherValues):

    adjPointsVert = []
    adjPointsHor = []
    vert = -1
    hor = -1
    # each line for each side is divided up into 4 segments. Looking at mins and maxes determines which segment it is in.
    if vertDirVal == 'FNL':
        y = max(lineVert) - y
    if horDirVal == 'FEL':
        x = max(lineHor) - x

    lineVert2 = list(lineVert)
    lineVert2.append(y)
    if y < min(lineVert):
        y = min(lineVert) + 1
    if x < min(lineHor):
        x = min(lineHor) + 1

    for i in range(4):
        if lineHor[i] < x < lineHor[i + 1] or lineHor[i] > x > lineHor[i + 1]:
            if lineHor[i] != lineHor[i + 1]:
                adjPointsHor.append([lineHor[i], lineHorOtherValues[i]])
                adjPointsHor.append([lineHor[i + 1], lineHorOtherValues[i + 1]])
                hor = i


        if lineVert[i] <= y <= lineVert[i + 1] or lineVert[i] >= y >= lineVert[i + 1]:
            if lineVert[i] != lineVert[i + 1]:
                adjPointsVert.append([lineVertOtherValues[i], lineVert[i]])
                adjPointsVert.append([lineVertOtherValues[i + 1], lineVert[i + 1]])
                vert = i


    return vert, hor, adjPointsVert, adjPointsHor


def findLineSegmentID2(xSide, ySide, x, y, corner):
    lineX = [i[0] for i in xSide]
    lineXOtherValues = [i[1] for i in xSide]

    lineY = [i[1] for i in ySide]
    lineYOtherValues = [i[0] for i in ySide]

    adjPointsVert = []
    adjPointsHor = []
    xVal, yVal = -1, -1

    lineY2 = list(lineY)
    lineY2.append(y)
    lineY2 = sorted(lineY2)
    vertIndex = lineY2.index(y)
    outputY = [[lineYOtherValues[vertIndex - 1], lineY2[vertIndex - 1]], [lineYOtherValues[vertIndex], lineY2[vertIndex + 1]]]

    lineX2 = list(lineX)
    lineX2.append(x)
    lineX2 = sorted(lineX2)
    xIndex = lineX2.index(x)
    outputX = [[lineX2[xIndex - 1], lineXOtherValues[xIndex - 1]], [lineX2[xIndex + 1], lineXOtherValues[xIndex]]]

    return outputX, outputY


def testSolvingStuffX(lst, dirVal):
    m, b = slopeFinder2(lst[0], lst[1])
    inside = math.sqrt(dirVal ** 2 * (m ** 2 + 1))
    pos = b + inside
    neg = b - inside

    return m, neg, pos


def testSolvingStuffY(lst, dirVal):

    m, b = slopeFinder2(lst[0], lst[1])
    inside = math.sqrt(dirVal ** 2 * (m ** 2 + 1))
    pos = b + inside
    neg = b - inside
    return m, neg, pos


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


def findAllTheIntersectionsBetweenLines(mX, mY, bXNeg, bXPos, bYNeg, bYPos, vertDirVal, vertDir, horDirVal, horDir, lineHor, lineVert, coordLst):

    if mX == 0:
        pass
    elif mY == 0:
        ptsLst = verticalOrHorizontalDistanceSolver(mX, mY, bXNeg, bXPos, bYNeg, bYPos)
    else:
        pt1 = findIntersectionBetweenTwoLines(mX, bXNeg, mY, bYNeg)
        pt2 = findIntersectionBetweenTwoLines(mX, bXNeg, mY, bYPos)
        pt3 = findIntersectionBetweenTwoLines(mX, bXPos, mY, bYNeg)
        pt4 = findIntersectionBetweenTwoLines(mX, bXPos, mY, bYPos)
        ptsLst = [pt1, pt2, pt3, pt4]
    all_data = []
    for j in coordLst:
        for k in j:
            all_data.append(k)
    polygon = Polygon(all_data)
    for i in ptsLst:
        point = Point(i[0], i[1])
        if polygon.contains(point):
            return i
        # if min(lineHor) < i[0] < max(lineHor) and min(lineVert) < i[1] < max(lineVert):
        #     return i


def verticalOrHorizontalDistanceSolver(mX, mY, bXNeg, bXPos, bYNeg, bYPos):
    if mY == 0:
        x1 = bYNeg
        x2 = bYPos
        y1 = mX * bYNeg + bXNeg
        y2 = mX * bYPos + bXNeg
        y3 = mX * bYNeg + bXPos
        y4 = mX * bYPos + bXPos
        return [[x1, y1], [x2, y2], [x1, y3], [x2, y4]]


def getDirections(xMin, xMax, yMin, yMax, wellPath):
    minMaxLst = [False, False, False, False]
    NSBooLst = [False, False]
    EWBooLst = [False, False]
    vLst = []
    dirLst = []
    data_set = [[xMin, yMin], [xMin, yMax], [xMax, yMax], [xMax, yMin]]
    final_point = testTerminateWellpath(xMin, xMax, yMin, yMax, wellPath)
    if final_point == 'Null':
        return "Null", wellPath
    if final_point[0] > xMax:
        cut_index = wellPath.index(final_point)
        modWellPath = wellPath[cut_index:]
        return 'E', modWellPath
    elif final_point[0] < xMin:
        cut_index = wellPath.index(final_point)
        modWellPath = wellPath[cut_index:]
        return 'W', modWellPath

    elif final_point[1] > yMax:
        cut_index = wellPath.index(final_point)
        modWellPath = wellPath[cut_index:]
        return 'N', modWellPath
    elif final_point[1] < yMin:
        cut_index = wellPath.index(final_point)
        modWellPath = wellPath[cut_index:]
        return 'S', modWellPath
    return "Null", wellPath

    # for i in range(len(wellPath)):
    #
    #     # point = Point(wellPath[i][0], wellPath[i][1])
    #     # polygon = Polygon(data_set)
    #     # if polygon.contains(point):

    #     if wellPath[i][0] > xMax:
    #         minMaxLst[0] = True
    #         EWBooLst[0] = True
    #         vLst.append(i)
    #         dirLst.append('E')
    #
    #     elif wellPath[i][0] < xMin:
    #         minMaxLst[1] = True
    #         EWBooLst[1] = True
    #         vLst.append(i)
    #         dirLst.append('W')
    #
    #     if wellPath[i][1] > yMax:
    #         minMaxLst[2] = True
    #         NSBooLst[0] = True
    #         vLst.append(i)
    #         dirLst.append('N')
    #
    #     elif wellPath[i][1] < yMin:
    #         minMaxLst[3] = True
    #         NSBooLst[1] = True
    #         vLst.append(i)
    #         dirLst.append('S')
    # if True not in minMaxLst:
    #     return "Null", wellPath
    #
    # else:

    #     modWellPath = wellPath[vLst[0]:]
    #     return dirLst[0][0], modWellPath


def testTerminateWellpath(xMin, xMax, yMin, yMax, wellPath):
    data_set = [[xMin, yMin], [xMin, yMax], [xMax, yMax], [xMax, yMin]]
    while True:
        all_points = [Polygon(data_set).contains(Point(wellPath[i][0], wellPath[i][1])) for i in range(len(wellPath))]
        if False not in all_points:
            return 'Null'
        for i in range(len(wellPath)):
            point = Point(wellPath[i][0], wellPath[i][1])
            polygon = Polygon(data_set)
            if not polygon.contains(point):
                azimuth = np.arctan((wellPath[i][0] - wellPath[0][0]) / (wellPath[i][1] - wellPath[0][1]))

                return wellPath[i]


# def getDirection(xMin, xMax, yMin, yMax,wellPath):

#     minMaxLst = [False, False, False, False]
#     NSBooLst = [False, False]
#     EWBooLst = [False, False]
#     vLst = []
#     dirLst = []

#     for i in range(len(wellPath)):

#         if wellPath[i][0] > xMax:
#             minMaxLst[0] = True
#             EWBooLst[0] = True
#             vLst.append(i)
#             dirLst.append('E')
#
#         elif wellPath[i][0] < xMin:
#             minMaxLst[1] = True
#             EWBooLst[1] = True
#             vLst.append(i)
#             dirLst.append('W')
#
#         if wellPath[i][1] > yMax:
#             minMaxLst[2] = True
#             NSBooLst[0] = True
#             vLst.append(i)
#             dirLst.append('N')
#
#         elif wellPath[i][1] < yMin:
#             minMaxLst[3] = True
#             NSBooLst[1] = True
#             vLst.append(i)
#             dirLst.append('S')
#
#     if True not in minMaxLst:
#         return "Null", wellPath
#
#     else:
#         modWellPath = wellPath[vLst[0]:]
#         return dirLst[0][0], modWellPath
def getModifiedWellPath(bhlCoord, wellPath):
    for i in range(len(wellPath)):
        wellPath[i][0], wellPath[i][1] = wellPath[i][0] + bhlCoord[0], wellPath[i][1] + bhlCoord[1]

    return wellPath


def findIntersectionBetweenTwoLines(m1, a, m2, b):
    x = (a - b) / (m2 - m1)
    y = ((a * m2) - (b * m1)) / (m2 - m1)
    return x, y


def getNewCoords(direction, coordLst, valsLstTot, valsLst):
    coords = [0] * 20
    if direction == "E":
        coords, valsLst = directionE(coords, coordLst, valsLst, valsLstTot)
        return coords, valsLst
    elif direction == 'W':
        coords, valsLst = directionW(coords, coordLst, valsLst, valsLstTot)
        return coords, valsLst
    elif direction == 'S':
        coords, valsLst = directionS(coords, coordLst, valsLst, valsLstTot)
        return coords, valsLst
    elif direction == 'N':
        coords, valsLst = directionN(coords, coordLst, valsLst, valsLstTot)
        return coords, valsLst


def directionE(coords, coordLst, valsLst, valsLstTot):
    lineS = [valsLst[0], valsLst[1], valsLst[2], valsLst[3]]
    lineN = [valsLst[11], valsLst[10], valsLst[9], valsLst[8]]
    lineE = [valsLst[7], valsLst[6], valsLst[5], valsLst[4]]
    lineW = [valsLst[12], valsLst[13], valsLst[14], valsLst[15]]
    oldLineE = [valsLstTot[-1][7], valsLstTot[-1][6], valsLstTot[-1][5], valsLstTot[-1][4]]

    if len(coordLst) == 4:
        coordLst = list(itertools.chain.from_iterable(coordLst))

    coords[0] = coordLst[4]

    for i in range(6):
        coords[14 + i] = coordLst[10 - i]

    # coords = unevenSideChecker(oldLineE, lineW, coords, 'E')

    for i in range(4):
        coords[i + 1] = list(intersectCircleAndLine(coords[i][0], coords[i][1], lineS[i][1], lineS[i][0], 'E'))
        coords[13 - i] = list(intersectCircleAndLine(coords[14 - i][0], coords[14 - i][1], lineN[i][1], lineN[i][0], 'E'))

    coords[9] = coords[10]
    coords[5] = coords[4]

    for i in range(3):
        coords[8 - i] = list(intersectCircleAndLine(coords[9 - i][0], coords[9 - i][1], lineE[i][1], lineE[i][0], 'S'))

    return coords, valsLst


def directionW(coords, coordLst, valsLst, valsLstTot):
    lineS = [valsLst[0], valsLst[1], valsLst[2], valsLst[3]]
    lineN = [valsLst[11], valsLst[10], valsLst[9], valsLst[8]]
    lineE = [valsLst[7], valsLst[6], valsLst[5], valsLst[4]]
    lineW = [valsLst[12], valsLst[13], valsLst[14], valsLst[15]]
    oldLineW = [valsLstTot[-1][12], valsLstTot[-1][13], valsLstTot[-1][14], valsLstTot[-1][15]]

    if len(coordLst) == 4:
        coordLst = list(itertools.chain.from_iterable(coordLst))

    coords[4] = coordLst[0]

    for i in range(6):
        coords[5 + i] = coordLst[19 - i]

    # coords = unevenSideChecker(oldLineW, lineE, coords, 'W')

    for i in range(4):
        coords[3 - i] = list(intersectCircleAndLine(coords[4 - i][0], coords[4 - i][1], lineS[3 - i][1], lineS[3 - i][0], 'W'))

    for i in range(4):
        coords[11 + i] = list(intersectCircleAndLine(coords[10 + i][0], coords[10 + i][1], lineN[3 - i][1], lineN[3 - i][0], 'W'))

    coords[15] = coords[14]
    coords[19] = coords[0]
    for i in range(3):
        coords[18 - i] = list(intersectCircleAndLine(coords[19 - i][0], coords[19 - i][1], lineW[3 - i][1], lineW[3 - i][0], 'N'))

    return coords, valsLst


def directionS(coords, coordLst, valsLst, valsLstTot):
    lineS = [valsLst[0], valsLst[1], valsLst[2], valsLst[3]]
    lineN = [valsLst[11], valsLst[10], valsLst[9], valsLst[8]]
    lineE = [valsLst[7], valsLst[6], valsLst[5], valsLst[4]]
    lineW = [valsLst[12], valsLst[13], valsLst[14], valsLst[15]]
    oldLineS = [valsLstTot[-1][0], valsLstTot[-1][1], valsLstTot[-1][2], valsLstTot[-1][3]]

    if len(coordLst) == 4:
        coordLst = list(itertools.chain.from_iterable(coordLst))

    coords[15] = coordLst[19]
    for i in range(6):
        coords[14 - i] = coordLst[i]

    # coords = unevenSideChecker(oldLineS, lineN, coords, 'S')

    for i in range(4):
        coords[8 - i] = list(intersectCircleAndLine(coords[9 - i][0], coords[9 - i][1], lineE[i][1], lineE[i][0], 'S'))

    for i in range(4):
        coords[16 + i] = list(intersectCircleAndLine(coords[15 + i][0], coords[15 + i][1], lineW[i][1], lineW[i][0], 'S'))

    coords[0] = coords[19]
    coords[4] = coords[5]

    for i in range(3):
        try:
            coords[1 + i] = list(intersectCircleAndLine(coords[0 + i][0], coords[0 + i][1], lineS[i][1], lineS[i][0], 'E'))
        except TypeError:
            coords[1 + i] = coords[i]

    return coords, valsLst


def directionN(coords, coordLst, valsLst, valsLstTot):
    lineS = [valsLst[0], valsLst[1], valsLst[2], valsLst[3]]
    lineN = [valsLst[11], valsLst[10], valsLst[9], valsLst[8]]
    lineE = [valsLst[7], valsLst[6], valsLst[5], valsLst[4]]
    lineW = [valsLst[12], valsLst[13], valsLst[14], valsLst[15]]
    oldLineN = [valsLstTot[-1][11], valsLstTot[-1][10], valsLstTot[-1][9], valsLstTot[-1][8]]

    if len(coordLst) == 4:
        coordLst = list(itertools.chain.from_iterable(coordLst))

    coords[19] = coordLst[15]

    for i in range(6):
        coords[i] = coordLst[14 - i]

    for i in range(4):
        coords[6 + i] = list(intersectCircleAndLine(coords[5 + i][0], coords[5 + i][1], lineE[3 - i][1], lineE[3 - i][0], 'N'))

    for i in range(4):
        coords[18 - i] = list(intersectCircleAndLine(coords[19 - i][0], coords[19 - i][1], lineW[3 - i][1], lineW[3 - i][0], 'N'))

    coords[14] = coords[15]
    coords[10] = coords[9]

    for i in range(3):
        coords[11 + i] = list(intersectCircleAndLine(coords[10 + i][0], coords[10 + i][1], lineN[3 - i][1], lineN[3 - i][0], 'W'))

    return coords, valsLst


def intersectCircleAndLine(a, b, mr, r, dir):
    if mr == 0 or mr == 180 or mr == 90 and r == 0:
        return a, b

    if mr < 90:
        m = math.tan(math.radians(90 - mr))
    if 95 > mr >= 90:
        m = math.tan(math.radians(90 - mr))
    if mr >= 180:
        m = math.tan(math.radians(90 - (mr - 180)))
    if 180 > mr > 175:
        m = math.tan(math.radians(90 - (mr - 180)))

    d = b - (m * a)
    den = (1 + m ** 2)
    ang = (r ** 2 * den) - (b - m * a - d) ** 2
    sqAng = math.sqrt(ang)
    x1 = (a + b * m - d * m + sqAng) / den
    x2 = (a + b * m - d * m - sqAng) / den

    y1 = (d + (a * m) + (b * m ** 2) + (m * sqAng)) / den
    y2 = (d + (a * m) + (b * m ** 2) - (m * sqAng)) / den

    if dir == 'E':
        if x1 > a:
            return [x1, y1]
        elif x2 > a:
            return [x2, y2]

    elif dir == 'W':
        if a > x1:
            return [x1, y1]
        elif a > x2:
            return [x2, y2]

    elif dir == 'S':
        if y1 < b:
            return [x1, y1]
        elif y2 < b:
            return [x2, y2]

    elif dir == 'N':
        if y1 > b:
            return [x1, y1]
        elif y2 > b:
            return [x2, y2]


def getBHLMain(data_coords, bhlCoord):
    ix, iy = bhlCoord[0], bhlCoord[1]
    prox_lst = ProcessBHLLocation.findCorrectSide(data_coords[0], data_coords[1], data_coords[2], data_coords[3], [ix, iy])
    n_index, e_index = prox_lst[0][0], prox_lst[0][1]
    n_adjacent_values, e_adjacent_values = data_coords[n_index], data_coords[e_index]
    NS_vals, EW_vals = ProcessBHLLocation.determineValuesBetween(n_adjacent_values, e_adjacent_values, [ix, iy])
    x1_NS, y1_NS = [p[0] for p in NS_vals], [p[1] for p in NS_vals]
    x1_EW, y1_EW = [p[0] for p in EW_vals], [p[1] for p in EW_vals]
    m_NS1, b_NS1, m_EW1, b_EW1 = ProcessBHLLocation.generateLineEq(NS_vals, EW_vals, [ix, iy])  # GENERATE THE MX+B EQUATIONS FOR EACH POINTS
    b_NS2, b_EW2 = ProcessBHLLocation.getParallelLineParameter([ix, iy], m_NS1, m_EW1)
    NS_distance = round(ProcessBHLLocation.parallelLineDistance(b_NS1, b_NS2, m_NS1), 0)
    EW_distance = round(ProcessBHLLocation.parallelLineDistance(b_EW1, b_EW2, m_EW1), 0)
    ns_angle, ew_angle = np.rad2deg(np.arctan2(1, m_NS1)), np.rad2deg(np.arctan2(1, m_EW1))
    ns_angle, ew_angle = ProcessBHLLocation.returnAlteredAngle(ns_angle, ew_angle, n_index, e_index)
    xNS, yNS = ProcessBHLLocation.findPointMatchParallel(ix, iy, NS_distance, ns_angle)
    xEW, yEW = ProcessBHLLocation.findPointMatchParallel(ix, iy, EW_distance, ew_angle)
    x1_ns, y1_ns, x1_ew, y1_ew = [xNS, ix], [yNS, iy], [xEW, ix], [yEW, iy]
    mp_ns, mp_ew = [(xNS + ix) / 2, (yNS + iy) / 2], [(xEW + ix) / 2, (yEW + iy) / 2]


def getBHL(coord, bhlCoord):
    coord = [list(i) for i in coord]
    if len(coord) < 10:
        coord = list(itertools.chain.from_iterable(coord))

    coordLst = [[coord[0], coord[1], coord[2], coord[3], coord[4]],
                [coord[5], coord[6], coord[7], coord[8], coord[9]],
                [coord[10], coord[11], coord[12], coord[13], coord[14]],
                [coord[15], coord[16], coord[17], coord[18], coord[19]]]
    midPoint_coord_lst = [[[(coordLst[i][0][0] + coordLst[i][1][0]) / 2, (coordLst[i][0][1] + coordLst[i][1][1]) / 2] for j in range(len(coordLst[i]))] for i in range(len(coordLst))]

    # for ?
    # for i in range(len(coordLst)):
    #     for j in range(len(coordLst[i])):
    #         new_pt = [(coordLst[i][0][0] + coordLst[i][1][0])/2, (coordLst[i][0][1] + coordLst[i][1][1])/2]

    NLineDist = [coord[10][0], coord[11][0], coord[12][0], coord[13][0], coord[14][0]]
    NLineDistOther = [coord[10][1], coord[11][1], coord[12][1], coord[13][1], coord[14][1]]
    NLst = [coord[10], coord[11], coord[12], coord[13], coord[14]]

    SLineDist = [coord[0][0], coord[1][0], coord[2][0], coord[3][0], coord[4][0]]
    SLineDistOther = [coord[0][1], coord[1][1], coord[2][1], coord[3][1], coord[4][1]]
    SLst = [coord[0], coord[1], coord[2], coord[3], coord[4]]

    ELineDist = [coord[5][1], coord[6][1], coord[7][1], coord[8][1], coord[9][1]]
    ELineDistOther = [coord[5][0], coord[6][0], coord[7][0], coord[8][0], coord[9][0]]
    ELst = [coord[5], coord[6], coord[7], coord[8], coord[9]]

    WLineDist = [coord[15][1], coord[16][1], coord[17][1], coord[18][1], coord[19][1]]
    WLineDistOther = [coord[15][0], coord[16][0], coord[17][0], coord[18][0], coord[19][0]]
    WLst = [coord[15], coord[16], coord[17], coord[18], coord[19]]

    corners = SLst[-1], ELst[-1], NLst[-1], WLst[-1]

    # alignValNS/EW references if the closest line is to the E/W and N/S
    # the pt values reference which point is closest
    alignValNS, pt1 = getDistanceToPoints(NLst, SLst, bhlCoord[0], bhlCoord[1])
    alignValEW, pt2 = getDistanceToPoints(ELst, WLst, bhlCoord[0], bhlCoord[1])

    # NSLst, EWLst refer to which NLineDist/SLinedist, etc are being used
    # NSALign, EWAlign are indexes for which of the multidimensional lists to use

    # NSLst, EWLst, NSAlign, EWAlign, NSLstFull, EWLstFull = determineAlignmentLst(alignValNS, alignValEW, NLineDist, SLineDist, ELineDist, WLineDist, NLineDistOther, SLineDistOther, ELineDistOther,
    #                                                                              WLineDistOther)
    # EW2, NS2 = findClosestVal(NSLst, EWLst, bhlCoord[0], bhlCoord[1], alignValNS, alignValEW, NSLstFull, EWLstFull)

    # NSDir, EWDir, equationIDNS, equationIDEW = getEWDir(NSAlign, EWAlign, EW2, NS2)
    closestCorner, minIndex = findTheClosestCorner(corners, bhlCoord)
    xSide, ySide = returnTheRelativeLineSegmentsToTheCorner(minIndex, coord)

    xVal, yVal = findLineSegmentID2(xSide, ySide, bhlCoord[0], bhlCoord[1], closestCorner)

    mX, bX = slopeFinder2(xVal[0], xVal[1])
    mY, bY = slopeFinder2(yVal[0], yVal[1])
    mxBHL = bhlCoord[1] - (mX * bhlCoord[0])
    myBHL = bhlCoord[1] - (mY * bhlCoord[0])

    xDistance = parallelLineDistance(bX, xBHL, mX)
    yDistance = parallelLineDistance(bY, yBHL, mY)


    # abX, acX, bcX = findAllThreeSides(xVal, bhlCoord)
    # areaX = findTriangleArea(xVal[0], xVal[1], bhlCoord)
    # heightX = findTriangleAltitudeGivenAreaAndLengths(areaX, abX)
    #
    # abY, acY, bcY = findAllThreeSides(yVal, bhlCoord)
    # areaY = findTriangleArea(yVal[0], yVal[1], bhlCoord)
    # heightY = findTriangleAltitudeGivenAreaAndLengths(areaY, abY)
    #
    # return abs(heightX), abs(heightY), NSDir, EWDir


def parallelLineDistance(b2, b1, a2):
    top = abs(b2 - b1)
    bottom = math.sqrt(a2 ** 2 + 1)
    d = top / bottom
    return d


def findTheClosestCorner(cornersLst, bhl):
    minIndex = 99999999999
    minRange = 99999999999
    for i in range(4):
        output = equationDistance(bhl[0], bhl[1], cornersLst[i][0], cornersLst[i][1])
        if output < minRange:
            minRange = output
            minIndex = i

    return cornersLst[minIndex], minIndex


def returnTheRelativeLineSegmentsToTheCorner(val, coord):
    xSide = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    ySide = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

    if val == 0:
        xSide = [coord[0], coord[1], coord[2], coord[3], coord[4]]
        ySide = [coord[5], coord[6], coord[7], coord[8], coord[9]]
    elif val == 1:
        xSide = [coord[10], coord[11], coord[12], coord[13], coord[14]]
        ySide = [coord[5], coord[6], coord[7], coord[8], coord[9]]
    elif val == 2:
        xSide = [coord[10], coord[11], coord[12], coord[13], coord[14]]
        ySide = [coord[15], coord[16], coord[17], coord[18], coord[19]]
    elif val == 3:
        xSide = [coord[0], coord[1], coord[2], coord[3], coord[4]]
        ySide = [coord[15], coord[16], coord[17], coord[18], coord[19]]

    return xSide, ySide


def getEWDir(NSAlign, EWAlign, NS2, EW2):
    NSDir = ""
    EWDir = ""
    if NSAlign == 0:
        equationIDNS = 0 + NS2
        NSDir = 'FSL'
    elif NSAlign == 2:
        equationIDNS = 8 + NS2
        NSDir = 'FNL'
    if EWAlign == 1:
        equationIDEW = 4 + EW2
        EWDir = 'FEL'
    elif EWAlign == 3:
        equationIDEW = 12 + EW2
        EWDir = 'FWL'
    return NSDir, EWDir, equationIDNS, equationIDEW


def getDistanceToPoints(line1, line2, x, y):
    dist1Lst = [equationDistance(x, i[0], y, i[1]) for i in line1]
    dist2Lst = [equationDistance(x, i[0], y, i[1]) for i in line2]

    indexMin1 = min(range(len(dist1Lst)), key=dist1Lst.__getitem__)
    indexMin2 = min(range(len(dist2Lst)), key=dist2Lst.__getitem__)

    if min(dist1Lst) < min(dist2Lst):
        return 1, line1[indexMin1]
    else:
        return 2, line2[indexMin2]


def equationDistance(x1, x2, y1, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def findClosestVal(lineVert, lineHor, x, y, alignValNS, alignValEW, lineVertOther, lineHorOther):
    lineVert, lineHor = [i for i in lineVert], [i for i in lineHor]
    yMin, yMax = min(lineHor), max(lineHor)
    xMin, xMax = min(lineVert), max(lineVert)
    vert, hor, adjPointsVert, adjPointsHor = findLineSegmentID(lineHor, lineVert, x, y, alignValNS, alignValEW, xMax, yMax, lineHorOther, lineVertOther)

    return vert, hor


def determineAlignmentLst(alignValNS, alignValEW, NLineDist, SLineDist, ELineDist, WLineDist, NLineDistOther, SLineDistOther, ELineDistOther, WLineDistOther):
    if alignValNS == 1:
        NSAlign = 2
        NSLst = NLineDist
        NSLstFull = NLineDistOther
    else:
        NSAlign = 0
        NSLst = SLineDist
        NSLstFull = SLineDistOther
    if alignValEW == 1:
        EWAlign = 1
        EWLst = ELineDist
        EWLstFull = ELineDistOther
    else:
        EWAlign = 3
        EWLst = WLineDist
        EWLstFull = WLineDistOther

    return NSLst, EWLst, NSAlign, EWAlign, NSLstFull, EWLstFull
