import numpy as np
from scipy.interpolate import interp2d
from my_interpolator import get_f_value, get_interp
import tqdm
from skimage import io
import my_layer
import my_config
import plotly.graph_objects as go
import my_interpolator
import my_POI
import pandas as pd
import json
import os

from osgeo import gdal
import geopandas


if __name__ == '__main__':

    workplace=input('Do you want to modify the authorization file [A] or the sector file [S]')

    if workplace=='A':
        action=(input('Do you want to do Add user [A], Delete User [D], Modify User [M], Check the Users table[C]: '))

        if os.path.exists('auth_test.csv'):
            df=pd.read_csv('auth_test.csv', index_col=0)
        else:
            df = pd.DataFrame(columns=['User', 'PWD', 'Auth_level','init', 'end'])
            df.loc[0 if pd.isnull(df.index.max()) else df.index.max() + 1]=['root','test','100','0','20']
            df.loc[0 if pd.isnull(df.index.max()) else df.index.max() + 1]=['malta','malta','1','0','13']


        if action == 'A':
            user=input('input user: ')
            pwd=input('input pwd: ')
            auth_level=input('input auth_level: ')
            init=input('input init: ')
            end=input('input end: ')
            df.loc[0 if pd.isnull(df.index.max()) else df.index.max() + 1] = [user, pwd, auth_level, init, end]

        elif action == 'D':
            user = input('input user: ')
            df.drop(df[df['User'] == user].index.values[0], axis=0, inplace=True)


        elif action == 'M':
            old_user = input('input old user: ')

            user = input('input new user: ')
            pwd = input('input new pwd: ')
            auth_level = input('input new auth_level: ')
            init = input('input new init: ')
            end = input('input new end: ')


            df.loc[df['User'] == old_user, ['PWD']] = pwd
            df.loc[df['User'] == old_user, ['Auth_level']] = auth_level
            df.loc[df['User'] == old_user, ['init']] = init
            df.loc[df['User'] == old_user, ['end']] = end
            df.loc[df['User'] == old_user, ['User']] = user
        elif action == 'C':
            print(df)

        df.to_csv('auth_test.csv')


    if workplace=='S':
        action=(input('Do you want to do Add Sector [A], Delete a Sector [D], Modify a Sector [M], Check the Sector table[C]: '))

        if os.path.exists('sec_table.csv'):
            df=pd.read_csv('sec_table.csv', index_col=0)
        else:
            df = pd.DataFrame(columns=['Name', 'Lon', 'Lat'])

        if action == 'A':
            n_input=int(input('How many sectors do you want to add?'))

            for i in range(n_input):
                name=input('input Name: ')
                lon=input('input Lon: ')
                lat=input('input Lat: ')
                index = 0 if pd.isnull(df.index.max()) else df.index.max() + 1
                df.loc[index] = [name, lon, lat]
                df.reset_index(drop=True, inplace=True)

        elif action == 'D':
            index = int(input('input: '))
            df.drop(index, axis=0, inplace=True)
            df.reset_index(drop=True, inplace=True)


        elif action == 'M':
            index = int(input('input index: '))
            name = input('input Name: ')
            lon = input('input Lon: ')
            lat = input('input Lat: ')
            df.loc[index,'Name'] = name
            df.loc[index,'lLon'] = lon
            df.loc[index,'Lat'] = lat
            df.reset_index(drop=True, inplace=True)

        elif action == 'C':
            print(df)




        df.to_csv('sec_table.csv')







    
    