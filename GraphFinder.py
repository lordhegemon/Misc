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
from scipy.spatial import cKDTree
import geopandas as gpd
import libpysal as lp
from esda.moran import Moran
from scipy.interpolate import griddata


def mainProcess():
    # new_path = r'C:\Work\OldSurveyParser\application_4301950033 - Copy.pdf'
    new_path = r'C:\Work\OldSurveyParser\application_4301950033.pdf'
    key_words = ['tvd', 'md', 'inc', 'inclination', 'azi', 'azimuth', 'measured depth', 'dls']
    output = textBoxGather(new_path)
    pages_data = [i for i in output if i]
    pages = testRandomness(pages_data)

    num_pages = 10
    num_entries = 500
    min_linear_length = 10

    # pages_data = generate_page_data(num_pages, num_entries)
    pages_data = [pages_data[i] for i in range(len(pages_data)) if i in pages]
    # for i in range(len(pages_data)):
    #     if i in pages:
    #         pages_data[i]

    linear_patterns_columns = count_linear_patterns_columns(pages_data, min_linear_length)  # find areas with consistent x values
    linear_patterns_rows = count_linear_patterns_rows(pages_data, min_linear_length)  # find areas with consistent y values
    # print(len(linear_patterns_columns), len(linear_patterns_rows))
    for i in linear_patterns_rows:
        for j in i:
            txt_data = [r[-1].lower() for r in j[-1]]
            filtered_list = list(set([item for item in key_words if item in txt_data]))
            if len(filtered_list) > 3:
                width_count = len(txt_data)

    linear_patterns_rows = [[j for j in i if width_count + 1 >= len(j[1]) >= width_count - 1] for i in linear_patterns_rows]
    linear_pattern_pages = [[j[0] for j in i] for i in linear_patterns_rows]
    linear_patterns_rows = [[j[1] for j in i] for i in linear_patterns_rows]
    linear_patterns_rows = [sorted(i, key=lambda row: row[0][1], reverse=True) for i in linear_patterns_rows]
    linear_patterns_rows = [[[linear_pattern_pages[i][j], linear_patterns_rows[i][j]] for j in range(len(linear_pattern_pages[i]))] for i in range(len(linear_pattern_pages))]
    avg_height = findWidthHeight(linear_patterns_rows, 'row')
    avg_width = findWidthHeight(linear_patterns_columns, 'col')
    print('width', avg_width)
    interpolationProcess(linear_patterns_rows, width_count, avg_height, avg_width)

    # for i in range(len(linear_pattern_pages)):
    #     for j in range(len(linear_pattern_pages[i])):
    #         print(linear_pattern_pages[i][j], linear_patterns_rows[i][j])
    # for i in range(len(linear_patterns_rows)):
    #     for j in range(len(linear_patterns_rows[i])):
    #         line = linear_patterns_rows[i][j]
    # foo = [k for k in line if i]

    # txt_data = [r[-1].lower() for r in linear_patterns_rows[i][j][-1]]
    # if not width_count + 1 >= len(txt_data) >= width_count - 1:
    #     linear_patterns_rows[i][j] = []
    # occurrences = {item: filtered_list.count(item) for item in txt_data}
    # print(occurrences)
    # for k in j:
    #             print(k)

    # findConsistentRowGrids(linear_patterns_x)
    # findRowGridGrouping(linear_patterns_columns)
    # findConsistentVerticalPatterns(linear_patterns_rows)
    # print(f"Number of pages with a linear pattern of {min_linear_length} or more values: {linear_patterns_x}/{num_pages}")
    # print(f"Number of pages with a linear pattern of {min_linear_length} or more values: {linear_patterns_y}/{num_pages}")

    pass


"""x left, ylower, x_right, y upper """
def checkIfFloat(element):
    if isinstance(element, float):
        return True
    elif isinstance(element, int):
        return True
    elif isinstance(element, str):
        try:
            float_val = float(element)
            return True
        except ValueError:
            print(element)
            return False
    else:
        print(element)
        return False

