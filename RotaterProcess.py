import numpy as np
import math


def main():
    pts = [[0,0], [1,0], [2,0], [2,1], [2,2], [1,2], [0,2], [0,1]]
    center = [1,1]
    for i in range(len(pts)):
        angle = (math.degrees(math.atan2(pts[i][1] - center[1], pts[i][0] - center[0])) + 360) % 360
main()
