import struct

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
    return result
