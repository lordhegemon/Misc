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
# self.canvas_individual_well_individual_well.restore_region(self.background)
import random


class MainAPDProgram(QMainWindow):
    def __init__(self, flag=True):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.fig, self.ax_graphic_individual_well = plt.subplots()
        self.canvas_individual_well = self.fig.canvas
        self.ui.mp.addWidget(self.canvas_individual_well)
        self.draw_section_boo = True
        self.background_data = None
        self.colors = ['black', 'red', 'blue']
        self.canvas_individual_well.mpl_connect('button_press_event', self.onClickIndividualSection)
        self.canvas_individual_well.mpl_connect('button_release_event', self.onReleaseIndividualSection)
        self.canvas_individual_well.mpl_connect('motion_notify_event', self.onClickIndividualSection)

        self.ind_plot_1, self.ind_plot_2, self.ind_plot_3, self.ind_plot_4, self.ind_plot_5, self.ind_plot_6, self.ind_plot_7, self.ind_plot_8 = None, None, None, None, None, None, None, None
        self.plot_var = [self.ind_plot_1, self.ind_plot_2, self.ind_plot_3, self.ind_plot_4, self.ind_plot_5, self.ind_plot_6, self.ind_plot_7, self.ind_plot_8]
        self.scatter1, self.scatter2, self.scatter3, self.scatter4, self.scatter5, self.scatter6, self.scatter7, self.scatter8 = None, None, None, None, None, None, None, None
        self.coordinates1 = [[[0, 0], [-5.452572410321839, 1326.2587916217974], [-10.905144820643677, 2652.517583243595], [-16.357717230965516, 3978.7763748653924], [-22.62239326287512, 5304.081568484664], [1286.9973220663799, 5303.218075044675], [2596.6170373956347, 5302.354581604686],
                              [3906.226826710724, 5301.611728935967], [5216.116516303917, 5300.709954325495], [5211.976939031065, 3978.9664366943316], [5205.964463576867, 2655.430093166541], [5199.95198812267, 1331.893749638751], [5199.458178250363, 9.09384180997813],
                              [3914.066635667868, -16.68414797577519], [2614.0787100784582, -11.081173610080544], [1307.0405783925783, -5.511180873628965], [0.0024467066982651886, 0.05881186282261375]],
                             [[5199.458178250363, 9.09384180997813], [5199.95198812267, 1331.893749638751], [5205.964463576868, 2655.430093166541], [5211.976939031066, 3978.966436694331], [5216.116516303917, 5300.709954325495], [6534.083763451847, 5308.4543423134455],
                              [7852.051010599776, 5316.1987303013975], [9170.018257747706, 5323.943118289348], [10487.985504895636, 5331.6875062773], [10505.074819067824, 4009.087907214482], [10522.16413324001, 2686.488308151665], [10539.253447412197, 1363.888709088848],
                              [10556.342761584385, 41.28911002603081], [9217.37741075796, 27.15012539961433], [7998.151397675002, 21.310037914232097], [6598.80474819203, 15.197413209454382], [5199.458098709059, 9.084788504676665]],
                             [[5274.722417280049, -5263.778079616335], [5255.950851826577, -3946.4418168381385], [5237.179286373105, -2629.105554059942], [5218.318692541082, -1310.010382777633], [5199.458098709059, 9.084788504675998], [6598.804748192031, 15.19741320945377],
                              [7998.151397675002, 21.310037914231543], [9217.37741075796, 27.1501253996139], [10556.342761584385, 41.28911002603127], [10557.582758009099, -1277.1003068417112], [10558.822754433813, -2595.4897237094538], [10559.053068080737, -3915.0897036107963],
                              [10559.28338172766, -5234.689683512139], [9238.010566683652, -5241.428550307177], [7918.077930596666, -5248.198978097211], [6596.400898350248, -5255.990796389604], [5274.723866103831, -5263.782614681997]],
                             [[5293.586098552862, -10542.748916543285], [5288.870540440604, -9223.007341077964], [5284.154982328347, -7903.265765612641], [5279.439424216089, -6583.52419014732], [5274.723866103831, -5263.782614681998], [6596.400898350249, -5255.990796389605],
                              [7918.077930596666, -5248.198978097212], [9238.010566683653, -5241.428550307178], [10559.28338172766, -5234.68968351214], [10573.07871762797, -6580.028955520282], [10580.686094512457, -7901.947066227953], [10589.402523705252, -9217.13818247765],
                              [10603.047922774655, -10546.598157047865], [10603.047922774655, -10546.598157047865], [7954.201848781186, -10528.195320598485], [6622.206516991922, -10534.446415831422], [5290.211185202659, -10540.697511064358]]
                             ]
        self.coordinates2 = [[[0, 0], [4.884823767675411, 1313.6409178298152], [9.680339546146772, 2627.242164452404], [-0.42397490319480546, 3945.4734399611852], [-10.053317581338842, 5216.206955950902], [1301.1113184964743, 5219.957422446714], [2635.834851132124, 5256.3653862542615],
                              [3971.42185914976, 5293.023702016165], [5284.589583512617, 5290.578995146906], [5294.6072891281965, 3956.6466106257867], [5272.313348483678, 2633.094357101001], [5260.544222126085, 1320.2271078846993], [5248.775095768491, 7.3598586683974645],
                              [3936.71693108733, 5.165298689047401], [2624.3380890122567, 3.4219474078208503], [1312.159204892659, 1.7106699176618843], [-0.019679226938478678, -0.0006075724970817653]],
                             [[-10.067179113189013, 5216.221977573101], [-4.011911532680236, 6549.178223904739], [2.0433560478285404, 7882.134470236376], [8.098623628337318, 9215.090716568013], [14.153891208846094, 10548.04696289965], [1323.214216710651, 10543.014160786706],
                              [2636.4491847668787, 10546.649580206511], [3956.871537452823, 10542.155647928907], [5277.632406057158, 10537.244348353197], [5279.311183746095, 9230.555426763412], [5281.304178381057, 7917.18693891532], [5282.902467757879, 6603.757911380498],
                              [5284.589583512617, 5290.578995146906], [3971.42185914976, 5293.023702016163], [2635.8348511321246, 5256.36538625426], [1301.1113184964747, 5219.957422446713], [-10.053317581338433, 5216.2069559509]],
                             [[5284.589583512617, 5290.578995146906], [5282.902467757879, 6603.757911380498], [5281.304178381057, 7917.18693891532], [5279.311183746094, 9230.555426763412], [5277.632406057158, 10537.244348353197], [6522.429007354302, 10540.153196764411],
                              [7767.225608651445, 10543.06204517563], [9103.807488291384, 10547.721135018946], [10440.389367931322, 10552.380224862263], [10440.804049185681, 9236.470290201287], [10441.21873044004, 7920.5603555403095], [10441.186718435085, 6599.970355928306],
                              [10441.154706430134, 5279.380356316303], [9123.237773535106, 5282.223662238029], [7805.320840640078, 5285.066968159756], [6544.593867682596, 5287.829676516521], [5283.8668947251135, 5290.592384873287]],
                             [[10441.154706430134, 5279.380356316303], [10438.29957515615, 6596.857262613111], [10435.444443882168, 7914.334168909919], [10435.834904573408, 9234.634111173209], [10436.22536526465, 10554.9340534365], [11761.525299459385, 10554.51641312189],
                              [13086.825233654119, 10554.09877280728], [14412.125167848855, 10553.68113249267], [15737.425102043588, 10553.26349217806], [15729.245202126232, 9232.038813428324], [15721.065302208877, 7910.814134678588], [15712.88540229152, 6589.589455928852],
                              [15704.705502374163, 5268.364777179117], [14388.818388442829, 5271.120768735548], [13072.931274511491, 5273.876760291981], [11757.044160580155, 5276.632751848412], [10441.15704664882, 5279.388743404844]]]
        self.coordinates = self.coordinates1
        self.wells_data = []
        for j in range(3):
            self.wells_data.append([])
            for i in range(5):
                x = random.randint(100, 3000)
                y = random.randint(100, 3000)
                self.wells_data[j].append([x, y])

        self.wellbore_locate_graphic_checkbox = QtWidgets.QCheckBox("Awesome?", self)
        self.change_well_box = QtWidgets.QCheckBox("Change?", self)
        self.change_well_box.setGeometry(QtCore.QRect(100, 10, 10, 10))

        self.wellbore_buffer_linedit = QtWidgets.QLineEdit("", self)
        self.wellbore_buffer_linedit.setGeometry(QtCore.QRect(6, 91, 147, 17))



        self.wellbore_locate_graphic_checkbox.stateChanged.connect(self.onCheckRunStuff)
        self.change_well_box.stateChanged.connect(self.changeData)
        self.wellbore_buffer_linedit.returnPressed.connect(self.onCheckRunStuff)

        self.pts_wells = self.ax_graphic_individual_well.scatter([], [], c='black', s=50, zorder=3)
        self.polygon_shape, = self.ax_graphic_individual_well.fill([], [], linewidth=5, zorder=1, alpha=0.5)
        self.cursor_pts_text = self.ax_graphic_individual_well.text([], [], "", color='black')
        self.pts_text_ew = self.ax_graphic_individual_well.text([], [], "", color='black')
        self.pts_text_ns = self.ax_graphic_individual_well.text([], [], "", color='black')
        self.pts = self.ax_graphic_individual_well.scatter([], [], c='black', s=50, zorder=2, alpha=0.5)
        self.pts_tiny = self.ax_graphic_individual_well.scatter([], [], c='black', s=5, zorder=2, alpha=0.5)
        self.pts_lines_ew, = self.ax_graphic_individual_well.fill([], [], color='red', linewidth=2, zorder=1)
        self.pts_lines_ns, = self.ax_graphic_individual_well.fill([], [], color='red', linewidth=2, zorder=1)
        self.segment_lines_ew, = self.ax_graphic_individual_well.fill([], [], color='red', linewidth=3, zorder=1)
        self.segment_lines_ns, = self.ax_graphic_individual_well.fill([], [], color='red', linewidth=3, zorder=1)

        self.well_boundary = LineCollection([])
        self.ax_graphic_individual_well.add_collection(self.well_boundary)

        self.well_lines = LineCollection([])
        self.ax_graphic_individual_well.add_collection(self.well_lines)
        self.well_buffer_polygons = PolyCollection([])
        self.ax_graphic_individual_well.add_collection(self.well_buffer_polygons)

        self.polygon_coord = Polygon(self.coordinates[0])
        self.drawIndividualSections()

    def changeData(self):
        self.removeSections()
        self.clearTheWells()
        self.clearTriangulator()
        if self.change_well_box.isChecked():
            self.polygon_coord = Polygon(self.coordinates[1])
            self.coordinates = self.coordinates2
        else:
            self.polygon_coord = Polygon(self.coordinates[0])
            self.coordinates = self.coordinates1
        self.wellbore_locate_graphic_checkbox.setChecked(False)
        self.drawIndividualSections()

    def removeSections(self):
        self.ind_plot_1.remove()
        self.scatter1.remove()
        try:
            self.ind_plot_2.remove()
            self.scatter2.remove()
        except AttributeError:
            pass
        try:
            self.ind_plot_3.remove()
            self.scatter3.remove()
        except AttributeError:
            pass
        try:
            self.ind_plot_4.remove()
            self.scatter4.remove()
        except AttributeError:
            pass
        try:
            self.ind_plot_5.remove()
            self.scatter5.remove()
        except AttributeError:
            pass
        try:
            self.ind_plot_6.remove()
            self.scatter6.remove()
        except AttributeError:
            pass
        try:
            self.ind_plot_7.remove()
            self.scatter7.remove()
        except AttributeError:
            pass
        try:
            self.ind_plot_8.remove()
            self.scatter8.remove()
        except AttributeError:
            pass

    def drawIndividualSections(self):
        self.ind_plot_1, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[0]).exterior.xy, color='blue', linewidth=.7)
        self.scatter1 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[0]).exterior.xy, c='blue', s=5)
        try:
            self.ind_plot_2, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[1]).exterior.xy, color='blue', linewidth=.7)
            self.scatter2 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[1]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass
        try:
            self.ind_plot_3, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[2]).exterior.xy, color='blue', linewidth=.7)
            self.scatter3 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[2]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass
        try:
            self.ind_plot_4, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[3]).exterior.xy, color='blue', linewidth=.7)
            self.scatter4 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[3]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass
        try:
            self.ind_plot_5, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[4]).exterior.xy, color='blue', linewidth=.7)
            self.scatter5 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[5]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass
        try:
            self.ind_plot_6, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[5]).exterior.xy, color='blue', linewidth=.7)
            self.scatter6 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[5]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass
        try:
            self.ind_plot_7, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[6]).exterior.xy, color='blue', linewidth=.7)
            self.scatter7 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[6]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass
        try:
            self.ind_plot_8, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[7]).exterior.xy, color='blue', linewidth=.7)
            self.scatter8 = self.ax_graphic_individual_well.scatter(*Polygon(self.coordinates[7]).exterior.xy, c='blue', s=5)
        except IndexError:
            pass

        # for i in range(len(self.coordinates)):
        #     self.ind_plot_1, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[i]).exterior.xy, color='blue', linewidth=.7)

        # for i in range(len(self.coordinates)):
        #     poly_test = Polygon(self.coordinates[i])
        #     x1, y1 = poly_test.exterior.xy
        #     self.ind_plot_1, = self.ax_graphic_individual_well.plot(x1, y1, color='blue', linewidth=.7)
        #     self.scatter1 = self.ax_graphic_individual_well.scatter(x1, y1, c='blue', s=5)

            # self.plot_var[i], = self.ax_graphic_individual_well.plot(x1, y1, color='blue', linewidth=.7)
            # self.plot1, = self.ax_graphic_individual_well.plot(x1, y1, color='blue', linewidth=.7)
        # self.ind_plot_1, = self.ax_graphic_individual_well.plot(x1, y1, color='blue', linewidth=.7)
        # for i in range(len(self.coordinates)):
        #     self.ind_plot_1, = self.ax_graphic_individual_well.plot(*Polygon(self.coordinates[i]).exterior.xy, color='blue', linewidth=.7)
        #
        #
        # self.scatter1 = self.ax_graphic_individual_well.scatter(x1, y1, c='blue', s=5)
        self.canvas_individual_well.draw()
        self.canvas_individual_well.blit(self.ax_graphic_individual_well.bbox)

    def onCheckRunStuff(self):
        if self.wellbore_locate_graphic_checkbox.isChecked():
            try:
                buffer_distance = float(self.wellbore_buffer_linedit.text())
            except ValueError:
                buffer_distance = 0
            used_polygons = [LineString(self.wells_data[i]).buffer(buffer_distance) for i in range(len(self.wells_data)) if buffer_distance > 0]
            self.drawTheWells(self.wells_data)
            polygons_output = unary_union(used_polygons)
            if buffer_distance > 0:
                self.drawBufferPolygon(polygons_output)
        else:
            self.clearTheWells()
            self.canvas_individual_well.draw()

    def drawTheWells(self, well):
        self.well_lines.set_segments(well)
        ma.printLine(well)
        all_well_pts = list(chain.from_iterable(well))
        self.pts_wells.set_offsets(all_well_pts)
        self.ax_graphic_individual_well.draw_artist(self.pts_wells)
        self.ax_graphic_individual_well.draw_artist(self.well_lines)
        self.canvas_individual_well.blit(self.ax_graphic_individual_well.bbox)

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
            self.ax_graphic_individual_well.draw_artist(self.well_buffer_polygons)
        except AttributeError:
            x, y = polygons_output.exterior.xy
            polygon = list(zip(x, y))
            self.polygon_shape.set_color('red')
            self.polygon_shape.set_xy(polygon)
            self.ax_graphic_individual_well.draw_artist(self.polygon_shape)

        self.canvas_individual_well.blit(self.ax_graphic_individual_well.bbox)

    def clearTheWells(self):
        cleared_lst = [[None, None] for i in range(len(self.wells_data))]
        cleared_collection = [[[None, None], [None, None]] for i in range(len(self.wells_data))]
        self.well_lines.set_segments(cleared_collection)
        self.pts_wells.set_offsets(cleared_lst)
        self.polygon_shape.set_xy([[None, None], [None, None], [None, None]])
        self.ax_graphic_individual_well.draw_artist(self.pts_wells)
        self.ax_graphic_individual_well.draw_artist(self.polygon_shape)
        self.ax_graphic_individual_well.draw_artist(self.well_lines)

    def clearTriangulator(self):
        outline_ns = [[None, None], [None, None], [None, None]]
        outline_ew = [[None, None], [None, None], [None, None]]
        pts = [[None, None] for i in range(len(self.wells_data))]
        segment_ew = [[None, None], [None, None], [None, None]]
        segment_ns = [[None, None], [None, None], [None, None]]
        text_ns = [[None, None], [None, None]]
        text_ew = [[None, None], [None, None]]
        dist_ew, dist_ns = None, None

        self.pts_text_ew.set_position(text_ew)
        self.pts_text_ew.set_text(dist_ew)

        self.pts_text_ns.set_position(text_ns)
        self.pts_text_ns.set_text(dist_ns)

        self.pts_lines_ew.set_xy(outline_ew)
        self.pts_lines_ns.set_xy(outline_ns)

        self.segment_lines_ew.set_xy(segment_ew)
        self.segment_lines_ns.set_xy(segment_ns)
        self.pts_tiny.set_offsets(pts)
        self.pts.set_offsets(pts)



    def onClickIndividualSection(self, event):
        ix, iy = event.xdata, event.ydata
        self.draw_section_boo = True
        mods = QGuiApplication.queryKeyboardModifiers()
        self.canvas_individual_well.blit(self.ax_graphic_individual_well.bbox)

        try:
            if event.button == Qt.LeftButton and mods == Qt.ShiftModifier:
                if event.inaxes == self.ax_graphic_individual_well:
                    if self.draw_section_boo:
                        if self.polygon_coord.contains(Point(ix, iy)):
                            self.drawStuff(ix, iy, event)
                            self.canvas_individual_well.draw()
        except TypeError:
            pass

    def onReleaseIndividualSection(self, event):
        self.canvas_individual_well.draw()
        self.draw_section_boo = False

    def drawStuff(self, x, y, event):
        x1, y1 = self.polygon_coord.exterior.coords.xy
        xy_data = list(zip(x1, y1))
        xy_data = [list(i) for i in xy_data]
        dist_ns, dist_ew, mp_ns, mp_ew, original_ns_segment, original_ew_segment, pts = self.lineSegmentsForManualPointing(xy_data, [x, y])
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
        self.pts_tiny.set_offsets(pts)

        self.canvas_individual_well.draw()

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
            ew_m1 = 0.00000000000001
        ew_m2 = -1 / ew_m1
        ew_b2 = iy - (ew_m2 * ix)

        if ew_side[0][0] == ew_side[1][0]:
            intersect_ew = [ew_side[1][0], iy]
        else:
            intersect_ew = self.lineIntersectionPt(ew_m1, ew_m2, ew_b1, ew_b2)
        if ns_side[0][1] == ns_side[1][1]:
            intersect_ns = [ix, ns_side[1][1]]
        else:
            intersect_ns = self.lineIntersectionPt(ns_m1, ns_m2, ns_b1, ns_b2)

        pts = [intersect_ns, [ix, iy], intersect_ew]
        mp_ns, mp_ew = [(intersect_ns[0] + ix) / 2, (intersect_ns[1] + iy) / 2], [(intersect_ew[0] + ix) / 2, (intersect_ew[1] + iy) / 2]
        return float(output[0]), float(output[2]), mp_ns, mp_ew, ns_side, ew_side, pts

    def lineIntersectionPt(self, m1, m2, b1, b2):
        xi = (b1 - b2) / (m2 - m1)
        yi = m1 * xi + b1
        return [xi, yi]

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
        pts_lst = [[line[i], line[i + 1]] for i in range(len(line) - 1)]
        eq_lst = [i for i in eq_lst if str(i[0]) != 'nan']  # and i[0] != 0]
        distance_lst = []
        counter = 0
        for i in range(len(eq_lst)):
            x1, x2 = pts_lst[i][0][0], pts_lst[i][1][0]
            y1, y2 = pts_lst[i][0][1], pts_lst[i][1][1]
            if eq_lst[i][0] != 0:
                m = eq_lst[i][0]
                b = pt[1] - (m * pt[0])
                distance_lst.append(round(self.dist(m, eq_lst[i][1], b), 3))
            else:
                if x1 == x2:
                    distance = abs(pt[0] - line[counter][0])
                    distance_lst.append(distance)
                elif y1 == y2:
                    distance = abs(pt[1] - line[counter][1])
                    distance_lst.append(distance)
            counter += 1
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
        combo_list = [i for i in combo_list if str(i[1][0]) != 'nan']  # and i[1][0] != 0]
        pts_used_lst = [i[0] for i in combo_list]
        eq_lst = [i[1] for i in combo_list]
        for i in range(len(pts_used_lst)):
            x1, y1 = pts_used_lst[i][0][0], pts_used_lst[i][0][1]
            x2, y2 = pts_used_lst[i][1][0], pts_used_lst[i][1][1]
            m = eq_lst[i][0]
            if m != 0:
                m = 1 / m * -1
                b1 = y1 - (m * x1)
                b2 = y2 - (m * x2)
                line1 = (m * x) + b1 - y
                line2 = (m * x) + b2 - y
                between_line_boo = True if line1 * line2 < 0 else False
                if between_line_boo:
                    return i
            if m == 0:
                if x1 == x2:
                    if y1 > pt[1] > y2 or y2 > pt[1] > y1:
                        return i
                elif y1 == y2:
                    if x1 > pt[0] > x2 or x2 > pt[0] > x1:
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
