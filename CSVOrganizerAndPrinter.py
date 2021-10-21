import csv
import re
import statistics as st
import math
import operator
import itertools

"""Csv wrtier takes the data and writs it into a component file.
All of the various lines just exist to take into account the formatting of the report."""


def mainCSVProcess(data, counter):
    data_names = ["DateRun", 'ReportPeriod', 'POW', 'PGW', 'CBPGW', 'SOW', 'SGW', 'CBSGW', 'AWI', 'AGI', 'AWD', 'AGS', 'AWS', 'ATW', 'IWI', 'IGI', 'IWD', 'IGS', 'IWS', 'ITW', 'TA', 'PA', 'LA', 'NEWOW', 'NEWGW', 'NEWGWCB', 'NEWWI', 'NEWGI', 'NEWWD', 'NEWGS', 'NEWWS', 'NEWTW', 'NEWUNK', 'APDOW',
                  'APDGW', 'APDGWCB', 'APDWI', 'APDGI', 'APDWD', 'APDGS', 'APDWS', 'APDTW', 'APDUNK', 'SPUDOW', 'SPUDGW',
                  'SPUDGWCB', 'SPUDWI', 'SPUDGI', 'SPUDWD', 'SPUDGS', 'SPUDWS', 'SPUDTW', 'SPUDUNK', 'OPS', 'TOTDRILLED', 'TOTNONPA', 'TOTCAPPROD', 'TOTNOTCOMP', 'FEDPROD', 'FEDSI', 'INDPROD', 'INDSI', 'STPROD', 'STSI', 'FEEPROD', 'FEESI', 'MULTPROD', 'MULTISI']

    for i in range(len(data)):
        for j in range(len(data[i])):
            for k in range(len(data[i][j])):
                lst_out = checkReorder(data[i][j][k], k)
                if isinstance(lst_out, list):
                    data[i][j][k] = lst_out
                    pass
                else:
                    data[i][j][k] = [lst_out]


    assembled_data_lst = [[assembleDataIntoFormat(j) for j in i][0] for i in data]

    assembled_data_lst = lastMinuteEditor(assembled_data_lst)

    assembled_data_lst = dataQuickCorrector(assembled_data_lst)

    assembled_data_lst = checkForStrangeValues(assembled_data_lst)

    assembled_data_lst.insert(0, data_names)

    csvWriterMain(assembled_data_lst, counter)


def checkReorder(lst, k):
    reordered_lst = []
    order = ['Oil Wells', 'Gas Wells', 'Coalbed Methane', 'Water Injection', 'Gas Injection', 'Water Disposal', 'Gas Storage', 'Water Source', 'Test Wells', 'Unknown Type', 'Total']
    ignore_lst = ['Temporarily-Abandoned Wells', 'Plugged & Abandoned Wells', 'Locations Abandoned', 'Federal Lease Wells', 'Indian Lease Wells', 'State Lease Wells', 'Fee Lease Wells', 'Multi Lease', 'Total Wells Drilled', 'Total Non-Plugged Wells', 'Total Wells Capable of Producing', 'Total Holes not Completed']

    if k > 1:
        if lst[0] not in ignore_lst:
            for i in order:
                for j in lst:
                    if i == j[0]:
                        reordered_lst.append(j)
            reordered_lst.insert(0, lst[0])
            return reordered_lst

    # else:
    return lst


def words_in_string(word_list, a_string):
    return set(word_list).intersection(a_string.split())


def regexByData(i, data):
    for j in range(1, len(i)):
        if re.search(data, i[j][0], re.IGNORECASE) is not None:
            try:
                data = int(float(i[j][1]))
                return data
            except ValueError:
                return i[j][1]


"""checks and attempts to fix missing data values using science"""




