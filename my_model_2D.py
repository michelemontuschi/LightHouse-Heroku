import numpy as np
import plotly.graph_objects as go
import pandas as pd
import math
import ast
import random
from my_config import get_map_data, get_colorscale, calc_dist,rotation, get_point_str,get_2D_coord, get_range, \
    get_range_new, get_value_deg
from my_layer import import_polyline, poly_color_converter

from my_POI import import_POI, import_annotation
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle


axis_template = {
    'showbackground': True,
    'backgroundcolor': '#FFFFFF',
    'gridcolor': '#000000',
    'zerolinecolor': '#000000',
}

colorbar_txt ={'title': {'side': 'right', 'text': 'Depth [km]'}, 'xpad':10, 'thickness':10}



'''
Library to draw the selected section on a 2D Map

main function is:
draw_2D( sel_mod, relayoutData, new_draw, fig_old, colorscale, mapbox_access_token, width,
                                 POI_label_value, poly_label_value, zoom, max_zoom, load_polyd, inv_point_polyd, table_polyd)
         
         
         
         sel_mod: selected section name
         relayoutData: data from the graph containing LAT/LON range and zoom level
         new_draw: True if the draw has to be re-do                       
         fig_old: dict containing the figure before the modifications this function apply
         colorscale: chosen colorscale
         mapbox_access_token: mapbox access token
         width: width of the window
         POI label_value: POI to be displayed 
         poly_label_value:polylines to be displayed 
         zoom: actual zoom 
         max_zoom: max zoom
         load_polyd:load drawn polylines
         inv_point_polyd: add invisible point used to draw the polyline 
         table_polyd: table with the selected point of the polyline
         
         
         
'''

#get the zoom level of the map
def zoom_level(lon_dist, lat, px_width):

    c=40075.016
    A=(px_width/lon_dist)*c*math.cos(math.radians(lat))
    zoom=math.log(A, 2)-10.6

    return zoom

#create an empty map
def create_map(sel_mod, colorscale_name):

    col_th, col_ha, col_deep, lat_c,lon_c, zoom_c, c_min_c, c_max_c =get_map_data(sel_mod)

    colorscale = get_colorscale(colorscale_name, 5)

    data=(go.Scattermapbox(
        name="map2D",
        lat=[lat_c],
        lon=[lon_c],
        mode='markers',
        marker=dict(
            size=1,
            showscale=False,
            colorscale=colorscale,
            cmin=c_min_c/1000,
            cmax=c_max_c/1000,
            colorbar=colorbar_txt,
        ),
        hoverinfo='none'

    ))

    return data

#update the map layout (assigning the center, zoom level and colorscale)
def update_2D_map_layout(fig, sel_mod, mapbox_access_token, colorscale_name,lon_range, lat_range, width):

    lon_dist=calc_dist(lat_range[0], lat_range[0], lon_range[0], lon_range[1])
    zoom=zoom_level(lon_dist, lat_range[0], 0.35*width)
    col_th, col_ha, col_deep, lat_c,lon_c, zoom_c, c_min_c, c_max_c=get_map_data(sel_mod)

    if colorscale_name == "thermal":
        colorscale_st = col_th
    elif colorscale_name == "haline":
        colorscale_st = col_ha
    else:
        colorscale_st = col_deep

    fig.update_layout(
        mapbox = dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat_c,
                lon=lon_c,
            ),
            zoom=zoom,
            pitch=0,
            style=colorscale_st,
        ),
    )


    fig.update_layout(title='', margin=dict(t=0, b=0, l=0, r=0), font=dict(size=12, color='white'),
                      showlegend=False,
                      plot_bgcolor='#515151', paper_bgcolor='#515151',
                      scene=dict(xaxis=axis_template, yaxis=axis_template),)

    return fig


def get_center_zoom(sel_mod, lon_range, lat_range, width):


    lon_dist=calc_dist(lat_range[0], lat_range[0], lon_range[0], lon_range[1])
    zoom=zoom_level(lon_dist, lat_range[0], 0.35*width)
    col_th, col_ha, col_deep, lat_c,lon_c, zoom_c, c_min_c, c_max_c=get_map_data(sel_mod)

    return lat_c, lon_c, zoom



#add POI

