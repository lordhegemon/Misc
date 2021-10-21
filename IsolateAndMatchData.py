import copy
import re
import statistics as st
from itertools import chain
import ModuleAgnostic


def isolateData(lst, bound_lst, pos_lst):
    bounded_comp = initCompilers(lst, bound_lst)


    for i in range(len(bounded_comp)):
        """sort data by y values"""
        bounded_comp[i] = sorted(bounded_comp[i], key=lambda x: x[1], reverse=True)

        """insert the label """
        bounded_comp[i].insert(0, pos_lst[i])

        """Remove any numbers that get picked up"""
        bounded_comp[i] = [bounded_comp[i][j] for j in range(len(bounded_comp[i])) if not re.sub(r'[^a-zA-Z. ]+', '', bounded_comp[i][j][-1]).strip() == '']
        for r in range(len(bounded_comp[i])):
            if 'coalbed' in bounded_comp[i][r][-1].lower():
                bounded_comp[i][r][-1] = bounded_comp[i][r][-1].replace("(", "").replace("{", "")

    return bounded_comp


def boundedCompCorrector(bounded_comp, i, corrector):
    for r in range(len(bounded_comp[i])):
        bounded_comp_split = bounded_comp[i][r][-1].split()
        for j in corrector:
            for p in range(len(bounded_comp_split)):
                if j[0] in bounded_comp_split[p].lower():
                    bounded_comp_split[p] = j[1]
        bounded_comp[i][r][-1] = " ".join(bounded_comp_split)
        bounded_comp[i][r][-1] = bounded_comp[i][r][-1].replace("·", "-").replace("SHUT -IN WELLS", "SHUT-IN WELLS")
        if 'coalbed' in bounded_comp[i][r][-1].lower():
            bounded_comp[i][r][-1] = bounded_comp[i][r][-1].replace("(", "").replace("{", "")
    return bounded_comp[i]


def initCompilers(lst, bound_lst):
    bounded_comp = []

    """parse the data"""
    for i in range(len(bound_lst)):

        """append a sublist"""
        bounded_comp.append([])

        """Get the coordinates for the label"""
        pos_x_min, pos_x_max, pos_y_min, pos_y_max = bound_lst[i][1], bound_lst[i][2], bound_lst[i][3], bound_lst[i][4]

        """Parse the data sublist"""
        for j in range(len(lst)):

            """Get the coordinates for the value we're parsing"""
            val_x_min, val_x_max, val_y_min, val_y_max = lst[j][0], lst[j][2], lst[j][1], lst[j][3]

            """Does the data fit into a y area"""
            if pos_y_max > val_y_max > val_y_min > pos_y_min:
                """Does the data ft into an x area?"""
                if pos_x_min < val_x_min < val_x_max < pos_x_max:
                    bounded_comp[i].append(lst[j])

                else:

                    """try doing a different check, just to see if part of the data lies between the appropriate bounds"""
                    if pos_x_min < val_x_min < pos_x_max:

                        """odds are, this is probably the coalbed methane line"""
                        if 'coal' in lst[j][-1].lower() or 'wells' in lst[j][-1].lower():
                            bounded_comp[i].append(lst[j])
    return bounded_comp


"""Take the date and match and format it"""


def matchCountAndLabel(lst, all_data_lst):
    tot_lst = []
    all_visual = []

    for i in lst:

        if i[0][2] < 350:
            align = "L"
        else:
            align = "R"
        tot_lst.append([])
        set_lst = matchCountAndLabelSetListMaker(i, all_data_lst, align)
        foo_lst = copy.deepcopy(set_lst)
        foo_lst = [i[0] for i in foo_lst]
        # end([pos_left, pos_right, pos_down, pos_up, all_left, all_right, all_down, all_up, j[-1], align_line[-1]])
        foo_lst = [[k[4], k[6], k[5], k[7], k[-1]] for k in foo_lst]
        # foo_lst = [[k[0], k[2], k[1], k[3], k[-1]] for k in foo_lst]

        all_visual.append(foo_lst)
        set_lst = sorted([ele[0] for ele in set_lst], key=lambda x: x[2], reverse=True)


        tot_lst[-1].append([i[0][-1], ""])
        for p in range(len(set_lst)):
            """Ditch non depths"""
            editedDepth = re.sub(r'[^0-9. ]+', '', set_lst[p][-1]).strip()

            """Append the label and the well count"""
            tot_lst[-1].append([set_lst[p][-2], editedDepth])

        """Compare the formatted list with the original list of found labels. If there's a difference in length, an miscount has occured."""
        if len(i) != len(tot_lst[-1]):
            """Search for which parameter is missing and return the parameter"""
            missing = findMissingData(i, tot_lst[-1])
            returned_lst = missingDataRangeFinder(i, all_data_lst, missing)
            tot_lst[-1] = tot_lst[-1] + returned_lst
            tot_lst[-1] = resortData(tot_lst[-1])

    """"Ditch the extra space"""
    for i in range(len(tot_lst)):
        tot_lst[i][0] = tot_lst[i][0][0]
    return tot_lst, all_visual