def assembleDataIntoFormat(lst):
    POW, PGW, CBPGW, SOW, SGW, CBSGW, AWI, AGI, AWD, AGS,\
    AWS, ATW, IWI, IGI, IWD, IGS, IWS, ITW, TA, PA,\
    LA, NEWOW, NEWGW, NEWGWCB, NEWWI, NEWGI, NEWWD, NEWGS, NEWWS, NEWTW,\
    NEWUNK, APDOW, APDGW, APDGWCB, APDWI, APDGI, APDWD, APDGS, APDWS, APDTW,\
    APDUNK, SPUDOW, SPUDGW, SPUDGWCB, SPUDWI, SPUDGI, SPUDWD, SPUDGS, SPUDWS,\
    SPUDTW, SPUDUNK, OPS, TOTDRILLED, TOTNONPA, TOTCAPPROD, TOTNOTCOMP, FEDPROD,\
    FEDSI, INDPROD, INDSI, STPROD, STSI, FEEPROD, FEESI, MULTPROD, MULTISI = "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing",\
                                                                             "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing", "Missing"
    DateRun = 'NULL'

    for i in lst:

        reg_date1 = re.compile(r"[\d]{2}[/\//][\d]{2}[/\//][\d]{2}")
        if reg_date1.search(str(i[0])) is not None:
            DateRun = i[0]
        try:
            if re.search(r'Producing Wells', i[0], re.IGNORECASE) is not None:
                POW = regexByData(i, r'Oil Wells')
                PGW = regexByData(i, r'Gas Wells')
                CBPGW = regexByData(i, r'Coalbed Methane')
            elif re.search(r'New APDs - Not yet approved', i[0], re.IGNORECASE) is not None:
                NEWOW = regexByData(i, r'Oil Wells')
                NEWGW = regexByData(i, r'Gas Wells')
                NEWGWCB = regexByData(i, r'Coalbed Methane')
                NEWWI = regexByData(i, r'Water Injection')
                NEWGI = regexByData(i, r'Gas Injection')
                NEWWD = regexByData(i, r'Water Disposal')
                NEWGS = regexByData(i, r'Gas Storage')
                NEWWS = regexByData(i, r'Water Source')
                NEWTW = regexByData(i, r'Test Wells')
                NEWUNK = regexByData(i, r'Unknown Type')
            elif re.search(r'Approved APDS - Not yet spudded', i[0], re.IGNORECASE) is not None:
                APDOW = regexByData(i, r'Oil Wells')
                APDGW = regexByData(i, r'Gas Wells')
                APDGWCB = regexByData(i, r'Coalbed Methane')
                APDWI = regexByData(i, r'Water Injection')
                APDGI = regexByData(i, r'Gas Injection')
                APDWD = regexByData(i, r'Water Disposal')
                APDGS = regexByData(i, r'Gas Storage')
                APDWS = regexByData(i, r'Water Source')
                APDTW = regexByData(i, r'Test Wells')
                APDUNK = regexByData(i, r'Unknown Type')

            elif re.search(r'Shut-in Wells', i[0], re.IGNORECASE) is not None:
                SOW = regexByData(i, r'Oil Wells')
                SGW = regexByData(i, r'Gas Wells')
                CBSGW = regexByData(i, r'Coalbed Methane')

            elif re.search(r'Active Service Wells', i[0], re.IGNORECASE) is not None and 'inactive' not in i[0].lower():
                AWI = regexByData(i, r'Water Injection')
                AGI = regexByData(i, r'Gas Injection')
                AWD = regexByData(i, r'Water Disposal')
                AGS = regexByData(i, r'Gas Storage')
                AWS = regexByData(i, r'Water Source')
                ATW = regexByData(i, r'Test Wells')

            elif re.search(r'Drilling operations suspended', i[0], re.IGNORECASE) is not None:
                OPS = regexByData(i, r'Total')
            elif re.search(r'Inactive Service Wells', i[0], re.IGNORECASE) is not None:
                IWI = regexByData(i, r'Water Injection')
                IGI = regexByData(i, r'Gas Injection')
                IWD = regexByData(i, r'Water Disposal')
                IGS = regexByData(i, r'Gas Storage')
                IWS = regexByData(i, r'Water Source')
                ITW = regexByData(i, r'Test Wells')
            elif re.search(r'Plugged & Abandoned Wells', i[0], re.IGNORECASE) is not None:
                PA = regexByData(i, r'Total')
            elif re.search(r'Temporarily-Abandoned Wells', i[0], re.IGNORECASE) is not None:
                TA = regexByData(i, r'Total')
            elif re.search(r'Locations Abandoned', i[0], re.IGNORECASE) is not None:
                LA = regexByData(i, r'Total')
            elif re.search(r'Federal Lease Wells', i[0], re.IGNORECASE) is not None:
                FEDPROD, FEDSI = i[1], i[2]
            elif re.search(r'Indian Lease Wells', i[0], re.IGNORECASE) is not None:
                INDPROD, INDSI = i[1], i[2]
            elif re.search(r'State Lease Wells', i[0], re.IGNORECASE) is not None:
                STPROD, STSI = i[1], i[2]
            elif re.search(r'Fee Lease Wells', i[0], re.IGNORECASE) is not None:
                FEEPROD, FEESI = i[1], i[2]
            elif re.search(r'Multi Lease', i[0], re.IGNORECASE) is not None:
                MULTPROD, MULTISI = i[1], i[2]
            elif re.search(r'Total Wells Drilled', i[0], re.IGNORECASE) is not None:
                TOTDRILLED = i[1]
            elif re.search(r'Total Non-Plugged Wells', i[0], re.IGNORECASE) is not None:

                TOTNONPA = i[1]
            elif re.search(r'Total Wells Capable of Producing', i[0], re.IGNORECASE) is not None:

                TOTCAPPROD = i[1]
            elif re.search(r'Total Holes not Completed', i[0], re.IGNORECASE) is not None:

                TOTNOTCOMP = i[1]
            elif re.search(r'Spudded Wells - Not yet completed', i[0], re.IGNORECASE) is not None:
                SPUDOW, SPUDGW, SPUDGWCB, SPUDWI, SPUDGI, SPUDWD, SPUDGS, SPUDWS, SPUDTW, SPUDUNK = i[1][1], i[2][1], i[3][1], i[4][1], i[5][1], i[6][1], i[7][1], i[8][1], i[9][1], i[10][1]
        except (AttributeError, TypeError):
            pass

    data = [DateRun, 'ReportPeriod', POW, PGW, CBPGW, SOW, SGW, CBSGW, AWI, AGI, AWD, AGS, AWS, ATW, IWI, IGI, IWD, IGS, IWS, ITW, TA, PA, LA, NEWOW, NEWGW, NEWGWCB, NEWWI, NEWGI, NEWWD, NEWGS, NEWWS, NEWTW, NEWUNK, APDOW, APDGW, APDGWCB, APDWI, APDGI, APDWD, APDGS, APDWS, APDTW, APDUNK, SPUDOW,
            SPUDGW, SPUDGWCB, SPUDWI, SPUDGI, SPUDWD, SPUDGS, SPUDWS, SPUDTW, SPUDUNK, OPS, TOTDRILLED, TOTNONPA, TOTCAPPROD, TOTNOTCOMP, FEDPROD, FEDSI, INDPROD, INDSI, STPROD, STSI, FEEPROD, FEESI, MULTPROD, MULTISI]
    for i in range(len(data)):
        if data[i] == '':
            data[i] = "Missing"

    return data


