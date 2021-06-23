import numpy as np
import os
import pandas as pd
import tqdm



try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

def find_coord(x,range, div):

    delta = (range[1]-range[0])/div

    n = int((x-range[0])/delta)

    return n

def get_f_value(lon, lat, lonmin, lonmax, latmin, latmax, lon_div, lat_div, my_dict):


    lon_range=[lonmin, lonmax]
    lat_range=[latmin, latmax]

    i_lon=find_coord(lon, lon_range, lon_div)
    i_lat=find_coord(lat, lat_range, lat_div)

    isOut_lon=(lon<=lonmin) or (lon>=lonmax)
    isOut_lat=(lat<=latmin) or (lat>=latmin)



    if '{},{}'.format(i_lon, i_lat) in my_dict:
        f = my_dict['{},{}'.format(i_lon, i_lat)]
        out = f([lon], [lat])

        if out == 0:
            print(lon, lat, i_lon, i_lat, lon_range, lat_range, lon_div)

    else:
        out = "nan"

    #if not isOut_lon or isOut_lat:
         #print('éfuori-------------------->', lon, lon_range, lat, lat_range)



    return out

def get_f_value_all(lon, lat, lonmins, lonmaxs, latmins, latmaxs, lon_divs, lat_divs, my_dicts):

    my_dict=-99
    lonmin=-99
    lonmax=-99
    latmin=-99
    latmax=-99
    lon_div=-99
    lat_div=-99
    out='nan'

    
    for lomin, loMax, lamin, laMax, loDiv, laDiv, dict_i in zip(lonmins, lonmaxs, latmins, latmaxs,lon_divs, lat_divs,  my_dicts):
        isOut_lon = (lon <= lomin) or (lon >= loMax)
        isOut_lat = (lat <= lamin) or (lat >= laMax)

        if not isOut_lon and not isOut_lat:
            my_dict=dict_i
            lonmin = lomin
            lonmax = loMax
            latmin = lamin
            latmax = laMax
            lon_div = loDiv
            lat_div = laDiv
            break

    lon_range=[lonmin, lonmax]
    lat_range=[latmin, latmax]

    if my_dict!=-99:
        i_lon=find_coord(lon, lon_range, lon_div)
        i_lat=find_coord(lat, lat_range, lat_div)

        isOut_lon=(lon<=lonmin) or (lon>=lonmax)
        isOut_lat=(lat<=latmin) or (lat>=latmin)



        if '{},{}'.format(i_lon, i_lat) in my_dict:
            f = my_dict['{},{}'.format(i_lon, i_lat)]
            out = f([lon], [lat])

    return out


def get_interp(f_config, f_interp, lon_range=[-150.29851795, -150.28791342], lat_range=[35.90668655, 35.91943936], n_div=100):


    lon_axis = np.linspace(lon_range[0], lon_range[1], n_div, False)
    lat_axis = np.linspace(lat_range[0], lat_range[1], n_div, False)


    grid = np.array(np.meshgrid(lon_axis, lat_axis))
    grid = np.array(grid).T.reshape(-1, 2)

    lonlon = grid[:, 0]
    latlat = grid[:, 1]


    with open(f_config, 'r') as f:
        lonmin = float(f.readline().split()[1])
        lonmax = float(f.readline().split()[1])
        latmin = float(f.readline().split()[1])
        latmax = float(f.readline().split()[1])
        lon_div = int(f.readline().split()[1])
        lat_div = int(f.readline().split()[1])


    with open(f_interp, 'rb') as fInterp:
        my_dict = pickle.load(fInterp)


    func=np.vectorize(get_f_value, otypes=[float])
    zz = func(lonlon, latlat, lonmin, lonmax, latmin, latmax, lon_div, lat_div, my_dict)
    #zz=[]

    #for (lon, lat) in tqdm.tqdm(zip (lonlon, latlat)):
     #   z=get_f_value(lon, lat, lonmin, lonmax, latmin, latmax, lon_div, lat_div, my_dict)
     #   zz.append(z)
    #zz = np.array(zz, dtype=float)

    np.where(zz == 0, np.nan, zz)

    Z = zz.reshape(n_div, n_div)
    result = np.where(Z == 0)

    if False:#result!=[]:
        for i, j in zip(result[0], result[1]):
            Z[i, j]=Z[i-1, j-1]

    result = np.where(Z == 0)
    if False:#result!=[]:
        for i, j in zip(result[0], result[1]):
            Z[i, j]=Z[i+1, j+1]



    return lon_axis, lat_axis, Z

