import math
import pyproj
from geopy import distance


class TrackPoint:
    # Time,Vehicleid,Lng,Lat,Speed
    def __init__(self, Time,Vehicleid,Lon,Lat,Speed):
        self.Time=Time
        self.Vehicleid=Vehicleid
        self.Lon=Lon
        self.Lat=Lat
        self.Speed=Speed

# directly based on xy coordinate to compute distance
def CalDistBy_XY(x1,y1,x2,y2):
    return math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

# choose WGS-84 model，distance error calculated is about 0.5%.
def CalDistBy_lonlat(lon1,lat1,lon2,lat2):
    return distance.distance((lon1,lat1), (lon2,lat2)).m

def Replace_first_0(strs):
    if strs[0]=='0':
        return strs[1]
    else:
        return strs

# calculate time difference between two GPS points
def TimeDifference(p1,p2):
    # the 0 in the hour must be removed
    p2_TIME_Hour=p2.Time.split(' ')[1].split(':')[0].replace('0','')
    p1_TIME_Hour=p2.Time.split(' ')[1].split(':')[0].replace('0','')
    # only the first digit of 0 in minutes and seconds needs to be removed
    p2_TIME_Min=Replace_first_0(p2.Time.split(' ')[1].split(':')[1])
    p1_TIME_Min=Replace_first_0(p1.Time.split(' ')[1].split(':')[1])

    p2_TIME_Sec=Replace_first_0(p2.Time.split(' ')[1].split(':')[2])
    p1_TIME_Sec=Replace_first_0(p1.Time.split(' ')[1].split(':')[2])
    # calculate the hour difference
    diffHour=int(p2_TIME_Hour)-int(p1_TIME_Hour)
    # calculate the minutes difference
    diffMinu=int(p2_TIME_Min)-int(p1_TIME_Min)
    # calculate the second difference
    diffSec =int(p2_TIME_Sec)-int(p1_TIME_Sec)
    # integrate various time differences and return the time difference in second
    TimeDiff=diffHour*3600+diffMinu*60+diffSec
    return abs(TimeDiff)

# coordinate system conversion Geographical coordinates to projected coordinates: from wgs-84 to Gaussian projection ellipsoid unchanged
def TransCoordinateSystem(lon,lat):
    GCS_WGS_1984 = pyproj.Proj(init="epsg:4326")
    WGS_1984_Web_Mercator_Auxiliary_Sphere = pyproj.Proj(init="epsg:3857")
    x, y = pyproj.transform(GCS_WGS_1984, WGS_1984_Web_Mercator_Auxiliary_Sphere, lon, lat)
    return [x,y]

# find the distance between two points according to latitude and longitude
def getDistanceBtwP(LonA, LatA,LonB, LatB):
    # calculate the distance based on the latitude and longitude of two points, X longitude, Y latitude
    radLng1 = LatA * math.pi / 180.0
    radLng2 = LatB * math.pi / 180.0
    a = radLng1 - radLng2
    b = (LonA - LonB) * math.pi/ 180.0
    s = 2 * math.asin(math.sqrt(pow(math.sin(a / 2), 2)+ math.cos(radLng1) * math.cos(radLng2) * pow(math.sin(b / 2), 2))) * 6378.137
    return s*1000

#  point PCx,PCyto line PAx,PAy,PBx,PBy distance
def GetNearestDistance(PAx, PAy,PBx, PBy,PCx,PCy):
    a=getDistanceBtwP(PAy,PAx,PBy,PBx) #the distance between two points in the longitude and latitude coordinate system
    b=getDistanceBtwP(PBy,PBx,PCy,PCx) #the distance between two points in the longitude and latitude coordinate system
    c=getDistanceBtwP(PAy,PAx,PCy,PCx) #the distance between two points in the longitude and latitude coordinate system
    if b*b>=c*c+a*a:
        return c
    if c*c>=b*b+a*a:
        return b
    l=(a+b+c)/2 #half of the circumference
    s=math.sqrt(l*(l-a)*(l-b)*(l-c)) #for area
    return 2*s/a

