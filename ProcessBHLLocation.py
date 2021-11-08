import openpyxl
import ModuleAgnostic
import copy
import re
import itertools
import sqlite3
import pandas as pd
import numpy as np
import math
import operator
import statistics
import matplotlib.pyplot as plt
import numpy as np
from geopy import distance
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# easting - left to right 500,000
# northing - up to down, 4,500,000

def findOtherBHL(side_data, bhl):

    side_data = ModuleAgnostic.oneToMany(side_data, 5)
    bhl_poss_lst = findCorrectSide(side_data[0], side_data[1], side_data[2], side_data[3], bhl)

    y_index, x_index = bhl_poss_lst[0][0], bhl_poss_lst[0][1]
    y_adjacent_values, x_adjacent_values = side_data[y_index], side_data[x_index]

    NS_vals, EW_vals = determineValuesBetween(y_adjacent_values, x_adjacent_values, bhl)  # find which values does the bhl lie between (bounded)

    m_NS1, b_NS1, m_EW1, b_EW1 = generateLineEq(NS_vals, EW_vals, bhl)  # GENERATE THE MX+B EQUATIONS FOR EACH POINTS
    b_NS2, b_EW2 = getParallelLineParameter(bhl, m_NS1, m_EW1)  # solve for y intercepts of parallel lines
    nearestPointDistance(1, m_NS1, b_NS1, bhl[0], bhl[1])
    nearestPointDistance(1, m_EW1, b_EW1, bhl[0], bhl[1])
    NS_distance = round(parallelLineDistance(b_NS1, b_NS2, m_NS1), 0)
    EW_distance = round(parallelLineDistance(b_EW1, b_EW2, m_EW1), 0)
    bhl_coords = [NS_distance, translateSide(y_index), EW_distance, translateSide(x_index)]
    return bhl_coords

def translateSide(data_pt):
    if data_pt == 0:
        return 'FSL'
    elif data_pt == 1:
        return 'FEL'
    elif data_pt == 2:
        return 'FNL'
    elif data_pt == 3:

        return 'FWL'
def findBHLLocation(side_data, bhl):
    bhl_poss_lst = findCorrectSide(side_data[0], side_data[1], side_data[2], side_data[3], bhl)
    northing_index, easting_index = bhl_poss_lst[0][0], bhl_poss_lst[0][1]
    northing_adjacent_values, easting_adjacent_values = side_data[northing_index], side_data[easting_index]

    NS_vals, EW_vals = determineValuesBetween(northing_adjacent_values, easting_adjacent_values, bhl)  # find which values does the bhl lie between (bounded)
    m_NS1, b_NS1, m_EW1, b_EW1 = generateLineEq(NS_vals, EW_vals, bhl)  # GENERATE THE MX+B EQUATIONS FOR EACH POINTS
    b_NS2, b_EW2 = getParallelLineParameter(bhl, m_NS1, m_EW1)  # solve for y intercepts of parallel lines
    nearestPointDistance(1, m_NS1, b_NS1, bhl[0], bhl[1])
    nearestPointDistance(1, m_EW1, b_EW1, bhl[0], bhl[1])
    NS_distance = round(parallelLineDistance(b_NS1, b_NS2, m_NS1) * 3.2808399, 0)
    EW_distance = round(parallelLineDistance(b_EW1, b_EW2, m_EW1) * 3.2808399, 0)

    return NS_distance, EW_distance, side_data, northing_index, easting_index


def determineIfInside(shl, data):
    point = Point(shl[0], shl[1])
    polygon = Polygon(data)

    return polygon.contains(point)


