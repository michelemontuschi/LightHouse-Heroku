import numpy as np
import cmocean
import json
import pandas as pd
import math
import utm



from my_interpolator import get_f_value

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
font_size_big_str = "20px"
font_size_small_str = "15px"
font_size_big = 20
font_size_small = 15


def get_config_data(fName):

    with open('./data/config/config' + fName + '.txt', 'r') as f:
            lonmin = float(f.readline().split()[1])
            lonmax = float(f.readline().split()[1])
            latmin = float(f.readline().split()[1])
            latmax = float(f.readline().split()[1])

    return (lonmin, lonmax, latmin, latmax)

def get_map_data(fName):
    with open('./data/map_config/map_' + fName + '.txt', 'r') as f:
        col_th = (f.readline().split()[1])
        col_ha = (f.readline().split()[1])
        col_deep = (f.readline().split()[1])
        lat_c = float(f.readline().split()[1])
        lon_c = float(f.readline().split()[1])
        zoom_c = float(f.readline().split()[1])
        c_min_c = float(f.readline().split()[1])
        c_max_c = float(f.readline().split()[1])

    return col_th, col_ha, col_deep, lat_c, lon_c, zoom_c, c_min_c, c_max_c

def get_depth(sel_mod, lonlon, latlat):

    with open('./data/config/config' + sel_mod + '.txt', 'r') as f:
        lonmin = float(f.readline().split()[1])
        lonmax = float(f.readline().split()[1])
        latmin = float(f.readline().split()[1])
        latmax = float(f.readline().split()[1])
        lon_div = int(f.readline().split()[1])
        lat_div = int(f.readline().split()[1])

    with open('./data/interpol/interpolator' + sel_mod + '.pkl', 'rb') as fInterp:
        my_dict = pickle.load(fInterp)

    func = np.vectorize(get_f_value, otypes=[float])
    zz = func(lonlon, latlat, lonmin, lonmax, latmin, latmax, lon_div, lat_div, my_dict)

    return zz


def cmocean_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale


def get_colorscale(colorscale_name, max_len=7):
    #max_len=8
    if colorscale_name == "thermal":
        colorscale = cmocean_to_plotly(cmocean.cm.thermal, max_len)
    elif colorscale_name == "haline":
        colorscale = cmocean_to_plotly(cmocean.cm.haline, max_len)
    elif colorscale_name == "phase":
        colorscale = cmocean_to_plotly(cmocean.cm.phase, max_len)
    elif colorscale_name == "terrain":
        colorscale=[[0.0, 'rgb(200,215,133)'], [0.05, 'rgb(171,217,177)'], [0.1, 'rgb(124,196,120)'], [0.15000000000000002, 'rgb(117,193,120)'], [0.2, 'rgb(175,204,166)'], [0.25, 'rgb(219,208,78)'], [0.30000000000000004, 'rgb(241,207,14)'], [0.35000000000000003, 'rgb(242,167,0)'], [0.4, 'rgb(192,159,13)'], [0.45, 'rgb(211,192,112)'], [0.5, 'rgb(240,219,161)'], [0.55, 'rgb(252,236,192)'], [0.6000000000000001, 'rgb(248,250,234)'], [0.65, 'rgb(229,254,250)'], [0.7000000000000001, 'rgb(219,255,253)'], [0.75, 'rgb(214,251,252)'], [0.8, 'rgb(183,244,247)'], [0.8500000000000001, 'rgb(115,224,241)'], [0.9, 'rgb(29,188,239)'], [0.9500000000000001, 'rgb(0,137,245)'], [1.0, 'rgb(0,80,250)']]
    elif colorscale_name == "rainbow":
        colorscale=[[0.0, 'rgb(153,102,255)'], [0.20, 'rgb(0,0,255)'], [0.40, 'rgb(0,255,0)'], [0.6, 'rgb(255,255,0)'], [0.80, 'rgb(255,102,0)'], [1.0, 'rgb(255,0,0)']]
    elif colorscale_name == "spring":
        colorscale=[[0.0, 'rgba(203,151,206,255)'], [0.2, 'rgba(204,153,229,255)'], [0.4, 'rgba(108,153,255,255)'], [0.5, 'rgba(151,249,255,255)'], [0.6, 'rgba(160,254,18,255)'], [0.8, 'rgba(246,254,143,255)'], [1.0, 'rgba(230,154,125,255)']]
    elif colorscale_name == "autumn":
        colorscale=[[0.0, 'rgba(77,34,134,255)'], [0.2, 'rgba(149,138,189,255)'], [0.4, 'rgba(222,225,237,255)'], [0.5, 'rgba(244,243,246,255)'], [0.6, 'rgba(252,229,197,255)'], [0.8, 'rgba(237,158,60,255)'], [1.0, 'rgba(185,72,1,255)']]
    else:
        colorscale = cmocean_to_plotly(cmocean.cm.deep_r, max_len)


    return colorscale


