import numpy as np
import plotly.graph_objects as go

font_size_big_str = "20px"
font_size_small_str = "15px"
font_size_big = 20
font_size_small = 15

'''
Library to draw the world map using mapbox layer
lat_list, lon_list, text_list are arrays with the same dimensions with, respectively, latitude, longitude and 
name of each sections to be shown
'''

def draw_map(mapbox_access_token, lat_list, lon_list, text_list, txt_color="#e74610"):

    fig = go.Figure(go.Scattermapbox(
        name='',
        lat=lat_list,
        lon=lon_list,
        mode='markers',
        marker=go.scattermapbox.Marker(
            color=txt_color,
            size=9
        ),

        text=text_list,
        hovertemplate=
        '<b>lat</b>: %{lat:.3f}' +
        '<br><b>lon</b>: %{lon:.3f}<br>' +
        '<b>%{text}</b>',

    ))



    fig.update_layout(
        title='',
        autosize=True,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=np.asarray(lat_list).mean(),
                lon=np.asarray(lon_list).mean()),
            pitch=0,
            # With Malta and Israele
            # style='mapbox://styles/michelemontuschi/ckk5bn88a66yr17jsk3m1ipi6',
            style='mapbox://styles/michelemontuschi/cko141z420icq17o1m71is2vz',

            zoom=3.2),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    fig.update_layout(
        #mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "vector",
                "sourcelayer":"michelemontuschi.0u5hn1fq"
            }
        ])
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


    return fig