def determineValuesBetween(lstNS_o, lstEW_o, val):
    lstNS, northing_val = [i[0] for i in lstNS_o], val[0]  # get the northing val as well as the list for northing values
    lstEW, easting_val = [i[1] for i in lstEW_o], val[1]
    diff_lst_NS, diff_lst_EW = [i - northing_val for i in lstNS], [i - easting_val for i in lstEW]
    pos_NS = lstNS_o[diff_lst_NS.index(min([i - northing_val for i in lstNS if i - northing_val > 0]))]
    neg_NS = lstNS_o[diff_lst_NS.index(max([i - northing_val for i in lstNS if i - northing_val < 0]))]
    pos_EW = lstEW_o[diff_lst_EW.index(min([i - easting_val for i in lstEW if i - easting_val > 0]))]
    neg_EW = lstEW_o[diff_lst_EW.index(max([i - easting_val for i in lstEW if i - easting_val < 0]))]

    return [pos_NS, neg_NS], [pos_EW, neg_EW]


def generateLineEq(lstNS, lst_EW, bhl):
    ns_m, ew_m = ModuleAgnostic.slopeFinder2(lstNS[0], lstNS[1]), ModuleAgnostic.slopeFinder2(lst_EW[0], lst_EW[1])
    return ns_m[0], ns_m[1], ew_m[0], ew_m[1]



def findCorrectSide(south_bounds, east_bounds, north_bounds, west_bounds, bhl):
    bhl_northing, bhl_easting = bhl[1], bhl[0]
    south_avg_easting, south_avg_northing = statistics.mean([i[0] for i in south_bounds]), statistics.mean([i[1] for i in south_bounds])  # get statistical average for trhe north/easting for this line
    north_avg_easting, north_avg_northing = statistics.mean([i[0] for i in north_bounds]), statistics.mean([i[1] for i in north_bounds])
    east_avg_easting, east_avg_northing = statistics.mean([i[0] for i in east_bounds]), statistics.mean([i[1] for i in east_bounds])
    west_avg_easting, west_avg_northing = statistics.mean([i[0] for i in west_bounds]), statistics.mean([i[1] for i in west_bounds])

    west_diff_val, east_diff_val = abs(west_avg_easting - bhl_easting), abs(east_avg_easting - bhl_easting)
    north_diff_val, south_diff_val = abs(north_avg_northing - bhl_northing), abs(south_avg_northing - bhl_northing)
    min_northing = [north_diff_val, south_diff_val].index(min([north_diff_val, south_diff_val]))
    min_easting = [west_diff_val, east_diff_val].index(min([west_diff_val, east_diff_val]))
    ns_val, ew_val, ns_ind, ew_ind = 0, 0, -1, -1
    if min_northing == 0:
        ns_val = north_diff_val
        ns_ind = 2
    elif min_northing == 1:
        ns_val = south_diff_val
        ns_ind = 0
    if min_easting == 0:
        ew_val = east_diff_val
        ew_ind = 3
    elif min_easting == 1:
        ew_val = west_diff_val
        ew_ind = 1

    return [[ns_ind, ew_ind], [ns_val, ew_val]]


def getParallelLineParameter(coord, m_NS1, m_EW1):
    b_NS = coord[1] - (m_NS1 * coord[0])
    b_EW = coord[1] - (m_EW1 * coord[0])
    return b_NS, b_EW


def parallelLineDistance(b2, b1, a2):
    top = abs(b2 - b1)
    bottom = math.sqrt(a2 ** 2 + 1)
    d = top / bottom
    return d

def nearestPointDistance(a,b,c,y,x):
    top = abs(a*x + b*y + c)
    bottom = math.sqrt(a**2 + b**2)
    d = top / bottom

def findPointMatchParallel(x, y, distance, angle):
    x_new = x + (distance * math.cos(math.radians(angle)))
    y_new = y + (distance * math.sin(math.radians(angle)))
    return x_new, y_new


def returnAlteredAngle(ns_angle, ew_angle, n_index, e_index):
    if n_index == 0:
        ns_angle = -1 * ns_angle
    else:
        if ns_angle > 90:
            ns_angle = -1 * ns_angle - 180
        else:
            ns_angle = -1 * ns_angle - 180
    if e_index == 1:
        if ew_angle < 5:
            ew_angle = ew_angle
        else:
            ew_angle = -1 * (ew_angle - 180)
    else:
        if ew_angle > 5:
            ew_angle = -1 * ew_angle
        else:
            ew_angle = -1 * ew_angle - 180
    return ns_angle, ew_angle