def get_file_range(mypath):

    df=pd.DataFrame()

    model_list = [f[12:f.find('.pkl')] for f in os.listdir(mypath)]

    model_list = ['Segment_1','Segment_2','Segment_3','Segment_4long']

    df['Segment']=model_list

    lon_min=[]
    lon_max=[]
    lat_min=[]
    lat_max=[]
    lon_div=[]
    lat_div=[]

    for f in model_list:
        lonmin, lonmax, latmin, latmax, londiv, latdiv = get_config_data(f)

        lon_min.append(lonmin)
        lon_max.append(lonmax)
        lat_min.append(latmin)
        lat_max.append(latmax)
        lon_div.append(londiv)
        lat_div.append(latdiv)

    df['lonmin'] = lon_min
    df['lonmax'] = lon_max
    df['latmin'] = lat_min
    df['latmax'] = lat_max
    df['londiv'] = lon_div
    df['latdiv'] = lat_div

    return df

def get_config_data(fName):

    with open('./data/config/config' + fName + '.txt', 'r') as f:
        lonmin = float(f.readline().split()[1])
        lonmax = float(f.readline().split()[1])
        latmin = float(f.readline().split()[1])
        latmax = float(f.readline().split()[1])
        lon_div = int(f.readline().split()[1])
        lat_div = int(f.readline().split()[1])

    return (lonmin, lonmax, latmin, latmax, lon_div, lat_div)


def get_file(value, df_files):

    for row in df_files.iterrows():
        lonmin = row[1][1]
        lonmax = row[1][2]
        latmin = row[1][3]
        latmax = row[1][4]

        if value[0]>=lonmin and value[0]<=lonmax and value[1]>=latmin and value[1]<=latmax:
            return row[1][0]
    return -1



def get_interp_files( lon_range=[-150.29851795, -150.28791342], lat_range=[35.90668655, 35.91943936], n_div=100):


    lon_axis = np.linspace(lon_range[0], lon_range[1], n_div, False)
    lat_axis = np.linspace(lat_range[0], lat_range[1], n_div, False)

    grid = np.array(np.meshgrid(lon_axis, lat_axis))
    grid = np.array(grid).T.reshape(-1, 2)

    lonlon = grid[:, 0]
    latlat = grid[:, 1]


    with open('./data/interpol/interpolator_malta.pkl', 'rb') as fInterp:
        my_dict = pickle.load(fInterp)


    func=np.vectorize(get_f_value_sing, otypes=[float])

    zz=func(lonlon,latlat, my_dict)

    zz=np.array(zz)
    np.where(zz == 0, np.nan, zz)
    Z = zz.reshape(n_div, n_div)

    return lon_axis, lat_axis, Z

def get_interp_tot(df_file):

    new_dict={}

    for f in df_file.Segment:
        with open('./data/interpol/interpolator'+f+ '.pkl', 'rb') as fInterp:
            my_dict = pickle.load(fInterp)
            new_dict[f] = my_dict

    with open('./interpolator_malta.pkl ', 'wb') as fInterp:
        pickle.dump(new_dict, fInterp)

    return 0



def get_conf_from_df(df_file, fName):

    lonmin=0
    lonmax=0
    latmin=0
    latmax=0
    lon_div=0
    lat_div=0

    for row in df_file.iterrows():
        if row[1][0]==fName:
            lonmin = row[1][1]
            lonmax = row[1][2]
            latmin = row[1][3]
            latmax = row[1][4]
            lon_div = row[1][5]
            lat_div = row[1][6]
            return lonmin, lonmax, latmin, latmax, lon_div, lat_div
    return lonmin, lonmax, latmin, latmax, lon_div, lat_div

def get_f_value_sing(lon, lat, my_dict):

    df_file=get_file_range("./data/interpol/")
    fName=get_file([lon, lat], df_file)

    lonmin, lonmax, latmin, latmax, lon_div, lat_div= get_conf_from_df(df_file, fName)

    lon_range=[lonmin, lonmax]
    lat_range=[latmin, latmax]

    i_lon=find_coord(lon, lon_range, lon_div)
    i_lat=find_coord(lat, lat_range, lat_div)

    if '{},{}'.format(i_lon, i_lat) in my_dict[fName]:
        f = my_dict[fName]['{},{}'.format(i_lon, i_lat)]
        out = f([lon], [lat])
        if out == 0:
            print('get_f_value_sing', lon, lat)
    else:
        out = "nan"
    return out












