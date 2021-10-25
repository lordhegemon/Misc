def findTotalOccurencesAndMatch(pos_lst, lst):
    bounds_lst = []
    for k in range(len(pos_lst)):

        """Mark the positions of the data"""
        pos_x1, pos_y1, pos_x2, pos_y2 = pos_lst[k][0], pos_lst[k][1], pos_lst[k][2], pos_lst[k][3]

        """Find occurences of the word "Total that is blow pos_y1"""
        pos_total_lst = [lst[j] for j in range(len(lst)) if lst[j][-1].lower() == 'total' and lst[j][3] < pos_y1] # find all occurences of Total

        """Remove empty data"""
        pos_total_lst = [[r for r in pos_total_lst[i] if r] for i in range(len(pos_total_lst))]

        occurence_lst = [searchForOccurencesBelowSection(pos_x1, pos_y1, pos_x2, pos_y2, pos_total_lst[i]) for i in range(len(pos_total_lst))]

        """Remove empty data"""
        occurence_lst = [j for j in occurence_lst if j]

        """use the 0th index"""
        occurence_lst = [j[0] for j in occurence_lst]

        """Get the average x width for the word"""
        pos_y_avg = (pos_y1 + pos_y2) / 2

        "Parse through the data, looking for occurences of the word 'total' that are closest to the label"
        used_index = findOccurenceToBeUsed(occurence_lst, pos_y_avg)

        bounds_lst.append([pos_lst[k][-1], pos_lst[k][0]-2, pos_lst[k][2]+2,  used_index[1]-2, pos_lst[k][1] + 2])
    return bounds_lst

"""The purpose here will be to determine the lower bounds of the word total, for designing the text box
This is a proximity based calculation"""
def findOccurenceToBeUsed(occurence_lst, pos_y_avg):
    min_dist_val, used_index = 9999, []
    for i in range(len(occurence_lst)):
        """Get the top and bottom of the occurence of total"""
        tot_y1, tot_y2 = occurence_lst[i][1], occurence_lst[i][3]
        """Get the average position"""
        tot_avg_y = (tot_y1 + tot_y2) / 2
        """get the difference for that value"""
        diff = pos_y_avg - tot_avg_y

        """Cycle through the data, checking to see the proximity difference between the label and the positon of the word total
        continue to adjust min_dist_val and used_index as shorter and shorter proximity is found"""
        if diff < min_dist_val:
            min_dist_val = diff
            used_index = occurence_lst[i]
    return used_index

def searchForOccurencesBelowSection(pos_left, pos_down, pos_right, pos_up, t_lst):
    occurence_lst = []
    t_left, t_down, t_right, t_up = t_lst[0], t_lst[1], t_lst[2], t_lst[3]

    """Check if the left boundary of the word 'total' occurs between the bounds of the label"""
    if pos_left < t_left < pos_right:

        """Check if the word occurs below the label"""
        if pos_down > t_up > t_down:
            occurence_lst.append(t_lst)
    return occurence_lst