# extend outward along the same straight line for a certain distance and find the latitude and longitude of the target point.
def StretchalongLine(lonA,latA,lonB,latB,target_dist):
    # extend from A -> B
    # Two straight lines determine the direction of a ray P1 (x1, y1), P2 (x2, y2), P3 (x3, y3) The condition for the three points to be collinear is: (y2-y1)/(x2-x1) =(y3-y1)/(x3-x1)
    # All plane conversion relations should be transferred to the projected coordinate system
    GCS_WGS_1984 = pyproj.Proj(init="epsg:4326")
    WGS_1984_Web_Mercator_Auxiliary_Sphere = pyproj.Proj(init="epsg:3857")
    xA, yA = TransCoordinateSystem(lonA,latA)
    xB, yB = TransCoordinateSystem(lonB, latB)
    s_AB=math.sqrt((xB-xA)*(xB-xA)+(yB-yA)*(yB-yA))

    xC=xB+(xB-xA)*(target_dist/s_AB)
    yC = yB + (yB - yA) * (target_dist / s_AB)

    dist = math.sqrt((xC-xB)*(xC-xB)+(yC-yB)*(yC-yB))
    # print('Extended actual distance='+str(dist))
    lonC, latC = pyproj.transform( WGS_1984_Web_Mercator_Auxiliary_Sphere,GCS_WGS_1984, xC, yC)

    # print('Calculate B-C distance according to xy：',CalDistBy_XY(xB, yB,xC, yC))
    # print('Calculate B-C distance based on latitude and longitude：',CalDistBy_lonlat(lonB,latB,lonC, latC))
    return lonC, latC,xC,yC

# the position of the target point that needs to be passed is known, and a parallel line segment is given
def GetParallelLine(lonA,latA,lonB,latB,lonC,latC):
    [xA,yA]=TransCoordinateSystem(lonA,latA)
    [xB,yB] = TransCoordinateSystem(lonB,latB)
    [xC,yC] = TransCoordinateSystem(lonC,latC)

# judging whether two line segments intersect according to latitude and longitude
###   l1 [xa, ya, xb, yb]   l2 [xa, ya, xb, yb]
def Intersect(l1, l2):
    v1 = (l1[0] - l2[0], l1[1] - l2[1])
    v2 = (l1[0] - l2[2], l1[1] - l2[3])
    v0 = (l1[0] - l1[2], l1[1] - l1[3])
    a = v0[0] * v1[1] - v0[1] * v1[0]
    b = v0[0] * v2[1] - v0[1] * v2[0]

    temp = l1
    l1 = l2
    l2 = temp
    v1 = (l1[0] - l2[0], l1[1] - l2[1])
    v2 = (l1[0] - l2[2], l1[1] - l2[3])
    v0 = (l1[0] - l1[2], l1[1] - l1[3])
    c = v0[0] * v1[1] - v0[1] * v1[0]
    d = v0[0] * v2[1] - v0[1] * v2[0]

    if a*b < 0 and c*d < 0:
        return True
    else:

        return False
# get the vertical feet of the line and the point
def get_foot(start_point, end_point, point_a):
    start_x, start_y = start_point
    end_x, end_y = end_point
    pa_x, pa_y = point_a

    p_foot = [0, 0]
    if start_point[0] == end_point[0]:
        p_foot[0] = start_point[0]
        p_foot[1] = point_a[1]
        return p_foot

    k = (end_y - start_y) * 1.0 / (end_x - start_x)
    a = k
    b = -1.0
    c = start_y - k * start_x
    p_foot[0] = ((b * b * pa_x - a * b * pa_y - a * c) / (a * a + b * b))
    p_foot[1] = ((a * a * pa_y - a * b * pa_x - b * c) / (a * a + b * b))

    return p_foot

if __name__ == '__main__':
    print()


