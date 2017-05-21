from __future__ import print_function
import numpy as np
import pprint
from operator import itemgetter

FIG_TYPES = {
    'LINE_1': {
        'color': [0.4, 1, 1]
    },
    'LINE_2': {
        'color': [0.5, 1, 1]
    },
    'BROKEN_LINE': {
        'color': [0.6, 1, 1]
    },
    'CIRCLE_L': {
        'color': [0.2, 1, 1]
    },
    'CIRCLE_R': {
        'color': [0.3, 1, 1]
    },
    'ZIGZAG': {
        'color': [0.1, 1, 1]
    },
    'SPIRAL_L': {
        'color': [0.7, 1, 1]
    },
    'SPIRAL_R': {
        'color': [0.8, 1, 1]
    }
}


def read(filename):
    """
    return dict:
    {
        "file_name"     : "string",
        "patient_id"    : "int",
        "operation_num" : "int",
        "surgery"       : "bool" 0-before surgery 1-after,
        "gender"        : "string",
        "arm"           : "string",
        "hemisphere"    : "string",
        "treatment" : "string",
        "date"  : "string",
        "notes" : "string",
        "data": [
            {
                "time"  : "int",
                "x"     : "int",
                "y"     : "int",
                "force" : "int",
                "width" : "int",
                "height": "int",
                * "speed" : float - wyliczone dla niektórch punktów
            },
            ...
        ],
        "min_force": int,
        "min_force": int,
        "max_force": int,
        "avg_force:" float,
        "max_speed": float,
        "avg_speed": float,
        "line_breaks": int,
        "avg_width": int,
        "avg_height": int,
        "pos_x": (min, max),
        "pos_y": (min, max),
        "line_len": float,
        "time" : int,
        "image": Image in hsv,
        "figures": [                #TODO
            {
                "type": string,
                "pos_x": [min, max],
                "pos_y": [min, max],
                "max_force": int,
                "min_force": int,
                "avg_force": float,
                "line_len": float,
                "max_speed": float,
                "avg_speed": float,
                "line_breaks": int,
                "avg_width": int,
                "avg_height": int,
                "time": int,
                "diff": float       #TODO
            },
            ...
        ]
    }
    :param filename: path to the file
    """
    result = {}
    with open(filename, 'rb') as f:
        for i in ['file_name', 'date', 'notes']:
            num = int.from_bytes(f.read(4), byteorder='little')
            result[i] = str(f.read(num), "utf-8")
        f.read(16)
        data_p = int.from_bytes(f.read(4), byteorder='little')
        result['data'] = []
        for i in range(0, data_p):
            tmp = {}
            for indx in ["time", "x", "y", "force", "width", "height"]:
                tmp[indx] = int.from_bytes(f.read(4), byteorder='little')
            result['data'].append(tmp)
        name_tags = result['file_name'].split('_')
        result['patient_id'] = int(name_tags[1])
        for i, v in enumerate(['operation_num', 'surgery', 'gender', 'arm', 'hemisphere', 'treatment']):
            result[v] = str(name_tags[2][i])
    return set_test_details(result, result['data'])