def csvWriterMain(lst, counter):
    name = "MonthlyWellData" + str(counter) + ".csv"
    file = open(name, 'w+', newline='')
    with file:
        filewriter = csv.writer(file)
        for x in lst:

            filewriter.writerow(x)


def lastMinuteEditor(lst):
    for i in range(len(lst)):
        for j in range(len(lst[i])):
            val = str(lst[i][j])
            val_split = val.split()
            for k in range(len(val_split)):
                val_split[k] = val_split[k].strip()
            try:
                lst[i][j] = int(float("".join(val_split)))
            except ValueError:
                # pass
                lst[i][j] = "".join(val_split)
    return lst
    pass


def dataQuickCorrector(lst):
    data_lst, reassemble_lst = [], []
    if len(lst) > 10:
        for i in range(len(lst[0])):
            data_column = [lst[j][i] for j in range(len(lst))]
            only_data_column = [lst[j][i] for j in range(len(lst)) if not isinstance(lst[j][i], str)]
            if 'Missing' in data_column and not all(ele == 'Missing' for ele in data_column):
                min_data, max_data = min(only_data_column), max(only_data_column)
                data_mode, data_mean = st.multimode(only_data_column)[0], st.mean(only_data_column)
                if max_data < 4 or data_mode < 2 and data_mean < 2:
                    data_column[:] = [x if x != 'Missing' else 1 for x in data_column]
                else:
                    pass
            data_lst.append(data_column)
    if data_lst:
        for i in range(len(data_lst[0])):
            reassemble_lst.append([data_lst[j][i] for j in range(len(data_lst))])
        return reassemble_lst
    else:
        return lst



