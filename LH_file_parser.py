import numpy as np
from scipy.interpolate import interp2d
from my_interpolator import get_f_value, get_interp
import tqdm
from skimage import io
import utm
import matplotlib.pyplot as plt
import pandas as pd



try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle


def import_raster(fName):

    name = 'C:/Users/Michele Montuschi/Desktop/datiLH/NewData/Rasters/' + fName + '.txt'
    with open(name, 'r') as f:

        ncols = int(f.readline().split()[1])
        nrows = int(f.readline().split()[1])
        xllcorner = float(f.readline().split()[1])
        yllcorner = float(f.readline().split()[1])
        cellsize = float(f.readline().split()[1])
        NODATA_value = int(f.readline().split()[1])

        print('ncols = ', ncols)
        print('nrows = ', nrows)
        print('xllcorner = ', xllcorner)
        print('yllcorner = ', yllcorner)


        print("Start reading file")
        data_table = np.loadtxt(name, skiprows=6)
        print("Inserting NAN")
        data_table[data_table == NODATA_value] = np.nan
        print("Finished file processing")



    return data_table, ncols, nrows, xllcorner, yllcorner, cellsize


def get_row_compressor(old_dimension, new_dimension):
    dim_compressor = np.zeros((new_dimension, old_dimension))
    bin_size = float(old_dimension) / new_dimension
    next_bin_break = bin_size
    which_row = 0
    which_column = 0
    while which_row < dim_compressor.shape[0] and which_column < dim_compressor.shape[1]:
        if round(next_bin_break - which_column, 10) >= 1:
            dim_compressor[which_row, which_column] = 1
            which_column += 1
        elif next_bin_break == which_column:

            which_row += 1
            next_bin_break += bin_size
        else:
            partial_credit = next_bin_break - which_column
            dim_compressor[which_row, which_column] = partial_credit
            which_row += 1
            dim_compressor[which_row, which_column] = 1 - partial_credit
            which_column += 1
            next_bin_break += bin_size
    dim_compressor /= bin_size
    return dim_compressor


def get_column_compressor(old_dimension, new_dimension):
    return get_row_compressor(old_dimension, new_dimension).transpose()

def compress_and_average(array, new_shape):
    # Note: new shape should be smaller in both dimensions than old shape
    return np.mat(get_row_compressor(array.shape[0], new_shape[0])) * \
           np.mat(array) * \
           np.mat(get_column_compressor(array.shape[1], new_shape[1]))


def get_subaxis(i, div, axis, llcorner, n_points, cellsize, rem):

    if i == div:
        log_subaxis = (np.logical_and(axis >= llcorner + (((i * n_points) - 1) * cellsize),
                                          axis < llcorner + (((i * n_points) + rem) * cellsize)))
    elif i == 0:
        log_subaxis = (np.logical_and(axis >= llcorner,
                                          axis < llcorner + ((1 + n_points) * cellsize)))
    else:
        log_subaxis = (np.logical_and(axis >= llcorner + (((i * n_points) - 1) * cellsize),
                                          axis < llcorner + ((1 + (i + 1) * n_points) * cellsize)))

    subaxis = axis[log_subaxis]

    if (len(subaxis) <= n_points) and (i < div):
        log_subaxis = (np.logical_and(axis >= llcorner + (((i * n_points) - 2) * cellsize),
                                          axis < llcorner + ((2 + (i + 1) * n_points) * cellsize)))
    subaxis = axis[log_subaxis]
    if (len(subaxis) <= n_points) and (i < div):
        print('error = ', i)
    return subaxis, log_subaxis


