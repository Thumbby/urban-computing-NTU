import os
from os import path
import csv
import shapefile
import pickle

#roorDir='D:\MyDocument\DeskTop\道路轨迹剔除/2020高德全国路网分省.rar等4个文件\全国路网-wgs84'
MaxBoundary_minLon=73.645291
MaxBoundary_minLat=16.452144
MaxBoundary_maxLon=134.764275
MaxBoundary_maxLat=53.556479

FileList = []

def ReadShpFile(fileName):
    sf = shapefile.Reader(fileName)
    shapes = sf.shapes()
    print('ReadShpFile has finished!')
    return shapes

# divide large shp files into chunks and save many small shp files
def BreakUpTheBlock(fileName,block_size):
    sf = shapefile.Reader(fileName)
    shapes = sf.shapes()
    overall_size=len(shapes)
    block_num=int(overall_size/block_size)
    for i in range(1,block_num+1):
        ini_index=(i-1)*block_size
        end_index=i*block_size
        # if the last
        if i==block_num:
            end_index=len(shapes)
        this_block_shapes=shapes[ini_index:end_index]
        this_sf = roorDir + '/pinckle/城市二级路_分块_' + str(i) + '.pkl'
        with open(this_sf, "wb") as f:
            pickle.dump(this_block_shapes, f)
            print(this_sf)


# find all shp files in the specified directory
def findfiles(path):
    shpFileList=[]
    # first traverse all files and folders in the current directory
    file_list = os.listdir(path)
    # loop to determine whether each element is a folder or a file, if it is a folder, recursively
    for file in file_list:
        #
        cur_path = os.path.join(path, file)
        # determine whether it is a folder
        if os.path.isdir(cur_path):
            findfiles(cur_path)
        else:
            # determine whether it is a specific file name
            if file.split('.')[1]=='shp' and len(file.split('.'))==2 and file.split('.')[0]!='铁路-4326':
                real_url = path+'/'+file
                shpFileList.append(real_url)
                print(file)
    return shpFileList

def GetBoundary():
    shpFileList = findfiles(roorDir)
    for fileName in shpFileList:
        print('Searching...'+fileName)
        Shapes=ReadShpFile(fileName)
        for shape in Shapes:
            thisBox=shape.bbox
            # minLon minLat maxLon maxLat
            minLon=thisBox[0]
            minLat= thisBox[1]
            maxLon = thisBox[2]
            maxLat = thisBox[3]
            if minLon<MaxBoundary_minLon:
                MaxBoundary_minLon=minLon

            if minLat<MaxBoundary_minLat:
                MaxBoundary_minLat=minLat

            if maxLon>MaxBoundary_maxLon:
                MaxBoundary_maxLon=maxLon

            if maxLat>MaxBoundary_maxLat:
                MaxBoundary_maxLat=maxLat
    return [MaxBoundary_minLon,MaxBoundary_minLat,MaxBoundary_maxLon,MaxBoundary_maxLat]

def GetAllPkls(path):
    file_type='pkl'
    #  traverse all files and folders in the current directory
    file_list = os.listdir(path)
    # loop to determine whether each element is a folder or a file, if it is a folder, recursively
    for file in file_list:
        #
        cur_path = os.path.join(path, file)
        # determine whether it is a folder
        if os.path.isdir(cur_path):
            GetAllPkls(cur_path)
        else:
            # determine whether it is a specific file name
            if file.split('.')[1] == file_type:
                real_url = path + '/' + file
                FileList.append(real_url)
                # print(file)
    return FileList

def mainFun():
    #fileName='D:\\MyDocument\\DeskTop\\道路轨迹剔除/2020高德全国路网分省.rar等4个文件\\全国路网-wgs84/城市二级道路-4326.shp'
    block_size=100000
    BreakUpTheBlock(fileName,block_size)

if __name__ == '__main__':
    #mainFun()
