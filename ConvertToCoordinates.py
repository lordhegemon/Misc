import sqlite3
import FindSurfaceLocationsAndPlats
import pandas as pd
import numpy as np
import math
import utm
import pyodbc
import itertools
import ModuleAgnostic as ma
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import copy


def turnIntoDB():
    conn = sqlite3.connect("C:\\Work\\RewriteAPD\\APD_Data.db")
    df_parsed_utm_latlon = pd.read_excel("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\LatLonUTM.xlsx", dtype='object')
    df_parsed_utm_latlon.to_sql("SectionDataCoordinates", conn, if_exists='replace')

    df_parsed_utm_latlon = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\CasingStrengths.csv", dtype='object')
    df_parsed_utm_latlon.to_sql("CasingStrengths", conn, if_exists='replace')

    df_parsed_utm_latlon = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\UTM\\PlatGridNumbers.csv", dtype='object')
    df_parsed_utm_latlon.to_sql("SectionSidesData", conn, if_exists='replace')



def main2():
    # df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\OddballSections.csv", encoding="ISO-8859-1")
    # df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\All_Data_Lat_Lon.csv", encoding="ISO-8859-1")
    df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\ConvertedData.csv", encoding="ISO-8859-1")
    data_test = df_parsed.to_numpy().tolist()
    new_data_file = []
    for i in data_test:
        data_init = i[:8]
        data_init[:6] = [int(r) for r in data_init[:6]]
        conc_code = addZeroesForConc(i)
        data_init[2] = int(float(translateDirectionToNumber('township', data_init[2])))

        data_init[4] = int(float(translateDirectionToNumber('rng', data_init[4])))
        data_init[5] = int(float(translateDirectionToNumber('baseline', data_init[5])))
        latlon = list(utm.to_latlon(i[6], i[7], 12, 'T'))

        line = data_init + latlon + [conc_code] + ['V.1']
        new_data_file.append(line)
        # print(line)
        # print(line)
    df_test = [{'Section': i[0], 'Township': int(float(i[1])), 'Township Direction': i[2], 'Range': int(float(i[3])),
                'Range Direction': i[4], 'Baseline': i[5], 'Easting': float(i[6]), 'Northing': float(i[7]), 'Latitude': float(i[8]), "Longitude": float(i[9]), 'Conc': i[10], 'Version': i[11]} for i in new_data_file]
    df = pd.DataFrame(df_test, columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', "Latitude", "Longitude", 'Conc', 'Version'])
    # df.to_csv('OddballUTMLatLon.csv', index=False)
    # df.to_csv('All_Data_Lat_Lon_UTM.csv', index=False)
    df.to_csv('ConvertedData_Out.csv', index=False)




def addZeroesForConc(i):
    conc_code_merged = i[:6]
    conc_code_merged = [int(r) for r in conc_code_merged]
    conc_code_merged[2] = translateNumberToDirection('township', str(conc_code_merged[2]))
    conc_code_merged[4] = translateNumberToDirection('rng', str(conc_code_merged[4]))
    conc_code_merged[5] = translateNumberToDirection('baseline', str(conc_code_merged[5]))

    conc_code = [str(r) for r in conc_code_merged]
    len_lst = [len(r) for r in conc_code]
    if len_lst[0] == 1:
        conc_code[0] = "0" + str(conc_code[0])
    if len_lst[1] == 1:
        conc_code[1] = "0" + str(conc_code[1])
    if len_lst[3] == 1:
        conc_code[3] = "0" + str(conc_code[3])
    conc_code = "".join([str(q) for q in conc_code])
    # print(conc_code)
    return conc_code


def main():
    added_data = []
    df_parsed = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\FinalCoords\\PlatGridNumbers.csv", encoding="ISO-8859-1")
    data_test = df_parsed.to_numpy().tolist()
    data_test = [i for i in data_test if 'agrc' not in i[-1].lower()]
    # ma.printLine(data_test)
    # data_sorted = ma.oneToMany(data, 16)
    new_data_file = []
    conn, cursor = sqlConnect()
    sql_lst, sql_conc = parseDatabaseForDataWithSectionsAndSHL(cursor)
    output = FindSurfaceLocationsAndPlats.matcherDF1(df_parsed, sql_lst)
    for i in output:
        lst = FindSurfaceLocationsAndPlats.transformData2(i)
        if lst != []:
            data = lst[0]
            for j in data:
                out = reTranslateData(j)
                print(out)
                # added_data.append(out)
            # ma.printLine(lst[0])
    ma.printLine(added_data)
    print("boo")
    # ma.printLine(output)
    # for i in sql_lst:
    #     section_data_df = df_parsed[(df_parsed['Section'] == i[0])
    #                                 & (df_parsed['Township'] == i[1])
    #                                 & (df_parsed['Township Direction'] == i[2])
    #                                 & (df_parsed['Range'] == i[3])
    #                                 & (df_parsed['Range Direction'] == i[4])
    #                                 & (df_parsed['Baseline'] == i[5])
    #                                 & (df_parsed['Version'].str.contains(r'AGRC') == False)]
    #     tsr_data, conc_code, conc_code_all = reTranslateData(i)
    #     if conc_code not in codes:
    #         codes.append(conc_code)
    #         if len(section_data_df) > 0:
    #             counter += 1
    #             data = section_data_df.to_numpy().tolist()
    #             data_sorted = ma.oneToMany(data, 16)
    #
    #             try:
    #                 for j in data_sorted:
    #                     version_name = j[-1][-1]
    #                     conv_data = convertToDecimal(copy.deepcopy(j))
    #                     conv_data = pointsConverter(conv_data)
    #
    #                     modified_shl = findSurfaceCoordinate(conv_data, tsr_data)
    #                     data_utm = convertData(modified_shl, conv_data, i[8:10])
    #                     for r in range(len(data_utm)):
    #                         latlon = list(utm.to_latlon(data_utm[r][0], data_utm[r][1], 12, 'T'))
    #                         conc_code_all[2] = int(float(translateDirectionToNumber('township', conc_code_all[2])))
    #                         conc_code_all[4] = int(float(translateDirectionToNumber('rng', conc_code_all[4])))
    #                         conc_code_all[5] = int(float(translateDirectionToNumber('baseline', conc_code_all[5])))
    #                         new_line = conc_code_all + data_utm[r] + latlon + [conc_code] + [version_name]
    #                         # print(new_line)
    #                         new_data_file.append(new_line)
    #
    #
    #             except TypeError:
    #                 pass
    #     # print("counter", counter)
    # # print(counter)
    # df_test = [{'Section': i[0], 'Township': int(float(i[1])), 'Township Direction': i[2], 'Range': int(float(i[3])),
    #             'Range Direction': i[4], 'Baseline': i[5], 'Easting': float(i[6]), 'Northing': float(i[7]), 'Latitude': float(i[8]), "Longitude": float(i[9]), 'Conc': i[10], 'Version': i[11]} for i in new_data_file]
    # df = pd.DataFrame(df_test, columns=['Section', 'Township', 'Township Direction', 'Range', 'Range Direction', 'Baseline', 'Easting', 'Northing', "Latitude", "Longitude", 'Conc', 'Version'])
    # # df.to_csv('DataPointsLatLon.csv', index=False)


def reTranslateData(i):
    tsr_data = i[11:]
    conc_code_merged = i[:6]

    conc_code_merged[2] = translateNumberToDirection('township', str(conc_code_merged[2]))
    conc_code_merged[4] = translateNumberToDirection('rng', str(conc_code_merged[4]))
    conc_code_merged[5] = translateNumberToDirection('baseline', str(conc_code_merged[5]))
    conc_code = [str(r) for r in conc_code_merged]
    len_lst = [len(r) for r in conc_code]
    if len_lst[0] == 1:
        conc_code[0] = "0" + str(conc_code[0])
    if len_lst[1] == 1:
        conc_code[1] = "0" + str(conc_code[1])
    if len_lst[3] == 1:
        conc_code[3] = "0" + str(conc_code[3])
    conc_code = "".join([str(q) for q in conc_code])
    return tsr_data, conc_code, conc_code_merged


def convertData(shl, data_lst, utm_data):
    utm_x = abs(shl[0] - float(utm_data[0]))
    utm_y = abs(shl[1] - float(utm_data[1]))
    data_utm = []
    for i in data_lst:
        x = i[0] + utm_x
        y = i[1] + utm_y
        data_utm.append([x, y])
    return data_utm


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


def sqlConnect():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS01;"
        "Database=UTRBDMSNET;"
        "Trusted_Connection = yes;")
    cursor = conn.cursor()
    return conn, cursor


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


