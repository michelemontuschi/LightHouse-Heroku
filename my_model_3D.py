import plotly.graph_objects as go
from my_interpolator import get_interp
import pandas as pd
import numpy as np
import time
import warnings
from scipy import interpolate

from stl_3d import get_stl
from my_layer import import_polyline, poly_color_converter
from my_POI import import_POI, import_annotation
from my_config import  get_depth, get_colorscale, calc_dist,calc_dist_3D, get_colorscale_from_vec, get_range, \
    get_2D_coord, get_2D_zoom, get_resolution_slider, set_axis_coord, get_value_deg


try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle


colorbar_txt ={'title': {'side': 'right', 'text': 'Depth [m]'}}



'''
Library to draw the selected section on a 3D Map

main function is:
def draw_3D(sel_mod, relayoutData, POI_label_value, poly_label_value,  table_polyd, ctx, exag_input, max_zoom,
               colorscale = 'deep',  ris = 5, coord_value=2)
               
                       
         sel_mod: selected section name
         relayoutData: data from the graph containing LAT/LON range and zoom level
         POI_label_value: POI to be displayed 
         poly_label_value:polylines to be displayed 
         table_polyd: table with the selected point of the polyline
         ctx: callback trigger infos
         exag_input: exaggeration on z axis
         max_zoom: max zoom
         colorscale: chosen colorscale
         ris : risolution
         coord_value: coordinate type (UTM, Lat/lon, Relative) 

'''
def get_axis_template(title, bgcolor):
    axis_template = {
        'showbackground': True,
        'backgroundcolor': bgcolor,
        'gridcolor': 'rgb(255, 255, 255)',
        'zerolinecolor': 'rgb(255, 255, 255)',
        'title': title,
    }
    return axis_template




# get data from interpolator
def get_data(f_config, f_interp, lon_range_in, lat_range_in, n_div=50):

    lon_range = lon_range_in
    lat_range = lat_range_in

    lon_subaxis, lat_subaxis, data_table = get_interp(f_config, f_interp, lon_range, lat_range, n_div)

    return data_table, lon_subaxis, lat_subaxis

# set axis label from coordinates
def set_axis_label(coord_value):
    x_name = 'X'
    y_name = 'Y'
    if coord_value == 0:
        mu = ' m'
    elif coord_value == 1:
        mu = ' °'
        x_name = 'lon'
        y_name = 'lat'
    elif coord_value == 2:
        mu = ' km'
    return x_name, y_name, mu

#draw the model
def draw_model_depth(lon_subaxis, lat_subaxis, data_table, colorscale_name,  coord_value):

    colorscale = get_colorscale(colorscale_name, 10)

    lat_subaxis, lon_subaxis=set_axis_coord(lat_subaxis, lon_subaxis, np.nanmin(lat_subaxis), np.nanmin(lon_subaxis), coord_value)

    x_name, y_name, mu = set_axis_label(coord_value)

    data = go.Surface(name="", x=lat_subaxis, y=lon_subaxis,
                      z=data_table,
                      colorscale=colorscale,
                      colorbar=colorbar_txt,
                      contours= dict(
                          z=dict(show= False,
                                 usecolormap=True,
                                 highlightcolor="#42f462",
                                 project= dict(z=True)
                                 ),
                      ),


                      hovertemplate=
                      '<br><b>' + x_name + '</b>: %{y:.3f}' + mu + '<br>' +
                      '<b>' + y_name + '</b>: %{x:.3f}' + mu +
                      '<br><b>depth</b>: %{z:.3f} m<br>',

                      )
    return data

