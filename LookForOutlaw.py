import os
import re
from tika import parser

def mainRun():
    path = 'J:\\Work\\WellPlat'
    for fileName in os.listdir(path):
        print(fileName)
        new_path = os.path.join(path, fileName)

        parsed_data_full = parser.from_file(new_path, xmlContent=True)
        parsed_data_full = parsed_data_full['content']
        for i in parsed_data_full:
            if 'outlaw' in i.lower():
                print(new_path)


mainRun()