def add_POI_2D(lon_range, lat_range, label):

    POI =import_POI("./data/POI/Malta_POI.csv", lon_range, lat_range, label)

    lon_POI = POI["lon"].to_list()
    lat_POI = POI["lat"].to_list()
    POI_name = POI["ID"].to_list()
    POI_symbol = POI["symbol"].to_list()
    POI_color = POI["color"].to_list()
    POI_attr = POI["attr"].to_list()
    POI_desc = POI["desc"].to_list()
    POI_text=[]


    for name, attr, desc in zip(POI_name, POI_attr, POI_desc):

        attr_=str(attr)
        desc_=str(desc)
        if attr_ == 'nan':
            attr_=''
        if desc_ == 'nan':
            desc_=''
        POI_text.append(str(name)+'\n\r'+attr_+'\n\r'+desc_)


    data=go.Scattermapbox(
        name="POI_2D",
        lat=lat_POI,
        lon=lon_POI,
        mode='markers',
        marker=dict(size= 8, symbol= POI_symbol),
        text=POI_text,
        hovertemplate=
        '<b>lat</b>: %{lat:.3f}' +
        '<br><b>lon</b>: %{lon:.3f}<br>'+
        '<b>%{text}</b>',
        hoverlabel=dict(bgcolor=POI_color)
    )


    return data


#add point grid for polyline creation
def add_points_2D(lon_range, lat_range):


    lon_axis = np.linspace(lon_range[0], lon_range[1], 50, False)
    lat_axis = np.linspace(lat_range[0], lat_range[1], 50, False)
    grid = np.array(np.meshgrid(lon_axis, lat_axis))
    grid = np.array(grid).T.reshape(-1, 2)

    lonlon = grid[:, 0]
    latlat = grid[:, 1]

    data=(go.Scattermapbox(
        name="",
        lat=latlat,
        lon=lonlon,
        mode='markers',
        marker=dict(
            size=0,
            showscale=False,
            color='black'
        ),
        # hoverinfo='none'
        hovertemplate=
        '<b>lat</b>: %{lat:.3f}' +
        '<br><b>lon</b>: %{lon:.3f}<br>'
    ))

    return data

#add annotations
def add_annotations_2D(lon_range, lat_range, label):

    ann = import_annotation("./data/POI/Malta_morph_annotations.csv", lon_range, lat_range, label)

    lon_ann = ann["lon"].to_list()
    lat_ann = ann["lat"].to_list()
    ann_attr = ann["attr"].to_list()
    ann_color = ann["color"].to_list()


    data=(go.Scattermapbox(
        name="Annotation",
        lat=lat_ann,
        lon=lon_ann,
        mode='text',
        text=ann_attr,
        marker=dict(
            size=0,
            showscale=False,
            color=ann_color
        ),
        hoverinfo='none'
    ))

    return data


# add created polylines

def add_poly_points_2D(sel_mod, table):

    if sel_mod != 'empty':
        table=pd.DataFrame.from_dict(table)
        lon_points=table['lon']
        lat_points=table['lat']

        colorscale = get_colorscale('thermal', len(lon_points))
        col_points=[]
        for col in colorscale:
            col_points.append(col[1])

        data=go.Scattermapbox(
            name="",
            lat=lat_points,
            lon=lon_points,
            mode='markers+lines',
            marker=dict(
                size=12,
                color=col_points,
            ),
            line=dict(
                color='black',
                width=5),
            hovertemplate=
            '<b>lat</b>: %{lat:.3f}' +
            '<br><b>lon</b>: %{lon:.3f}<br>'
        )

    return data

#add polylines from file

def add_poly_2D_from_file(lon_range, lat_range, label):

    traces = {}

    df = import_polyline("./data/SHP/Malta_morph_polyline_lat_lon",lon_range, lat_range, label)

    f_color_conv = np.vectorize(poly_color_converter, otypes=[str])
    colors = f_color_conv(df.Color.values)

    for i in range(len(df.geometry.values)):

        lon_points = []
        lat_points = []

        for points in df.geometry.values[i].coords:
            lon_points.append(points[0])
            lat_points.append(points[1])

        traces['trace_' + str(i)] = go.Scattermapbox(
            name='trace_' + str(i),
            lat=lat_points,
            lon=lon_points,
            mode='lines',
            line=dict(
                color=colors[i],
                width=1),
            hoverinfo='none'
        )
    data = list(traces.values())
    return data

def add_points_axis(axis, n_points):
    axis_new = []
    for i in range(len(axis) - 1):
        for j in range(n_points):
            axis_new.append(axis[i]+j*(axis[i + 1]-axis[i])/n_points)
    axis_new.append(axis[len(axis)-1])
    return axis_new

