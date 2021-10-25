import pandas as pd
import numpy as np
import os

def main():
    file_path = ""
    df = pd.read_excel(file_path, dtype='object')
    df_txt = df.to_numpy().tolist()