def set_test_details(gdata, data, speed_points=100):
    """
    Oblicza wartości charakretystyczne
    :param gdata: dict - gdzie dane mają zostać zapisane
    :param data: [{...},{...},...] tablica z danymi
    :param speed_points: int - liczba punktów na podstawie których liczona jest prędkość chwilowa
    :return: dict
    """
    max_x, max_y = 0, 0
    min_x, min_y = -1, -1
    max_f, avg_f = 0, [0, 0]
    avg_w, avg_h = 0, 0
    speed_l, speed_t0, speed_t1 = 0, 0, 0
    avg_speed = [0, 0]
    prev, state = None, None

    gdata['line_len'] = 0
    gdata['line_breaks'] = 0
    gdata['min_force'] = -1
    gdata['max_speed'] = 0
    for idx, i in enumerate(data):
        if i['force'] > max_f:
            max_f = i['force']
        if i['force'] > 0:
            if i['x'] > max_x: max_x = i['x']
            if i['y'] > max_y: max_y = i['y']
            if i['x'] < min_x or min_x == -1: min_x = i['x']
            if i['y'] < min_y or min_y == -1: min_y = i['y']

            if gdata['min_force'] == -1 or gdata['min_force'] > i['force']:
                gdata['min_force'] = i['force']
            avg_f[0] += i['force']
            avg_f[1] += 1
            if prev is not None and prev['force'] > 0:
                gdata['line_len'] += np.sqrt(pow(prev['x'] - i['x'], 2) + pow(prev['y'] - i['y'], 2))
            avg_w += i['width']
            avg_h += i['height']

        if speed_t0 == 0: speed_t0 = i['time']
        if idx > 0 and idx % min(speed_points, len(data) - 2) == 0:
            speed_t1 = i['time']
            speed = (gdata['line_len'] - speed_l) / (speed_t1 - speed_t0)
            speed_l = gdata['line_len']
            speed_t0 = i['time']
            if speed > gdata['max_speed']: gdata['max_speed'] = speed
            i['speed'] = speed
            avg_speed[0] += speed
            avg_speed[1] += 1
        prev = i
        # LINE BRAKES
        if state is not None:
            if state == 0 and i['force'] > 0: state = 1
            if state > 0 and i['force'] == 0:
                state = 0
                gdata['line_breaks'] += 1
        if state is None: state = (i['force'] > 0)

    gdata['avg_speed'] = avg_speed[0] / avg_speed[1]
    gdata['max_force'] = max_f
    gdata['pos_x'] = (min_x, max_x)
    gdata['pos_y'] = (min_y, max_y)
    gdata['avg_force'] = avg_f[0] / avg_f[1]
    gdata['avg_width'] = avg_w / avg_f[1]
    gdata['avg_height'] = avg_h / avg_f[1]
    gdata['time'] = len(data)
    return gdata


def find_figures_merge(figures):
    def merge(prev, next):
        next['pos_x'] = [min(next['pos_x'][0], prev['pos_x'][0]),
                         max(next['pos_x'][1], prev['pos_x'][1])]
        next['pos_y'] = [min(next['pos_y'][0], prev['pos_y'][0]),
                         max(next['pos_y'][1], prev['pos_y'][1])]
        next['points'] += prev['points']
        next['data'] += prev['data']
        next['zeros_ahead'] = prev['zeros_ahead']


    def merge_same_area(figures, m = 50):
        def check_the_same_area(prev, fig):
            if (fig['pos_x'][0] - m <= prev['pos_x'][0] <= fig['pos_x'][1] + m) and (
                                fig['pos_y'][0] - m <= prev['pos_y'][0] <= fig['pos_y'][1] + m):
                return True
            if (fig['pos_x'][0] - m <= prev['pos_x'][1] <= fig['pos_x'][1] + m) and (
                                fig['pos_y'][0] - m <= prev['pos_y'][0] <= fig['pos_y'][1] + m):
                return True
            if (fig['pos_x'][0] - m <= prev['pos_x'][0] <= fig['pos_x'][1] + m) and (
                                fig['pos_y'][0] - m <= prev['pos_y'][1] <= fig['pos_y'][1] + m):
                return True
            if (fig['pos_x'][0] - m <= prev['pos_x'][1] <= fig['pos_x'][1] + m) and (
                                fig['pos_y'][0] - m <= prev['pos_y'][1] <= fig['pos_y'][1] + m):
                return True
            if (prev['pos_x'][0] - m <= fig['pos_x'][0] <= prev['pos_x'][1] + m) and (
                                prev['pos_y'][0] - m <= fig['pos_y'][0] <= prev['pos_y'][1] + m):
                return True
            if (prev['pos_x'][0] - m <= fig['pos_x'][1] <= prev['pos_x'][1] + m) and (
                                prev['pos_y'][0] - m <= fig['pos_y'][0] <= prev['pos_y'][1] + m):
                return True
            if (prev['pos_x'][0] - m <= fig['pos_x'][0] <= prev['pos_x'][1] + m) and (
                                prev['pos_y'][0] - m <= fig['pos_y'][1] <= prev['pos_y'][1] + m):
                return True
            if (prev['pos_x'][0] - m <= fig['pos_x'][1] <= prev['pos_x'][1] + m) and (
                                prev['pos_y'][0] - m <= fig['pos_y'][1] <= prev['pos_y'][1] + m):
                return True
            return False
        loop = 1
        while loop:
            loop = 0
            for idx, fig in enumerate(figures):
                for i in range(1, idx + 1):
                    if check_the_same_area(figures[idx - i], fig):
                        merge(figures[idx - i], fig)
                        figures.pop(idx - i)
                        loop = 1
                        break
        return figures

    def small_fig(fig, small=1000, s_points=10):
        if (fig['pos_x'][1] - fig['pos_x'][0]) * (fig['pos_y'][1] - fig['pos_y'][0]) < small:
            return True
        if fig['points'] < s_points:
            return True
        return False

    def merge_small_breaks(figures, small_merge=30):
        loop = 1
        while loop:
            loop = 0
            for idx, fig in enumerate(figures):
                if idx > 0 and fig['zeros_ahead'] < small_merge:
                    merge(figures[idx - 1], fig)
                    figures.pop(idx - 1)
                    loop = 1
                    break
        return figures

    def merge_one_fig(figures, avg_diff=500, max_p=400, max_d=400, max_s=300):
        def check_create_one_fig(prev, fig):
            avg_1 = (prev['pos_x'][1] + prev['pos_x'][0]) / 2
            avg_2 = (fig['pos_x'][1] + fig['pos_x'][0]) / 2

            if prev['pos_y'][1] < fig['pos_y'][0]:
                dis = fig['pos_y'][0] - prev['pos_y'][1]
            else:
                dis = prev['pos_y'][0] - fig['pos_y'][1]

            if abs(avg_2 - avg_1) < avg_diff and \
                    (fig['points'] < max_p or prev['points'] < max_p or dis < max_d or (
                                    prev['pos_x'][1] - prev['pos_x'][0] < max_s)):
                return True

            return False

        loop = 1
        while loop:
            loop = 0
            for idx, fig in enumerate(figures):
                if idx > 0 and check_create_one_fig(figures[idx - 1], fig):
                    merge(figures[idx - 1], fig)
                    figures.pop(idx - 1)
                    loop = 1
                    break
        return figures

    merge_small_breaks(figures)
    merge_same_area(figures)
    figures = [x for x in figures if not small_fig(x)]
    figures = merge_one_fig(figures)

    figures = find_circles_spirals(figures)
    not_recognized = [x for x in figures if 'type' not in x]
    figures = [x for x in figures if 'type' in x]
    not_recognized = merge_same_area(not_recognized)
    not_recognized = merge_one_fig(not_recognized, max_p=1000, max_d=2000, max_s=1000)
    figures += find_zigzag_lines(not_recognized)
    return figures