#draw the model with polyline
def draw_model_depth_kp(lon_subaxis, lat_subaxis, data_table, colorscale_name,  coord_value, sel_mod, lon_range, lat_range):

    colorscale = get_colorscale(colorscale_name, 10)
    lon_KP_points, lat_KP_points=get_KP_point(sel_mod, lon_range, lat_range)
    if(len(lon_KP_points))<200:
        lon_KP_points, lat_KP_points = get_KP_point(sel_mod, lon_range, lat_range,int((200/len(lon_KP_points))*100))

    img_data_table=np.copy(data_table)

    for lat, lon in zip(lat_KP_points, lon_KP_points):
        i_lat=0
        i_lon=0
        for i in range(len(lat_subaxis)):
            if lat_subaxis[i]>lat:
                i_lat=i
                break
        for j in range(len(lon_subaxis)):
            if lon_subaxis[j]>lon:
                i_lon=j
                break
        img_data_table[i_lon][i_lat]=9000


    lat_subaxis, lon_subaxis=set_axis_coord(lat_subaxis, lon_subaxis, np.nanmin(lat_subaxis), np.nanmin(lon_subaxis), coord_value)

    x_name, y_name, mu = set_axis_label(coord_value)


    data = go.Surface(name="", x=lat_subaxis, y=lon_subaxis,
                      z=data_table,
                      surfacecolor=img_data_table,
                      colorscale=colorscale,
                      colorbar=colorbar_txt,
                      cmin=np.nanmin(data_table),
                      cmax=np.nanmax(data_table),
                      contours= dict(
                          z=dict(show= False,
                                 usecolormap=True,
                                 highlightcolor="#42f462",
                                 project= dict(z=True)
                                 ),
                      ),


                      hovertemplate=
                      '<br><b>' + x_name + '</b>: %{y:.3f}' + mu + '<br>' +
                      '<b>' + y_name + '</b>: %{x:.3f}' + mu +
                      '<br><b>depth</b>: %{z:.3f} m<br>',

                      )
    return data

#draw the compass
def draw_arrow(fName, lon_subaxis, lat_subaxis, data_table, coord_value,scale_fact, color='#e74610'):

    df_points, df_faces=get_stl(fName)
    lat_subaxis, lon_subaxis = set_axis_coord(lat_subaxis, lon_subaxis, np.nanmin(lat_subaxis), np.nanmin(lon_subaxis), coord_value)

    lon_max = np.amax(lon_subaxis)
    lat_max = np.amax(lat_subaxis)
    lon_min = np.amin(lon_subaxis)
    lat_min = np.amin(lat_subaxis)

    z_max = np.nanmax(data_table)
    z_min = np.nanmin(data_table)


    x = (0.9+df_points.z.values * 0.01) * (lat_max - lat_min) + lat_min
    y = (0.9-df_points.x.values * 0.01) * (lon_max - lon_min) * scale_fact + lon_min
    z = (1+df_points.y.values * 0.01) * (z_max - z_min) + z_min

    color=[color for i in df_faces.j]
    data = go.Mesh3d(
        x=x, y=y, z=z,
        i=df_faces.i, j=df_faces.j, k=df_faces.k,
        facecolor=color,
        hoverinfo="none"
    )
    return data

#add POI to the surface
def add_POI(sel_mod, lon_range, lat_range, label_value, coord_value):
    data = []

    if sel_mod != 'empty':

        POI = import_POI("./data/POI/Malta_POI.csv", lon_range, lat_range, label_value)

        lon_POI = POI["lon"].to_list()
        lat_POI = POI["lat"].to_list()

        POI_name = POI["ID"].to_list()
        POI_symbol = POI["symbol3D"].to_list()
        POI_attr = POI["attr"].to_list()
        POI_color = POI["color"].to_list()
        POI_desc = POI["desc"].to_list()
        POI_text = []

        for name, attr, desc in zip(POI_name, POI_attr, POI_desc):

            attr_ = str(attr)
            desc_ = str(desc)
            if attr_ == 'nan':
                attr_ = ''
            if desc_ == 'nan':
                desc_ = ''
            POI_text.append(str(name) + '\n\r' + attr_ + '\n\r' + desc_)

        depth = get_depth(sel_mod, lon_POI, lat_POI)
        lat_POI, lon_POI = set_axis_coord(lat_POI, lon_POI, np.nanmin(lat_range),np.nanmin(lon_range), coord_value)

        x_name, y_name, mu = set_axis_label(coord_value)

        data = go.Scatter3d(
            name="",
            x=lat_POI,
            y=lon_POI,
            z=depth,
            mode='markers',
            marker=dict(
                symbol=POI_symbol,
                size=8,
                color=POI_color,
                line=dict(
                    color='black',
                    width=5
                )
            ),
            text=POI_text,
            hovertemplate=
            '<br><b>'+x_name+'</b>: %{y:.3f} '+mu+'<br>'+
            '<b>'+y_name+'</b>: %{x:.3f} '+mu+
            '<br><b>depth</b>: %{z:.3f} m<br>'+
            '<b>%{text}</b>',
            hoverlabel=dict(bgcolor=POI_color)
        )


    return data

