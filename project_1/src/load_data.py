from dataclasses import dataclass
from src.sample.compute import *
from pathlib import Path


@dataclass
class PathData:
    # acce in sample
    acce: np.array
    # gyro in sample
    gyro: np.array
    # ahrs in sample
    ahrs: np.array
    # magn in sample
    magn: np.array
    # wifi in sample
    wifi: np.array
    # ibeacon in sample
    ibeacon: np.array
    # waypoint in sample
    waypoint: np.array


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
            bssid = data_line[3]
            rssi = data_line[4]
            wifi_data = [ts, bssid, rssi]
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
    type_wif = np.array(type_wif)
    type_bea = np.array(type_bea)
    type_way = np.array(type_way)

    return PathData(type_acc, type_gyr, type_rot, type_mag, type_wif, type_bea, type_way)


def read_path_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    return assmble_path_data(lines)


def combine_data_with_position(path_data_files, augmentation=True):
    combined_data = {}
    for path_filename in list(Path(path_data_files).resolve().glob("*.txt")):
        print('Processing file:', path_filename)
        path_data = read_path_data(path_filename)
        acce_data = path_data.acce
        magn_data = path_data.magn
        ahrs_data = path_data.ahrs
        wifi_data = path_data.wifi
        ibeacon_data = path_data.ibeacon
        waypoint_data = path_data.waypoint

        if augmentation:
            positions = compute_step_positions(acce_data, ahrs_data, waypoint_data)
        else:
            positions = waypoint_data

        if wifi_data.size != 0:
            sep_tss_wifi = np.unique(wifi_data[:, 0].astype(float))
            wifi_data_list = split_ts_seq(wifi_data, sep_tss_wifi)
            for wifi in wifi_data_list:
                diff = np.abs(positions[:, 0] - float(wifi[0, 0]))
                index = np.argmin(diff)
                position_key = tuple(positions[index, 1:3])
                if position_key in combined_data:
                    combined_data[position_key]['wifi'] = np.append(combined_data[position_key]['wifi'], wifi, axis=0)
                else:
                    combined_data[position_key] = {
                        'magnetic': np.zeros((0, 4)),
                        'wifi': wifi,
                        'ibeacon': np.zeros((0, 3))
                    }

        if ibeacon_data.size != 0:
            sep_tss_ibeacon = np.unique(ibeacon_data[:, 0].astype(float))
            ibeacon_data_list = split_ts_seq(ibeacon_data, sep_tss_ibeacon)
            for ibeacon in ibeacon_data_list:
                diff = np.abs(positions[:, 0] - float(ibeacon[0, 0]))
                index = np.argmin(diff)
                position_key = tuple(positions[index, 1:3])
                if position_key in combined_data:
                    combined_data[position_key]['ibeacon'] = np.append(combined_data[position_key]['ibeacon'], ibeacon,
                                                                       axis=0)
                else:
                    combined_data[position_key] = {
                        'magnetic': np.zeros((0, 4)),
                        'wifi': np.zeros((0, 3)),
                        'ibeacon': ibeacon
                    }

        sep_tss_magn = np.unique(magn_data[:, 0].astype(float))
        magnetic_data_list = split_ts_seq(magn_data, sep_tss_magn)
        for magnetic in magnetic_data_list:
            diff = np.abs(positions[:, 0] - float(magnetic[0, 0]))
            index = np.argmin(diff)
            position_key = tuple(positions[index, 1:3])
            if position_key in combined_data:
                combined_data[position_key]['magnetic'] = np.append(combined_data[position_key]['magnetic'], magnetic,
                                                                    axis=0)
            else:
                combined_data[position_key] = {
                    'magnetic': magnetic,
                    'wifi': np.zeros((0, 3)),
                    'ibeacon': np.zeros((0, 3))
                }
    return combined_data
