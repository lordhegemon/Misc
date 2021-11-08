import pandas as pd
import numpy as np
import os
import utm
def main():
    d = {}
    df_new_dataframe = pd.DataFrame(columns=['Group', 'Easting', 'Northing'])
    file_path = "C:\\Users\\colto\\My Drive\\Geyser App\\ArcFiles\\LowerGBPolygons.csv"
    df = pd.read_csv(file_path, dtype='object')
    df_txt = df.to_numpy().tolist()
    for row in df_txt:
        if row[0] not in d:
            d[row[0]] = []
        d[row[0]].append(row[1:])
    edited_lst = [v for item, v in d.items()]
    for i in range(len(edited_lst)):
        for j in range(len(edited_lst[i])):
            edited_lst[i][j][1], edited_lst[i][j][2] = float(edited_lst[i][j][2]), float(edited_lst[i][j][1])
            foo = utm.from_latlon(edited_lst[i][j][1], edited_lst[i][j][2])
            edited_lst[i][j][1], edited_lst[i][j][2] = foo[0], foo[1]
            new_row = {'Group': edited_lst[i][j][0],
                       'Easting': edited_lst[i][j][1],
                       'Northing': edited_lst[i][j][2]}

            df_new_dataframe = df_new_dataframe.append(new_row, ignore_index=True)

    df_new_dataframe.to_csv('C:\\Users\\colto\\My Drive\\Geyser App\\ArcFiles\\GroupOutlines.csv')

main()