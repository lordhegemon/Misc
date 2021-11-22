import re
import os
import tkinter as tk
from tkinter import filedialog
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine

import ModuleAgnostic
import findPositionsForSections
import findOccurencesOfWordTotal
import IsolateAndMatchData
import findDataBoxes
from tika import parser
import CSVOrganizerAndPrinter
from difflib import SequenceMatcher
import itertools
"""
main() is the base function.
The first line and the try/except generate a prompt for a pdf and then run the process on that pdf.
The second section performs a parse through the folder where the .py file is currently location and runs the process off any pdfs located there. It will throw a general error if the pdf doesn't work.
"""


def main():
    print("Beginning")
    # counter = 1
    # i, fileName = getFileThroughPrompt()
    # runData([os.path.join(i, fileName)][0], fileName, counter)
    # try:
    #     runData([os.path.join(i, fileName)][0], fileName)
    # except Exception as e:
    #     print(e)
    # try:
    #     runData([os.path.join(i, fileName)], fileName)
    # except pdfminer.pdfparser.PDFSyntaxError:
    #     print('Not a pdf or not the right pdf format')
    counter = 1
    path = os.getcwd()
    for fileName in os.listdir(path):
        if os.path.isfile(os.path.join(path, fileName)) and 'pdf' in fileName:
            runData(os.path.join(path, fileName), fileName, counter)
            counter += 1
    print("Completed")


"""
RunData is the true main function that calls the correct various processes.
Two parses are performed, one through tika (which seemed to have a better time with parsing for dates)
And through pdfminer which generated coordinates for every text box.
Note: Finding the data is easy. Organizing the data, not much so.
"""


def runData(i, fileName, counter):
    print(i)
    print(fileName)
    """use tika parser to parse the data"""
    parsedData = parser.from_file(fileName)
    parsedDataContent = parsedData['content']

    """use the pdfminer parser to gather the data and coordinates"""
    text_data_edited = textBoxGather(i)

    """re-edit the text. Mostly rounding. Eliminating blank indexes"""
    text_data_edited = reeditText(text_data_edited)
    text_data_edited = [i for i in text_data_edited if i]

    """in the event that a pdf for a well is two pages, this merges the pages into one "page"
    See that section for better explanation"""

    text_data_edited, lst_page = pageMerger(text_data_edited)

    parsedDataContent_edit = list(itertools.chain.from_iterable(text_data_edited))
    """Use the tika parsed content to find the dates for each page"""
    date_lst = findCorrectDates(parsedDataContent_edit)

    """Use the pdfminer data, and find the data for the two boxed data sections at the bottom of the page"""
    count_data_left, count_data_right, visual_lst = findDataBoxes.findMain(text_data_edited)


    """Use the pdfminer data, find the data, organize it and return it. This only returns the coordinates for the LABEL on each section
    ie - Plugged & Abandoned Wells, Producing Wells, etc. 
    Positions2 returns a list of those labels for later use."""
    sorted_positions, positions2 = findPositionsForSections.findPositions(text_data_edited)


    """Takes the previous data and generates a bounding box for the data of each box. In otherwords, the previous function finds the coordinates for the label itself. 
    This gets the coordinates for the data that corresponds to that label
    Example: The coordinates given go from the top of the label "Producing Wells" to the bottom of the label "Total" that occurs below it."""
    bounded_lst = [findOccurencesOfWordTotal.findTotalOccurencesAndMatch(sorted_positions[i], text_data_edited[i]) for i in range(len(sorted_positions))]

    """This uses those bounding boxes and then finds the appropriate labels and their locations. In other words, it takes the bounding box defined previously, and finds the coordinates
    
     for each well count LABEL that occurs (Oil wells, gas wells, etc). It doesn't find the actual count number"""



    bounded_comp_lst = [IsolateAndMatchData.isolateData(text_data_edited[i], bounded_lst[i], sorted_positions[i]) for i in range(len(bounded_lst))]

    """This takes all previously Mused data and finds the actual counts, then formats the data"""
    tot_lst = []
    for i in range(len(bounded_comp_lst)):
        print("______________________________________________\nPage ", i)
        out, all_visual = IsolateAndMatchData.matchCountAndLabel(bounded_comp_lst[i], text_data_edited[i])
        tot_lst.append(out)
        test = bounded_comp_lst[i] + visual_lst[i] + all_visual

        # ModuleAgnostic.graphData(test)

    """Merge all the data into a list of sublists where each sublist corresponds to a page."""

    all_data_merged = [[date_lst[i] + tot_lst[i] + count_data_left[i] + count_data_right[i]] for i in range(len(tot_lst))]


    """Write to a csv"""
    CSVOrganizerAndPrinter.mainCSVProcess(all_data_merged, counter)


"""I'm not going to lie, I don't truthfully know how all this works. I just stole it off google and it worked."""


