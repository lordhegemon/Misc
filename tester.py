import os
from glob import glob
def main():
    new_path = "C:\\test"
    files = glob(new_path + '/**/', recursive=True)
    for i in files:
        for j in os.listdir(i):
            if 'cara' in j.lower() and 'tn' not in i.lower():
                print(i, j)
            # if searcher_var in j:
            #     print(j)
    # path = "C:\\test"
    # for root, dirs, files in os.walk(path):
    #     for x in dirs:
    #         print(x)
    #     for file in files:
    #         if 'brush' in file.lower():
    #             print(file)
    #             file_path = os.path.join(path, file)
    #             print(file_path)
                # os.remove(file_path)
main()