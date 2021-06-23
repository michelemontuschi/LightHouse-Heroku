import numpy as np
from scipy.interpolate import interp2d
from my_interpolator import get_f_value_all, get_interp
import tqdm
from skimage import io
import my_layer
import my_config
import plotly.graph_objects as go
import my_interpolator
import my_POI
import pandas as pd
import json
from my_config import get_depth
import pickle
import math
from osgeo import gdal
import geopandas

from my_config import calc_dist, calc_dist_3D, get_value_deg,calc_dist_2

def add_points_axis(axis, n_points):
    axis_new = []
    for i in range(len(axis) - 1):
        for j in range(n_points):
            axis_new.append(axis[i]+j*(axis[i + 1]-axis[i])/n_points)
    axis_new.append(axis[len(axis)-1])
    return axis_new

def increase_depth(depths, perc):
    depth_new = []
    for depth in depths:
        depth_new.append(depth + perc)
    return depth_new


def get_depth_all(files, lonlon, latlat):
    lonmins = []
    lonmaxs = []
    latmins = []
    latmaxs = []
    lon_divs = []
    lat_divs = []
    my_dicts=[]
    fnames=[]

    for file in files:
        with open('./data/config/config' + file + '.txt', 'r') as f:
            lonmins.append(float(f.readline().split()[1]))
            lonmaxs.append(float(f.readline().split()[1]))
            latmins.append(float(f.readline().split()[1]))
            latmaxs.append(float(f.readline().split()[1]))
            lon_divs.append(int(f.readline().split()[1]))
            lat_divs.append(int(f.readline().split()[1]))
            fnames.append(file)

        with open('./data/interpol/interpolator' + file + '.pkl', 'rb') as fInterp:
            my_dicts.append(pickle.load(fInterp))




    func = np.vectorize(get_f_value_all, otypes=[float])

    func.excluded.add(2)
    func.excluded.add(3)
    func.excluded.add(4)
    func.excluded.add(5)
    func.excluded.add(6)
    func.excluded.add(7)
    func.excluded.add(8)

    zz = func(lonlon, latlat, lonmins, lonmaxs, latmins, latmaxs, lon_divs, lat_divs, my_dicts)


    return zz


if __name__ == '__main__':

    sec_table = pd.read_csv('./data/auth/sec_table.csv')
    text_list_hidden = sec_table['Name'].values
    text_list = text_list_hidden[13:19 + 1]


    print('KP---------------------------------->')
    df = pd.read_csv('./data/SHP/IGI002_RPL_OSS1_A_06.csv', ',')

    lat_points = []
    lat_points_selected = []
    lon_points = []
    lon_points_selected = []
    for i, j in zip(df.Latitude, df.Longitude):
        lat_points.append(get_value_deg(i))
        lon_points.append(get_value_deg(j))

    df['Latitude_tot'] = lat_points
    df['Longitude_tot'] = lon_points

    lon_points = add_points_axis(lon_points, 2000)
    lat_points = add_points_axis(lat_points, 2000)


    depthAll = get_depth_all(text_list, lon_points, lat_points)
    depthAll = increase_depth(depthAll, 1)

    dist_arr3D = []
    dist_arr2D = []
    dist_arr_3Dselected = []
    dist_arr_2Dselected = []
    dist_arr3D.append(0)
    dist_arr2D.append(0)
    dist3D = 0
    dist2D = 0


    for i in range(len(lon_points) - 1):

        tDist2D_1 = calc_dist(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1])
        tDist2D = calc_dist_2(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1], 0, 0)


        h=((depthAll[i]-depthAll[i + 1])/1000)


        tDist3D_1 = np.sqrt(tDist2D**2+h**2)
        tDist3D = calc_dist_2(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1], depthAll[i], depthAll[i+1])



        if math.isnan(tDist3D):
            tDist3D = tDist2D


        dist3D = dist3D + tDist3D
        dist2D = dist2D + tDist2D

        dist_arr3D.append(dist3D)
        dist_arr2D.append(dist2D)

    #print(len(lat_points), len(lon_points), len(depthAll), len(dist_arr3D), len(dist_arr2D), max(dist_arr3D), max(dist_arr2D))


    df= pd.DataFrame()
    df['lat']=lat_points
    df['lon']=lon_points
    df['depth']=depthAll
    df['dist2D']=dist_arr2D
    df['dist3D']=dist_arr3D
    print(df)
    df.to_csv('IsraelKP.csv')

    dist_arr = df['dist2D']
    labels_value = np.arange(0, int(max(dist_arr)), 5)
    labels_value = np.append(labels_value, np.amax(labels_value) + 5)
    label_lon = []
    label_lat = []



    counter=0
    print(len(lat_points),len(lon_points),len(dist_arr),)
    for tlat, tlon, tdist in zip(lat_points, lon_points, dist_arr):
        if (int(tdist) == labels_value[counter]):
            print(labels_value[counter])
            label_lon.append(tlon)
            label_lat.append(tlat)
            counter = counter + 1

    label_lon.append(max(lon_points))
    label_lat.append(max(lat_points))
    #label_depth.append(max(label_depth))

    depth_increase = 1
    label_depth = get_depth_all(text_list, label_lon, label_lat)

    label_depth = increase_depth(label_depth, 1)

    df_label = pd.DataFrame()
    df_label['lat'] = label_lat
    df_label['lon'] = label_lon
    df_label['depth'] = label_depth
    df_label['value'] = labels_value
    print(df_label)
    df_label.to_csv('IsraelKP_label.csv')