"""this function is designed to look in a data list for values that are too high to be correct."""


def checkForStrangeValues(lst):
    wrong_data, reassemble_lst, all_data = [], [], []
    if len(lst) > 10:
        for i in range(len(lst[0])):
            data_column = [lst[j][i] for j in range(len(lst))]
            """Transform data into columns"""
            only_data_column = [lst[j][i] for j in range(len(lst)) if not isinstance(lst[j][i], str)]
            only_data_column_stats = sorted(only_data_column)

            try:
                """Fix the data to check for outliers"""
                percent_val = math.floor(0.1 * len(only_data_column))
                only_data_column_stats = only_data_column_stats[percent_val:(-1 * percent_val)]
                st_dev, data_mean = st.stdev(only_data_column_stats) + 1, math.ceil(st.mean(only_data_column_stats))
                """Generate a dictionary where values are grouped by relative proximity (in this case, two standard deviations"""
                dictPlan = dict(enumerate(grouper(sorted(only_data_column), st_dev * 2), 1))
                dict_lst = [j for t, j in dictPlan.items()]

                """I wanted to create a value that would weight depending on the size of the values. IE, it will flag when the standard deviation is 2 and the mean is 3, vs std dev of 2 and the mean of 150
                Basically, a flag is raised if it sees a value in a list like [1,1,1,3,2,2,13], vs [145,149,155,150,167]"""
                eval_val = round(data_mean / st_dev, 2)
                if len(dict_lst) > 1:
                    wrong_data = checkDataMeanMax(dict_lst, data_mean, eval_val)
                """Replace any values found to be flagged with Missing"""
                only_data_column = [x if x not in wrong_data else 'Missing' for x in data_column]
                all_data.append(only_data_column)
            except:
                all_data.append(data_column)
            # all_data.append(only_data_column)

    all_data = [i for i in all_data if i]
    if all_data:
        for i in range(len(all_data[0])):
            reassemble_lst.append([all_data[j][i] for j in range(len(all_data))])
        return reassemble_lst
    else:
        return lst


"""Evaluate the above data for flags
Again, the idea is to be looking for data values that are too far away to be correct
The eval_val parameter is weighted so that it gets larger as the average of the dataset gets larger. I'm sure there's an actual name for it."""


def checkDataMeanMax(dict_lst, data_mean, eval_val):
    len_lst, wrong_data = [len(i) for i in dict_lst], []
    """Get the index of the list in our dictionary list with the most values. This is highly likely to be the correct assemblage of values for this column"""
    index, max_val = max(enumerate(len_lst), key=operator.itemgetter(1))
    main_lst = dict_lst[index]
    for j in range(len(dict_lst)):
        if j != index:
            lst_mean, lst_max, lst_min = st.mean(dict_lst[j]), max(dict_lst[j]), min(dict_lst[j])
            """Check if the flagged list averages is above or below the average of the dataset. Then check the difference between the min/max of the flagged data, versus the main data
            Then it's kind of like we're checking to see if it is larger than two... standard deviations?"""
            if lst_mean < data_mean:
                difference = abs(min(main_lst) - lst_min)
                if eval_val * 2 < difference:
                    wrong_data.append(dict_lst[j])
            elif lst_mean > data_mean:
                difference = abs(max(main_lst) - lst_max)

                if eval_val * 2 < difference:
                    wrong_data.append(dict_lst[j])
    wrong_data = list(set(list(itertools.chain.from_iterable(wrong_data))))
    return wrong_data

def grouper(iterable, val):
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= val:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group


