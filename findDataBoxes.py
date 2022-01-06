import copy
import re
import statistics as st
from itertools import chain
import ModuleAgnostic

"""Use the pdfminer data, and find the data for the two boxed data sections at the bottom of the page. harder than you'd think"""


def findMain(lst):
    """These are the parameters we're looking for that occur inside each box."""
    data_parameters1 = ['Federal Lease Wells', 'Indian Lease Wells', 'State Lease Wells', 'Fee Lease Wells', 'Multi Lease']
    data_parameters2 = ['Total Wells Drilled', 'Total Non-Plugged Wells', 'Total Wells Capable of Producing', 'Total Holes not Completed']
    multi_lst = [[True for j in i if 'multi' in j[-1].lower()] for i in lst]

    """Location markers mark... the location. Returns the coordinates of the labels"""
    location_marker1, location_marker2 = locationMarkerFinder(lst, data_parameters1, data_parameters2)
    visual_lst = copy.deepcopy(location_marker1)
    visual_lst = [[i] for i in visual_lst]



    """For the left side, it's harder to determine due to the Producing/Shut-In headers above the data that can be used to find the coordinates"""
    count_data_left = findMatchingCount(lst)

    count_data_left = [sorted(count_data_left[i], key=lambda x: x[0]) for i in range(len(count_data_left))]

    for i in range(len(count_data_left)):
        if multi_lst[i] is True and len(count_data_left[i][0]) > len(count_data_left[i][1]):

            left, right = count_data_left[i][0][-1][0], count_data_left[i][0][-1][2]
            down, up = count_data_left[i][1][-1][1], count_data_left[i][1][-1][3]
            count_data_left[i][1].append([left, down, right, up, "1"])

        elif multi_lst[i] is True and len(count_data_left[i][0]) < len(count_data_left[i][1]):

            left, right = count_data_left[i][1][-1][0], count_data_left[i][1][-1][2]
            down, up = count_data_left[i][0][-1][1], count_data_left[i][0][-1][3]
            count_data_left[i][0].append([left, down, right, up, "1"])


    for i in range(len(count_data_left)):
        if multi_lst[i] is not True and len(count_data_left[i][0]) > 5:
            count_data_left[i][0] = count_data_left[i][0][:5]
        if multi_lst[i] is not True and len(count_data_left[i][1]) > 5:
            count_data_left[i][1] = count_data_left[i][1][:5]

    for i in range(len(visual_lst)):
        left_data = []
        for j in range(len(count_data_left[i])):
            visual_lst[i].append([])
            foo = [k for k in count_data_left[i][j] if isinstance(k, list)]
            for k in foo:
                visual_lst[i][j].append(k)
                # print('foo', k)
            # left_data.append(foo)
        # print('left', left_data)
        # visual_lst[i].append(left_data)

    # for i in visual_lst[i]:
    #     print(len(i))


    """Seperate the generated data into whether it is shut in or producing"""
    prod_lst = [[count_data_left[i][0][k][-1] for k in range(1, len(count_data_left[i][0]))] for i in range(len(count_data_left))]

    shut_lst = [[count_data_left[i][1][k][-1] for k in range(1, len(count_data_left[i][0]))] for i in range(len(count_data_left))]

    for i in range(len(prod_lst)):
        if len(prod_lst[i]) != 5:
            prod_lst[i].append("0")
        if len(shut_lst[i]) != 5:
            shut_lst[i].append("0")


    count_data_left = [[[data_parameters1[j], prod_lst[i][j], shut_lst[i][j]] for j in range(len(data_parameters1))] for i in range(len(count_data_left))]

    """Find the data for the right box"""

    count_data_right, marker_data_for_visuals = findBoxTotalCount(location_marker2, lst, data_parameters2)

    for i in range(len(marker_data_for_visuals)):
        for j in range(len(marker_data_for_visuals[i])):
            visual_lst[i].append(marker_data_for_visuals[i][j])
        visual_lst[i] = [r for r in visual_lst[i] if r]



    return count_data_left, count_data_right, visual_lst


