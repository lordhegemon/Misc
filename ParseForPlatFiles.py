import pyodbc
import ModuleAgnostic as ma
import os


def main():
    conn, cursor = sqlConnect()
    section = "12"
    ts = "7"
    ts_dir = "2"
    rng = "19"
    rng_dir = "1"

    if ts_dir == "2":
        ts_dir = "S"
    else:
        ts_dir = 'N'

    if rng_dir == "2":
        rng_dir = "W"
    else:
        rng_dir = 'E'


    line = findData(section, ts, ts_dir, rng, rng_dir, cursor)
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