def interpolationProcess(pages_data, width_length, avg_height, avg_width):
    # pages_data = [sorted(i, key=lambda row: row[0][1], reverse=True) for i in pages_data]
    for r, page in enumerate(pages_data):
        # page = [[j for j in i[1] if checkIfFloat(j[-1])] for i in page]
        # page = [[j for j in i[1] if (j[-1].replace('.', '', 1).isdigit() or (j[-1][0] == '-' and j[-1][1:].replace('.', '', 1).isdigit()))] for i in page]
        page = [[r, [j for j in i[1] if checkIfFloat(j[-1])]] for i in page]
        for i in page:
            ma.printLine(i[1])

        # new_data = []
        # for i in page:
        #     print(i)
        #     new_data.append([r, []])
        #     for j in i[1]:
        #         if checkIfFloat(j[-1]):
        #             print(j[-1])
        #             new_data[-1][-1].extend([j])
                    # print(new_data[-1][-1])
                    # pass
        #         print(j[-1], j[-1][0], j[-1][1:])

        #         if float(j[-1]):
        #             print(foo)
        #         print(j)
        # ma.printLine(page)
        length_columns = 0
        prev_length_columns = 0
        xy_pts = [[k[:2] for k in i[1]] for i in page]
        xy_pts_text = [[k for k in i[1]] for i in page]
        # print(xy_pts)
        x_start = xy_pts[-1][0][0]
        y_start = xy_pts[-1][0][1]
        # print(x_start, y_start)
        xy_pts = np.array(list(itertools.chain.from_iterable(xy_pts)))


        width = width_length
        height = 40
        delta_x = avg_height
        delta_y = avg_width
        # Creating the known dataset forming a 5x5 grid (without missing points)
        for i in range(50):
            height = i
            grid_x, grid_y = np.meshgrid(np.arange(x_start, x_start + width * delta_x, delta_x),
                                         np.arange(y_start, y_start + height * delta_y, delta_y))
            grid_points = np.column_stack((grid_x.ravel(), grid_y.ravel()))
            known_values = np.arange(width * height).reshape((height, width))
            if len(grid_points) > 0:
                output, missing_points = findProximalPoints(grid_points, xy_pts, avg_width)
                # print(len(output), prev_length_columns, length_columns)
                if prev_length_columns == len(output):
                    print("____________________________________________________")
                    height = i-2
                    grid_x, grid_y = np.meshgrid(np.arange(x_start, x_start + width * delta_x, delta_x),
                                                 np.arange(y_start, y_start + height * delta_y, delta_y))
                    grid_points = np.column_stack((grid_x.ravel(), grid_y.ravel()))
                    known_values = np.arange(width * height).reshape((height, width))
                    output, missing_points = findProximalPoints(grid_points, xy_pts, avg_width)
                    break
                # else:
                prev_length_columns = length_columns
                length_columns = len(output)
                # ma.printLine(known_values)



        #



        # Simulating some missing points (you can remove or change any points here)
        # missing_points = np.array([[x_start + 1 * delta_x, y_start + 1 * delta_y],
        #                            [x_start + 2 * delta_x, y_start + 3 * delta_y],
        #                            [x_start + 3 * delta_x, y_start + 2 * delta_y]])

        # Combining known grid points and missing points
        all_points = np.vstack((grid_points, missing_points))
        # Performing interpolation to estimate values at the missing points
        # interpolated_values = griddata(grid_points, known_values.ravel(), missing_points, method='linear')
        plt.scatter(grid_points[:, 0], grid_points[:, 1], c='b', marker='o', label='Known Points')
        plt.scatter(missing_points[:, 0], missing_points[:, 1], c='r', marker='x', label='Missing Points')
        plt.scatter(output[:, 0], output[:, 1], c='g', marker='*', label='O Points')
        # plt.text(output[:, 0], output[:, 1], output[:, 2])
        for i in xy_pts_text:
            for j in i:
                plt.text(j[0], j[1], j[2])
                # print(j)
            # print(i)
            # plt.text(i[0], i[1], i[2])
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.grid()
        plt.title('Grid with Missing Points')
        plt.show()


