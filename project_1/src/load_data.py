from dataclasses import dataclass
from compute_tools import *
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

    return PathData(type_acc, type_gyr, type_rot, type_mag, type_wif, type_bea, type_way)


def read_path_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    return assmble_path_data(lines)


def calibrate_magnetic_wifi_ibeacon_to_position(path_data_files):
    mwi_datas = {}
    for path_filename in list(Path(path_data_files).resolve().glob("*.txt")):
        print('Processing file:', path_filename)
        path_datas = read_path_data(path_filename)
        acce_datas = path_datas.acce
        magn_datas = path_datas.magn
        ahrs_datas = path_datas.ahrs
        wifi_datas = path_datas.wifi
        ibeacon_datas = path_datas.ibeacon
        posi_datas = path_datas.waypoint

        step_positions = compute_step_positions(acce_datas, ahrs_datas, posi_datas)

        if wifi_datas.size != 0:
            sep_tss = np.unique(wifi_datas[:, 0].astype(float))
            wifi_datas_list = split_ts_seq(wifi_datas, sep_tss)
            for wifi_ds in wifi_datas_list:
                diff = np.abs(step_positions[:, 0] - float(wifi_ds[0, 0]))
                index = np.argmin(diff)
                position_key = tuple(step_positions[index, 1:3])
                if position_key in mwi_datas:
                    mwi_datas[position_key]['wifi'] = np.append(mwi_datas[position_key]['wifi'], wifi_ds, axis=0)
                else:
                    mwi_datas[position_key] = {
                        'magnetic': np.zeros((0, 4)),
                        'wifi': wifi_ds,
                        'ibeacon': np.zeros((0, 3))
                    }

        if ibeacon_datas.size != 0:
            sep_tss = np.unique(ibeacon_datas[:, 0].astype(float))
            ibeacon_datas_list = split_ts_seq(ibeacon_datas, sep_tss)
            for ibeacon_ds in ibeacon_datas_list:
                diff = np.abs(step_positions[:, 0] - float(ibeacon_ds[0, 0]))
                index = np.argmin(diff)
                position_key = tuple(step_positions[index, 1:3])
                if position_key in mwi_datas:
                    mwi_datas[position_key]['ibeacon'] = np.append(mwi_datas[position_key]['ibeacon'], ibeacon_ds,
                                                                    axis=0)
                else:
                    mwi_datas[position_key] = {
                        'magnetic': np.zeros((0, 4)),
                        'wifi': np.zeros((0, 5)),
                        'ibeacon': ibeacon_ds
                    }

        sep_tss = np.unique(magn_datas[:, 0].astype(float))
        magn_datas_list = split_ts_seq(magn_datas, sep_tss)
        for magn_ds in magn_datas_list:
            diff = np.abs(step_positions[:, 0] - float(magn_ds[0, 0]))
            index = np.argmin(diff)
            position_key = tuple(step_positions[index, 1:3])
            if position_key in mwi_datas:
                mwi_datas[position_key]['magnetic'] = np.append(mwi_datas[position_key]['magnetic'], magn_ds, axis=0)
            else:
                mwi_datas[position_key] = {
                    'magnetic': magn_ds,
                    'wifi': np.zeros((0, 5)),
                    'ibeacon': np.zeros((0, 3))
                }
    return mwi_datas
