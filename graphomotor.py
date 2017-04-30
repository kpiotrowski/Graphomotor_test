import numpy as np


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
                "height": "int"
            },
            ...
        ],
        "min_force": int,
        "min_force": int,
        "max_force": int,
        "avg_force:" float,
        "max_speed": float,         #TODO
        "avg_speed": float,         #TODO
        "line_brakes": int,
        "pos_x": (min, max),
        "pos"y": (min, max),
        "line_len": float,
        "image": Image in hsv,
        "figures": [                #TODO
            {
                "type": string,     #TODO
                "max_force": int,   #TODO
                "avg_force": float, #TODO
                "line_len": float,  #TODO
                "max_speed": float, #TODO
                "avg_speed": float, #TODO
                "line_brakes": int  #TODO
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
        for i,v in enumerate(['operation_num', 'surgery', 'gender', 'arm', 'hemisphere', 'treatment']):
            result[v] = str(name_tags[2][i])
    return set_test_details(result)


def set_test_details(gdata):
    max_x, max_y = 0, 0
    min_x, min_y = -1, -1
    max_f = 0
    avg_f = [0, 0]
    prev, state = None, None

    gdata['line_len'] = 0
    gdata['line_brakes'] = 0
    gdata['min_force'] = -1
    for i in gdata['data']:
        if i['x'] > max_x: max_x = i['x']
        if i['y'] > max_y: max_y = i['y']
        if i['x'] < min_x or min_x == -1: min_x = i['x']
        if i['y'] < min_y or min_y == -1: min_y = i['y']
        if i['force'] > max_f: max_f = i['force']
        if i['force'] > 0:
            if gdata['min_force'] == -1 or gdata['min_force'] > i['force']:
                gdata['min_force'] = i['force']
            avg_f[0] += i['force']
            avg_f[1] += 1
            if prev is not None and prev['force']>0:
                len = np.sqrt(pow(prev['x'] - i['x'], 2) + pow(prev['y'] - i['y'], 2))
                gdata['line_len'] += len
        if state is not None:
            if state == 0 and i['force'] > 0: state = 1
            if state > 0 and i['force'] == 0:
                state = 0
                gdata['line_brakes'] += 1

        if state is None: state = (i['force'] > 0)
        prev = i

    gdata['max_force'] = max_f
    gdata['pos_x'] = (min_x, max_x)
    gdata['pos_y'] = (min_y, max_y)
    gdata['avg_force'] = avg_f[0]/avg_f[1]
    return gdata

def create_image(gdata, scale=20):
    """
    Tworzy obraz w przestrzeni hsv przedstawiający przegieb testu grafomotorycznego.
    Wsp scale oznacza jka bardzo obraz ma być przeskalowany w stosunku do rozmiaru danych wejściowych
    Siła nacisku reprezentowana jest jako barwa (H): zielony - zółty - czerwony : słaba - średnia - wysoka
    Prędkość rysowania reprezentowana jest jako (V): większa wartość to większa prędkość                            #TODO
    Kąty rysowania reprezentowane jako wektory wychodzące                                                           #TODO
    :param gdata: dict
    :param scale: int
    :return: dict
    """
    # TODO draw vectors
    w,h = int((gdata['pos_x'][1])/scale)+2, int((gdata['pos_y'][1])/scale)+2
    data = np.zeros((w, h, 3), dtype=np.float)
    for i in gdata['data']:
        if i['force'] > 0:
            X,Y = i['x']/scale, i['y']/scale
            if int(X) != X: Xt = [int(X), int(X)+1]
            else: Xt = [int(X)]
            if int(Y) != Y: Yt = [int(Y), int(Y)+1]
            else: Yt = [int(Y)]
            for x in Xt:
                for y in Yt:
                    color = 0.350 - (0.350 * i['force']/gdata['max_force'])
                    data[x,y] = [color, 1, 1]


    gdata["image"] = data
    return gdata

