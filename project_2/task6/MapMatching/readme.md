# MapMatching

## Step 1 load road network to DB

#### In advance：

mongodb:create db collection: road.
```python
def RoadToDB(shpFile):
    dataBase = MongoDBLink('db').db
    # all_collections=dataBase.list_collection_names()
    this_col = dataBase['road']
```

### Tools/read_files.py

 shp road network file address

```python
shp_path='C:\\Users\\Sunseap\\Desktop\portugal-latest-free.shp/gis_osm_roads_free_1.shp'
```

## Step 2 map matching

### portugal/matching2.py

the search range, the range of latitude and longitude.

```python
lon_range = 0.005
lat_range = 0.0025
```

The file path of the trajectory to be matched

```
train_data = pd.read_csv('./train-1000.csv')
```

output format

```python
str(train_data.loc[i, 'TRIP_ID']) + ','
 + str(train_data.loc[i, 'CALL_TYPE']) + ','
 + str(train_data.loc[i, 'ORIGIN_CALL']) + ','
 + str(train_data.loc[i, 'ORIGIN_STAND']) + ','
 + str(train_data.loc[i, 'TAXI_ID']) + ','
 + str(train_data.loc[i, 'TIMESTAMP']) + ','
 + str(train_data.loc[i, 'DAY_TYPE']) + ','
 + str(train_data.loc[i, 'MISSING_DATA']) + ','
 + str(thisLon) + ',' + str(thisLat) + ','
 + str(new_lon) + ',' + str(new_lat) + ','
 + str(road_id))
```

new_lon, new_lat are the new longitude and latitude of the track points after matching.