def get_function(fName, n_points=100):

    data_table, ncols, nrows, xllcorner, yllcorner, cellsize = import_raster(fName)

    #data_table=df_from_jpg('moon_bell.jpg', data_table.shape)
    #print(data_table)


    lon_axis = np.linspace(xllcorner, xllcorner + (cellsize * (ncols)), ncols, False)
    lat_axis = np.linspace(yllcorner, yllcorner + (cellsize * (nrows)), nrows, False)



    lon_div=int(ncols / n_points)
    lat_div=int(nrows / n_points)

    lon_rem = int(ncols % n_points)
    lat_rem = int(nrows % n_points)

    i_excluded=0
    i_tot=0

    with open('./config'+fName+'.txt', 'w') as fConfig:

        fConfig.write('lonmin= {}\n'.format(xllcorner))
        fConfig.write('lonmax= {}\n'.format(xllcorner + (cellsize * lon_div * n_points)))
        fConfig.write('latmin= {}\n'.format(yllcorner))
        fConfig.write('latmax= {}\n'.format(yllcorner + (cellsize * lat_div * n_points)))
        fConfig.write('lon_div= {}\n'.format(lon_div))
        fConfig.write('lat_div= {}\n'.format(lat_div))
        fConfig.write('cellsize= {}\n'.format(cellsize))
        fConfig.write('n_points= {}\n'.format(n_points))
        fConfig.write('lon_rem= {}\n'.format(lon_rem))
        fConfig.write('lat_rem= {}\n'.format(lat_rem))

    dict_func={}

    lon_div_max=lon_div+1
    if (lon_div%n_points)==0:
        lon_div_max = lon_div

    lat_div_max=lat_div+1
    if (lat_div%n_points)==0:
        lat_div_max = lat_div

    f_out = open("test.txt", "a")

    for i in tqdm.tqdm(range(lon_div_max)):

        lon_subaxis, lon_log_subaxis=get_subaxis(i, lon_div, lon_axis, xllcorner, n_points, cellsize, lon_rem)



        for j in range(lat_div_max):
            i_tot=i_tot+1
            lat_subaxis = get_subaxis(j, lat_div, lat_axis, yllcorner, n_points, cellsize, lat_rem)
            if j == lat_div:
                lat_log_subaxis = (np.logical_and(lat_axis >= yllcorner + (((j * n_points)-1) * cellsize),
                                                  lat_axis < yllcorner + (((j * n_points) + lat_rem) * cellsize)))
            elif j==0:
                lat_log_subaxis = (np.logical_and(lat_axis >= yllcorner ,
                                                  lat_axis < yllcorner + ((1 + n_points) * cellsize)))
            else:
                lat_log_subaxis = (np.logical_and(lat_axis >= yllcorner + (((j * n_points)-1) * cellsize),
                                                  lat_axis < yllcorner + ((1 + (j + 1) * n_points) * cellsize)))

            #####################


            lat_subaxis = lat_axis[lat_log_subaxis]
            lat_log_subaxis = np.flip(lat_log_subaxis)
            data = data_table[:, lon_log_subaxis]
            data = data[lat_log_subaxis, :]

            data = np.flip(data, 0)

            nan_max=(data.shape[0]*data.shape[1])

            if (np.count_nonzero(np.isnan(data))>=nan_max):
                i_excluded = i_excluded+1


            if lat_subaxis.shape[0]!=0 and lon_subaxis.shape[0]!=0 and (np.count_nonzero(np.isnan(data))<nan_max):
                f = interp2d(lon_subaxis, lat_subaxis, data, kind='linear', copy=True, bounds_error=False, fill_value=0)
                dict_func['{},{}'.format(i, j)]=f

                f_out.write(str(i)+' ' +str(j)+' ' +str(lon_subaxis)+' ' +str(lat_subaxis)+'\n\r')



    with open('./interpolator'+fName+'.pkl ', 'wb') as fInterp:
        pickle.dump(dict_func, fInterp)


    print("you excluded  ", (i_excluded/i_tot)*100 , " % of the tiles")
    f_out.close()




def calc_interval(fName, n_points=100):

    name = 'C:/Users/Michele Montuschi/Desktop/datiLH/NewData/Rasters/' + fName + '.txt'
    with open(name, 'r') as f:

        ncols = int(f.readline().split()[1])
        nrows = int(f.readline().split()[1])
        xllcorner = float(f.readline().split()[1])
        yllcorner = float(f.readline().split()[1])
        cellsize = float(f.readline().split()[1])


        print('ncols = ', ncols)
        print('nrows = ', nrows)
        print('xllcorner = ', xllcorner)
        print('yllcorner = ', yllcorner)
        print('cellsize = ', cellsize)


    lat_axis = np.linspace(yllcorner, yllcorner + (cellsize * (nrows)), nrows, False)
    lon_axis = np.linspace(xllcorner, xllcorner + (cellsize * (ncols)), ncols, False)

    #y_axis = np.linspace(yllcorner, yllcorner + (cellsize * (nrows)), nrows, False)
    #x_axis = np.linspace(xllcorner, xllcorner + (cellsize * (ncols)), ncols, False)

    dx_vec=[]
    dy_vec=[]

    #print(utm.to_latlon(xllcorner, yllcorner, 33, 'N'))
    

    for i in tqdm.tqdm(range(nrows-1)):
        for j in range(ncols-1):

    #for i in tqdm.tqdm(range(4000)):
        #for j in range(4000):

            xy_UTM = utm.from_latlon(lat_axis[i], lon_axis[j])
            xy_UTM_1 = utm.from_latlon(lat_axis[i], lon_axis[j + 1])
            dx=xy_UTM_1[0]-xy_UTM[0]

            #lat_lon = utm.to_latlon(x_axis[i], y_axis[j], 33, 'N')
            #lat_lon_1 = utm.to_latlon(x_axis[i], y_axis[j+1], 33, 'N')
            #d_lat=lat_lon_1[0]-lat_lon[0]
            dx_vec.append(dx)

    plt.hist(dx_vec, bins=100)
    plt.savefig('dx.png')
    plt.clf()

    for i in tqdm.tqdm(range(nrows - 1)):
        for j in range(ncols - 1):
            xy_UTM = utm.from_latlon(lat_axis[i], lon_axis[j])
            xy_UTM_1 = utm.from_latlon(lat_axis[i+1], lon_axis[j])
            dy=xy_UTM_1[1]-xy_UTM[1]

            #lat_lon = utm.to_latlon(x_axis[i], y_axis[j], 33, 'N')
            #lat_lon_1 = utm.to_latlon(x_axis[i+1], y_axis[j], 33, 'N')
            #d_lon = lat_lon_1[1] - lat_lon[1]

            dy_vec.append(dy)
    plt.hist(dy_vec, bins=100)
    plt.savefig('dy.png')










