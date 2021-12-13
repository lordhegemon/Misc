import pyodbc
import pandas as pd
import numpy as np

import ModuleAgnostic
import ModuleAgnostic as ma


def main():
    conn, cursor = sqlConnect()
    df_parsed = pd.read_csv("PlatSidesAll.csv", encoding="ISO-8859-1")
    # print(len(df_parsed))

    pd.set_option('display.max_columns', None)
    # print(df_parsed)
    # print(df_parsed)
    # df_parsed = df_parsed.to_numpy().tolist()
    # unique_col = df_parsed.new_code.unique().tolist()
    data_out = sqlRun(cursor)
    data_out = list(set(data_out))
    # print(list(df_parsed.columns.values))
    #
    # df_parsed = translateDF(df_parsed)
    # print(df_parsed)
    # df_parsed.to_csv("LatLonEdited.csv")
    # df['min_distance'] = np.vectorize(equationDistance)(df['Easting'], df['Northing'], shl[0], shl[1])
    # df_parsed['is_present'] = np.vectorize(checkIfDataPresent)(df_parsed['new_code'], data_out)

    # print(len(df_parsed))
    # print(df_parsed)
    df_parsed['is_present'] = np.where(df_parsed['ConcCode'].isin(data_out), True, False)
    df_parsed_test = df_parsed.query('is_present == True')
    print(df_parsed_test)
    # print(len(df_parsed_test))
    unique_col = df_parsed_test.ConcCode.unique().tolist()
    df_parsed_test.to_csv("PlatSidesAll.csv")


def checkIfDataPresent(data, lst):
    if any([k in data for k in lst]):
        return True
    else:
        return False


def translateDF(df_parsed):
    df_parsed['TownshipDirectionConverted'] = df_parsed.apply(lambda x: translateNumberToDirection('township', x['Township Direction']), axis=1)
    df_parsed['RangeDirectionConverted'] = df_parsed.apply(lambda x: translateNumberToDirection('rng', x['Range Direction']), axis=1)
    df_parsed['BaselineConverted'] = df_parsed.apply(lambda x: translateNumberToDirection('baseline', x['Baseline']), axis=1)
    df_parsed['new_code'] = df_parsed.apply(lambda x: tntd(x['Section']) + tntd(x['Township']) + x['TownshipDirectionConverted'] + tntd(x['Range']) + x['RangeDirectionConverted'] + x['BaselineConverted'], axis=1)
    return df_parsed


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


def sqlRun(cursor):
    execute1 = ' select Sec, Township, TownshipDir, Range, RangeDir, PM'
    execute2 = ' from [dbo].[LocExt]'
    execute3 = ' '
    execute4 = ' where Sec is not Null and Township is not Null and Range is not Null'
    # execute1 = ' select Wh_sec,[Wh_Twpn],[Wh_Twpd], [Wh_RngN], [Wh_RngD], [Wh_Pm]'
    # execute2 = ' from [dbo].[DirectionalSurveyHeader] as dsh'
    # execute3 = ' join [dbo].[tblAPDLoc] tal on SUBSTRING(tal.API, 0, 11) = dsh.APINumber'
    # execute4 = " where Wh_Sec is not Null and Wh_Twpn is not Null and Wh_Twpd is not Null and Wh_RngD is not Null and Wh_RngN is not Null and Wh_Pm is not Null"
    data_lst = cursor.execute(execute1 + execute2 + execute3 + execute4)
    data_lst = fixer(data_lst)
    for i in range(len(data_lst)):
        data_lst[i][0] = int(float(data_lst[i][0]))
        data_lst[i][1] = int(float(data_lst[i][1]))
        # data_lst[i][2] = translateNumberToDirection('township', data_lst[i][2])
        data_lst[i][3] = int(float(data_lst[i][3]))
        # data_lst[i][4] = translateNumberToDirection('range', data_lst[i][4])
        # data_lst[i][5] = translateNumberToDirection('baseline', data_lst[i][5])
        # print(data_lst[i])
        if len(str(data_lst[i][0])) == 1:
            data_lst[i][0] = "0" + str(data_lst[i][0])
        if len(str(data_lst[i][1])) == 1:
            data_lst[i][1] = "0" + str(data_lst[i][1])
        if len(str(data_lst[i][3])) == 1:
            data_lst[i][3] = "0" + str(data_lst[i][3])
        for j in range(len(data_lst[i])):
            data_lst[i][j] = str(data_lst[i][j])
        data_lst[i] = "".join(data_lst[i])
    return data_lst


def tntd(val):
    val = str(int(val))
    if len(str(val)) == 1:
        val = "0" + str(val)
    return str(val)


def sqlConnect():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS01;"
        "Database=UTRBDMSNET;"
        "Trusted_Connection = yes;")
    cursor = conn.cursor()
    return conn, cursor


def fixer(lst):
    fixed_lst = []
    for row in lst:
        fixed_lst.append(list(map(str, list(row))))
    return fixed_lst


main()
