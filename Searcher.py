from glob import glob
import os


# def parseAllFoldersForString(searcher_var):
#     paths = ['C:\\', 'E:\\', 'F:\\', 'J:\\']
#     for k in paths:
#         print(k)
#         files = glob(k + '/**/', recursive=True)
#         for i in files:
#             print(i)
#             try:
#                 if searcher_var in i:
#
#
#                     print(i)
#                 # for j in os.listdir(i):
#                 #     print(j)
#                     # if searcher_var in j:
#                     #     print(i, j)
#             except:
#                 pass


def main():
    # search_for_gms_files("C:\\Users\\colto\\My Drive")
    search_for_gms_files("F:")
    search_for_gms_files("H:/")
    search_for_gms_files("C:/")
    search_for_gms_files("J:/")
    search_for_gms_files("G:/")



def search_for_gms_files(directory):
    print(directory)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if 'croft' in file.lower():# and file.endswith(".jpg"):
            # if file.endswith(".gms"):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_modified = os.path.getmtime(file_path)
                print("File Path:", file_path)
                # print("File Size:", file_size, "bytes")
                # print("Last Modified:", file_modified)
                # print("--------------------------------------")

# Example usage
# search_for_gms_files("C:/")  # Replace "C:/" with the desired hard drive path




# parseAllFoldersForString('C:\\', '.dupe')
# parseAllFoldersForString('E:\\', '.dupe')
# parseAllFoldersForString('F:\\', '.dupe')
# parseAllFoldersForString('J:\\', '.dupe')
# parseAllFoldersForString('.gms')
main()