def find_circles_spirals(figures):
    squares = []
    for idx, fig in enumerate(figures):
        dim_x = fig['pos_x'][1] - fig['pos_x'][0]
        dim_y = fig['pos_y'][1] - fig['pos_y'][0]
        if 0.8 <= dim_x / dim_y <= 1.2:
            squares.append((idx, fig['points']))
    squares = sorted(squares, key=itemgetter(1), reverse=True)
    if figures[squares[0][0]]['pos_y'][0] < figures[squares[1][0]]['pos_y'][0]:
        figures[squares[0][0]]['type'] = 'SPIRAL_L'
        figures[squares[1][0]]['type'] = 'SPIRAL_R'
    else:
        figures[squares[0][0]]['type'] = 'SPIRAL_R'
        figures[squares[1][0]]['type'] = 'SPIRAL_L'
    if figures[squares[2][0]]['pos_y'][0] < figures[squares[3][0]]['pos_y'][0]:
        figures[squares[2][0]]['type'] = 'CIRCLE_L'
        figures[squares[3][0]]['type'] = 'CIRCLE_R'
    else:
        figures[squares[2][0]]['type'] = 'CIRCLE_R'
        figures[squares[3][0]]['type'] = 'CIRCLE_L'
    return figures

def find_zigzag_lines(figures):
    figures = sorted(figures, key=itemgetter('points'), reverse=True)
    figures[0]['type'] = 'ZIGZAG'
    figures2 = figures[1:4]
    for x in figures2:
        x = set_test_details(x, x['data'])
    figures2 = sorted(figures2, key=itemgetter('line_breaks'), reverse=True)
    figures2[0]['type'] = 'BROKEN_LINE'
    if figures2[1]['pos_x'][0] < figures2[2]['pos_x'][0]:
        figures2[1]['type'] = 'LINE_1'
        figures2[2]['type'] = 'LINE_2'
    else:
        figures2[1]['type'] = 'LINE_2'
        figures2[2]['type'] = 'LINE_1'
    return [figures[0]] + figures2