#add points on the surface from the drawn polylines
def add_drawn_poly(sel_mod, lon_range, lat_range, table, coord_value):
    data = []
    if sel_mod != 'empty':
        table=pd.DataFrame.from_dict(table)
        lon_points=table['lon']
        lat_points=table['lat']

        lat_points_axis, lon_points_axis = set_axis_coord(lat_points, lon_points, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)


        lon_sel_points=[]
        lat_sel_points=[]
        col_sel_points=[]

        colorscale = get_colorscale('thermal', len(lon_points))
        col_points=[]
        for col in colorscale:
            col_points.append(col[1])

        x_name, y_name, mu = set_axis_label(coord_value)

        if lon_range == []:

            depth = get_depth(sel_mod, lon_points, lat_points)
            data = go.Scatter3d(
                name="",
                x=lat_points_axis,
                y=lon_points_axis,
                z=depth,
                mode='markers+lines',
                marker=dict(
                    size=8,
                    color=col_points,
                    line=dict(
                        color='black',
                        width=5
                    )
                ),
                line=dict(
                    color='black',
                    width=5),
                hovertemplate=
                '<br><b>'+x_name+'</b>: %{y:.3f} '+ mu +'<br>'+
                '<b>'+y_name+'</b>: %{x:.3f} '+mu+
                '<br><b>depth</b>: %{z:.3f} m<br>'
            )


        else:
            for lon, lat, col in zip(lon_points, lat_points,col_points):
                if (lon>=lon_range[0])&(lon<=lon_range[1]):
                    if (lat >= lat_range[0]) & (lat <= lat_range[1]):
                        lon_sel_points.append(lon)
                        lat_sel_points.append(lat)
                        col_sel_points.append(col)


            if lon_sel_points !=[]:
                depth = get_depth(sel_mod, lon_sel_points, lat_sel_points)
                lat_points_axis, lon_points_axis = set_axis_coord(lat_sel_points, lon_sel_points, np.nanmin(lat_range),
                                                                  np.nanmin(lon_range), coord_value)

                data = go.Scatter3d(
                    name="",
                    x=lat_points_axis,
                    y=lon_points_axis,
                    z=depth,
                    mode='markers+lines',
                    marker=dict(
                        size=12,
                        color=col_sel_points,
                        line=dict(
                            color='black',
                            width=5
                        ),
                    ),
                    line=dict(
                        color='black',
                        width=5),
                    hovertemplate=
                    '<br><b>'+x_name+'</b>: %{y:.3f} '+mu+'<br>'+
                    '<b>'+y_name+'</b>: %{x:.3f} '+mu+
                    '<br><b>depth</b>: %{z:.3f} m<br>'
                )

    return data


#add point to the polylines from file
def add_points_axis(axis, n_points):
    axis_new = []
    for i in range(len(axis) - 1):
        for j in range(n_points):
            axis_new.append(axis[i]+j*(axis[i + 1]-axis[i])/n_points)
    axis_new.append(axis[len(axis)-1])
    return axis_new

#modify the depth of the polyline from file as a % of the z data range
def increase_depth(depths, perc,data_range):
    depth_new = []


    if perc==1:
        for depth in depths:
            depth_new.append(depth + perc)
            # depth_new.append(depth*perc)
    else:

        for depth in depths:
            depth_new.append(depth+(data_range*perc))
            #depth_new.append(depth*perc)
    return depth_new

#add the polylines from file
def add_poly_file(sel_mod, lon_range, lat_range,lat_subaxis,data_range,  label, coord_value):
    data = []
    traces = {}


    if sel_mod != 'empty':


        df = import_polyline("./data/SHP/Malta_morph_polyline_lat_lon",lon_range, lat_range, label)
        f_color_conv = np.vectorize(poly_color_converter, otypes=[str])
        colors = f_color_conv(df.Color.values)

        for i in range(len(df.geometry.values)):

            lon_points = []
            lat_points = []

            for points in df.geometry.values[i].coords:
                lon_points.append(points[0])
                lat_points.append(points[1])

            func_interp = interpolate.interp1d(lat_points, lon_points)

            lat_points=np.asarray(lat_points)
            lat_min=np.amin(lat_points)
            lat_max=np.amax(lat_points)
            log_subaxis = (np.logical_and(lat_subaxis > lat_min, lat_subaxis < lat_max))
            lat_subaxis_n = lat_subaxis[log_subaxis]


            lon_subaxis_n=(func_interp(lat_subaxis_n))

            #lon_points = lon_subaxis_n
            #lat_points = lat_subaxis_n

            lon_points = add_points_axis(lon_points, 2)
            lat_points = add_points_axis(lat_points, 2)

            depth = get_depth(sel_mod, lon_points, lat_points)
            #depth = increase_depth(depth, 0.9993, data_range)
            depth = increase_depth(depth, 0.005, data_range)

            depth=np.asarray(depth)

            lat_points, lon_points = set_axis_coord(lat_points, lon_points, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)
            traces['trace_' + str(i)] = go.Scatter3d(
                name="",
                x=lat_points,
                y=lon_points,
                z=depth,
                mode='lines',
                line=dict(
                    color=colors[i],
                    width=5),
                hoverinfo='none'

            )

            data = list(traces.values())

    return data