def textBoxGather(path):
    fp = open(path, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp, caching=False)
    counter = 0
    for i in pages:
        counter += 1
        try:
            interpreter.process_page(i)
            device.get_result()
        except TypeError:
            pass
    """Generate an actual list from the Aggregator
    Each entry consists of five components, x1, y1, x2, y2, and the text"""

    data_lst = textBoxGrouperDataManager(device, counter)
    return data_lst


def textBoxGrouperDataManager(device, counter):
    """create an empty list of sublists"""
    data_lst = [[] for p in range(counter + 1)]

    """parse through the aggregator and pull out the correct data"""
    for (page_nb, x_min, y_min, x_max, y_max, text) in device.rows:
        data_lst[page_nb].append([x_min, y_min, x_max, y_max, text])

    """Sort the data based on the y coordinates"""
    data_lst = [sorted(data_lst[i], key=lambda x: x[1], reverse=True) for i in range(len(data_lst)) if data_lst[i]]
    return data_lst


def reeditText(text_data_edited):
    """Round the data to three decimal places, mostly for peace of mind on my part"""
    for i in range(len(text_data_edited)):
        for j in range(len(text_data_edited[i])):
            text_data_edited[i][j][0], text_data_edited[i][j][1], text_data_edited[i][j][2], text_data_edited[i][j][3] = round(text_data_edited[i][j][0], 3), round(text_data_edited[i][j][1], 3), round(text_data_edited[i][j][2], 3), round(text_data_edited[i][j][3], 3)
    return text_data_edited


"""Page merger exists to examine and process monthly reports that are two pages long. 
This is done by:
Comparing the number of well reports to the number of pages in the pdf and noticing any missing pages
Generate a new list showing those merged pages, ie [0,2,3,4] -> [[0,1],2,3,4. This has identified that pages 0 and 1 are the same monthly report
"""


def pageMerger(lst):
    lst = pageMergerCorrector(lst)
    """
    all_pages just lists a total number of pages in the pdf"""
    all_pages = [i for i in range(len(lst))]
    """
    The phrase "well statuses" is used as a marker for the beginning of each monthly report. The following list is just a list of those pages. Any pages that don't have it are left as an empty sublist"""

    lst_page0 = [[i for j in range(len(lst[i])) if 'well statuses' in lst[i][j][-1].lower()] for i in range(len(lst))]
    lst_page = [[i for j in range(len(lst[i])) if 'federal lease' in lst[i][j][-1].lower()] for i in range(len(lst))]

    checker_lst_page = [i for i in lst_page if i]
    checker_lst_page0 = [i for i in lst_page0 if i]
    collapsed_lst_page0 = list(itertools.chain.from_iterable(lst_page0))
    pages = list(set(all_pages).intersection(list(itertools.chain.from_iterable(lst_page0))))


    if len(checker_lst_page) > len(checker_lst_page0):
        lst = correctForMissingWellStatuses(lst_page0, lst_page, lst)


    """
    Comparing the number of well reports to the number of pages in the pdf and noticing any missing pages
    Generate a new list showing those merged pages, ie [0,2,3,4] -> [[0,1],2,3,4. This has identified that pages 0 and 1 are the same monthly report"""
    for i in range(len(lst_page)):
        if not lst_page[i]:
            lst_page[i - 1].append(all_pages[i])

    """
    Remove any empty sublists that remain"""
    lst_page = [i for i in lst_page if i]



    """
    Adjust page y counts by 800 (roughly the height of a page) This effectively turns the two pages into one page that is twice as tall as a normal page"""
    modded_lst = pageMergerCorrectForTwoPages(lst_page, lst)

    """
    Given these are scanned pages, errors are expected. This module attempts to correct most of them."""

    modded_lst = pageMergerCorrector(modded_lst)

    """
    One error that required it's own module was a merging of Producing and Shut-in in the bottom of the report. This corrects that"""
    modded_lst = pageMergerShutInCorrector(modded_lst)
    return modded_lst, lst_page


"""
Merges the two pages, effectively creating one page twice as tall"""

def correctForMissingWellStatuses(lst_well, lst_new, lst_all):
    for i in range(len(lst_well)):
        if lst_well[i] != lst_new[i]:
            lst_all[i].insert(0, [61.2, 731.693, 258.799, 741.293, 'WELL STATUSES -- 99/99/99 99:99:99 PM'])
    return lst_all


