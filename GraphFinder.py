import traceback
import re
import ModuleAgnostic as ma
import math
import numpy as np
from glob import glob
import os
import more_itertools
import pdfminer
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
import PyPDF2
from PyPDF2 import PdfReader
import itertools
import csv
import shutil
import tabula
import random
import ModuleAgnostic as ma
import matplotlib.pyplot as plt
import statistics as st

def mainProcess():
    new_path = r'C:\Work\OldSurveyParser\application_4301950033.pdf'
    output = textBoxGather(new_path)
    pages_data = [i for i in output if i]
    ma.printLine(output)

    num_pages = 10
    num_entries = 500
    min_linear_length = 10

    # pages_data = generate_page_data(num_pages, num_entries)
    linear_patterns_x = count_linear_patterns_x(pages_data, min_linear_length)
    linear_patterns_y = count_linear_patterns_Y(pages_data, min_linear_length)
    # for i in linear_patterns_x:
    #     for j in i:
    #         ma.printLine(j[1])

    findConsistenHorizontalPatterns(linear_patterns_x)
    # ma.printLine(linear_patterns_y)
    # print(f"Number of pages with a linear pattern of {min_linear_length} or more values: {linear_patterns_x}/{num_pages}")
    # print(f"Number of pages with a linear pattern of {min_linear_length} or more values: {linear_patterns_y}/{num_pages}")

    pass


def generate_page_data(num_pages, num_entries):
    pages_data = []
    for _ in range(num_pages):
        page = []
        xy_lst = []
        for _ in range(num_entries):
            left_x = random.randint(0, 1000)
            lower_y = random.randint(0, 1000)
            right_x = left_x + random.randint(1, 250)
            upper_y = lower_y + random.randint(1, 250)
            label = random.choice(['Title', 'Graph', 'MD', 'Inc', 'Azi'])
            text_box = [left_x, lower_y, right_x, upper_y, label]
            page.append(text_box)
            xy_lst.append([(left_x+right_x)/2, (lower_y + upper_y)/2])
        pages_data.append(page)
    return pages_data


def has_linear_pattern(x_bounds, tolerance=2):
    min_x = min(x_bounds)
    max_x = max(x_bounds)
    interpolated_values = [min_x + (max_x - min_x) * (i / (len(x_bounds) - 1)) for i in range(len(x_bounds))]
    indices = [i for i, x in enumerate(x_bounds) if abs(x - interpolated_values[i]) <= tolerance]
    is_linear = all(abs(x - interpolated_values[i]) <= tolerance for i, x in enumerate(x_bounds))
    return is_linear, indices


def count_linear_patterns_x(pages_data, min_linear_length):
    all_pages =[]
    for r, page in enumerate(pages_data):
        x_bounds = [(text_box[0] + text_box[2])/2 for text_box in page]
        sorted_lst = sorted(enumerate(x_bounds), key=lambda x: x[1])
        sorted_indices = [index for index, _ in sorted_lst]
        x_bounds = [element for _, element in sorted_lst]
        if len(x_bounds) >= min_linear_length:
            output = list(ma.grouper3(x_bounds, 2))
            indices = output[1]
            sorted_groups = [[page[sorted_indices[j]] for j in i] for i in indices]
            sorted_groups = [i for i in sorted_groups if len(i) >= min_linear_length]
            xy_sorted_groups = [[[(j[0] + j[2])/2, (j[1] + j[3])/2, j[-1]] for j in i] for i in sorted_groups]
            xy_sorted_groups = [sorted(i, key=lambda x: x[0])for i in xy_sorted_groups]
            xy_pts = [[[j[0], j[1]] for j in i] for i in xy_sorted_groups]
            xy_sorted_groups = [[r, i] for i in xy_sorted_groups]
            all_pages.append(xy_sorted_groups)
    return all_pages


def count_linear_patterns_Y(pages_data, min_linear_length):
    all_pages =[]
    for r, page in enumerate(pages_data):
        y_bounds = [(text_box[1] + text_box[3])/2 for text_box in page]
        sorted_lst = sorted(enumerate(y_bounds), key=lambda x: x[1])
        sorted_indices = [index for index, _ in sorted_lst]
        y_bounds = [element for _, element in sorted_lst]
        if len(y_bounds) >= min_linear_length:
            output = list(ma.grouper3(y_bounds, 2))
            indices = output[1]
            sorted_groups = [[page[sorted_indices[j]] for j in i] for i in indices]
            sorted_groups = [i for i in sorted_groups if len(i) >= min_linear_length]
            xy_sorted_groups = [[[(j[0] + j[2])/2, (j[1] + j[3])/2, j[-1]] for j in i] for i in sorted_groups]
            xy_sorted_groups = [sorted(i, key=lambda x: x[1])for i in xy_sorted_groups]
            xy_sorted_groups = [[r, i] for i in xy_sorted_groups]
            all_pages.append(xy_sorted_groups)
    return all_pages

def findConsistenHorizontalPatterns(hor_lst):
    for i, data in enumerate(hor_lst):
        print(i)
        for j in data:
            # print('foo', j[0])
            second_column = [sublist[1] for sublist in j[1]]
            # print(second_column)
            min_val, max_val = min(second_column), max(second_column)
            print(abs(max_val - min_val))
            print(min_val, max_val)




def grapherOriginal(lst1):
    fig, ax = plt.subplots()
    x1, y1 = [k[1] for k in lst1], [k[0] for k in lst1]
    plt.scatter(x1, y1, c='red')
    # plt.plot(x1, y1, c='red')
    plt.show()
def grapherSeveral(lst):
    colors = ["#000000", "#E69F00", "#56B4E9", '#0072B2', '#D55E00', '#CC79A7', "#56B4E9", "#000000", "#E69F00"]
    counter = 0
    for x, i in enumerate(lst):
        print(i)
        x2, y2 = [k[0] for k in i], [k[1] for k in i]
        plt.scatter(x2, y2, c=colors[x])
        plt.plot(x2, y2, c=colors[x])
        # counter += 1
    plt.show()

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



mainProcess()

# pages_data = generate_page_data(num_pages, num_entries)
# linear_patterns_x = count_linear_patterns_x(pages_data)
# linear_patterns_y = count_linear_patterns_y(pages_data)
# print(f"Number of pages with a rough linear pattern: {linear_patterns_x}/{num_pages}")
# print(f"Number of pages with a rough linear pattern: {linear_patterns_x}/{num_pages}")
#
# def count_linear_patterns_y(pages_data, min_linear_length):
#     linear_pattern_count = 0
#     for r, page in enumerate(pages_data):
#         y_bounds = [text_box[3] for text_box in page if isinstance(text_box[3], int)]
#         if len(y_bounds) >= min_linear_length:
#             dictPlan = dict(enumerate(ma.grouper2(sorted(y_bounds), 2), 1))
#             for k, group in dictPlan.items():
#                 if len(group) >= min_linear_length and has_linear_pattern(group):
#                     linear_pattern_count += 1
#     return linear_pattern_count