import random

from load_data import *
from visualize import *
import numpy as np
import os
import json


def extract_wifi_rssi(mwi_data):
    wifi_rssi = {}
    for position_key in mwi_data:
        wifi_data = mwi_data[position_key]['wifi']
        for wifi_d in wifi_data:
            bssid = wifi_d[2]
            rssi = int(wifi_d[3])

            if bssid in wifi_rssi:
                position_rssi = wifi_rssi[bssid]
                if position_key in position_rssi:
                    rssi = position_rssi[position_key][0]
                    wifi_count = position_rssi[position_key][1]
                    position_rssi[position_key][0] = (rssi * wifi_count + rssi) / (wifi_count + 1)
                    position_rssi[position_key][1] = wifi_count + 1
                else:
                    position_rssi[position_key] = np.array([rssi, 1])
            else:
                position_rssi = {position_key: np.array([rssi, 1])}

            wifi_rssi[bssid] = position_rssi

    return wifi_rssi


def vis_wifi(site, floor, select_random=True):
    print('Processing wifi rssi on floor', floor, 'in', site)
    file_path = os.path.join('../data/', site, floor)
    floor_info_path = os.path.join(file_path, 'floor_info.json')
    floor_image_path = os.path.join(file_path, 'floor_image.png')

    with open(floor_info_path) as floor_info_file:
        map_info = json.load(floor_info_file)['map_info']

    map_height = map_info['height']
    map_width = map_info['width']

    path_data_files = os.path.join(file_path, 'path_data_files')
    mwi_data = calibrate_magnetic_wifi_ibeacon_to_position(path_data_files)
    wifi_rssi = extract_wifi_rssi(mwi_data)
    if select_random:
        target_wifi = random.choice(list(wifi_rssi.keys()))
        print(target_wifi)
    else:
        target_wifi = input(f"Please input target wifi ap bssid:\n")
    position = np.array(list(wifi_rssi[target_wifi].keys()))
    values = np.array(list(wifi_rssi[target_wifi].values()))[:, 0]
    visualize_heatmap(position, values, floor_image_path, map_width, map_height, colorbar_title='wifi_rssi', save_path='../out/wifi_rssi', save_name=f'{target_wifi.replace(":", "-")}.png',
                      title=f'Wifi: {target_wifi} RSSI', show=True)


if __name__ == '__main__':
    vis_wifi('site1', 'F1')
