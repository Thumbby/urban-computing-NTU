import os

import pandas as pd
import matplotlib.pyplot as plt
import shapefile

from Tools.Matching_tools import Get_Nearest_line
from TrajectoryMatch import Search_within

train_data = pd.read_csv('./train-1000.csv')
output_file='C:\\Users\\Sunseap\Desktop\\out'
existed_files=os.listdir(output_file)
shp_file='C:\\Users\\Sunseap\Desktop\\portugal-latest-free.shp/gis_osm_roads_free_1.shp'

lon_range = 0.005
lat_range = 0.0025

def MapMatching():
    # 1 read the geometric data and attribute data of the original file
    try:
        shp = shapefile.Reader(shp_file, encoding='utf-8')
        shape_records = shp.shapeRecords()
        shape_type = shp.shapeType
        shape_fields = shp.fields
    except UnicodeDecodeError:
        shp = shapefile.Reader(shp_file, encoding="gbk")
        shape_records = shp.shapeRecords()
        shape_type = shp.shapeType
        shape_fields = shp.fields

    f = open('log.txt', 'w')
    f2 = open('error.txt', 'w')
    for i in range(train_data.shape[0]):
        # each record is independent - a track
        if str(i) not in existed_files:
            this_dir=os.path.join(output_file,str(i))
            os.mkdir(this_dir)
            out_f=open(os.path.join(this_dir, 'log.txt'), 'w')
            tra=eval(train_data['POLYLINE'][i])
            # record the matching road segment id corresponding to the current track
            road_id_list=[]

            for p in tra:
                print(p)
                thisLon = float(p[0])
                thisLat = float(p[1])
                # define the neighborhood of a query
                # reference http://www.360doc.com/content/19/1217/07/2495754_880250359.shtml
                lon_min = thisLon - lon_range
                lon_max = thisLon + lon_range
                lat_min = thisLat - lat_range
                lat_max = thisLat + lat_range
                # lon_min,lat_min,lon_max,lat_max
                all_results = Search_within(lon_min, lat_min, lon_max, lat_max)
                # print('points in range：',len(all_results))
                # find the nearest one, subject to direction requirements
                nearst_line,new_lon,new_lat = Get_Nearest_line(p, all_results)
                if nearst_line != None:
                    road_id = nearst_line['id_num']
                else:
                    f2.write(str(thisLon)+','+str(thisLat)+'\n')

                # "TRIP_ID","CALL_TYPE","ORIGIN_CALL","ORIGIN_STAND","TAXI_ID","TIMESTAMP","DAY_TYPE","MISSING_DATA","POLYLINE"
                result=str(train_data.loc[i,'TRIP_ID']) + ','\
                       + str(train_data.loc[i,'CALL_TYPE']) + ','\
                       + str(train_data.loc[i, 'ORIGIN_CALL']) + ','\
                       + str(train_data.loc[i, 'ORIGIN_STAND']) + ','\
                       + str(train_data.loc[i, 'TAXI_ID']) + ','\
                       + str(train_data.loc[i, 'TIMESTAMP']) + ','\
                       + str(train_data.loc[i, 'DAY_TYPE']) + ','\
                       + str(train_data.loc[i, 'MISSING_DATA']) + ','+ str(thisLon)+','+str(thisLat)+','+ str(new_lon)+','+str(new_lat)+','+str(road_id)+ '\n'
                road_id_list.append(road_id)
                f.write(result)
                out_f.write(result)
                print(result)

            out_f.close()
            # write the road segment that has been matched to shp
            # 2 create export file
            new_path=os.path.join(this_dir,str(i)+'.shp')
            w = shapefile.Writer(target=new_path, shapeType=shape_type, autoBalance=1)
            # 3 create the same attributes as the original file
            for shape_field in shape_fields:
                w.field(*shape_field)
            # 4 filter records based on attributes and write to a new file
            for shape_record in shape_records:
                if shape_record.shape.oid in road_id_list:
                    w.shape(shape_record.shape)
                    w.record(*shape_record.record)
    f.close()
    f2.close()

def vis_single_GPS_point(trip_number, color, savepath=None, if_line=False, show=True):
    fig, ax =plt.subplots()
    gps_points = eval(train_data['POLYLINE'][trip_number])
    x, y = zip(*gps_points)

    # resize the map
    x_gap, y_gap = (max(x) - min(x))/2, (max(y) - min(y))/2
    x_mid, y_mid = (max(x) + min(x))/2, (max(y) + min(y))/2
    ax.set_xlim(x_mid - x_gap*1.2, x_mid + x_gap*1.2)
    ax.set_ylim(y_mid - y_gap*1.2, y_mid + y_gap*1.2)

    if if_line:
        ax.plot(x, y, linewidth = 4, color=color, linestyle='-', marker='o', markersize=50)
    else:
        ax.scatter(x, y, c=color, marker='o',s=50)

    if savepath:
        fig.savefig(savepath)
        print(f'GPS{trip_number+1} picture is completed.')

    if show:
        plt.show()

if __name__ == '__main__':
    MapMatching()
