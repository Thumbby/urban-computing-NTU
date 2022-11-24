
import csv

from pymongo.errors import DuplicateKeyError
import os
from ReadShpFiles import MaxBoundary_minLon, ReadShpFile, roorDir, findfiles, GetAllPkls
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import pickle

from ReadTraFiles import FindAllFiles, GetAllTrackPts
from GeoTools import GetNearestDistance
from mongo.base import MongoDBLink

# add to database
def AddToBase(shpFile):
    file_name=shpFile.split('全国路网-wgs84')[1]
    print('reading...' + file_name)
    dataBase = MongoDBLink('RoadData').db

    all_collections=dataBase.list_collection_names()
    if file_name not in all_collections:
        # create new collection
        print('create new collection：',file_name)
        this_col = dataBase[file_name]
    else:
        print('Collection already exists, record can be inserted directly.')
        this_col = dataBase[file_name]

    # create unique index
    this_col.create_index([("id_num", 1)], unique=True)
    # create space index
    this_col.create_index([("geo_lines", "2dsphere")], background=True)

    all_items=this_col.find({})
    count=0
    for item in all_items:
        count+=1

    shapes = ReadShpFile(shpFile)
    for shape in shapes[count:]:
        id_num = shapes.index(shape)
        MultiLineString_coor=[]
        for i in range(1,len(shape.points)):
            this_p=list(shape.points[i])
            last_p=list(shape.points[i-1])
            MultiLineString_coor.append([last_p,this_p])

        data={
            'id_num':id_num,
            "geo_lines":{
                "type": "MultiLineString",
                "coordinates": MultiLineString_coor
            }
        }
        try:
            this_col.insert_one(data)
            print(file_name + ': ' + str(id_num) + '/' + str(len(shapes)))
        except DuplicateKeyError:
            print('DuplicateKey:'+str(id_num))

# multiProcess add to database
def AddToBase_multiProcess():
    shpFileList=findfiles(roorDir)
    # do multiprocessing InsertNode(shpFile)
    pool = Pool(processes=8)
    result = pool.map(AddToBase, shpFileList)
    pool.close()
    pool.join()

def AddToBase_single(pinckle_file):
    shapes=[]
    with open(pinckle_file, "rb") as f:
        shapes = pickle.load(f)

    print('AddToBase_single')
    file_name=pinckle_file.split('pinckle')[1]
    dataBase = MongoDBLink('RoadData').db

    all_collections = dataBase.list_collection_names()
    if file_name not in all_collections:
        #
        print('create new collection：', file_name)
        this_col = dataBase[file_name]
    else:
        print('Collection already exists, record can be inserted directly.')
        this_col = dataBase[file_name]

    #
    this_col.create_index([("geo_lines", 1)], unique=True)
    #
    this_col.create_index([("geo_lines", "2dsphere")], background=True)

    for shape in shapes:
        id_num = shapes.index(shape)
        MultiLineString_coor=[]
        for i in range(1,len(shape.points)):
            this_p=list(shape.points[i])
            last_p=list(shape.points[i-1])
            MultiLineString_coor.append([last_p,this_p])

        data={
            'id_num':id_num,
            "geo_lines":{
                "type": "MultiLineString",
                "coordinates": MultiLineString_coor
            }
        }
        try:
            this_col.insert_one(data)
            print(file_name + ': ' + str(id_num) + '/' + str(len(shapes)))
        except DuplicateKeyError:
            print('DuplicateKey:'+str(id_num))

def AddToBase_single_File_multiProcess():
    # get all pinckle files
    all_pkls=GetAllPkls('D:\MyDocument\DeskTop\道路轨迹剔除/2020高德全国路网分省.rar等4个文件\全国路网-wgs84\pinckle')

    # p = ThreadPool(15)
    # pool_output = p.map(AddToBase_single, paraList)
    pool = Pool(processes=8)
    result = pool.imap(AddToBase_single, all_pkls)
    pool.close()
    pool.join()


