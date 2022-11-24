from GeoTools import GetNearestDistance, getDistanceBtwP

def Get_Nearest_line(p,all_results):
    nearst_line=None
    min_dist=999999
    for raod in all_results:
        line_list=raod["geo_lines"]["coordinates"]
        for line in line_list:
            # distance from PCx,PCy to PAx,PAy,PBx,PBy
            pA=line[0]
            pB=line[1]
            dist=GetNearestDistance(pA[0], pA[1], pB[0], pB[1], float(p[0]), float(p[1]))
            if dist<min_dist:
                # p_foot=get_foot(pA, pB,[float(p[0]), float(p[1])])
                # nearest neightbour
                dist_a=getDistanceBtwP(pA[0], pA[1], float(p[0]), float(p[1]))
                dist_b = getDistanceBtwP(pB[0], pB[1], float(p[0]), float(p[1]))
                if dist_a<dist_b:
                    new_lon=pA[0]
                    new_lat=pA[1]
                else:
                    new_lon = pB[0]
                    new_lat = pB[1]
                min_dist=dist
                nearst_line=raod

    return nearst_line,new_lon,new_lat
