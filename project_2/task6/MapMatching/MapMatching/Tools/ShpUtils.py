import shapefile


# filter out some elements according to oid and write them into a new shp file
def CreateNewShpByAttribute(shp_file,oid_list,new_path):
    # 1 read the geometric data and attribute data of the original file
    try:
        shp = shapefile.Reader(shp_file,encoding='utf-8')
        shape_records = shp.shapeRecords()
        shape_type = shp.shapeType
        shape_fields = shp.fields
    except UnicodeDecodeError:
        shp = shapefile.Reader(shp_file, encoding="gbk")
        shape_records = shp.shapeRecords()
        shape_type = shp.shapeType
        shape_fields = shp.fields

    # 2 create export file
    w = shapefile.Writer(target=new_path, shapeType=shape_type, autoBalance=1)

    # 3 create the same attributes as the original file
    for shape_field in shape_fields:
        w.field(*shape_field)

    # 4 filter records based on attributes and write to a new file
    for shape_record in shape_records:
        if shape_record.shape.oid in oid_list:
            w.shape(shape_record.shape)
            w.record(*shape_record.record)


if __name__ == '__main__':
    #shp_file='E:\DataSet\世界各国路网\portugal-latest-free.shp/gis_osm_roads_free_1.shp'
    #CreateNewShpByAttribute(shp_file, [0,1,2,3], 'D:\MyDocument\DeskTop\out/t1.shp')