def get_coordinates(rdata, coordinates_begin):

    coordinates = rdata[coordinates_begin + 33:]
    NO_lon = float(coordinates[:coordinates.find(',')])
    coordinates = coordinates[coordinates.find(','):]
    NO_lat = float(coordinates[10:coordinates.find(']')])
    coordinates = coordinates[coordinates.find('[') + 10:]

    NE_lon = float(coordinates[:coordinates.find(',')])
    coordinates = coordinates[coordinates.find(','):]
    NE_lat = float(coordinates[10:coordinates.find(']')])
    coordinates = coordinates[coordinates.find('[') + 10:]

    SE_lon = float(coordinates[:coordinates.find(',')])
    coordinates = coordinates[coordinates.find(','):]
    SE_lat = float(coordinates[10:coordinates.find(']')])
    coordinates = coordinates[coordinates.find('[') + 10:]

    SO_lon = float(coordinates[:coordinates.find(',')])
    coordinates = coordinates[coordinates.find(','):]
    SO_lat = float(coordinates[10:coordinates.find(']')])
    coordinates = coordinates[coordinates.find('[') + 10:]

    NO = [NO_lon, NO_lat]
    NE = [NE_lon, NE_lat]
    SE = [SE_lon, SE_lat]
    SO = [SO_lon, SO_lat]

    lon_range = [NO[0], NE[0]]
    lat_range = [SE[1], NE[1]]

    return lon_range, lat_range

def get_2D_zoom(relayoutData):
    zoom = 0
    rdata = json.dumps(relayoutData, indent=2)
    zoom_in = rdata.find('"mapbox.zoom": ')

    if rdata.find('"mapbox.zoom": ') > 0:
        zoom = rdata[zoom_in + 15:]
        zoom = float(zoom[:zoom.find(',')])

    return zoom



def get_2D_coord(relayoutData):
    lon_range = [0, 0]
    lat_range = [0, 0]
    if 'mapbox._derived' in relayoutData:
        minmin=np.asarray(relayoutData['mapbox._derived']['coordinates'][3])
        maxmax=np.asarray(relayoutData['mapbox._derived']['coordinates'][1])
        lon_range[0]=minmin[0]
        lon_range[1]=maxmax[0]
        lat_range[0]=minmin[1]
        lat_range[1]=maxmax[1]
    else:
        lon_range = []
        lat_range = []

    return lon_range, lat_range



def get_POI(sel_mod):
    POI = pd.read_csv('./data/POI/POI_' + sel_mod + '.txt', sep=";")

    lon_POI = POI["lon"].to_list()
    lat_POI = POI["lat"].to_list()
    POI_name = POI["name"].to_list()

    return lon_POI, lat_POI, POI_name

def calc_dist(min_lat,max_lat,min_lng,max_lng):

    min_lat = math.radians(min_lat)
    max_lat = math.radians(max_lat)
    min_lng = math.radians(min_lng)
    max_lng = math.radians(max_lng)

    A = math.sin(min_lat)*math.sin(max_lat)
    B = math.cos(min_lat)*math.cos(max_lat)
    C = math.cos(max_lng-min_lng)
    R = 6372.795477598

    if abs(A+B*C)>1:
        dist=R*math.acos(1)
    else:
        dist=R*math.acos(A+B*C)

    return dist



def calc_dist_2(lat1,lat2,lon1,lon2, h1, h2):

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    R = 6372795.477598

    x1=(R+h1)*np.cos(lat1)*np.cos(lon1)
    x2=(R+h2)*np.cos(lat2)*np.cos(lon2)
    y1=(R+h1)*np.cos(lat1)*np.sin(lon1)
    y2=(R+h2)*np.cos(lat2)*np.sin(lon2)
    z1=(R+h1)*np.sin(lon1)
    z2=(R+h2)*np.sin(lon2)

    dist=(np.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))/1000

    return dist


def calc_dist_3D(min_lat,max_lat,min_lng,max_lng, depth_min, depth_max):

    min_lat = math.radians(min_lat)
    max_lat = math.radians(max_lat)
    min_lng = math.radians(min_lng)
    max_lng = math.radians(max_lng)

    A = math.sin(min_lat)*math.sin(max_lat)
    B = math.cos(min_lat)*math.cos(max_lat)
    C = math.cos(max_lng-min_lng)
    R = 6372.795477598

    if abs(A+B*C)>1:
        dist=R*math.acos(1)
    else:
        dist=R*math.acos(A+B*C)

    h=(depth_max-depth_min)/1000
    dist3D=np.sqrt((dist**2)+(h**2))

    return dist3D

