import os
from glob import glob
import shutil
import numpy as np
from datetime import datetime
def main():
    parseForUpdatedApds()



def parseForUpdatedApds():
    path = "C:\\Work\\Well design"
    file_paths_new = parseAllFoldersForString(path)
    for item in file_paths_new:
        print(item)
        copyToNewLocation(item)
    pass

def parseAllFoldersForString(new_path):
    files = glob(new_path + '/**/', recursive=True)
    created_data = []
    original_time = 1636398382.4097853
    file_paths_new = []
    for i in files:
        for j in os.listdir(i):
            file_path = os.path.join(i, j)
            created = os.path.getctime(file_path)
            if created > original_time:
                file_paths_new.append(file_path)
                # print(file_path)
    return file_paths_new

def copyToNewLocation(path):
    shutil.copy(path, "C:\\Work\\newapds")

main()