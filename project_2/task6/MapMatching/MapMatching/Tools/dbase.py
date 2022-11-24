
# load road network to DB
import csv
from itertools import islice

from pymongo.errors import DuplicateKeyError
from ReadShpFiles import ReadShpFile
from mongo.base import MongoDBLink

# load shp file of road network into MongoDB
def RoadToDB(shpFile):
    dataBase = MongoDBLink('db').db
    # all_collections=dataBase.list_collection_names()
    this_col = dataBase['road']
    # create unique index
    this_col.create_index([("id_num", 1)], unique=True)
    # create spatial index
    this_col.create_index([("geo_lines", "2dsphere")], background=True)

    shapes = ReadShpFile(shpFile)
    for shape in shapes:
        id_num = shape.oid
        MultiLineString_coor = []
        for i in range(1, len(shape.points)):
            this_p = list(shape.points[i])
            last_p = list(shape.points[i - 1])
            MultiLineString_coor.append([last_p, this_p])

        data = {
            'id_num': id_num,
            "geo_lines": {
                "type": "MultiLineString",
                "coordinates": MultiLineString_coor
            }
        }
        try:
            this_col.insert_one(data)
            print('insert √')
        except DuplicateKeyError:
            print('DuplicateKey:' + str(id_num))
