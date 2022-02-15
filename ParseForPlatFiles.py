import pyodbc
import ModuleAgnostic as ma
import os
from itertools import chain

def main():
    conn, cursor = sqlConnect()
    section = "25"
    ts = "3"
    ts_dir = "2"
    rng = "2"
    rng_dir = "2"
    if ts_dir == "2":
        ts_dir = "S"
    else:
        ts_dir = 'N'

    if rng_dir == "2":
        rng_dir = "W"
    else:
        rng_dir = 'E'
    line = findData(section, ts, ts_dir, rng, rng_dir, cursor)
    # line = list(chain.from_iterable(line))
    line = list(set(list(chain.from_iterable(line))))
    for i in line:
        beg = "https://oilgasweb.ogm.utah.gov/apd/attachments/"
        ending = r"/" + str(i) + "_wellplat.pdf"
        full_url = beg + str(i) + ending

    ma.printLine(line)

def findData(section, ts, ts_dir, rng, rng_dir, cursor):
    selectCommand = 'select a.APDNo'
    fromCommand = ' from [dbo].[tblAPDLoc] loc'
    joinCommand = ' inner join [dbo].[tblAPD] a on a.APDNo = loc.APDNO'
    whereCommand = ' where Wh_Sec = ' + str(section) + ' and Wh_Twpn = ' + str(ts) + " and Wh_Twpd = '" + str(ts_dir) + "'" + ' and Wh_RngN = ' + str(rng) + " and Wh_RngD = '" + str(rng_dir) + "'"
    orderCommand = ' '
    print(selectCommand)
    print(fromCommand)
    print(joinCommand)
    print(whereCommand)



    line = cursor.execute(selectCommand + fromCommand + joinCommand + whereCommand + orderCommand)
    # print(line)
    line = fixer(line)
    return line

def sqlConnect():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS;"
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