def get_range(sel_mod, lon_range, lat_range):

    lonmin, lonmax, latmin, latmax = get_config_data(sel_mod)

    if lon_range == []:
        lon_range = [lonmin, lonmax]
        lat_range = [latmin, latmax]
    else:
        if lon_range[0] < lonmin: lon_range[0] = lonmin
        if lon_range[1] > lonmax: lon_range[1] = lonmax
        if lat_range[0] < latmin: lat_range[0] = latmin
        if lat_range[1] > latmax: lat_range[1] = latmax

    return lon_range, lat_range


def get_range_new(sel_mod):

    lonmin, lonmax, latmin, latmax = get_config_data(sel_mod)

    lon_range = [lonmin, lonmax]
    lat_range = [latmin, latmax]

    return lon_range, lat_range

def get_colorscale_from_vec(index_array, color_array, n_col):

    pl_colors = []

    for i in range(n_col):

        if i in index_array:
            k=color_array[index_array.index(i)]
        else:
            k= 'rgb(0, 0, 0)'

        pl_colors.append([i / 255, k])



    return pl_colors

def get_colorscale_RGB():

    color_array=[]
    for i in range(256):
        for j in range(256):
            for k in range(256):
                color_array.append('#%02x%02x%02x' % (i, j, k))


    index_array = []
    for i in range(256):
        for j in range(256):
            for k in range(256):
                index_array.append(i+1000000+j*1000+k)

    colorscale=get_colorscale_from_vec(index_array, color_array, 256256256)


    return colorscale

def colorscale_trad(icol):
    cols=['deep', 'thermal', 'haline', 'terrain', 'rainbow', 'spring', 'autumn']
    return cols[icol]
def colorscale_index(col):
    cols=['deep', 'thermal', 'haline', 'terrain', 'rainbow', 'spring', 'autumn']
    return cols.index(col)

def get_value_deg(string):
    deg=float(string[:2])
    deg_60=float(string[3:5])
    deg_3600=float(string[6:12])

    emisphere=string[13:14]
    if emisphere=='S'or emisphere=='W':
        multiplier=-1
    else:
        multiplier=1

    deg_tot=multiplier*(deg+deg_60/60+deg_3600/3600)
    return(deg_tot)

def get_resolution_slider(lon_dist, lat_dist, txt_color):

    marks_value=[100, 200, 300, 400, 500]
    marks_lon=[]
    for mark in marks_value:
        marks_lon.append(lon_dist/mark)



    marks = {
        0: {'label': '0', 'style': {'color': txt_color}},
        100: {'label': '{:.2f} km'.format(marks_lon[0]), 'style': {'color': txt_color}},
        200: {'label': '{:.2f} km'.format(marks_lon[1]), 'style': {'color': txt_color}},
        300: {'label': '{:.2f} km'.format(marks_lon[2]), 'style': {'color': txt_color}},
        400: {'label': '{:.2f} km'.format(marks_lon[3]), 'style': {'color': txt_color}},
        500: {'label': '{:.2f} km'.format(marks_lon[4]), 'style': {'color': txt_color}},
    }

    return marks

def rotation(coord, alfa):
    x=coord[0]
    y=coord[1]
    x_n = x * math.cos(alfa) - y * math.sin(alfa)
    y_n = x * math.sin(alfa) + y * math.cos(alfa)

    return x_n, y_n

def get_point_str(matN):


    point_1 = str(matN[0][0]) + ',' + str(matN[0][1])
    point_2 = str(matN[1][0]) + ',' + str(matN[1][1])
    point_3 = str(matN[2][0]) + ',' + str(matN[2][1])

    arrN = 'M ' + point_1 + ' L ' + point_2 + ' L ' + point_3 + ' Z'

    return arrN


def set_axis_coord(axis_lat, axis_lon, lat_min, lon_min, coord_value=2):
    if coord_value==0:
        n_axis_lat=[]
        n_axis_lon=[]
        axis_lat=np.asarray(axis_lat)
        axis_lon=np.asarray(axis_lon)

        for lon in axis_lon:
            xy_UTM = utm.from_latlon(lat_min, lon)
            n_axis_lon.append(xy_UTM[0])
        for lat in axis_lat:
            xy_UTM = utm.from_latlon(lat, lon_min)
            n_axis_lat.append(xy_UTM[1])

        return n_axis_lat,n_axis_lon

    elif coord_value==1:
        return axis_lat, axis_lon
    else:
        n_axis_lat = []
        n_axis_lon = []
        axis_lat = np.asarray(axis_lat)
        axis_lon = np.asarray(axis_lon)

        for lat in axis_lat:
            n_axis_lat.append(calc_dist(lat_min, lat, lon_min, lon_min))
        for lon in axis_lon:
            n_axis_lon.append(calc_dist(lat_min, lat_min, lon_min, lon))

        return n_axis_lat, n_axis_lon


def get_bool_array_range(array, range):
    log = (np.logical_and(array >= range[0], array <= range[1]))
    return log

def get_bool_array_label(array, label):
    log=np.equal(array, label)
    return log