def findProximalPoints(theory_lst, actual_lst, threshold_x):
    # print(threshold_x)
    # Set the threshold value
    threshold_x = 5
    threshold_y = 5
    # Find the corresponding points within the threshold
    corresponding_points = []
    missing_pts = []

    for point in actual_lst:
        # Calculate the differences along x and y axes separately
        diff_x = np.abs(theory_lst[:, 0] - point[0])
        diff_y = np.abs(theory_lst[:, 1] - point[1])

        # Check if the minimum distance along x-axis and y-axis are within their respective thresholds
        if np.min(diff_x) <= threshold_x and np.min(diff_y) <= threshold_y:
            corresponding_points.append(point)
        else:
            missing_pts.append(point)
    return np.array(corresponding_points), np.array(missing_pts)


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
            xy_lst.append([(left_x + right_x) / 2, (lower_y + upper_y) / 2])
        pages_data.append(page)
    return pages_data


def has_linear_pattern(x_bounds, tolerance=2):
    min_x = min(x_bounds)
    max_x = max(x_bounds)
    interpolated_values = [min_x + (max_x - min_x) * (i / (len(x_bounds) - 1)) for i in range(len(x_bounds))]
    indices = [i for i, x in enumerate(x_bounds) if abs(x - interpolated_values[i]) <= tolerance]
    is_linear = all(abs(x - interpolated_values[i]) <= tolerance for i, x in enumerate(x_bounds))
    return is_linear, indices


def testRandomness(pages_data):
    new_data = []
    for r, page in enumerate(pages_data):
        x_bounds = [(text_box[0] + text_box[2]) / 2 for text_box in page]
        y_bounds = [(text_box[1] + text_box[3]) / 2 for text_box in page]
        # data = np.array([[(text_box[0] + text_box[2]) / 2, (text_box[1] + text_box[3]) / 2]for text_box in page])# Sample data (replace this with your spatial dataset)
        # Assuming you have a GeoDataFrame with spatial information
        data = gpd.GeoDataFrame({'ID': range(len(x_bounds)),
                                 'geometry': gpd.points_from_xy(x_bounds, y_bounds)})

        # Create a spatial weights matrix (W) using k-nearest neighbors
        W = lp.weights.KNN.from_dataframe(data, k=2)

        # Check if the W matrix is row-standardized (optional)

        # Calculate spatial autocorrelation using Moran's I
        moran = Moran(data['ID'], W)
        if moran.I > 0.9:
            new_data.append(r)
            # print("Spatial Autocorrelation Statistics:")
            # print("Moran's I:", moran.I)
            # print("Expected Moran's I:", moran.EI)
            # print("Z-Score:", moran.z_norm)
            # print("P-Value:", moran.p_norm)
    return new_data


def count_linear_patterns_columns(pages_data, min_linear_length):
    all_pages = []
    for r, page in enumerate(pages_data):
        data = [text_box[-1].lower() for text_box in page]
        x_bounds = [(text_box[0] + text_box[2]) / 2 for text_box in page]
        sorted_lst = sorted(enumerate(x_bounds), key=lambda x: x[1])
        sorted_indices = [index for index, _ in sorted_lst]
        x_bounds = [element for _, element in sorted_lst]
        if len(x_bounds) >= min_linear_length:
            output = list(ma.grouper3(x_bounds, 3))
            indices = output[1]
            sorted_groups = [[page[sorted_indices[j]] for j in i] for i in indices]
            sorted_groups = [i for i in sorted_groups if len(i) >= min_linear_length]
            xy_sorted_groups = [[[(j[0] + j[2]) / 2, (j[1] + j[3]) / 2, j[-1]] for j in i] for i in sorted_groups]
            xy_sorted_groups = [sorted(i, key=lambda x: x[1]) for i in xy_sorted_groups]

            xy_pts = [[[j[0], j[1]] for j in i] for i in xy_sorted_groups]
            xy_text = [[j[-1] for j in i] for i in xy_sorted_groups]
            # grapherSeveralWithText(xy_pts, xy_text)
            xy_sorted_groups = [[r, i] for i in xy_sorted_groups]
            all_pages.append(xy_sorted_groups)

    return all_pages