# query geometric features within a specific range
def Search_within(lon_min,lat_min,lon_max,lat_max):
    conn=MongoDBLink('db')
    dataBase = conn.db
    all_results=[]
    all_ids=[]
    all_collections = dataBase.list_collection_names()
    for col_name in all_collections:
        result=dataBase[col_name].find(
            {
                "geo_lines": {
                    "$geoWithin": {
                        "$geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [lon_min, lat_min],
                                [lon_min, lat_max],
                                [lon_max, lat_max],
                                [lon_max, lat_min],
                                [lon_min, lat_min]
                            ]]
                        }
                    }
                }
            }
        )
        # print(col_name)
        for item in result:
            all_results.append(item)
            all_ids.append(item['id_num'])

    print('### The number of results found in the range',len(all_ids))
    conn.client.close()
    return all_results

# Parse the find query result and judge the relationship with point
def Relation_p_road(point,all_results):
    flag=False
    bufferDist = 12
    for raod in all_results:
        line_list=raod["geo_lines"]["coordinates"]
        for line in line_list:
            # Distance from point PCx, PCy to line segment PAx, PAy, PBx, PBy
            pA=line[0]
            pB=line[1]
            dist=GetNearestDistance(pA[0], pA[1], pB[0], pB[1], point[0], point[1])
            if dist<bufferDist:
                # print(dist)
                flag=True
                break
    if flag:
        return 1
    else:
        return 0

def RelationCal_multi_process():
    FileList = FindAllFiles('./tra_data')
    pool = Pool(processes=15)
    result = pool.map(RelationshipTrajToRoad, FileList)
    pool.close()
    pool.join()

def RelationshipTrajToRoad(file):
    ountput_dir='./out/'
    file_strs=file.split('/')
    precision_type=file_strs[1].split('\\')[1]
    csv_name=precision_type+'_'+file_strs[2].split('.')[0]+'.csv'

    try:
        track_pts = GetAllTrackPts(file)
        # print(csv_name + '；track_p_num=' + str(len(track_pts)))
        #Determine whether the current file exists, and exit the function if it exists
        if os.path.exists(ountput_dir + csv_name):
            # print('the file already exists！！')
            return
        # open the file in the write mode
        f = open(ountput_dir + csv_name, 'w', newline='',encoding='GBK')
        print(csv_name + '； Writenfile Opened.')
        # create the csv writer
        writer = csv.writer(f, delimiter=',')
        # For each track point, query the road segments within a certain range nearby, and then judge the relationship between the track point and the road segment
        line_count = 0
        for p in track_pts:
            thisLon = p[2]
            thisLat = p[3]
            # Define the neighborhood of a query
            # reference http://www.360doc.com/content/19/1217/07/2495754_880250359.shtml The relationship between latitude and longitude and distance
            lon_range = 0.07
            lat_range = 0.03
            lon_min = thisLon - lon_range
            lon_max = thisLon + lon_range
            lat_min = thisLat - lat_range
            lat_max = thisLat + lat_range
            # lon_min,lat_min,lon_max,lat_max
            all_results = Search_within(lon_min, lat_min, lon_max, lat_max)
            # Determine the relationship between track points and roads
            if_in = Relation_p_road([thisLon, thisLat], all_results)
            p.append(if_in)
            # Divide the track segment according to the result of if in: if there is a drift point, add blank lines before and after writing
            if if_in == 0:
                writer.writerow([])
            # write a row to the csv file
            writer.writerow(p)
            line_count += 1
        # close the file
        print(csv_name + '； has writed but not close.')
        print(csv_name + ':  lines=' + str(line_count))
        f.close()
        print(csv_name + ':  file Closed!!')
    except Exception as e:
        # print('The error type is',e.__class__.__name__)
        print('error:', e.__class__.__name__, e)


if __name__ == '__main__':
    # AddToBase_multiProcess()
    # AddToBase_single_File_multiProcess()
    # shpFile = findfiles(roorDir)[0]
    # AddToBase(shpFile)
    RelationCal_multi_process()

    # file='D:\MyDocument\DeskTop\道路轨迹剔除\csv//亚米级/000781101011364_2020-11-05.csv'
    # RelationshipTrajToRoad(file)