def findSurfaceCoordinate(data, tsr_data):
    eq_lst, data = getLineSegmentSlopeEquation(data)
    ns_lines, ns_points, ew_lines, ew_points = generateParallelLineSegmentLinesAndPoints(eq_lst, data, tsr_data)
    intersection, ns_side, ew_side = createParallelLineSegments(ns_points, ew_points, tsr_data)
    surfaceRelativeCoordinate, nsSidePts, ewSidePts = intersection, ns_side, ew_side
    return surfaceRelativeCoordinate
    # data = list(itertools.chain.from_iterable(data))
    # data = list(data for data, _ in itertools.groupby(data))
    # data = [[i[0] + surfaceRelativeCoordinate[0], i[1] + surfaceRelativeCoordinate[1]] for i in data]


def getLineSegmentSlopeEquation(data):
    # data = data[getVersionGrid1()]
    eq_lst = [ma.slopeFinder2(data[i], data[(i + 1) % len(data)]) for i in range(len(data))]
    eq_lst = list(itertools.chain.from_iterable(eq_lst))
    data = [data[:5], data[4:9], data[8:13], data[12:]]
    return ma.oneToMany(eq_lst, 4), data


def generateParallelLineSegmentLinesAndPoints(eq_lst, data, tsr_data):
    ns_dir, ew_dir = tsr_data[1], tsr_data[3]
    ns_eq = [eq_lst[4:9], eq_lst[12:]]
    ew_eq = [eq_lst[:5], eq_lst[8:13]]
    ns_lines = [ns_eq[0] if ns_dir == 'FNL' else ns_eq[1]]  # for i in ns_eq]
    ew_lines = [ew_eq[0] if ns_dir == 'FWL' else ew_eq[1]]  # for i in ew_eq]
    ns_points = data[1] if ns_dir == 'FNL' else data[3]
    ew_points = data[0] if ew_dir == 'FWL' else data[2]
    return ns_lines, ns_points, ew_lines, ew_points


