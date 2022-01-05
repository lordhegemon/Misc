import ModuleAgnostic as ma
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import ProcessCoordData
import ProcessBHLLocation
from itertools import chain
from matplotlib import pyplot as plt
import math
import pandas as pd
import numpy as np


def main():
    center = [1, 1]
    points = [[0,0], [0,1], [0,2], [1,2], [2,2], [2,1], [2,0], [1,0]]
    new_data = []
    df = pd.read_excel("C:\\Work\\RewriteAPD\\Datasets\\AngleToBearing.xlsx", dtype='object')
    min_df = df[df['min_distance'] == df['min_distance'].min()]
    print(df)



main()