#Select point in a 2D Range
def select_point(lon_points, lat_points, lon_range, lat_range):

    dist_arr = []
    dist_arr_selected = []
    dist_arr.append(0)
    dist = 0

    lat_points_selected=[]
    lon_points_selected=[]

    for i in range(len(lon_points) - 1):
        dist = dist + calc_dist(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1])
        dist_arr.append(dist)

    for tlat, tlon, tdist in zip(lat_points, lon_points, dist_arr):
        isOut_lon = (tlon <= lon_range[0]) or (tlon >= lon_range[1])
        isOut_lat = (tlat <= lat_range[0]) or (tlat >= lat_range[1])

        if not isOut_lon and not isOut_lat:
            lat_points_selected.append(tlat)
            lon_points_selected.append(tlon)
            dist_arr_selected.append(tdist)

    return lon_points_selected, lat_points_selected, dist_arr_selected


def get_KP_point(sel_mod, lon_range, lat_range, n_point=100):

    df = pd.read_csv('./data/SHP/IGI002_RPL_OSS1_A_06.csv', ',')

    lat_points = []
    lon_points = []
    dist_arr = []
    dist_arr.append(0)
    dist = 0

    for i, j in zip(df.Latitude, df.Longitude):
        lat_points.append(get_value_deg(i))
        lon_points.append(get_value_deg(j))
    df['Latitude_tot'] = lat_points
    df['Longitude_tot'] = lon_points

    lon_points = add_points_axis(lon_points, n_point)
    lat_points = add_points_axis(lat_points, n_point)

    for i in range(len(lon_points) - 1):
        dist = dist + calc_dist(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1])
        dist_arr.append(dist)

    lon_range, lat_range = get_range(sel_mod, lon_range, lat_range)
    lon_points_selected, lat_points_selected, dist_arr_selected = select_point(lon_points, lat_points, lon_range,
                                                                               lat_range)
    return lon_points_selected, lat_points_selected





