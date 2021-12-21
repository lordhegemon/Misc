import os
import sqlite3
import pandas as pd
import time



def main():
    time_1 = time.perf_counter()
    dataframe_features = pd.read_csv("C:\\Work\\Test scripts\\AnchorPoints\\All_Data_Lat_Lon.csv", dtype='object')
    print(time.perf_counter() - time_1)
    conn = sqlite3.connect("C:\\Work\\Test scripts\\AnchorPoints\\LatLonPlats.db")
    # dataframe_features.to_sql("LatLonData", conn, if_exists='replace')
    time_1 = time.perf_counter()
    string_sql = 'select * from LatLonData'
    output = pd.read_sql(string_sql, conn, index_col='index')
    print(time.perf_counter() - time_1)

def sqlConnect():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-CMK3OJU\SQLEXPRESS01;"
        "Database=UTRBDMSNET;"
        "Trusted_Connection = yes;")
    cursor = conn.cursor()
    return conn, cursor


main()