def count_linear_patterns_rows(pages_data, min_linear_length):
    all_pages = []
    for r, page in enumerate(pages_data):
        y_bounds = [(text_box[1] + text_box[3]) / 2 for text_box in page]
        sorted_lst = sorted(enumerate(y_bounds), key=lambda x: x[1])
        sorted_indices = [index for index, _ in sorted_lst]
        y_bounds = [element for _, element in sorted_lst]
        if len(y_bounds) >= min_linear_length:
            output = list(ma.grouper3(y_bounds, 2))
            indices = output[1]
            sorted_groups = [[page[sorted_indices[j]] for j in i] for i in indices]
            sorted_groups = [i for i in sorted_groups if len(i) >= min_linear_length]
            xy_sorted_groups = [[[(j[0] + j[2]) / 2, (j[1] + j[3]) / 2, j[-1]] for j in i] for i in sorted_groups]
            xy_sorted_groups = [sorted(i, key=lambda x: x[0]) for i in xy_sorted_groups]
            xy_pts = [[[j[0], j[1]] for j in i] for i in xy_sorted_groups]
            xy_text = [[j[-1] for j in i] for i in xy_sorted_groups]
            # grapherSeveralWithText(xy_pts, xy_text)
            xy_sorted_groups = [[r, i] for i in xy_sorted_groups]
            all_pages.append(xy_sorted_groups)
    return all_pages


def findConsistentRowGrids(data):
    for i, data in enumerate(data):
        for j in data:
            relevant_data = [sublist[1] for sublist in j[1]]


def findWidthHeight(lst, label):
    if label == 'col':
        val = 1
    if label == 'row':
        val = 0
    gaps_lst_all = []
    for i, data in enumerate(lst):

        gaps_lst = [np.mean(np.diff(sorted([sublist[val] for sublist in j[1]]))) for j in data]
        if len(gaps_lst) > 1:
            gaps_lst_mean = np.mean(select_within_one_std_deviation(gaps_lst))
        gaps_lst_all.append(gaps_lst_mean)
    gaps_lst_all_mean = np.mean(select_within_one_std_deviation(gaps_lst_all))
    return gaps_lst_all_mean


def findRowGridGrouping(hor_lst):
    # ma.printFunctionName()
    for i, data in enumerate(hor_lst):
        gaps_lst = [np.mean(np.diff(sorted([sublist[1] for sublist in j[1]]))) for j in data]

        # for j in data:
        #     second_column = sorted([sublist[1] for sublist in j[1]])
        #     # print(second_column)
        #     gaps = np.diff(second_column).tolist()
        #     print(gaps)
        #     gaps_lst.append(st.mean(gaps))
        # gaps_lst_mean = np.mean(select_within_one_std_deviation(gaps_lst))
        #
        if len(gaps_lst) > 1:
            gaps_lst_mean = np.mean(select_within_one_std_deviation(gaps_lst))
            # print(i)
            # print(gaps_lst_mean)
        # for j in data:
        #     filtered_data_new = []
        #     second_column = sorted([sublist[1] for sublist in j[1]])
        #     gaps = np.diff(second_column)
        #     filtered_data = [second_column[r + 1] for r, diff in enumerate(gaps) if abs(diff) <= gaps_lst_mean + 1]
        #     for k in j[1]:
        #         if k[1] in filtered_data:
        #             filtered_data_new.append(k)
        #     # print([j[0], filtered_data_new])
        #     # filter_lists_by_data(j[1], filtered_data)
        #
        #     # for val in j[1]:
        #     #     lst_data = [item[0] for item in val]
        #     #     print(lst_data)
        #
        #
        #     #
        #     # for r, diff in enumerate(gaps):
        #     #     if abs(diff) <= gaps_lst_mean + 1:
        #     #         filtered_data.append(second_column[r+1])
        #
        #     # print(filtered_data)
        #
        #     # min_val, max_val = min(second_column), max(second_column)
        #     # print(round(abs(max_val - min_val),0))
        #     # lengths.append(round(abs(max_val - min_val),0))
        #