def find_figures(gdata):
    groups = []
    zeros = 0
    x = [0, 0]
    y = [0, 0]
    non_zeros = 0
    prev = None
    data = []
    for i in gdata['data']:
        if i['force'] == 0:
            zeros += 1
            data.append(i)
        if i['force'] > 0:
            data.append(i)
            non_zeros += 1
            if i['x'] > x[1]: x[1] = i['x']
            if i['y'] > y[1]: y[1] = i['y']
            if x[0] == 0 or i['x'] < x[0]: x[0] = i['x']
            if y[0] == 0 or i['y'] < y[0]: y[0] = i['y']
        if prev is not None and prev['force'] > 0 and i['force'] == 0:
            groups.append(
                {"pos_x": x, "pos_y": y, "points": non_zeros, "zeros_ahead": zeros, "data": data}
            )
            data = []
            x = [0, 0]
            y = [0, 0]
            zeros = 1
            non_zeros = 0
            pass
        prev = i
    # TODO Find point groups which create figures
    # TODO recognize figures based on group dimensions and sth else?
    groups = find_figures_merge(groups)

    # TODO
    for x in groups:
        if 'type' in x:
            x = set_test_details(x, x["data"])
        del x["data"]

    gdata['figures'] = groups

    return gdata


def save_metrics(gdata, file_name):
    data = gdata['data']
    gdata['data'] = "NOT VISIBLE"
    file = open(file_name, "w")
    file.write(pprint.pformat(gdata))
    gdata['data'] = data
    file.close()

def create_image(gdata, scale=30, show_speed=True, show_figure_box=False, show_width=False, show_height=False, max_force=None, max_speed=None):
    """
    Tworzy obraz w przestrzeni hsv przedstawiający przegieb testu grafomotorycznego.
    Wsp scale oznacza jka bardzo obraz ma być przeskalowany w stosunku do rozmiaru danych wejściowych
    Siła nacisku reprezentowana jest jako barwa (H): zielony - zółty - czerwony : słaba - średnia - wysoka
    Prędkość rysowania reprezentowana jest jako (V): większa wartość to większa prędkość
    Kąty rysowania są również reprezentowane przez barwę.
    :param gdata: dict
    :param scale: int - pomniejszenie jakie zastosować (wejściowe dane mają bardzo dużą rozdzielczość)
    :param show_speed: bool
    :return: dict
    """
    if max_force is None:
        max_force = gdata['max_force']
    if max_speed is None:
        max_speed = gdata['max_speed']
    # TODO draw vectors
    w, h = int((gdata['pos_x'][1]) / scale) + 2, int((gdata['pos_y'][1]) / scale) + 2
    data = np.zeros((w, h, 3), dtype=np.float)
    cur_speed = gdata['avg_speed']
    for i in gdata['data']:
        if i['force'] > 0:
            x, y = i['x'] / scale, i['y'] / scale
            if int(x) != x:
                xt = [int(x), int(x) + 1]
            else:
                xt = [int(x)]
            if int(y) != y:
                yt = [int(y), int(y) + 1]
            else:
                yt = [int(y)]
            for x in xt:
                for y in yt:
                    if 'speed' in i: cur_speed = i['speed']
                    color = 0.350 - (0.350 * i['force'] / max_force)
                    if show_width:
                        color = 0.125+(0.75*i['width']/1800)
                    elif show_height:
                        color = 0.125+(0.75*i['height']/1800)

                    if show_speed:
                        data[x, y] = [color, 1, cur_speed / max_speed]
                    else:
                        data[x, y] = [color, 1, 1]

    if show_figure_box == True:
        for fig in gdata['figures']:
            color = [1, 0, 1]
            if 'type' in fig:
                color = FIG_TYPES[fig['type']]['color']
            for y in fig['pos_y']:
                for x in range(fig['pos_x'][0], fig['pos_x'][1]):
                    data[int(x / scale), int(y / scale)] = color
            for x in fig['pos_x']:
                for y in range(fig['pos_y'][0], fig['pos_y'][1]):
                    data[int(x / scale), int(y / scale)] = color

    gdata["image"] = data
    return gdata
