import pandas as pd
import numpy as np

def main():
    compile_lst = []
    df = pd.read_csv("C:\\Users\\colto\\Google Drive\\crypto\\1yrprice.csv")
    lst = df.to_numpy().tolist()
    # for i in range(len(lst)):
    #     if str(lst[i][0]) != 'nan':
    #         compile_lst.append(lst[i][:2])
    compile_lst = [lst[i][:2] for i in range(len(lst)) if str(lst[i][0]) != 'nan']

    for i in range(len(lst)):
        for j in range(len(compile_lst)):
            if compile_lst[j][0] == lst[i][3]:
                compile_lst[j].append(lst[i][4])
    compile_lst = [i for i in compile_lst if len(i) == 3]

    for i in range(len(compile_lst)):
        for j in range(1, len(compile_lst[i])):
            compile_lst[i][j] = float(compile_lst[i][j].replace("$", "").replace(",", ""))
    final_compare_lst = []
    for i in range(len(compile_lst)):
        try:
            perc = round(compile_lst[i][2]/compile_lst[i][1],2) * 100
            compile_lst[i].append(perc)
            final_compare_lst.append([perc, compile_lst[i][0]] + compile_lst[i][1:3] )
            # print(perc, compile_lst[i][0])
        except ZeroDivisionError:
            pass

    final_compare_lst = sorted(final_compare_lst, key=lambda x: x[0])
    for i in final_compare_lst:
        print(i)
main()