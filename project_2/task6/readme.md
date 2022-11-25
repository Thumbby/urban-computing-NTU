
structure of code:
-   MapMatching 
    - MapMatching
      - Tools                 # tools to deal with DB
        - matching_tools.py
        - ShpUtils.py
        - dbase.py
        - read_files.py       # main function for execute load shape file to database

      - portugal
        - error.txt           # save the error info
        - log.txt             # save the map matching results.txt file which is relocated and rename to out folders
        - matching2.py        # main function for execute mapmatching
        - train-1000.csv      # source dataset
                              # train_data = pd.read_csv('./train-1000.csv')

    - Trajectory_util         # Trajectory utility tools
      - mongo
        - base.py
      - GeoTools.py
      - ReadShpFiles.py
      - TrajectoryMatch.py

    - readme.md               # readme file
    
    - venv                    # environment (already zipped, if needed, please unzip it)

-   out                       # the output files for road segmented .shp file and trace point of log.txt files
                              # output_file='C:\\Users\\Sunseap\Desktop\\out'

-   portugal-latest-free.shp  # road network shape file
                              # shp_file='C:\\Users\\Sunseap\Desktop\\portugal-latest-free.shp/gis_osm_roads_free_1.shp'

-   visualization_result      # visualization is implemented by ArcGIS Pro
                              # load .shp file output_file and then load log.txt specifically to ArcGIS Pro


# MapMatching Procedures

## Step 1 load road network to DB

### In advance：
mongodb:create db collection: road

### code for load road network to DB
```python
def RoadToDB(shpFile):
    dataBase = MongoDBLink('db').db
    # all_collections=dataBase.list_collection_names()
    this_col = dataBase['road']
```

### Tools/read_files.py  
  main function to load road network to DB

### shp road network file address
```python
shp_path='C:\\Users\\Sunseap\\Desktop\portugal-latest-free.shp/gis_osm_roads_free_1.shp'
```

## Step 2 map matching

### portugal/matching2.py
  main function to run mapmatching

### the search range, the range of latitude and longitude.
```python
lon_range = 0.005
lat_range = 0.0025
```

### The file path of the trajectory to be matched
```
train_data = pd.read_csv('./train-1000.csv')
```

### output format
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
### new_lon, new_lat are the new longitude and latitude of the track points after matching.