#add the KP polyline from file
def add_KP_poly_3D_new(sel_mod, lon_range, lat_range,data_range, coord_value, n_points):

    data = []
    traces = {}

    if sel_mod != 'empty':

        df = pd.read_csv('./IsraelKP.csv', ',')
        df_label = pd.read_csv('./IsraelKP_label.csv', ',')

        with open('./data/config/config' + sel_mod + '.txt', 'r') as f:
            lonmin = float(f.readline().split()[1])
            lonmax = float(f.readline().split()[1])
            latmin = float(f.readline().split()[1])
            latmax = float(f.readline().split()[1])

        if lonmin < lon_range[0]:
            lonmin = lon_range[0]

        if lonmax > lon_range[1]:
            lonmax = lon_range[1]

        if latmin < lat_range[0]:
            latmin = lat_range[0]

        if latmax > lat_range[1]:
            latmax = lat_range[1]

        df_sel=df.loc[df['lat'] >= latmin]
        df_sel=df_sel.loc[df_sel['lat'] <= latmax]
        df_sel=df_sel.loc[df_sel['lon'] >= lonmin]
        df_sel=df_sel.loc[df_sel['lon'] <= lonmax]

        df_sel_label=df_label.loc[df_label['lat'] >= latmin]
        df_sel_label=df_sel_label.loc[df_sel_label['lat'] <= latmax]
        df_sel_label=df_sel_label.loc[df_sel_label['lon'] >= lonmin]
        df_sel_label=df_sel_label.loc[df_sel_label['lon'] <= lonmax]


        lat_points_selected_1 = df_sel['lat']
        lon_points_selected_1 = df_sel['lon']
        dist_arr_selected_1 = df_sel['dist2D']
        depth_selected_1 = df_sel['depth']

        lat_points_selected_label_1 = df_sel_label['lat']
        lon_points_selected_label_1 = df_sel_label['lon']
        depth_selected_label_1 = df_sel_label['depth']
        value_selected_label_1 = df_sel_label['value']

        lat_points_selected, lon_points_selected = set_axis_coord(lat_points_selected_1, lon_points_selected_1, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)
        label_lat_selected, label_lon_selected = set_axis_coord(lat_points_selected_label_1, lon_points_selected_label_1, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)

        traces['KP'] = go.Scatter3d(
            name="",
            x=lat_points_selected,
            y=lon_points_selected,
            z=depth_selected_1,
            customdata=dist_arr_selected_1,
            mode='markers+lines',

            marker=dict(
                size=3,
                color='yellow',
            ),
            line=dict(
                width=8,
                color='yellow'
            ),
            hovertemplate='<b>KP:%{customdata:.3f} km<b><br>Depth:%{z:.3f}'
        )

        traces['KP_' + 'labels'] = go.Scatter3d(
            name="",
            x=label_lat_selected,
            y=label_lon_selected,
            z=depth_selected_label_1,
            customdata=value_selected_label_1,
            mode='markers+text',
            # text=text,
            textfont=dict(size=15, color='white',),
            texttemplate='KP:%{customdata:.0f}',
            hoverinfo='none',
            textposition="top right",
            marker=dict(
                size=8,
                color='darkorange',
            ),
            hovertemplate='<b>KP:%{customdata:.3f}<b><br>Depth:%{z:.3f}',
        )

        data = list(traces.values())

    return data

def add_KP_poly_3D(sel_mod, lon_range, lat_range,data_range, coord_value, n_points):

    data = []
    traces = {}

    if sel_mod != 'empty':

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

        lon_points = add_points_axis(lon_points, n_points)
        lat_points = add_points_axis(lat_points, n_points)


        dist_arr = []
        dist_arr_selected = []
        dist_arr.append(0)
        dist = 0
        #depthAll = get_depth(sel_mod, lon_points, lat_points)


        for i in range(len(lon_points) - 1):
            dist = dist + calc_dist(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1])
            #dist = dist + calc_dist_3D(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1], depthAll[i], depthAll[i+1])
            dist_arr.append(dist)


        with open('./data/config/config' + sel_mod + '.txt', 'r') as f:
            lonmin = float(f.readline().split()[1])
            lonmax = float(f.readline().split()[1])
            latmin = float(f.readline().split()[1])
            latmax = float(f.readline().split()[1])

        labels_value = np.arange(0, int(max(dist_arr)), 5)
        labels_value = np.append(labels_value, np.amax(labels_value) + 5)
        label_lon = []
        label_lat = []
        label_lon_selected = []
        label_lat_selected = []
        labels_value_selected = []

        counter = 0
        if lonmin < lon_range[0]:
            lonmin = lon_range[0]

        if lonmax > lon_range[1]:
            lonmax = lon_range[1]

        if latmin < lat_range[0]:
            latmin = lat_range[0]

        if latmax > lat_range[1]:
            latmax = lat_range[1]

        for tlat, tlon, tdist in zip(lat_points, lon_points, dist_arr):
            if int(tdist) == labels_value[counter]:
                label_lon.append(tlon)
                label_lat.append(tlat)
                counter = counter + 1


        for tlat, tlon, tdist in zip(lat_points, lon_points, dist_arr):
            isOut_lon = (tlon <= lonmin) or (tlon >= lonmax)
            isOut_lat = (tlat <= latmin) or (tlat >= latmax)

            if not isOut_lon and not isOut_lat:
                lat_points_selected.append(tlat)
                lon_points_selected.append(tlon)
                dist_arr_selected.append(tdist)



        for tlat, tlon, tdist in zip(label_lat, label_lon, labels_value):
            isOut_lon = (tlon <= lonmin) or (tlon >= lonmax)
            isOut_lat = (tlat <= latmin) or (tlat >= latmax)

            if not isOut_lon and not isOut_lat:
                label_lat_selected.append(tlat)
                label_lon_selected.append(tlon)
                labels_value_selected.append(tdist)


        depth_increase=1

        depth = get_depth(sel_mod, lon_points_selected, lat_points_selected)
        depth = increase_depth(depth, depth_increase, data_range)
        label_depth = get_depth(sel_mod, label_lon_selected, label_lat_selected)
        label_depth = increase_depth(label_depth, depth_increase, data_range)


        depth=np.asarray(depth)

        lat_points_selected, lon_points_selected = set_axis_coord(lat_points_selected, lon_points_selected, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)
        label_lat_selected, label_lon_selected = set_axis_coord(label_lat_selected, label_lon_selected, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)

        traces['KP'] = go.Scatter3d(
            name="",
            x=lat_points_selected,
            y=lon_points_selected,
            z=depth,
            customdata=dist_arr_selected,
            mode='markers+lines',

            marker=dict(
                size=3,
                color='yellow',
            ),
            line=dict(
                width=8,
                color='yellow'
            ),
            hovertemplate='<b>KP:%{customdata:.3f} km<b><br>Depth:%{z:.3f}'
        )

        traces['KP_' + 'labels'] = go.Scatter3d(
            name="",
            x=label_lat_selected,
            y=label_lon_selected,
            z=label_depth,
            customdata=labels_value_selected,
            mode='markers+text',
            # text=text,
            textfont=dict(size=15, color='white',),
            texttemplate='KP:%{customdata:.0f}',
            hoverinfo='none',
            textposition="top right",
            marker=dict(
                size=8,
                color='darkorange',
            ),
            hovertemplate='<b>KP:%{customdata:.3f}<b><br>Depth:%{z:.3f}',
        )

        data = list(traces.values())

    return data