def get_close(axis, value, cellsize):

    for i in range(len(axis)):
        if (abs(axis[i]-value)<=cellsize):
            return i+1





def get_single_data(fName, lon, lat):
    data_table, ncols, nrows, xllcorner, yllcorner, cellsize = import_raster(fName)
    lon_axis = np.linspace(xllcorner, xllcorner + (cellsize * (ncols)), ncols, False)
    lat_axis = np.linspace(yllcorner, yllcorner + (cellsize * (nrows)), nrows, False)
    i_lon = get_close(lon_axis, lon, cellsize)
    i_lat = get_close(lat_axis, lat, cellsize)
    return data_table[i_lat][i_lon]




def find_coord(x,range, div):

    delta = (range[1]-range[0])/div

    n = int((x-range[0])/delta)

    return n


def get_single_func(fName, lon, lat):


    with open('./data/config/config' + fName + '.txt', 'r') as f:
        lonmin = float(f.readline().split()[1])
        lonmax = float(f.readline().split()[1])
        latmin = float(f.readline().split()[1])
        latmax = float(f.readline().split()[1])
        lon_div = int(f.readline().split()[1])
        lat_div = int(f.readline().split()[1])



    with open('./data/interpol/interpolator' + fName + '.pkl ', 'rb') as fInterp:
        my_dict = pickle.load(fInterp)


    return (get_f_value(lon , lat , lonmin, lonmax, latmin, latmax,lon_div, lat_div, my_dict))

def get_matrix(fName):
    lon_min = float(input('lon_min= '))
    lon_max = float(input('lon_max= '))
    lat_min = float(input('lat_min= '))
    lat_max = float(input('lat_max= '))
    lon_range = [lon_min, lon_max]
    lat_range = [lat_min, lat_max]
    div = int(input('div= '))

    f_config = './data/config/config' + fName + '.txt'
    f_interp = './data/interpol/interpolator' + fName + '.pkl'

    print(np.sum(get_interp(f_config, f_interp, lon_range, lat_range, div)))


def df_from_jpg(path, shape):

    print(shape)
    img = io.imread(path)[1]
    print(img.shape)
    img_avg=compress_and_average(img, shape)
    print(img_avg.shape)

    #img_avg = np.flipud(img_avg)

    return img_avg



if __name__ == '__main__':

    #fName=input("Insert file name: ")
    #div_size=int(input("Insert div_size: "))
    #get_function(fName, div_size)

    #lon = float(input('get lon: '))
    #lat = float(input('get lat: '))
    #print('the original value is:', get_single_data(fName, lon, lat))
    #print('the interpolated value is:', get_single_func(fName, lon, lat))

    #get_matrix(fName)
    columns=['name', 'ambient', 'diffuse', 'roughness', 'specular', 'fresnel', 'x', 'y', 'z']




    data = pd.DataFrame([['Default', 0.8, 0.8, 0.5, 0.05, 0.2, 10, 10000, 0]], columns=columns)
    data1 = pd.DataFrame([['Scene 1', 0.6, 0.8, 0.5, 0.05, 0.2, 0, 0, 100000]], columns=columns)
    data2 = pd.DataFrame([['Scene 2', 0.6, 0.8, 0.5, 0.05, 0.2, 0, 0, -100000]], columns=columns)
    data3 = pd.DataFrame([['Scene 3', 0.4, 0.8, 0.5, 0.05, 0.2, 0, 0, 100000]], columns=columns)
    data4 = pd.DataFrame([['Scene 4', 0.4, 0.8, 0.5, 0.05, 0.2, 0, 0, -100000]], columns=columns)

    data=data.append(data1, ignore_index=True)
    data=data.append(data2, ignore_index=True)
    data=data.append(data3, ignore_index=True)
    data=data.append(data4, ignore_index=True)
    data.to_csv('light.csv', index=False)

    data = pd.read_csv('light.csv')
    ldict = data.to_dict('index')
    ldict=ldict[0]
    pos_keys = ['x', 'y', 'z']  # The keys you want
    light_keys = ['name', 'ambient', 'diffuse', 'roughness', 'specular', 'fresnel']  # The keys you want
    light_dict=dict((k, ldict[k]) for k in light_keys if k in ldict)
    pos_dict=dict((k, ldict[k]) for k in pos_keys if k in ldict)

    #print(ldict)

    rindex=data[data['name'] == 'Default'].index[0]

    print(rindex)



    #df.at[0, 'amb']=3
    #df.to_csv('light.csv')