def filter_lists_by_data(original_lists, filtered_data):
    # Initialize a list to store the filtered lists
    filtered_lists = []

    # Iterate through the original lists
    for lst in original_lists:
        # Extract the 1st column of each list
        list_data = [item[0] for item in lst]

        # Check if any data in the list matches the filtered data
        if any(x in filtered_data for x in list_data):
            filtered_lists.append(lst)

    return filtered_lists


def findConsistentVerticalPatterns(vert_lst):
    for i, data in enumerate(vert_lst):
        # print(i)
        lengths = []
        for j in data:
            # print(j)
            second_column = [sublist[0] for sublist in j[1]]
            # print(len(second_column))
            min_val, max_val = min(second_column), max(second_column)
            # print(round(abs(max_val - min_val),0))
            lengths.append(round(abs(max_val - min_val), 0))
            # # print(min_val, max_val)
        # print(lengths)


def remove_outliers(data):
    # Calculate the first quartile (Q1) and the third quartile (Q3)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)

    # Calculate the Interquartile Range (IQR)
    iqr = q3 - q1

    # Define the lower and upper bounds to identify outliers
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Remove outliers from the data
    cleaned_data = [x for x in data if lower_bound <= x <= upper_bound]

    return cleaned_data


def select_within_one_std_deviation(numbers):
    # Remove outliers from the data
    cleaned_numbers = remove_outliers(numbers)

    # Convert the list to a NumPy array for efficient computations
    numbers_array = np.array(cleaned_numbers)

    # Calculate the mean and standard deviation of the numbers
    mean = np.mean(numbers_array)
    std_deviation = np.std(numbers_array) * 2

    # Select the data within 1 standard deviation of the mean
    selected_data = numbers_array[(numbers_array >= mean - std_deviation) & (numbers_array <= mean + std_deviation)]

    return selected_data


def grapherOriginal(lst1):
    fig, ax = plt.subplots()
    x1, y1 = [k[1] for k in lst1], [k[0] for k in lst1]
    plt.scatter(x1, y1, c='red')
    # plt.plot(x1, y1, c='red')
    plt.show()


def grapherSeveral(lst):
    colors = [
        "#1f77b4",  # Dark blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#17becf",  # Light blue
        "#7f7f7f",  # Gray
        "#bcbd22",  # Yellow
        "#ff9896",  # Light red
        "#98df8a",  # Light green
        "#ffbb78",  # Light orange
        "#aec7e8",  # Light purple
        "#c49c94",  # Light brown
        "#f7b6d2",  # Light pink
        "#1f78b4",  # Slightly different dark blue
        "#ff8f0e",  # Slightly different orange
        "#33a02c",  # Slightly different green
        "#e62728",  # Slightly different red
        "#7567bd",  # Slightly different purple
        "#9c564b",  # Slightly different brown
        "#ee77c2",  # Slightly different pink
        "#27becf",  # Slightly different light blue
        "#8f8f8f",  # Slightly different gray
        "#ccbd22",  # Slightly different yellow
        "#df9896",  # Slightly different light red
        "#88df8a",  # Slightly different light green
        "#dfbb78",  # Slightly different light orange
        "#bec7e8",  # Slightly different light purple
        "#c49c77",  # Slightly different light brown
        "#f788d2",  # Slightly different light pink
        "#1f77b4",  # Dark blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#17becf",  # Light blue
        "#7f7f7f",  # Gray
        "#bcbd22",  # Yellow
        "#ff9896",  # Light red
        "#98df8a",  # Light green
        "#ffbb78",  # Light orange
        "#aec7e8",  # Light purple
        "#c49c94",  # Light brown
        "#f7b6d2",  # Light pink
        "#1f78b4",  # Slightly different dark blue
        "#ff8f0e",  # Slightly different orange
        "#33a02c",  # Slightly different green
        "#e62728",  # Slightly different red
        "#7567bd",  # Slightly different purple
        "#9c564b",  # Slightly different brown
        "#ee77c2",  # Slightly different pink
        "#27becf",  # Slightly different light blue
        "#8f8f8f",  # Slightly different gray
        "#ccbd22",  # Slightly different yellow
        "#df9896",  # Slightly different light red
        "#88df8a",  # Slightly different light green
        "#dfbb78",  # Slightly different light orange
        "#bec7e8",  # Slightly different light purple
        "#c49c77",  # Slightly different light brown
        "#f788d2"  # Slightly different light pink
    ]
    counter = 0
    for x, i in enumerate(lst):
        x2, y2 = [k[0] for k in i], [k[1] for k in i]
        plt.scatter(x2, y2, c=colors[x])
        plt.plot(x2, y2, c=colors[x])
        # counter += 1
    plt.show()