#set the axis
def adjust_axis(fig,  coord_value, scale_fact, exag_value):

    fig.update_scenes(xaxis_autorange="reversed")

    fig.update_scenes(aspectmode='manual', aspectratio=dict(x= scale_fact, y=1, z=exag_value))
    #fig.update_scenes(yaxis=dict(scaleanchor="x",scaleratio=1,))


    if coord_value==0:
        fig.update_layout(scene=dict(xaxis=dict(title = "Y [m]"), yaxis=dict(title = "X [m]")))
    elif coord_value==2:
        fig.update_layout(scene=dict(xaxis=dict(title="Y [km]"), yaxis=dict(title="X [km]")))

    return True

#get distace from two poin in lat-lon
def get_dist(lon_axis, lat_axis):

    lon_min=min(lon_axis)
    lat_min=min(lat_axis)
    lon_max=max(lon_axis)
    lat_max=max(lat_axis)

    lon_dist=calc_dist(lat_min, lat_min, lon_min, lon_max)
    lat_dist=calc_dist(lat_min, lat_max, lon_min, lon_min)

    return lon_dist, lat_dist

#add annotations on the surface
def update_annotation(fig, sel_mod, lon_range, lat_range, label_value, coord_value):

    ann = import_annotation("./data/POI/Malta_morph_annotations.csv", lon_range, lat_range, label_value)

    lon_ann = ann["lon"].to_list()
    lat_ann = ann["lat"].to_list()
    ann_attr = ann["attr"].to_list()
    ann_color = ann["color"].to_list()

    depth = get_depth(sel_mod, lon_ann, lat_ann)
    lat_ann, lon_ann = set_axis_coord(lat_ann, lon_ann, np.nanmin(lat_range), np.nanmin(lon_range), coord_value)

    annotations=[]

    for i in range(len(ann_attr)):
        annotation= dict(
                    showarrow=False,
                    x=lat_ann[i],
                    y=lon_ann[i],
                    z=depth[i],
                    text=ann_attr[i],
                    font=dict(
                        #color=ann_color[i]
                    ),
                    xanchor="left",
                    xshift=0,
                    yshift=0,
                    opacity=0.8)
        annotations.append(annotation)


    fig=go.Figure(fig)
    fig.update_layout(
        scene=dict(annotations=annotations)),


    return fig

#Get Scale Factor for Compass draw
def get_scale_fact(relayoutData, sel_mod):

    t_lon_range, t_lat_range = get_2D_coord(relayoutData)   #get range from 2D map
    t_lon_range, t_lat_range = get_range(sel_mod, t_lon_range, t_lat_range) #correct the range with the sector range
    lat_range_Sc, lon_range_Sc = set_axis_coord(t_lat_range, t_lon_range, np.nanmin(t_lat_range), np.nanmin(t_lon_range), 2)
    if(lon_range_Sc[1]!=0):
        scale_fact = lat_range_Sc[1] / lon_range_Sc[1]
    else:
        scale_fact = lat_range_Sc[0] / lon_range_Sc[0]

    return scale_fact




