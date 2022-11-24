import csv
from itertools import islice
from Tools.dbase import RoadToDB


class Point():
    def __init__(self,time,id,num1,lon,lat,speed1,num2,speed2):
        self.time=time
        self.id=id
        self.num1=num1
        self.num2 = num2
        self.speed1=speed1
        self.speed2 = speed2
        self.lon=lon
        self.lat=lat
        self.new_lon=0
        self.new_lat=0
        self.road_id=0

# slove shp file
shp_path='C:\\Users\\Sunseap\Desktop\\portugal-latest-free.shp/gis_osm_roads_free_1.shp'

def ShpUtils():
    # load Road network to MongoDB
    RoadToDB(shp_path)

if __name__ == '__main__':
    ShpUtils()

