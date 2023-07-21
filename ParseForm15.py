import os
import numpy as np
import pandas as pd
import ModuleAgnostic as ma
import math
from glob import glob
import more_itertools
import pdfminer
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
import GatherSQLDataOldSurvey
import GatherDirectionalOldSurvey
import PyPDF2
import itertools
import regex as re
from collections import defaultdict
import statistics
import tkinter as tk
from tkinter import filedialog
import subprocess
import tabula
import pandas as pd
def mainParserProcess():
    pd.set_option('display.max_columns', None)
    # file_path = openFile()
    file_path = r'C:\\Work\\Form 15\\Files\\123920.pdf'
    # file_path = r'C:\\Work\\Form 15\\Files\\123910 - Copy.pdf'
    new_path = r'C:\\Work\\Form 15\\Files\\'
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    new_path = new_path + file_name + '.csv'
    # print(new_path)
    dfs = tabula.read_pdf(file_path, pages='all', pandas_options={'header': None})
    search_string = "R&M Labor"
    # print(dfs[0])
    dataframes = []
    counter = 0
    # findFirstPageTable(dfs[0])
    for x, database in enumerate(dfs):
        # Perform search within each database
        columns = database.columns
        print(database)
        # print(len(columns))
        for j in columns:
            try:
                # pass
                # print(x)
                # print("j", j)

                test = database[j].to_numpy().tolist()
                # for i in test:
                #     print([i])
                # ma.printLine(database[j].to_numpy().tolist())
                if j == 'Lease & Rental Equipment':
                    print(database[j])
                    print([database[j][7]] == ["R&M Labor"])
                matching_rows = database[j].str.contains(search_string)
                print(matching_rows)
                # if len(matching_rows) > 0:
                #     # pass
                #     print(matching_rows)
                #     print('MATCHED')
            except (ValueError, AttributeError):
                pass
        # if check_column_names(database):
        #     columns = database.columns
        #     # print(x, counter, columns)
        #     for j in columns:
        #         try:
        #             pass
        #             # print("j", .j)
        #             # print(database[j])
        #             # matching_rows = database[database[j].str.contains(search_string)]
        #             # print('match')
        #             # print(matching_rows)
        #         except ValueError:
        #             pass
        #     counter += 1
        # if not matching_rows.empty:
        #     # print(f"Found in {database_name}:")
        #     print(matching_rows)
        # column_name = i.columns[-2]
        # print(column_name)
    # print(dfs[1])
    # output = textBoxGather(file_path)
    # ma.printLine(output)
    pass

def findFirstPageTable(df):
    df.iloc[:, 0] = df.iloc[:, 0].fillna('')
    df.iloc[:, 1] = df.iloc[:, 1].fillna('')
    filtered_df_start = df[df.iloc[:, 0].str.contains('Description Of Work')]
    filtered_df_end = df[df.iloc[:, 0].str.contains('Total approved expenses')]
    row_numbers_start, row_numbers_end = filtered_df_start.index.tolist()[0], filtered_df_end.index.tolist()[0]
    new_df = df.iloc[row_numbers_start+1:row_numbers_end+1]
    new_df = new_df.to_numpy().tolist()
    updated_data = []
    for sublist in new_df:
        split_values = sublist[1].split()
        updated_sublist = [sublist[0]] + split_values
        if updated_sublist[0] == 'n. Other (itemize)':
            updated_sublist = [updated_sublist[0]] + updated_sublist[-2:]
        updated_data.append(updated_sublist)

    ma.printLine(updated_data)

def check_column_names(df):
    column_names = df.columns.tolist()
    for column_name in column_names:
        try:
            if re.match(r'^-?\$?[\d,]+(\.\d+)?$|^(\d{1,2}/\d{1,2}/\d{4})$', column_name) or re.match(r'^\d+(\.\d+)*$', column_name):
                return False
            float_value = float(column_name)
            return False
        except ValueError:
            pass
    return True

def openFile():
    # Create the Tkinter root window

    root = tk.Tk()
    root.withdraw()

    # Open the file dialog
    file_path = filedialog.askopenfilename(title="Select PDF file", filetypes=(("PDF files", "*.pdf"),))

    # Check if a file was selected
    if file_path:
        # Open the PDF file using the default PDF viewer
        return file_path


def textBoxGather(path):
    fp = open(path, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(char_margin=0.1)
    device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp, caching=False)
    counter = 0
    page_counts_total = more_itertools.ilen(pages)
    pages = PDFPage.get_pages(fp, caching=False)
    # ui.progressBar_main.setValue(10)
    for i in pages:
        counter += 1
        current_value = int(float(10 + ((counter / page_counts_total) * 80)))
        # QApplication.processEvents()
        try:
            interpreter.process_page(i)
            device.get_result()
        except (TypeError, ValueError):
            print('error')
            pass

    data_lst = textBoxGrouperDataManager(device, counter)
    return data_lst


def textBoxGrouperDataManager(device, counter):
    data_lst = [[] for p in range(counter + 1)]
    for (page_nb, x_min, y_min, x_max, y_max, text) in device.rows:
        data_lst[page_nb].append([x_min, y_min, x_max, y_max, text])

    for i in range(len(data_lst)):
        if data_lst[i]:
            data_lst[i] = sorted(data_lst[i], key=lambda x: (x[0], x[1]))
    return data_lst


class PDFPageDetailedAggregator(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.page_number = 0

    def receive_layout(self, ltpage):
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = ''
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    row = (page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str)  # bbox == (x1, y1, x2, y2)
                    self.rows.append(row)
                for child in item:
                    render(child, page_number)
            return

        render(ltpage, self.page_number)
        self.page_number += 1
        self.rows = sorted(self.rows, key=lambda x: (x[0], -x[2]))
        self.result = ltpage

    def clearDataReboot(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        # exitCode = 0
        # while True:
        #     try:
        #         app = QApplication(sys.argv)
        #     except RuntimeError:
        #         app = QApplication.instance()
        #     window = MainUI()
        #     window.show()
        #     exitCode = app.exec_()
        #     if exitCode != EXIT_CODE_REBOOT: break
        # return exitCode


mainParserProcess()