def matchCountAndLabelSetListMaker(i, all_data_lst, align):
    set_lst = []
    value_coordinates = []
    for r in range(1, len(i)):
        align_value = 99999
        align_line = ['foo']
        set_lst.append([])
        j = i[r]
        pos_left, pos_down, pos_right, pos_up = j[0], j[1], j[2], j[3]
        for k in all_data_lst:
            if re.sub(r'[^a-zA-Z. ]+', '', k[-1]).strip() == '':
                all_left, all_down, all_right, all_up = k[0], k[1], k[2], k[3]
                avg_pos, avg_all = round(st.mean([pos_up, pos_down]), 2), round(st.mean([all_up, all_down]), 2)
                avg_x_pos, avg_x_all = round(st.mean([pos_left, pos_right]), 2), round(st.mean([all_left, all_right]), 2)
                avg_diff = round(avg_pos - avg_all, 2)

                if testLeftAlign(align, avg_x_all, pos_right, avg_diff) or testRightAlign(align, avg_x_all, all_left, avg_diff):

                    if re.sub(r'[^0-9. ]+', '', k[-1]).strip() != '' and re.sub(r'[^a-zA-Z. ]+', '', k[-1]).strip() == '':
                        if abs(avg_diff) < align_value:
                            align_value = abs(avg_diff)
                            align_line = k
                            tru_diff = avg_diff
                            label_line = j
                            if abs(tru_diff) > 5:
                                left, right = align_line[0], align_line[2]
                                down, up = label_line[1], label_line[3]
                                set_lst[-1].append([label_line[0], label_line[1], label_line[2], label_line[3], left, down, right, up, j[-1], "MANUAL CHECK"])
                            else:
                                set_lst[-1].append([pos_left, pos_right, pos_down, pos_up, all_left, all_right, all_down, all_up, j[-1], align_line[-1]])

        set_lst = sorted([y for y in set_lst if y], key=lambda x: x[0])
        for u in range(len(set_lst)):
            right_left_align = [[i[4], i[5]] for i in set_lst[u]]
            avg_align = [sum(i) / 2 for i in right_left_align]
            if len(set_lst[u]) > 1:
                for j in range(len(set_lst[u])):
                    if align == 'L' and avg_align[j] < 350:
                        set_lst[u] = [set_lst[u][j]]
                    elif align == 'R' and avg_align[j] > 350:
                        set_lst[u] = [set_lst[u][j]]

                set_lst[u] = set_lst[u][:1]
    return set_lst


def testLeftAlign(align, avg_x_all, pos_right, avg_diff):
    if align == 'L' and avg_x_all < 350 and avg_x_all > pos_right and avg_diff >= -5:
        return True
    return False


def testRightAlign(align, avg_x_all, all_left, avg_diff):
    if align == 'R' and avg_x_all > 330 and avg_x_all > all_left and avg_diff >= -5:
        return True
    return False


def findMissingData(expected, found):
    expected_data = [i[-1] for i in expected]
    found_data = [i[0] for i in found]

    """Search for which data is missing from the list"""
    missing = set(expected_data) ^ set(found_data)

    """transform back to a list"""
    missing = list(missing)
    return missing


def missingDataRangeFinder(i, lst, miss_data):
    missing_lst, combo_lst = [], []
    for w in range(len(miss_data)):
        missing_lst.append([])
        """What follows is the usual position compare I've done before that is attempting to find values are in the correct alignment to correspend to each label."""
        for r in range(1, len(i)):
            j = i[r]
            pos_left, pos_down, pos_right, pos_up = j[0], j[1], j[2], j[3]
            for k in lst:
                all_left, all_down, all_right, all_up = k[0], k[1], k[2], k[3]
                if pos_left < all_left < all_right:
                    """Check if data is a string"""
                    if re.sub(r'[^a-zA-Z. ]+', '', k[-1]).strip() == '':

                        """Does the data match with the missing parameters found previously?"""
                        if j[-1].lower() == miss_data[w].lower():
                            """This attempts to find the vertical overlap between the two datapoints.
                            IE, how closely are two values along a horizontal line overlapping?"""
                            diff = abs(all_down - pos_up)
                            dist_pos_y, dist_all_y = abs(pos_up - pos_down), abs(all_up - all_down)
                            overlap_pos, overlap_all = diff / dist_pos_y, diff / dist_all_y
                            """If the overlap is more than 50%, then do this"""
                            if 1 > overlap_pos > 0.5 and 1 > overlap_all > 0.5:
                                missing_lst[w].append([overlap_pos, overlap_all, k[-1]])
        """Check to make sure data is a list"""
        missing_lst[w] = [list(t) for t in set(tuple(element) for element in missing_lst[w])]

        """Check for count of missing data and if two data values are found. Odds are very unlikely this will happen, but it could."""
        if len(missing_lst[w]) > 1:
            """Merge the missing data"""
            data_val_lst = [i[0] + i[1] for i in missing_lst[w]]

            """Find the index of the larger value"""
            index_val = data_val_lst.index(max(data_val_lst))

            """Return that data"""
            out = missing_lst[w][index_val][-1]

        elif len(missing_lst[w]) == 0:
            """As mentioned before, the OCR has a hard time with lone "1"s on the image and will sometimes not scan them. Subsequently, if the missing_lst turns up nothing, the missing value is very like a 1"""
            out = "MANUAL CHECK"
        else:
            """Or just return the last value in the missing data lst for the first datapoint"""
            out = missing_lst[w][0][-1]
            # out = "MANUAL CHECK"
        combo_lst.append([miss_data[w], out])
    return combo_lst


"""Reorder the data in order for it to be sorted with the proper strings"""


def resortData(lst):
    ordered_lst = [lst[0]]
    data = ['Oil Wells', 'Gas Wells', 'Coalbed Methane', 'Water Injection', 'Gas Injection', 'Water Disposal', 'Gas Storage', 'Water Source', 'Test Wells', 'Unknown Type', 'Total']
    for i in data:
        for j in lst:
            if j[0] == i:
                ordered_lst.append(j)

    return ordered_lst
