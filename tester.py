import os
from glob import glob

new_path = "C:\\Work\\"
searcher_var = "4304755748"
files = glob(new_path + '/**/', recursive=True)
for i in files:
    for j in os.listdir(i):
        if searcher_var in j:
            print(i, j)
