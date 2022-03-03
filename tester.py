import os
from glob import glob

new_path = "F:\\OGMImages"
searcher_var = "53378"
files = glob(new_path + '/**/', recursive=True)
for i in files:
    for j in os.listdir(i):
        if searcher_var in j:
            print(i, j)