def createParallelLineSegments(ns_p, ew_p, tsr_data):
    ns_d, ew_d = int(float(tsr_data[0])), int(float(tsr_data[2]))
    ns_segments = [lineSegmentCalculator(ns_p[i], ns_p[i + 1], ns_d, 'ns') for i in range(len(ns_p) - 1)]
    ew_segments = [lineSegmentCalculator(ew_p[i], ew_p[i + 1], ew_d, 'ew') for i in range(len(ew_p) - 1)]
    intersection, ns_id, ew_id, i, j = detectIntersectionParseProcess(ns_segments, ew_segments)

    return intersection, ns_id, ew_id


def detectIntersectionParseProcess(ns, ew):
    for i in range(len(ns)):
        for j in range(len(ew)):
            line_ns = LineString([Point(ns[i][0]), Point(ns[i][1])])
            line_ew = LineString([Point(ew[j][0]), Point(ew[j][1])])
            outcome = line_ns.intersection(line_ew)
            try:
                intersection = [outcome.x, outcome.y]
                return intersection, ns[i], ew[j], i, j
            except AttributeError:
                pass


def lineSegmentCalculator(xy1, xy2, direct, cardinal_dir):
    x1, y1, x2, y2 = xy1[0], xy1[1], xy2[0], xy2[1]
    r = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    data_out = []
    if r != 0:
        delta_x = (direct / r) * (xy1[1] - xy2[1])
        delta_y = (direct / r) * (xy2[0] - xy1[0])
        x3, y3 = xy1[0] - delta_x, xy1[1] - delta_y
        x4, y4 = xy2[0] - delta_x, xy2[1] - delta_y
        data_out = [[x3, y3], [x4, y4]]
    if r == 0:
        if cardinal_dir == 'ns':
            y1 = y1 + direct
            y2 = y2 + direct
        else:
            x1 = x1 + direct
            x2 = x2 + direct
        data_out = [[x1, y1], [x2, y2]]
    return data_out


main()
# main2()
# turnIntoDB()