def locationMarkerFinder(lst, data_parameters1, data_parameters2):
    location_marker1, location_marker2 = [], []

    """Parse the data O0"""
    for i in range(len(lst)):

        """Prepare for multivariate list"""
        location_marker1.append([])
        location_marker2.append([])
        for j in range(len(lst[i])):

            """take each parsed line and check to see if any of the labels occur there. If so, append that data to the list. """
            for r in data_parameters1:

                if lst[i][j][-1].lower() == r.lower():
                    location_marker1[i].append(lst[i][j])

            """take each parsed line and check to see if any of the labels occur there. If so, append that data to the list."""
            for r in data_parameters2:
                if r.lower() in lst[i][j][-1].lower():
                    location_marker2[i].append(lst[i][j])
                # if lst[i][j][-1].lower() == r.lower():
                #     location_marker2[i].append(lst[i][j])

        """Resort the data by y values"""
        location_marker1[i] = sorted(location_marker1[i], key=lambda x: x[1], reverse=True)
        location_marker2[i] = sorted(location_marker2[i], key=lambda x: x[1], reverse=True)
    location_marker1 = [i for i in location_marker1 if i]
    location_marker2 = [i for i in location_marker2 if i]
    return location_marker1, location_marker2


def findMatchingCount(lst):
    """Find occurences of the strings "producing" and "shut-in" """
    prod_shut_lst = [[lst[i][j] for j in range(len(lst[i])) if lst[i][j][-1].lower() == 'producing' or lst[i][j][-1].lower() == 'shut-in'] for i in range(len(lst))]
    prod_shut_lst = [i for i in prod_shut_lst if i]

    subset_lst = []
    """parse the data, blah blah blah"""
    for i in range(len(prod_shut_lst)):

        """Create a sublist"""
        subset_lst.append([])
        for j in range(len(prod_shut_lst[i])):
            """Create a sublist inside that sublist"""
            subset_lst[i].append([])

            """Assemble a list of numbers that occur directly below the producing and shut in strings"""
            subset_lst[i][j] = findSubsetList(lst, i, prod_shut_lst, subset_lst, j)

            """Resort the data by Y"""
            subset_lst[i][j] = sorted(subset_lst[i][j], key=lambda x: x[1], reverse=True)

            """Inser the label for whatever well count this is supposed to be"""
            subset_lst[i][j].insert(0, prod_shut_lst[i][j][-1])


    return subset_lst



def findSubsetList(lst, i, prod_shut_lst, subset_lst, j):
    """get boundary boxes"""
    pos_left, pos_down, pos_right, pos_up = prod_shut_lst[i][j][0], prod_shut_lst[i][j][1], prod_shut_lst[i][j][2], prod_shut_lst[i][j][3]
    for k in lst[i]:
        """Determine if the data is a number or a string (we want a number)"""
        if re.sub(r'[^0-9. ]+', '', k[-1]).strip() != '':
            k[-1] = re.sub(r'[^0-9. ]+', '', k[-1]).strip()
            """Get boundary boxes for that number"""
            all_left, all_down, all_right, all_up = k[0], k[1], k[2], k[3]
            all_avg_x = (all_right+all_left)/2
            """If the lowest bounds of the strings (producing/shut-in) are larger than the upper or lower bounds of the number
            Example:
            ____ <-- upper bound of string
            Producing <-- string
            ---- <-- lower bound of string
            ____ <-- upper bound of number
            43234 < -- number
            ____ <-- lower bound of number
            
            In other words, does the string occur above the number?"""
            if pos_down > all_up > all_down:

                """ if the string left bound is less than the number left bound is less than the number right bound is less than the string left bound +5...
                Example:
                string left bounds --> | "Producing" | <-- string right bounds
                number left bounds -->  | 2342342 | <- number right bounds
                In other words, does the number occur directly below the string?               
                """

                if pos_left < all_avg_x < pos_right + 5:
                    try:
                        float(k[-1])
                        subset_lst[i][j].append(k)
                    except ValueError:
                        pass

    return subset_lst[i][j]