#Main function
def draw_3D(sel_mod, relayoutData, POI_label_value, poly_label_value,  table_polyd, ctx, exag_input, max_zoom,
               colorscale = 'deep',  resolution = 100, coord_value=2, txt_color="#e74610", isMobile=False, bg_color="#171717", ):

    #Get Scale Factor for Compass draw
    scale_fact=get_scale_fact(relayoutData, sel_mod)


    zoom = get_2D_zoom(relayoutData)
    lon_range, lat_range = get_2D_coord(relayoutData)

    #Reset the range if changed map or zoomed too close
    if (ctx.triggered[0]['prop_id'].split('.')[0]=='map') or zoom > max_zoom:
        lon_range = []
        lat_range = []

    lon_range, lat_range = get_range(sel_mod, lon_range, lat_range)


    f_config_mod = './data/config/config' + sel_mod + '.txt'
    f_interp_mod = './data/interpol/interpolator' + sel_mod + '.pkl'

    # get interpolated data and lon-lat axis
    data_table, lon_subaxis, lat_subaxis = get_data(f_config_mod, f_interp_mod, lon_range, lat_range, resolution)




    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        z_max = np.nanmax(data_table)
        if not np.isnan(z_max): # Check not empty data table


            fig = go.Figure()


            # Add POI
            if POI_label_value < 100:
                POI_data = add_POI(sel_mod, lon_range, lat_range, POI_label_value, coord_value)
                #fig.add_trace(POI_data)
            #Add KP Line
            if True:
                data_range = (np.nanmax(data_table) - (np.nanmin(data_table)))
                for data_KP in add_KP_poly_3D(sel_mod, lon_range, lat_range, data_range, coord_value, 2000):  # add polylines (for poly selection)
                    fig.add_trace(data_KP)

            #Add 3D Compass
            data_N = draw_arrow("./ArrowN.stl", lon_subaxis, lat_subaxis, data_table, coord_value, scale_fact,'firebrick')
            data_S = draw_arrow("./ArrowS.stl", lon_subaxis, lat_subaxis, data_table, coord_value, scale_fact,'navy')
            data_WE = draw_arrow("./ArrowWE.stl", lon_subaxis, lat_subaxis, data_table, coord_value, scale_fact,'white')
            fig.add_trace(data_N)
            fig.add_trace(data_S)
            fig.add_trace(data_WE)

            #Add Surface
            #data_3D = draw_model_depth_kp(lon_subaxis, lat_subaxis, data_table, colorscale,  coord_value, sel_mod, lon_range, lat_range)
            data_3D = draw_model_depth(lon_subaxis, lat_subaxis, data_table, colorscale,  coord_value)
            fig.add_trace(data_3D)

            axis_template_lat=get_axis_template('lon', bg_color)
            axis_template_lon=get_axis_template('lat', bg_color)
            axis_template_z=get_axis_template('depth', bg_color)
            fig.update_layout(title='',
                              margin=dict(t=0, b=0, l=0, r=0),
                              font=dict(size=12, color='white'),
                              showlegend=False,
                              plot_bgcolor=bg_color, paper_bgcolor=bg_color,
                              scene=dict(xaxis=axis_template_lat, yaxis=axis_template_lon, zaxis=axis_template_z,),
                              hoverlabel=dict(namelength=0),
                              )

            exag_mult=1/exag_input
            adjust_axis(fig,coord_value, scale_fact, exag_mult)



        else:
            axis_template_lat = get_axis_template('lon', bg_color)
            axis_template_lon = get_axis_template('lat', bg_color)
            axis_template_z = get_axis_template('depth', bg_color)
            fig=go.Figure()
            fig.update_layout(title='',
                              margin=dict(t=0, b=0, l=0, r=0),
                              font=dict(size=12, color='white'),
                              showlegend=False,
                              plot_bgcolor=bg_color, paper_bgcolor=bg_color,
                              scene=dict(xaxis=axis_template_lat, yaxis=axis_template_lon, zaxis=axis_template_z, ),
                              hoverlabel=dict(namelength=0),
                              )



    return fig