def pageMergerCorrectForTwoPages(lst_page, lst):
    modded_lst = []

    """Parse through pages"""
    for i in range(len(lst_page)):
        modded_lst.append([])
        for j in range(len(lst_page[i])):

            """Determine if this is a two page record ([0,1] like in the list mentioned above"""
            if j > 0:
                """Add 800 to each y value, effectively making the page twice as tall. This shouldn't affect any of our processes"""
                modded_lst[i] = [[modded_lst[i][k][0], modded_lst[i][k][1] + 800, modded_lst[i][k][2], modded_lst[i][k][3] + 800, modded_lst[i][k][4]] for k in range(len(modded_lst[i]))]

            """Merge the data for those two pages into one page"""
            modded_lst[i] = modded_lst[i] + lst[lst_page[i][j]]
    return modded_lst


"""
Correct any common errors seen in the data due to scan quality"""


def pageMergerCorrector(modded_lst):
    """Each corrector component has two values. The first is the error, and the second is the corrected component"""
    corrector = [['wed.er', 'Water'], ['apos', 'APDs'], ['ap0s', 'APDs'], ['0~', 'Oil'], ['o~', 'Oil'], ['unkncwm', 'Unknown'], ['tnjecton', 'Injection'], ['lnjecton', 'Injection'], ['jnjecton', 'Injection'], ['wens', 'Wells'], ['TEMPORARIL Y-ABANOONED WELLS', 'Temporarily-Abandoned Wells'],
                 ['ABANOONED', 'Abandoned'], ['··', '-'], ['••', '-'], ['-·', '-'], ["SHUT -IN WELLS", "SHUT-IN WELLS"], ['TEMPORARILY-ABANDONED WELL~', 'TEMPORARILY-ABANDONED WELLS'], ['yijells', 'Wells'], ['cap?ble','Capable'], ['NEW APDs RECIEVED Not yet approved','New APDs - Not yet approved'],
                 ['drllled','Drilled'], ['fl!ew apds -- not yet approved', 'New APDs - Not yet approved'], ['r_il_le_d', 'Drilled'], ['---t-o-t-al-w-el-ls_d_','Total Wells'], ['1.ease', 'lease']]
    for i in range(len(modded_lst)):
        for j in range(len(modded_lst[i])):
            modded_lst[i][j][-1] = modded_lst[i][j][-1].replace('••', '- ')
            modded_lst[i][j][-1] = modded_lst[i][j][-1].replace('··', '- ')
            modded_lst[i][j][-1] = modded_lst[i][j][-1].replace('-·', '- ')
            modded_lst[i][j][-1] = modded_lst[i][j][-1].replace(r')', "")
            modded_lst[i][j][-1] = modded_lst[i][j][-1].replace(r'(', "")

            if len(modded_lst[i][j][-1]) > 1:
                # print(modded_lst[i][j])
                if modded_lst[i][j][-1][0] == '.':
                    modded_lst[i][j][-1] = modded_lst[i][j][-1][1:]
                elif modded_lst[i][j][-1][0] == "\'":
                    modded_lst[i][j][-1] = modded_lst[i][j][-1][1:]
                elif modded_lst[i][j][-1][-1] == '.':
                    modded_lst[i][j][-1] = modded_lst[i][j][-1][:-1]
                elif modded_lst[i][j][-1][-1] == "\'":
                    modded_lst[i][j][-1] = modded_lst[i][j][-1][:-1]
                if len(modded_lst[i][j][-1]) == 1:
                    modded_lst[i][j][-1] = 'NULL'

            if modded_lst[i][j][-1] == 'O':
                modded_lst[i][j][-1] = modded_lst[i][j][-1].replace(r'O', "0")
            modded_lst[i][j][-1] = modded_lst[i][j][-1].strip()

            """Take the text component of the line and transform it into a list"""
            bounded_comp_split = modded_lst[i][j][-1].split()
            """Parse the corrector list"""
            for k in corrector:

                """Parse the new list"""
                for p in range(len(bounded_comp_split)):
                    """Does the corrector value occur in that part of the new split list?"""
                    if k[0] in bounded_comp_split[p].lower():
                        """If so, transform it into the corrected component, then remerge the list"""
                        bounded_comp_split[p] = k[1]
                        modded_lst[i][j][-1] = " ".join(bounded_comp_split)

                """This additional check looks to see if the entire unsplit string matches any components and then corrects them."""

                if k[0].lower() == modded_lst[i][j][-1].lower():
                    modded_lst[i][j][-1] = k[1]
            modded_lst[i][j][-1] = doubleCheckLabels(modded_lst[i][j][-1])
    return modded_lst


"""Check for data gaps in the labels, such as W ater Injection versus Water Injection"""


def doubleCheckLabels(label):
    data = ['Oil Wells', 'Gas Wells', 'Coalbed Methane', 'Water Injection', 'Gas Injection', 'Water Disposal', 'Gas Storage', 'Water Source', 'Test Wells', 'Unknown Type', 'Total']
    for i in range(len(data)):
        data_lst, label_lst = [i for i in list(data[i]) if i != ' '], [i for i in list(label) if i != ' ']
        data_combined, label_combined = "".join(data_lst), "".join(label_lst)

        one_wrong_value_ratio = (len(data_lst) - 2) / len(data_lst)

        if SequenceMatcher(None, data_combined, label_combined).ratio() > one_wrong_value_ratio:
            return data[i]
        elif data[i] != label and data_combined == label_combined:
            return data[i]
    return label