def grapherSeveralWithText(lst, txt_lst):
    colors = [
        "#1f77b4",  # Dark blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#17becf",  # Light blue
        "#7f7f7f",  # Gray
        "#bcbd22",  # Yellow
        "#ff9896",  # Light red
        "#98df8a",  # Light green
        "#ffbb78",  # Light orange
        "#aec7e8",  # Light purple
        "#c49c94",  # Light brown
        "#f7b6d2",  # Light pink
        "#1f78b4",  # Slightly different dark blue
        "#ff8f0e",  # Slightly different orange
        "#33a02c",  # Slightly different green
        "#e62728",  # Slightly different red
        "#7567bd",  # Slightly different purple
        "#9c564b",  # Slightly different brown
        "#ee77c2",  # Slightly different pink
        "#27becf",  # Slightly different light blue
        "#8f8f8f",  # Slightly different gray
        "#ccbd22",  # Slightly different yellow
        "#df9896",  # Slightly different light red
        "#88df8a",  # Slightly different light green
        "#dfbb78",  # Slightly different light orange
        "#bec7e8",  # Slightly different light purple
        "#c49c77",  # Slightly different light brown
        "#f788d2",  # Slightly different light pink
        "#1f77b4",  # Dark blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#17becf",  # Light blue
        "#7f7f7f",  # Gray
        "#bcbd22",  # Yellow
        "#ff9896",  # Light red
        "#98df8a",  # Light green
        "#ffbb78",  # Light orange
        "#aec7e8",  # Light purple
        "#c49c94",  # Light brown
        "#f7b6d2",  # Light pink
        "#1f78b4",  # Slightly different dark blue
        "#ff8f0e",  # Slightly different orange
        "#33a02c",  # Slightly different green
        "#e62728",  # Slightly different red
        "#7567bd",  # Slightly different purple
        "#9c564b",  # Slightly different brown
        "#ee77c2",  # Slightly different pink
        "#27becf",  # Slightly different light blue
        "#8f8f8f",  # Slightly different gray
        "#ccbd22",  # Slightly different yellow
        "#df9896",  # Slightly different light red
        "#88df8a",  # Slightly different light green
        "#dfbb78",  # Slightly different light orange
        "#bec7e8",  # Slightly different light purple
        "#c49c77",  # Slightly different light brown
        "#f788d2"  # Slightly different light pink
    ]
    for x, i in enumerate(lst):
        x2, y2 = [k[0] for k in i], [k[1] for k in i]
        plt.scatter(x2, y2, c=colors[x])
        plt.plot(x2, y2, c=colors[x])
        for r in range(len(x2)):
            plt.text(x2[r], y2[r], txt_lst[x][r])
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
