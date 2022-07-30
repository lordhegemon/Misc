import math
import ModuleAgnostic as ma
from PyQt5.QtWidgets import QMainWindow, QApplication
import matplotlib.pylab as plt
from matplotlib.collections import LineCollection, PolyCollection, RegularPolyCollection, PathCollection, PatchCollection
from matplotlib import patches
from test_data import *
from PyQt5.QtCore import Qt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from itertools import chain
from PyQt5.QtGui import QGuiApplication
from shapely.ops import unary_union
from scipy.spatial.distance import cdist
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import numpy as np
from matplotlib.widgets import Button
# self.canvas_individual_well.restore_region(self.background)
import random


class MainAPDProgram(QMainWindow):
    def __init__(self, flag=True):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.fig, self.ax = plt.subplots()
        self.canvas = self.fig.canvas
        self.ui.mp.addWidget(self.canvas)
        self.draw_section_boo = True
        self.background_data = None
        self.colors = ['black', 'red', 'blue']
        self.canvas.mpl_connect('button_press_event', self.onClickIndividualSection)
        # self.canvas.mpl_connect('button_release_event', self.onReleaseIndividualSection)
        self.canvas.mpl_connect('motion_notify_event', self.onClickIndividualSection)

        self.coordinates = [[[0, 0], [-6.264676031909604, 1325.3051936192717], [-11.717248442231444, 2651.563985241069],
                             [-17.169820852553283, 3977.8227768628667], [-22.62239326287512, 5304.081568484664], [1286.9973220663799, 5303.218075044675],
                             [2596.6170373956347, 5302.354581604686], [3906.226826710724, 5301.611728935967], [5216.116516303917, 5300.709954325495],
                             [5211.976939031065, 3978.9664366943316], [5205.964463576867, 2655.430093166541], [5199.95198812267, 1331.893749638751],
                             [5199.458178250363, 9.09384180997813], [3914.066635667868, -16.68414797577519], [2614.0787100784582, -11.081173610080544],
                             [1307.0405783925783, -5.511180873628965], [0.0024467066982651886, 0.05881186282261375]],
                            [[0, 0], [0, 1320], [0, 2640], [0, 3960], [0, 5280],
                             [1320, 5280], [2640, 5280], [3960, 5280], [5280, 5280],
                             [5280, 3960], [5280, 2640], [5280, 1320], [5280, 0],
                             [3960, 0], [2640, 0], [1320, 0]]]

        self.wells_data = []
        for j in range(3):
            self.wells_data.append([])
            for i in range(5):
                x = random.randint(100, 3000)
                y = random.randint(100, 3000)
                self.wells_data[j].append([x, y])

        # self.wells_data = [[[100, 100], [100, 500], [100, 2000]],
        #                    [[2000, 100], [2000, 500], [2000, 2000]]]

        # self.wells_buffer = [
        #     [[70.1444581998341, 2002.940514209887], [70.5764415879031, 2005.852709660484], [71.29178992803375, 2008.7085403176338], [72.28361402466142, 2011.4805029709528], [73.54236206954937, 2014.14190210478], [75.05591163092366, 2016.667106990588], [76.80968639911792, 2019.0317985249094],
        #      [78.7867965644036, 2021.2132034355964], [80.96820147509065, 2023.190313600882], [83.33289300941195, 2024.9440883690763], [85.8580978952201, 2026.4576379304506], [88.51949702904733, 2027.7163859753387], [91.29145968236614, 2028.7082100719663], [94.14729033951616, 2029.423558412097],
        #      [97.05948579011319, 2029.8555418001658], [100.0, 2030.0], [102.94051420988681, 2029.8555418001658], [105.85270966048384, 2029.423558412097], [108.70854031763386, 2028.7082100719663], [111.48050297095268, 2027.7163859753387], [114.14190210477992, 2026.4576379304506],
        #      [116.66710699058805, 2024.9440883690763], [119.03179852490935, 2023.190313600882], [121.21320343559641, 2021.2132034355964], [123.19031360088209, 2019.0317985249094], [124.94408836907634, 2016.667106990588], [126.45763793045063, 2014.14190210478],
        #      [127.7163859753386, 2011.4805029709528], [128.70821007196625, 2008.7085403176338], [129.4235584120969, 2005.852709660484], [129.8555418001659, 2002.940514209887], [130.0, 2000.0], [130.0, 100.0], [129.8555418001659, 97.05948579011314], [129.4235584120969, 94.14729033951612],
        #      [128.70821007196625, 91.2914596823661], [127.7163859753386, 88.51949702904727], [126.45763793045063, 85.85809789522004], [124.94408836907634, 83.33289300941192], [123.19031360088209, 80.96820147509062], [121.21320343559641, 78.78679656440356], [119.03179852490935, 76.80968639911788],
        #      [116.66710699058805, 75.05591163092363], [114.14190210477992, 73.54236206954934], [111.48050297095268, 72.28361402466139], [108.70854031763388, 71.29178992803374], [105.85270966048385, 70.57644158790309], [102.94051420988683, 70.14445819983409], [100.00000000000001, 70.0],
        #      [97.0594857901132, 70.14445819983409], [94.14729033951616, 70.57644158790308], [91.29145968236615, 71.29178992803372], [88.51949702904733, 72.28361402466139], [85.8580978952201, 73.54236206954934], [83.33289300941196, 75.05591163092362], [80.96820147509065, 76.80968639911788],
        #      [78.7867965644036, 78.78679656440355], [76.80968639911792, 80.96820147509061], [75.05591163092367, 83.33289300941189], [73.54236206954937, 85.85809789522004], [72.28361402466142, 88.51949702904727], [71.29178992803375, 91.29145968236608], [70.5764415879031, 94.14729033951609],
        #      [70.1444581998341, 97.05948579011313], [70.0, 100.0], [70.0, 2000.0], [70.1444581998341, 2002.940514209887]],
        #     [[1970.1444581998342, 2002.940514209887], [1970.576441587903, 2005.852709660484], [1971.2917899280337, 2008.7085403176338], [1972.2836140246613, 2011.4805029709528], [1973.5423620695494, 2014.14190210478], [1975.0559116309237, 2016.667106990588], [1976.809686399118, 2019.0317985249094],
        #      [1978.7867965644036, 2021.2132034355964], [1980.9682014750906, 2023.190313600882], [1983.332893009412, 2024.9440883690763], [1985.85809789522, 2026.4576379304506], [1988.5194970290472, 2027.7163859753387], [1991.2914596823662, 2028.7082100719663], [1994.147290339516, 2029.423558412097],
        #      [1997.0594857901133, 2029.8555418001658], [2000.0, 2030.0], [2002.9405142098867, 2029.8555418001658], [2005.852709660484, 2029.423558412097], [2008.7085403176338, 2028.7082100719663], [2011.4805029709528, 2027.7163859753387], [2014.14190210478, 2026.4576379304506],
        #      [2016.667106990588, 2024.9440883690763], [2019.0317985249094, 2023.190313600882], [2021.2132034355964, 2021.2132034355964], [2023.190313600882, 2019.0317985249094], [2024.9440883690763, 2016.667106990588], [2026.4576379304506, 2014.14190210478], [2027.7163859753387, 2011.4805029709528],
        #      [2028.7082100719663, 2008.7085403176338], [2029.423558412097, 2005.852709660484], [2029.8555418001658, 2002.940514209887], [2030.0, 2000.0], [2030.0, 100.0], [2029.8555418001658, 97.05948579011314], [2029.423558412097, 94.14729033951612], [2028.7082100719663, 91.2914596823661],
        #      [2027.7163859753387, 88.51949702904727], [2026.4576379304506, 85.85809789522004], [2024.9440883690763, 83.33289300941192], [2023.190313600882, 80.96820147509062], [2021.2132034355964, 78.78679656440356], [2019.0317985249094, 76.80968639911788], [2016.667106990588, 75.05591163092363],
        #      [2014.14190210478, 73.54236206954934], [2011.4805029709528, 72.28361402466139], [2008.7085403176338, 71.29178992803374], [2005.852709660484, 70.57644158790309], [2002.9405142098867, 70.14445819983409], [2000.0, 70.0], [1997.0594857901133, 70.14445819983409],
        #      [1994.147290339516, 70.57644158790308], [1991.2914596823662, 71.29178992803372], [1988.5194970290472, 72.28361402466139], [1985.85809789522, 73.54236206954934], [1983.332893009412, 75.05591163092362], [1980.9682014750906, 76.80968639911788], [1978.7867965644036, 78.78679656440355],
        #      [1976.809686399118, 80.96820147509061], [1975.0559116309237, 83.33289300941189], [1973.5423620695494, 85.85809789522004], [1972.2836140246613, 88.51949702904727], [1971.2917899280337, 91.29145968236608], [1970.576441587903, 94.14729033951609], [1970.1444581998342, 97.05948579011313],
        #      [1970.0, 100.0], [1970.0, 2000.0], [1970.1444581998342, 2002.940514209887]]
        # ]

        self.box = QtWidgets.QCheckBox("Awesome?", self)
        self.buffer = QtWidgets.QLineEdit("", self)
        self.buffer.setGeometry(QtCore.QRect(6, 91, 147, 17))
        self.box.stateChanged.connect(self.onCheckRunStuff)
        self.buffer.returnPressed.connect(self.onCheckRunStuff)

        self.pts_wells = self.ax.scatter([], [], c='black', s=50, zorder=3)
        self.polygon_shape, = self.ax.fill([], [], linewidth=5, zorder=1, alpha=0.5)

        self.pts_text_ew = self.ax.text([], [], "", color='black')
        self.pts_text_ns = self.ax.text([], [], "", color='black')
        self.pts = self.ax.scatter([], [], c='black', s=50, zorder=2)

        self.pts_lines_ew, = self.ax.fill([], [], color='red', linewidth=2, zorder=1)
        self.pts_lines_ns, = self.ax.fill([], [], color='red', linewidth=2, zorder=1)
        self.segment_lines_ew, = self.ax.fill([], [], color='red', linewidth=3, zorder=1)
        self.segment_lines_ns, = self.ax.fill([], [], color='red', linewidth=3, zorder=1)

        self.well_lines = LineCollection([])
        self.ax.add_collection(self.well_lines)
        self.well_buffer_polygons = PolyCollection([])
        self.ax.add_collection(self.well_buffer_polygons)

        # self.well_buffer_polygons = PolyCollection(self.wells_buffer)
        # self.ax.add_collection(self.well_buffer_polygons)

        self.polygon_coord = Polygon(self.coordinates[0])
        self.drawIndividualSections()

    def drawIndividualSections(self):
        x1, y1 = self.polygon_coord.exterior.xy
        self.ax.plot(x1, y1, color='blue', linewidth=.7)
        self.ax.scatter(x1, y1, c='blue', s=5)
        self.canvas.draw()

    def onCheckRunStuff(self):
        used_polygons = []
        used_lines = []
        if self.box.isChecked():
            try:
                buffer_distance = float(self.buffer.text())
            except ValueError:
                buffer_distance = 0
            used_polygons = [LineString(self.wells_data[i]).buffer(buffer_distance) for i in range(len(self.wells_data)) if buffer_distance > 0]
            self.drawTheWells(self.wells_data)
            # for i in range(len(self.wells_data)):
            #     self.drawTheWells(self.wells_data[i])
            polygons_output = unary_union(used_polygons)
            if buffer_distance > 0:
                self.drawBufferPolygon(polygons_output)
            # try:
            #     self.drawBufferPolygon(polygons_output)
            # except TypeError:
            #     pass
            # try:
            #     for geom in polygons_output.geoms:
            #         self.drawBufferPolygon(geom)
            # except AttributeError:
            #     self.drawBufferPolygon(polygons_output)

        else:
            self.clearTheWells()
            self.canvas.draw()

    # def drawTheWells(self, well):  # polygon_shape):
    #     self.pts_wells.set_offsets(well)
    #     self.ax.draw_artist(self.pts_wells)
    #     self.canvas.blit(self.ax.bbox)
    # def drawBufferPolygon(self, polygon):
    #     x, y = polygon.exterior.xy
    #     polygon = list(zip(x, y))
    #     self.polygon_shape.set_color('red')
    #     self.polygon_shape.set_xy(polygon)
    #     self.ax.draw_artist(self.polygon_shape)
    #     self.canvas.blit(self.ax.bbox)

    def drawTheWells(self, well):  # polygon_shape):
        self.well_lines.set_segments(well)
        # foo = LineCollection(well)
        # self.ax.add_collection(foo)
        # self.well_lines.set_array(foo)

        all_well_pts = list(chain.from_iterable(well))
        self.pts_wells.set_offsets(all_well_pts)
        self.ax.draw_artist(self.pts_wells)
        self.ax.draw_artist(self.well_lines)
        self.canvas.blit(self.ax.bbox)

    def drawBufferPolygon(self, polygons_output):
        polygons_all = []
        try:
            for geom in polygons_output.geoms:
                x, y = geom.exterior.coords.xy
                polygon = list(zip(x, y))
                polygon = [list(i) for i in polygon]
                polygon = np.array(polygon)
                polygons_all.append(polygon)
            self.well_buffer_polygons.set_paths(polygons_all)
            self.ax.draw_artist(self.well_buffer_polygons)
        except AttributeError:
            x, y = polygons_output.exterior.xy
            polygon = list(zip(x, y))
            self.polygon_shape.set_color('red')
            self.polygon_shape.set_xy(polygon)
            self.ax.draw_artist(self.polygon_shape)
        self.canvas.blit(self.ax.bbox)

    def clearTheWells(self):
        cleared_lst = [[None, None] for i in range(len(self.wells_data))]
        cleared_collection = [[[None, None], [None, None]] for i in range(len(self.wells_data))]

        self.well_lines.set_segments(cleared_collection)
        self.pts_wells.set_offsets(cleared_lst)
        self.polygon_shape.set_xy([[None, None], [None, None], [None, None]])
        self.ax.draw_artist(self.pts_wells)
        self.ax.draw_artist(self.polygon_shape)
        self.ax.draw_artist(self.well_lines)

    def onClickIndividualSection(self, event):
        ix, iy = event.xdata, event.ydata
        self.draw_section_boo = True
        mods = QGuiApplication.queryKeyboardModifiers()
        self.canvas.blit(self.ax.bbox)
        try:
            if event.button == Qt.LeftButton and mods == Qt.ShiftModifier:
                if event.inaxes == self.ax:
                    if self.draw_section_boo:
                        if self.polygon_coord.contains(Point(ix, iy)):
                            self.drawStuff(ix, iy, event)
                            self.canvas.draw()
        except TypeError:
            pass
        # self.canvas.blit(self.ax.bbox)

    def onReleaseIndividualSection(self, event):
        self.canvas.draw()
        self.draw_section_boo = False
        # self.canvas.blit(self.ax.bbox)

    def drawStuff(self, x, y, event):
        # mods = QGuiApplication.queryKeyboardModifiers()
        # if event.button == Qt.LeftButton and mods == Qt.ShiftModifier:
        dist_ns, dist_ew, mp_ns, mp_ew, original_ns_segment, original_ew_segment, pts = self.lineSegmentsForManualPointing(self.coordinates[0], [x, y])
        outline_ns = [pts[1], pts[0], pts[1]]
        outline_ew = [pts[1], pts[2], pts[1]]
        segment_ew = [original_ew_segment[0], original_ew_segment[1], original_ew_segment[0]]
        segment_ns = [original_ns_segment[0], original_ns_segment[1], original_ns_segment[0]]
        text_ns = [((pts[1][0] + pts[0][0]) / 2), ((pts[1][1] + pts[0][1]) / 2)]
        text_ew = [((pts[1][0] + pts[2][0]) / 2), ((pts[1][1] + pts[2][1]) / 2)]

        self.pts_text_ew.set_position(text_ew)
        self.pts_text_ew.set_text(dist_ew)

        self.pts_text_ns.set_position(text_ns)
        self.pts_text_ns.set_text(dist_ns)

        self.pts_lines_ew.set_xy(outline_ew)
        self.pts_lines_ns.set_xy(outline_ns)

        self.segment_lines_ew.set_xy(segment_ew)
        self.segment_lines_ns.set_xy(segment_ns)
        self.pts.set_offsets(pts)

    def lineSegmentsForManualPointing(self, data, pt):
        ix, iy = pt[0], pt[1]
        output, ns_side, ew_side = self.sortAllDataIntoSides(data, pt)

        ns_m1, ns_b1 = ma.slopeFinder(ns_side[0], ns_side[1])
        if ns_m1 == 0:
            ns_m1 = 0.00000001
        ns_m2 = -1 / ns_m1
        ns_b2 = iy - (ns_m2 * ix)

        ew_m1, ew_b1 = ma.slopeFinder(ew_side[0], ew_side[1])
        if ew_m1 == 0:
            ew_m1 = 0.00000001
        ew_m2 = -1 / ew_m1
        ew_b2 = iy - (ew_m2 * ix)

        intersect_ns = ma.lineIntersectionPt(ns_m1, ns_m2, ns_b1, ns_b2)
        intersect_ew = ma.lineIntersectionPt(ew_m1, ew_m2, ew_b1, ew_b2)
        pts = [intersect_ns, [ix, iy], intersect_ew]
        mp_ns, mp_ew = [(intersect_ns[0] + ix) / 2, (intersect_ns[1] + iy) / 2], [(intersect_ew[0] + ix) / 2, (intersect_ew[1] + iy) / 2]
        return float(output[0]), float(output[2]), mp_ns, mp_ew, ns_side, ew_side, pts

    def sortAllDataIntoSides(self, lst, pt):
        ew_labels = ['FEL', 'FWL']
        ns_labels = ['FSL', 'FNL']
        corners, sides_generated = ma.cornerGeneratorProcess(lst)
        sides_generated = [[j[:-1] for j in i] for i in sides_generated]
        left_lst, up_lst, right_lst, down_lst = sides_generated[0], sides_generated[1], sides_generated[2], sides_generated[3]
        left_lst, up_lst, right_lst, down_lst = sorted(left_lst, key=lambda x: x[1]), sorted(up_lst, key=lambda x: x[0]), sorted(right_lst, key=lambda x: x[1], reverse=True), sorted(down_lst, key=lambda x: x[0], reverse=True)

        right_lst_segments = [[right_lst[i], right_lst[i + 1]] for i in range(len(right_lst) - 1)]
        left_lst_segments = [[left_lst[i], left_lst[i + 1]] for i in range(len(left_lst) - 1)]

        down_lst_segments = [[down_lst[i], down_lst[i + 1]] for i in range(len(down_lst) - 1)]
        up_lst_segments = [[up_lst[i], up_lst[i + 1]] for i in range(len(up_lst) - 1)]

        ew_lsts = [right_lst_segments, left_lst_segments]
        ns_lsts = [down_lst_segments, up_lst_segments]
        distance_down, down_index = self.directionDistanceFinder(down_lst, pt)
        distance_up, up_index = self.directionDistanceFinder(up_lst, pt)
        distance_right, right_index = self.directionDistanceFinder(right_lst, pt)
        distance_left, left_index = self.directionDistanceFinder(left_lst, pt)

        ns_lst, ew_lst = [distance_down, distance_up], [distance_right, distance_left]
        ns_index_lst, ew_index_lst = [down_index, up_index], [right_index, left_index]

        ew_true_index = ew_lst.index(min(ew_lst))
        ns_true_index = ns_lst.index(min(ns_lst))

        ew_correct_sides = ew_lsts[ew_true_index]
        ns_correct_sides = ns_lsts[ns_true_index]

        ns_index = ns_index_lst[ns_true_index]
        ew_index = ew_index_lst[ew_true_index]

        ns_side = ns_correct_sides[ns_index]
        ew_side = ew_correct_sides[ew_index]

        ew_true_label = ew_labels[ew_true_index]
        ns_true_label = ns_labels[ns_true_index]

        ns_distance = min(ns_lst)
        ew_distance = min(ew_lst)

        return [str(ns_distance), ns_true_label, str(ew_distance), ew_true_label], ns_side, ew_side

    def directionDistanceFinder(self, lst, pt):
        distance_lst = self.parallelLineDistancePointFinder(lst, pt)
        index = self.findProximalIndex(lst, pt)
        distance = distance_lst[index]
        return distance, index

    def parallelLineDistancePointFinder(self, line, pt):
        eq_lst = [list(ma.slopeFinder(line[i], line[i + 1])) for i in range(len(line) - 1)]
        eq_lst = [i for i in eq_lst if str(i[0]) != 'nan' and i[0] != 0]
        distance_lst = [round(self.dist(i[0], i[1], pt[1] - (i[0] * pt[0])), 3) for i in eq_lst if i[0] != 0]
        return distance_lst

    def dist(self, m, b1, b2):
        top = abs(b2 - b1)
        bottom = math.sqrt(m ** 2 + 1)
        d = top / bottom
        return d

    def findProximalIndex(self, lst, pt):
        x, y = pt[0], pt[1]
        eq_lst = [ma.slopeFinder(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]
        eq_lst = [list(i) for i in eq_lst]
        pts_used_lst = [[lst[i], lst[i + 1]] for i in range(len(lst) - 1)]
        pts_used_lst = [list(i) for i in pts_used_lst]

        combo_list = list(zip(pts_used_lst, eq_lst))
        combo_list = [i for i in combo_list if str(i[1][0]) != 'nan' and i[1][0] != 0]
        pts_used_lst = [i[0] for i in combo_list]
        eq_lst = [i[1] for i in combo_list]
        for i in range(len(pts_used_lst)):
            x1, y1 = pts_used_lst[i][0][0], pts_used_lst[i][0][1]
            x2, y2 = pts_used_lst[i][1][0], pts_used_lst[i][1][1]
            m = eq_lst[i][0]
            m = 1 / m * -1
            if m != 0:
                b1 = y1 - (m * x1)
                b2 = y2 - (m * x2)
                line1 = (m * x) + b1 - y
                line2 = (m * x) + b2 - y
                between_line_boo = True if line1 * line2 < 0 else False
                if between_line_boo:
                    return i


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainAPDProgram()
    w.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
