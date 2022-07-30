import math
import ModuleAgnostic as ma
from PyQt5.QtWidgets import QMainWindow, QApplication
import matplotlib.pylab as plt
from test_data import *
from PyQt5.QtCore import Qt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from PyQt5.QtGui import QGuiApplication
from matplotlib.widgets import Button
# self.canvas_individual_well.restore_region(self.background)

class MainAPDProgram(QMainWindow):
    def __init__(self, flag = True):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.fig, self.ax = plt.subplots()
        self.canvas = self.fig.canvas
        self.ui.mp.addWidget(self.canvas)
        self.canvas.mpl_connect('button_press_event', self.onClickIndividualSection)
        # self.canvas.mpl_connect('button_release_event', self.onReleaseIndividualSection)
        self.canvas.mpl_connect('motion_notify_event', self.onClickIndividualSection)
        self.draw_section_boo = True
        self.background_data = None
        self.coordinates = [[0, 0], [-6.264676031909604, 1325.3051936192717], [-11.717248442231444, 2651.563985241069],
                            [-17.169820852553283, 3977.8227768628667], [-22.62239326287512, 5304.081568484664], [1286.9973220663799, 5303.218075044675],
                            [2596.6170373956347, 5302.354581604686], [3906.226826710724, 5301.611728935967], [5216.116516303917, 5300.709954325495],
                            [5211.976939031065, 3978.9664366943316], [5205.964463576867, 2655.430093166541], [5199.95198812267, 1331.893749638751],
                            [5199.458178250363, 9.09384180997813], [3914.066635667868, -16.68414797577519], [2614.0787100784582, -11.081173610080544],
                            [1307.0405783925783, -5.511180873628965], [0.0024467066982651886, 0.05881186282261375]]

        # self.coordinates = [[0,0], [0, 1320], [0, 2640], [0, 3960], [0, 5280],
        #                [1320, 5280], [2640, 5280], [3960, 5280], [5280, 5280],
        #                [5280, 3960], [5280, 2640], [5280, 1320], [5280, 0],
        #                [3960, 0], [2640, 0], [1320, 0]]

        # self.pts_lines = self.ax.fill([], [])

        self.pts_text_ew = self.ax.text([], [], "", color='black')
        self.pts_text_ns = self.ax.text([], [], "", color='black')
        self.pts = self.ax.scatter([], [], c='black', s=50, zorder=2)

        self.pts_lines_ew, = self.ax.fill([], [], color='red', linewidth=2, zorder=1)
        self.pts_lines_ns, = self.ax.fill([], [], color='red', linewidth=2, zorder=1)
        self.segment_lines_ew, = self.ax.fill([], [], color='red', linewidth=3, zorder=1)
        self.segment_lines_ns, = self.ax.fill([], [], color='red', linewidth=3, zorder=1)


        self.polygon_coord = Polygon(self.coordinates)
        self.drawIndividualSections()


    def drawIndividualSections(self):
        x1, y1 = self.polygon_coord.exterior.xy
        self.ax.plot(x1, y1, color='blue', linewidth=.7, alpha=0.5)
        self.ax.scatter(x1, y1, c='blue', s=5, alpha=0.5)
        self.canvas.draw()
        # self.background_data = self.canvas.copy_from_bbox(self.ax.bbox)

    def onClickIndividualSection(self, event):
        ix, iy = event.xdata, event.ydata

        self.draw_section_boo = True
        try:
            if event.inaxes == self.ax:
                if self.draw_section_boo:
                    if self.polygon_coord.contains(Point(ix, iy)):

                        self.drawStuff(ix, iy, event)
                        self.canvas.draw()
        except TypeError:
            pass

    def onReleaseIndividualSection(self, event):
        self.canvas.draw()
        self.draw_section_boo = False
        self.canvas.blit(self.ax.bbox)

    def drawStuff(self, x, y, event):
        mods = QGuiApplication.queryKeyboardModifiers()
        if event.button == Qt.LeftButton and mods == Qt.ShiftModifier:
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

            # self.ax.draw_artist(self.pts)
            # self.ax.draw_artist(self.pts_lines_ew)
            # self.ax.draw_artist(self.pts_lines_ns)
            # self.ax.draw_artist(self.segment_lines_ew)
            # self.ax.draw_artist(self.segment_lines_ns)

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
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = MainAPDProgram()
    w.show()
    sys.exit(app.exec_())