from __future__ import print_function
import numpy as np
import pprint

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
        "line_brakes": int,
        "avg_width": int,
        "avg_height": int,
        "pos_x": (min, max),
        "pos_y": (min, max),
        "line_len": float,
        "image": Image in hsv,
        "figures": [                #TODO
            {
                "type": string,     #TODO
                "pos_x": [min, min],#TODO
                "pos_y": [max, max],#TODO
                "max_force": int,   #TODO
                "min_force": int,   #TODO
                "avg_force": float, #TODO
                "line_len": float,  #TODO
                "max_speed": float, #TODO
                "avg_speed": float, #TODO
                "line_brakes": int, #TODO
                "avg_width": int,   #TODO
                "avg_height": int   #TODO
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
    return set_test_details(result)


def set_test_details(gdata, speed_points=50):
    max_x, max_y = 0, 0
    min_x, min_y = -1, -1
    max_f, avg_f = 0, [0, 0]
    avg_w, avg_h = 0, 0
    speed_l, speed_t0, speed_t1 = 0, 0, 0
    avg_speed = [0, 0]
    prev, state = None, None

    gdata['line_len'] = 0
    gdata['line_brakes'] = 0
    gdata['min_force'] = -1
    gdata['max_speed'] = 0
    for idx, i in enumerate(gdata['data']):
        if i['x'] > max_x:
            max_x = i['x']
        if i['y'] > max_y:
            max_y = i['y']
        if i['x'] < min_x or min_x == -1:
            min_x = i['x']
        if i['y'] < min_y or min_y == -1:
            min_y = i['y']
        if i['force'] > max_f:
            max_f = i['force']
        if i['force'] > 0:
            if gdata['min_force'] == -1 or gdata['min_force'] > i['force']:
                gdata['min_force'] = i['force']
            avg_f[0] += i['force']
            avg_f[1] += 1
            if prev is not None and prev['force'] > 0:
                gdata['line_len'] += np.sqrt(pow(prev['x'] - i['x'], 2) + pow(prev['y'] - i['y'], 2))
            avg_w += i['width']
            avg_h += i['height']

        if speed_t0 == 0:
            speed_t0 = i['time']
        if idx > 0 and idx % speed_points == 0:
            speed_t1 = i['time']
            speed = (gdata['line_len'] - speed_l) / (speed_t1 - speed_t0)
            speed_l = gdata['line_len']
            speed_t0 = i['time']
            if speed > gdata['max_speed']:
                gdata['max_speed'] = speed
            i['speed'] = speed
            avg_speed[0] += speed
            avg_speed[1] += 1
        prev = i
        # LINE BRAKES
        if state is not None:
            if state == 0 and i['force'] > 0:
                state = 1
            if state > 0 and i['force'] == 0:
                state = 0
                gdata['line_brakes'] += 1
        if state is None:
            state = (i['force'] > 0)

    gdata['avg_speed'] = avg_speed[0] / avg_speed[1]
    gdata['max_force'] = max_f
    gdata['pos_x'] = (min_x, max_x)
    gdata['pos_y'] = (min_y, max_y)
    gdata['avg_force'] = avg_f[0] / avg_f[1]
    gdata['avg_width'] = avg_w / avg_f[1]
    gdata['avg_height'] = avg_h / avg_f[1]
    return gdata


def find_figures_merge(figures, small_merge=40):
    def merge(prev, next):
        next['pos_x'] = [min(next['pos_x'][0], prev['pos_x'][0]),
                        max(next['pos_x'][1], prev['pos_x'][1])]
        next['pos_y'] = [min(next['pos_y'][0], prev['pos_y'][0]),
                        max(next['pos_y'][1], prev['pos_y'][1])]
        next['points'] += prev['points']
        next['zeros_ahead'] = prev['zeros_ahead']

    #MAŁE PRZERWY
    small_break = 1
    while small_break:
        small_break = 0
        for idx, fig in enumerate(figures):
            if idx>0 and fig['zeros_ahead'] < small_merge:
                merge(figures[idx-1], fig)
                figures.pop(idx-1)
                small_break = 1
                break




    #ZAWIERAJĄ POKRYWAJĄCE SIĘ OBSZARY
    same_area = 1
    while same_area:
        same_area = 0
        prev = None
        for fig in figures:
            if prev is not None:
                #TODO CHECK if fig and prev contains the same area. If yes merge it, set same_area = 1.
                pass
            prev = fig

    return figures


def find_figures(gdata):
    groups = []
    group = {"x": [0 , 0], "y": [0, 0], "points": 0, "zeros_ahead": 0}
    zeros = 0
    x = [0, 0]
    y = [0, 0]
    non_zeros = 0
    prev = None
    for i in gdata['data']:
        if i['force'] == 0:
            zeros += 1
        if i['force'] > 0:
            non_zeros += 1
            if i['x'] > x[1]: x[1] = i['x']
            if i['y'] > y[1]: y[1] = i['y']
            if x[0] == 0 or i['x'] < x[0]: x[0] = i['x']
            if y[0] == 0 or i['y'] < y[0]: y[0] = i['y']
        if prev is not None and prev['force'] > 0 and i['force'] == 0:
            groups.append(
                {"pos_x": x, "pos_y": y, "points": non_zeros, "zeros_ahead": zeros }
            )
            x = [0, 0]
            y = [0, 0]
            zeros = 1
            non_zeros = 0
            pass
        prev=i
    # TODO Find point groups which create figures
    # TODO recognize figures based on group dimensions and sth else?
    groups = find_figures_merge(groups)
    pprint.pprint(groups)
    print(len(groups))
    gdata['figures'] = groups
    return gdata


def create_image(gdata, scale=30, show_speed=True, show_figure_box = False):
    """
    Tworzy obraz w przestrzeni hsv przedstawiający przegieb testu grafomotorycznego.
    Wsp scale oznacza jka bardzo obraz ma być przeskalowany w stosunku do rozmiaru danych wejściowych
    Siła nacisku reprezentowana jest jako barwa (H): zielony - zółty - czerwony : słaba - średnia - wysoka
    Prędkość rysowania reprezentowana jest jako (V): większa wartość to większa prędkość
    Kąty rysowania reprezentowane jako wektory wychodzące                                                         #TODO
    :param gdata: dict
    :param scale: int
    :param show_speed: bool
    :return: dict
    """
    # TODO draw vectors
    w, h = int((gdata['pos_x'][1]) / scale) + 2, int((gdata['pos_y'][1]) / scale) + 2
    data = np.zeros((w, h, 3), dtype=np.float)
    cur_speed = gdata['avg_speed']
    for i in gdata['data']:
        if i['force'] > 0:
            x, y = i['x'] / scale, i['y'] / scale
            if int(x) != x: xt = [int(x), int(x) + 1]
            else: xt = [int(x)]
            if int(y) != y: yt = [int(y), int(y) + 1]
            else: yt = [int(y)]
            for x in xt:
                for y in yt:
                    if 'speed' in i: cur_speed = i['speed']
                    color = 0.350 - (0.350 * i['force'] / gdata['max_force'])
                    if show_speed: data[x, y] = [color, 1, cur_speed / gdata['max_speed']]
                    else: data[x, y] = [color, 1, 1]

    if show_figure_box == True:
        for fig in gdata['figures']:
            for y in fig['pos_y']:
                for x in range(fig['pos_x'][0], fig['pos_x'][1]):
                    data[int(x/scale),int(y/scale)] = [1,0,1]
            for x in fig['pos_x']:
                for y in range(fig['pos_y'][0], fig['pos_y'][1]):
                    data[int(x/scale),int(y/scale)] = [1,0,1]

    gdata["image"] = data
    return gdata