def findBoxTotalCount(location_marker, lst, data_parameters2):
    lst_data = []
    missing_data = []

    for i in range(len(location_marker)):
        for j in range(len(location_marker[i])):
            if location_marker[i][j][-1] not in data_parameters2:
                location_marker[i][j] = []


    location_marker = [[i for i in r if i] for r in location_marker]

    for r in location_marker:
        missing_data.append([])
        found_labels = [i[-1] for i in r]
        for k in data_parameters2:
            if k not in found_labels:
                missing_data[-1].append(k)
    """Parse the data"""
    for i in range(len(location_marker)):


        """Append a sublist"""
        lst_data.append([])

        """Mark the maximum y value that can be obtained and add a little margin of error"""
        upperCap = location_marker[i][0][3] + 10

        for j in range(len(location_marker[i])):

            """Append a sublist to the sublist"""
            lst_data[i].append([])

            """Mark the positions of the location labels"""
            pos_left, pos_down, pos_right, pos_up = location_marker[i][j][0], location_marker[i][j][1], location_marker[i][j][2], location_marker[i][j][3]

            """Parse the original data"""
            for k in range(len(lst[i])):

                """Search if the data is a number (it should be)"""
                if re.sub(r'[^0-9]+', '', lst[i][k][-1]).strip() != '' and float(re.sub(r'[^0-9]+', '', lst[i][k][-1]).strip()) > 100:
                    lst[i][k][-1] = re.sub(r'[^0-9]+', '', lst[i][k][-1]).strip()

                    """Get the positions of the parsed number"""
                    all_left, all_down, all_right, all_up = lst[i][k][0], lst[i][k][1], lst[i][k][2], lst[i][k][3]

                    """ if the string left bound is less than the number left bound is less than the number right bound is less than the string left bound +5...
                    Example:
                    string left bounds --> | "Producing" | <-- string right bounds
                    number left bounds -->  | 2342342 | <- number right bounds
                    In other words, does the number occur directly below the string?                
                    
                    THEN
                    
                    If the lowest bounds of the strings (producing/shut-in) are larger than the upper or lower bounds of the number
                    Example:
                    ____ <-- upper bound of string
                    Producing <-- string
                    ---- <-- lower bound of string
                    ____ <-- upper bound of number
                    43234 < -- number
                    ____ <-- lower bound of number            
                    In other words, does the string occur above the number?
                    
                    """
                    if pos_left < pos_right < all_left < all_right and upperCap > all_up > all_down:
                        lst_data[i][j].append(lst[i][k])

    for i in range(len(lst_data)):
        try:
            lst_data[i] = sorted(lst_data[i], key=lambda x: x[1], reverse=True)
        except IndexError:
            pass

    """Resort the data"""
    parameter_lst = []
    for i in range(len(lst_data)):
        parameter_lst.append([])
        new_lst = []

        for j in range(len(lst_data[i])):
            if not lst_data[i][j]:
                lst_data[i][j] = [[0,0,0,0,'MISSING'],[0,0,0,0,'MISSING'],[0,0,0,0,'MISSING'],[0,0,0,0,'MISSING']]
        counter = 0
        for j in range(4):
            if data_parameters2[j] not in missing_data[i]:
                new_lst.append(lst_data[i][counter][counter])
                counter += 1
            else:
                new_lst.append([0,0,0,0,'MISSING'])



        for j in range(4):
            parameter_lst[i].append([data_parameters2[j], new_lst[j][-1]])

    """Combine the parameters into one list"""
    # parameter_lst = [[[data_parameters2[j], lst_data[i][j][j][-1]] for j in range(len(lst_data[i]))] for i in range(len(lst_data))]
    marker_data_for_visuals = copy.deepcopy(lst_data)
    for i in range(len(lst_data)):
        # print(location_marker[i])
        # printed_data = copy.deepcopy(lst_data[i])
        marker_data_for_visuals[i].append(location_marker[i])
        # printed_data.append(location_marker[i])
        # ModuleAgnostic.graphData(printed_data)

    return parameter_lst, marker_data_for_visuals
