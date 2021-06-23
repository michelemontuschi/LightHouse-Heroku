import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import geometry
from my_config import get_bool_array_label


try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle





def import_polyline(path, lon_range, lat_range, label=-9999):

    df_poly = gpd.read_file(path)

    geoms = df_poly.geometry
    color = df_poly.Color


    func = np.vectorize(get_if_in, otypes=[bool])
    is_in = func(geoms, lon_range[0],lon_range[1],lat_range[0],lat_range[1])

    if label > 0:
        lab_log = get_bool_array_label(color, label)
        is_in = np.logical_and(is_in, lab_log)

    else:
        lab_log_4 = get_bool_array_label(color, 4)
        lab_log_10 = get_bool_array_label(color, 10)
        lab_log_252 = get_bool_array_label(color, 252)
        is_in_label = np.logical_or(lab_log_4, lab_log_10)
        is_in_label = np.logical_or(is_in_label, lab_log_252)
        is_in = np.logical_and(is_in, is_in_label)



    geoms_n=(geoms[is_in])
    color_n=(color[is_in])

    f_color_conv = np.vectorize(poly_color_converter, otypes=[str])

    #color_nc = f_color_conv(color_n)

    df_geom=pd.DataFrame(geoms_n)
    df_geom['Color']=color_n


    return df_geom


def get_if_in(geom, lon_min, lon_max, lat_min, lat_max):

    for point in np.asarray(geom.coords):

        is_not_lon=(point[0]<lon_min) or (point[0]>lon_max)
        is_not_lat=(point[1]<lat_min) or (point[1]>lat_max)

        if is_not_lon or is_not_lat:
            return False

    return True

def get_polyin(geom, lon_min, lon_max, lat_min, lat_max):

    for point in np.asarray(geom.coords):

        is_not_lon=(point[0]<lon_min) or (point[0]>lon_max)
        is_not_lat=(point[1]<lat_min) or (point[1]>lat_max)

        if is_not_lon or is_not_lat:
            return False

    return True


def create_polygon(pointList):
    poly = geometry.Polygon([[p[0], p[1]] for p in pointList])
    return poly



def poly_color_converter(ID):
    Color = ['purple', 'orange', 'violet', 'red', 'pink','yellow', 'gold', 'fuchsia', 'brown']

    if ID == 3:
        return Color[0]
    elif ID == 4:
        return Color[1]
    elif ID == 6:
        return Color[2]
    elif ID == 10:
        return Color[3]
    elif ID == 42:
        return Color[4]
    elif ID == 51:
        return Color[5]
    elif ID == 61:
        return Color[6]
    elif ID == 211:
        return Color[7]
    elif ID == 252:
        return Color[8]
    else:
        return 'black'


def import_shape_file():

    for i in range(13):
        if i>0:
            geodf = gpd.read_file('./data/Sectors/Sector'+ str(i))
            geodf.to_file("./data/Sectors/Sector" + str(i)+ "_JSON", driver="GeoJSON")
    #with open("./data/Sectors/Sector1_JSON") as geofile:
        #j_file = json.load(geofile)

    return 0