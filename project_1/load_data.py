import numpy as np
from dataclasses import dataclass


@dataclass
class PathData:
    # acce in sample
    acc_data: np.array
    # gyro in sample
    gyr_data: np.array
    # ahrs in sample
    rot_data: np.array
    # magn in sample
    mag_data: np.array
    mag_uncal_data: np.array
    gyr_uncal_data: np.array
    acc_uncal_data: np.array
    # wifi in sample
    wif_data: np.array
    # ibeacon in sample
    bea_data: np.array
    # waypoint in sample
    way_data: np.array


def assmble_path_data(data_lines):
    type_acc = []
    type_gyr = []
    type_rot = []
    type_mag = []
    type_mag_uncal = []
    type_gyr_uncal = []
    type_acc_uncal = []
    type_wif = []
    type_bea = []
    type_way = []

    data_type_dict = {
        'TYPE_ACCELEROMETER': type_acc,
        'TYPE_GYROSCOPE': type_gyr,
        'TYPE_ROTATION_VECTOR': type_rot,
        'TYPE_MAGNETIC_FIELD': type_mag,
        'TYPE_MAGNETIC_FIELD_UNCALIBRATED': type_mag_uncal,
        'TYPE_GYROSCOPE_UNCALIBRATED': type_gyr_uncal,
        'TYPE_ACCELEROMETER_UNCALIBRATED': type_acc_uncal,
        'TYPE_WIFI': type_wif,
        'TYPE_BEACON': type_bea,
        'TYPE_WAYPOINT': type_way
    }

    for data_line in data_lines:
        data_line = data_line.strip()

        if data_line[0] == '#' or data_line[0] is None:
            continue

        data_line = data_line.split('\t')

        if not data_type_dict.__contains__(data_line[1]):
            continue

        if data_line[1] == 'TYPE_WIFI':
            ts = data_line[0]
            ssid = data_line[2]
            bssid = data_line[3]
            rssi = data_line[4]
            last_ts = data_line[6]
            wifi_data = [ts, ssid, bssid, rssi, last_ts]
            type_wif.append(wifi_data)
            continue

        elif data_line[1] == 'TYPE_BEACON':
            ts = data_line[0]
            uuid = data_line[2]
            major = data_line[3]
            minor = data_line[4]
            rssi = data_line[6]
            beacon_data = [ts, '_'.join([uuid, major, minor]), rssi]
            type_bea.append(beacon_data)
            continue

        elif data_line[1] == 'TYPE_WAYPOINT':
            type_way.append([int(data_line[0]), float(data_line[2]), float(data_line[3])])
            continue

        else:
            data_type_dict[data_line[1]].append(
                [int(data_line[0]), float(data_line[2]), float(data_line[3]), float(data_line[4])])
            continue

    type_acc = np.array(type_acc)
    type_gyr = np.array(type_gyr)
    type_rot = np.array(type_rot)
    type_mag = np.array(type_mag)
    type_mag_uncal = np.array(type_mag_uncal)
    type_gyr_uncal = np.array(type_gyr_uncal)
    type_acc_uncal = np.array(type_acc_uncal)
    type_wif = np.array(type_wif)
    type_bea = np.array(type_bea)
    type_way = np.array(type_way)

    return PathData(type_acc, type_gyr, type_rot, type_mag, type_mag_uncal, type_gyr_uncal, type_acc_uncal, type_wif,
                    type_bea, type_way)


def read_path_data(filename):
    lines = []

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    return assmble_path_data(lines)


path_data = read_path_data(r'data/site1/B1/path_data_files/5dda33219191710006b57318.txt')
print(path_data.wif_data)