def add_KP_poly_2D(sel_mod, lon_range, lat_range):
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

        lon_points = add_points_axis(lon_points, 100)
        lat_points = add_points_axis(lat_points, 100)

        dist_arr = []
        dist_arr_selected = []
        dist_arr.append(0)
        dist = 0
        for i in range(len(lon_points) - 1):
            dist = dist + calc_dist(lat_points[i], lat_points[i + 1], lon_points[i], lon_points[i + 1])
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

        if lonmin > lon_range[0]:
            lonmin = lon_range[0]

        if lonmax > lon_range[1]:
            lonmax = lon_range[1]

        if latmin > lat_range[0]:
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

        traces['KP'] = go.Scattermapbox(
            name="",
            lat=lat_points_selected,
            lon=lon_points_selected,
            customdata=dist_arr_selected,
            mode='lines',
            line=dict(
                color='yellow',
                width=1),
            hovertemplate='KP:%{customdata:.3f}'
        )
        text=[]
        for kp in labels_value_selected:
            text.append("KP:{:.3f}".format(kp))
        traces['KP_Annotation'] = (go.Scattermapbox(
            name="Annotation",
            lat=label_lat_selected,
            lon=label_lon_selected,
            customdata=labels_value_selected,
            mode='markers+text',
            #text=text,
            textfont=dict(size=15, color='black'),
            texttemplate='KP:%{customdata:.0f}',
            marker=dict(
                size=10,
                showscale=False,
                color='darkorange'
            ),
            hoverinfo='none',
            textposition = "middle right",
        ))


        data = list(traces.values())
    return data

#draw compass
def draw_compass(rdata, color='#515151'):
    x_eye = -1.25
    y_eye = 1.25
    if rdata!=None:
        if rdata != {'autosize': True} and rdata != {}:
            rdata=rdata['scene.camera']['eye']
            x_eye = -1 * rdata['x']
            y_eye = rdata['y']

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source="./assets/Bussola.png",
            xref="x",
            yref="y",
            x=-10.25,
            y=10,
            sizex=20,
            sizey=20,
            sizing="stretch",
            opacity=1,
            layer="below")
    )

    fig.update_yaxes(
        range=[-10, 10],
        zeroline=False,
    )
    fig.update_xaxes(
        range=[-10, 10],
        zeroline=False,
    )

    alfa = math.atan(y_eye / x_eye)
    if x_eye > 0:
        alfa = alfa + math.pi

    matN = [[-0.5, 0], [0.5, 0], [0, 9]]
    matS = [[-0.5, 0], [0.5, 0], [0, -9]]

    matN = [rotation(matN[0], alfa), rotation(matN[1], alfa), rotation(matN[2], alfa)]
    matS = [rotation(matS[0], alfa), rotation(matS[1], alfa), rotation(matS[2], alfa)]

    arrN = get_point_str(matN)
    arrS = get_point_str(matS)

    fig.update_layout(
        shapes=[
            dict(
                type="path",
                path=arrN,
                fillcolor="firebrick",
                line_color="darkred",
            ),
            dict(
                type="path",
                path=arrS,
                fillcolor="navy",
                line_color="midnightblue",
            ),

        ])

    axis_template_arr = {
        'gridcolor': '#515151',
        'zerolinecolor': '#515151',
        'showticklabels': False,
        'showgrid': False
    }

    fig.update_layout(title='',
                      margin=dict(t=0, b=0, l=0, r=0),
                      font=dict(size=12, color='white'),
                      showlegend=False,
                      plot_bgcolor=color, paper_bgcolor=color,
                      xaxis=axis_template_arr, yaxis=axis_template_arr)

    return fig
#remove unwanted traces
def remove_trace(fig, trace_name):
    i = 0
    for data in fig['data']:
        if trace_name in data['name']:
            fig['data'].pop(i)
        i = i + 1

    return fig

#main function
def draw_2D(sel_mod, relayoutData, new_draw, fig_old,  mapbox_access_token, width,
                                 POI_label_value, poly_label_value, zoom, max_zoom, load_polyd, inv_point_polyd, table_polyd, colorscale ='haline' ):

    if new_draw:
        lon_range, lat_range = get_range_new(sel_mod)
        fig=go.Figure()
        fig=update_2D_map_layout(fig, sel_mod, mapbox_access_token, colorscale, lon_range, lat_range,width)  # define background map

    else:
        lon_range, lat_range = get_2D_coord(relayoutData)
        lon_range, lat_range = get_range(sel_mod, lon_range, lat_range)

        fig_old = remove_trace(fig_old, 'POI_2D')
        fig_old = remove_trace(fig_old, 'Annotation')
        fig_old = remove_trace(fig_old, 'trace_')
        fig = go.Figure(fig_old)
        if load_polyd > 0:
            fig.add_trace(add_poly_points_2D(sel_mod, table_polyd))


    if POI_label_value < 100:
        fig.add_trace(add_POI_2D(lon_range, lat_range, POI_label_value))  # add POI

    if inv_point_polyd:
        fig.add_trace(add_points_2D(lon_range, lat_range))  # add invisible points (for poly selection)

    if poly_label_value < 500:
        for data in add_poly_2D_from_file(lon_range, lat_range,poly_label_value):  # add invisible polylines (for poly selection)
            fig.add_trace(data)
    for data in add_KP_poly_2D(sel_mod, lon_range, lat_range):  # add invisible polylines (for poly selection)
        fig.add_trace(data)

    return fig