"""Correct instances where "producing" and "shut-in" are merged into one component, versus 2"""


def pageMergerShutInCorrector(modded_lst):
    """
    Parse the data
    """
    for i in range(len(modded_lst)):
        for j in range(len(modded_lst[i])):
            """
            Check if the text component is shut in"""
            if modded_lst[i][j][-1].lower() == 'producing shut-in':
                """Get the xy components of that text component"""
                pos_left, pos_down, pos_right, pos_up = modded_lst[i][j][0], modded_lst[i][j][1], modded_lst[i][j][2], modded_lst[i][j][3]

                """These are previous measured values for that "Producing" and "Shut in" should be"""
                half1 = pos_left + 52.3
                half3 = pos_right - 37.5

                """We're effectively creating two new entries using the existing values, and the measured components.
                Example: 'producing shut in has a left bound where X = 100 and a right bound where X = 200
                The y component is irrelevant and is used.
                Now, the new entry for Producing uses the X =100 as its left bounds, but uses 152.3 as the right bound
                And the new entry for Shut in uses the right bound of 200, but the right bound of 200-37.5"""
                modded_lst[i].append([pos_left, pos_down, half1, pos_up, 'Producing'])
                modded_lst[i].append([half3, pos_down, pos_right, pos_up, 'Shut-In'])

                """delete the original component"""
                del modded_lst[i][j]
    return modded_lst


"""Find the correct dates using the tika parsed data"""


def findCorrectDates(parsedDataContent):
    """Reformat the parsed data"""
    parsedDataLst = [i[-1] for i in parsedDataContent]
    counter, lst = 0, []
    """Parse that data"""
    for i in range(len(parsedDataLst)):
        """Check for occurence of the string well status
        Expected output is something like: WELL STATUSES -- 03/10/15 03:25:07 PM """

        if 'well status' in parsedDataLst[i].lower():

            """Find occurence of the first colon, marking the clock time, ie: 03:25:07.
            Subtrace 2 to mark the two numbers occuring before that colon"""
            try:
                index = parsedDataLst[i].index(":") - 3
            except ValueError:
                index = len(parsedDataLst[i])-1

            """Get rid of the data after that index marker, then split into a list of components"""
            new_val_lst = parsedDataLst[i][:index].split()
            """Grab the component at the end. That should be the month"""
            date = new_val_lst[-1]

            """A common error occuring in the parser, is misinterpretting a / as a 1. Here we get a count of if that occurs. It should only occur twice"""
            count_slash = date.count("/")
            if count_slash == 0:
                date = '99/99/99'
                count_slash =2
            """If there are two of more slashes and the component at [2] or [5] is a 1 (should be a /), correct it through list splicing"""
            if count_slash < 2 and date[2] == '1':
                date = date[:2] + "/" + date[3:]
            elif count_slash < 2 and date[5] == '1':
                date = date[:5] + "/" + date[6:]

            """Counter is added to mark the page"""

            date = re.sub(r'[^0-9./ ]+', '', date).strip()
            re_com = re.compile(r"\d{2}[/]\d{2}[/]\d{2}")
            if re_com.search(date) is None:
                date = '99/99/99'
            lst.append([counter, date])
            counter += 1
    return lst


"""This just edits and processes the parsed data, getting rid of garbage strings, empty strings, etc."""


def textParserparsedDataSplitLines(parsedDataContent):
    parsedDataSplitLines = parsedDataContent.splitlines()
    parsedDataLst = []
    for i in range(len(parsedDataSplitLines)):
        if parsedDataSplitLines[i].isspace() or len(parsedDataSplitLines[i]) > 1 or re.compile(r"[\s]{1,5}").match(parsedDataSplitLines[i]) is not None:
            rawStr = parsedDataSplitLines[i].replace(",", "").replace("†", "")
            parsedDataLst.append(rawStr)
    return parsedDataLst


"""Standard file prompt script for manually finding a file location."""


def getFileThroughPrompt():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    directory = os.path.split(file_path)[0]
    name = file_path.replace(directory, "")[1:]
    return [directory, name]


"""Man, I don't even know. The overall purpose of this is a much more detailed aggregation than PDFPageAggregator.
I'd had issues where text boxes were getting merged that should be getting merged."""


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
                    row = (page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str)
                    self.rows.append(row)
                for child in item:
                    render(child, page_number)
            return

        render(ltpage, self.page_number)
        self.page_number += 1
        self.rows = sorted(self.rows, key=lambda x: (x[0], -x[2]))
        self.result = ltpage


main()
