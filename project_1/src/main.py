from visualize_wifi import vis_wifi
import os

if __name__ == '__main__':

    data_path = '../data/'
    print("There are the sites can be chosen:")
    for path in os.listdir(data_path):
        print(path)
    site = input(f'Please input the site:\n')
    print(f"There are the floor in {site} can be chosen:")
    for path in os.listdir(os.path.join(data_path, site)):
        print(path)
    floor = input(f'Please input the floor:\n')

    # visualize wifi heat rssi map
    random_wifi = input(f'whether choose wifi ap randomly(True or False):\n')
    vis_wifi(site, floor, random_wifi)
