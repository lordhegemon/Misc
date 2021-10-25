import re

def findPositions(lst):
    """Here, we'll find the positions for the appropriate sections"""
    positions_lst, positions2 = positionsListFinderMain(lst)

    """Here, we're sorting the data, but by the appropriate position it should be in, in the order.
    IE, 'New APDs - Not yet approved' must be followed by 'Approved APDS - Not yet spudded'"""
    sorted_lst = [[[j for j in r if i == j[-1]] for i in positions2] for r in positions_lst]

    """Check for garbage data"""
    sorted_lst = [[i for i in sorted_lst[r] if i] for r in range(len(sorted_lst))]

    """I'm not actually sure why I'm now resorting it by y value, but if I get rid of this, it breaks the code."""
    sorted_lst = [[sorted_lst[r][j][0] for j in range(len(sorted_lst[r]))] for r in range(len(sorted_lst))]

    return sorted_lst, positions2

def positionsListFinderMain(lst):
    """positions corresponds to a reduced label, while positions 2 corresponds to what it should be"""

    positions = ['new apds not yet approved', 'approved apds not yet spudded', 'producing wells', 'shut in wells', 'active service wells', 'spudded wells not yet completed', 'drilling operations suspended', 'inactive service wells', 'temporarily abandoned wells', 'plugged abandoned wells',
                 'locations abandoned', 'apds approved not yet spudded', 'wells spudded not yet completed']
    positions2 = ['New APDs - Not yet approved', 'Approved APDS - Not yet spudded', 'Producing Wells', 'Shut-in Wells', 'Active Service Wells', 'Spudded Wells - Not yet completed', 'Drilling operations suspended', 'Inactive Service Wells', 'Temporarily-Abandoned Wells', 'Plugged & Abandoned Wells',
                  'Locations Abandoned', 'Approved APDS - Not yet spudded', 'Spudded Wells - Not yet completed']
    positions_lst = []

    """Parse the data"""
    for i in lst:
        """append a sublist"""
        positions_lst.append([])
        for j in i:

            """check the positions list"""
            for k in range(len(positions)):

                """reedit the data into an easier format to process"""
                value = dataGather(j[-1])

                """check if the value exists, if the position exists in the value, and the value is not an empty string"""
                if value and positions[k] in value and value != '':

                    """append the data"""
                    positions_lst[-1].append([j[0], j[1], j[2], j[3], positions2[k]])

    """remove any empty indexes"""
    positions_lst = [i for i in positions_lst if i]
    return positions_lst, positions2


def dataGather(lst):
    """remove any uneeded data"""
    data = lst.replace("\n", " ").replace("†", "").lower().strip().replace(",", "").replace(" -", "-").replace("-", " ").replace("••", " ")

    """remove any non digits"""
    data = re.sub(r'[^a-zA-Z. ]+', '', data).strip()

    """split into a list"""
    data_lst = data.split(" ")

    """remove empty indexes"""
    data_lst = [i for i in data_lst if i]

    """join back into a list"""
    data_lst = " ".join(data_lst)
    return data_lst

