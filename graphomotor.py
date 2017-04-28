import struct
import numpy as np
import colorsys
from PIL import Image

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
        "image": Image
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
    return result


def create_image(gdata, scale=20):
    max_x, max_y = 0, 0
    min_x, min_y = -1, -1
    max_f = 0
    for i in gdata['data']:
        if i['x'] > max_x: max_x = i['x']
        if i['y'] > max_y: max_y = i['y']
        if i['x'] < min_x or min_x == -1: min_x = i['x']
        if i['y'] < min_y  or min_y == -1: min_y = i['y']
        if i['force'] > max_f: max_f = i['force']

    w,h = int((max_x)/scale)+2, int((max_y)/scale)+2
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
                    color = 0.33 - (0.33 * i['force']/max_f)
                    data[x,y] = [color, 1, 1]


    gdata["image"] = data
    return gdata

