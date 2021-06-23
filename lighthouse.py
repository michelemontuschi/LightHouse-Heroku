import json
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as tb
import dash_daq as daq
import dash_auth
import pandas as pd
import numpy as np
import ast

from my_model_3D import draw_3D
from my_model_2D import draw_compass, draw_2D
from my_config import get_2D_zoom, colorscale_trad
from my_legend import  get_legend_polyline, get_legend_POI
from my_map import draw_map
from my_POI import  modal_display
from dash.dependencies import ClientsideFunction, Input, Output,State
from stl_3d import get_stl
from flask import request
import math

import plotly.graph_objects as go

txt_color="#e74610"

#Constants and dicts

df = pd.read_csv('./data/auth/auth.csv')
VALID_USERNAME_PASSWORD_PAIRS = {}
for row in df.iterrows():
    VALID_USERNAME_PASSWORD_PAIRS[row[1]['User']] = row[1]['PWD']

mapbox_access_token = 'pk.eyJ1IjoibWljaGVsZW1vbnR1c2NoaSIsImEiOiJja2dtYzhidDgwanFtMnlvMTU0Zjdra2NsIn0.c9Sa8lhNyhy2_5MBaz52ug'


max_zoom = 20

click_store = 0
sel_mod = 'empty'
version='v 3.2.0'

#external scripts and stylesheets for the 3d mapbox integration using JavaScript
external_scripts = [{'src': 'https://api.mapbox.com/mapbox-gl-js/v2.0.1/mapbox-gl.js'}]
external_stylesheets = [
    {'href': 'https://api.mapbox.com/mapbox-gl-js/v2.0.1/mapbox-gl.css',
     'rel': 'stylesheet',
    }
]


axis_template = {
    'showbackground': True,
    'gridcolor': 'rgb(255, 255, 255)',
    'zerolinecolor': 'rgb(255, 255, 255)',
}
axis_template_lon = {
    'showbackground': True,
    'backgroundcolor': '#515151',
    'gridcolor': 'rgb(255, 255, 255)',
    'zerolinecolor': 'rgb(255, 255, 255)',
    'title': 'Lon',
}
axis_template_lat = {
    'showbackground': True,
    'backgroundcolor': '#515151',
    'gridcolor': 'rgb(255, 255, 255)',
    'zerolinecolor': 'rgb(255, 255, 255)',
    'title': 'Lat',
}

axis_template_z = {
    'showbackground': True,
    'backgroundcolor': '#515151',
    'gridcolor': 'rgb(255, 255, 255)',
    'zerolinecolor': 'rgb(255, 255, 255)',
    'title': 'Depth[m]'

}

init_plot_layout = {
    'title': '',
    'margin': {'t': 0, 'b': 0, 'l': 0, 'r': 0},
    'font': {'size': 12, 'color': 'white'},
    'showlegend': False,
    'plot_bgcolor': '#141414',
    'paper_bgcolor': '#141414',
    'scene': {
        'xaxis': axis_template_lon,
        'yaxis': axis_template_lat,
        'zaxis': axis_template_z,

    },
}
config3d = {'editable': False, 'scrollZoom': True, 'displayModeBar': False, 'displaylogo': False}
config2d = {'editable': False, 'scrollZoom': True, 'displayModeBar': False, 'displaylogo': False}



app = dash.Dash(
    __name__,
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'},
        {'name': 'theme-color', 'content': '#000000'},
        {'name': 'mobile-web-app-capable', 'content': 'yes'},
        ],
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets

)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
server = app.server

app.title = 'Lighthouse 3D Visualization'

app.layout = html.Div([

    html.Div(id='container', children=[
        # left column
        html.Div(id='left-column', children=[
            html.Div(id='header', children=[
                html.Img(src=app.get_asset_url('logo.svg'), style={'width': '80%'}),
                html.H4('Lighthouse 3D Visualization', className='header', ),
                html.H4(version, className='header pb-20', ),
            ]),
            # world map
            html.Div(id='world-map', children=[
                html.Span('Map', className='subheader'),
                dcc.Graph(id='map',
                          config={'editable': False, 'scrollZoom': True, 'displayModeBar': False, 'displaylogo': False},
                          style={'height': '25vw', 'width': '25vw', 'marginBttom': '10px'}
                          ),
                html.Br(),

            ],className='pb-20', ),
            # 2D map
            html.Div(id="map-2D", children=[
                html.Div(id='map-2D-div', children=[
                    html.Span(id='model_selected', className='subheader', children=['No model selected.']),
                    dcc.Graph(id='map-2D-fig',
                              config=config2d, style={'height': '25vw', 'width': '25vw', 'marginBttom': '10px'}),
                ]),
                html.Br(className='header pb20'),
                html.Div(id='arrow-div', children=[
                    dcc.Graph(id='map-2D-arrow',
                              figure={
                                  'data': [],
                                  'layout': {'zerolinecolor': '#515151', }},
                              config={'editable': False, 'scrollZoom': False, 'displayModeBar': False, 'displaylogo': False,
                                      'responsive': False, 'staticPlot':True},
                              style={'height': '15vw', 'width': '15vw', 'marginBttom': '10px', 'align-items': 'center', "vertical-align": "top"}
                              ),
                    html.Div(id='zoom-button-div', children=[
                        html.Div(children=[
                            html.Button('Zoom Out', id='zoom-button', className='button'),
                        ], style={"width": "5%", "display": "inline-block", "vertical-align": "top","horizontal-align": "center"}, ),
                    ], style={"display": "None"}),

                ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            ], style={'display': 'None'}),
            # Controls
            html.Div(id='map-controls', children=[
                html.Div(id='graph-controls', children=[
                    html.Div(id='colorscale-div', children=[
                        html.P(children='Colorscale', style={'display': 'inline-block'}, className='subheader'),
                        dcc.RadioItems(id="colorscale-radio",
                                       options=[
                                           {'label': 'Deep', 'value': 0},
                                           {'label': 'Thermal', 'value': 1},
                                           {'label': 'Haline', 'value': 2},
                                           {'label': 'Terrain', 'value': 3},
                                           {'label': 'Rainbow', 'value': 4},
                                           {'label': 'Spring', 'value': 5},
                                           {'label': 'Autumn', 'value': 6},
                                       ],
                                       value=2,

                                       className='legend'
                                       ),
                    ],style={"width": "50%", "height": "100%", "display": "inline-block","vertical-align": "top"}),
                    html.Div(id ='sliders-div', children=[
                        html.P(children='Light Controls', style={'display': 'inline-block'}, className='subheader'),
                        html.Div(id='ambient-div', children=[
                            html.P(children='Light Intensity:', className='legend'),
                            dcc.Slider(id="ambient-sl",
                                       min=0, max=1, step=0.1, value=0.4,
                                       marks={
                                           0: {'label': '0', 'style': {'color': txt_color}},
                                           0.2: {'label': '2', 'style': {'color': txt_color}},
                                           0.4: {'label': '4', 'style': {'color': txt_color}},
                                           0.6: {'label': '6', 'style': {'color': txt_color}},
                                           0.8: {'label': '8', 'style': {'color': txt_color}},
                                           1: {'label': '10', 'style': {'color': txt_color}}, }, className='legend'
                                       ),
                        ]),
                        #html.P(id='slider-position-div', children='Light Position:'),
                        html.Div(id='front-light-div', children=[
                            html.P(children='Front light:', className='legend'),
                            dcc.Slider(id="light-x-input-sl",
                                       min=-100000, max=100000, step=10, value=-75000,
                                       marks={
                                           -100000: {'label': '-1', 'style': {'color': txt_color}},
                                           -50000: {'label': '-0.5', 'style': {'color': txt_color}},
                                           0: {'label': '0', 'style': {'color': txt_color}},
                                           50000: {'label': '0.5', 'style': {'color': txt_color}},
                                           100000: {'label': '1', 'style': {'color': txt_color}}, }, className='legend'
                                       ),
                        ]),

                        html.Div(id='side-light-div', children=[
                            html.P(children='Side light:', className='legend'),
                            dcc.Slider(id="light-y-input-sl",
                                       min=-100000, max=100000, step=100, value=75000,
                                       marks={
                                           -100000: {'label': '-1', 'style': {'color': txt_color}},
                                           -50000: {'label': '-0.5', 'style': {'color': txt_color}},
                                           0: {'label': '0', 'style': {'color': txt_color}},
                                           50000: {'label': '0.5', 'style': {'color': txt_color}},
                                           100000: {'label': '1', 'style': {'color': txt_color}}, }, className='legend'
                                       ),
                        ]),
                        html.Div(id='zoom-div', children=[
                            html.P(children='Zoom:'),
                            dcc.Slider(id="zoom-input-sl",
                                       min=0.1, max=2, step=0.01, value=1,
                                       marks={
                                           0: {'label': '0', 'style': {'color': txt_color}},
                                           0.5: {'label': '0.5', 'style': {'color': txt_color}},
                                           1: {'label': '1', 'style': {'color': txt_color}},
                                           1.5: {'label': '1.5', 'style': {'color': txt_color}},
                                           2: {'label': '2', 'style': {'color': txt_color}}, },
                                       ),
                        ],style={"display": "None"}),
                        html.Br(),
                        html.Button('Load', id='load-params-button',style={'float':'right'})
                    ], style={"width": "50%", "height": "100%", "display": "inline-block","vertical-align": "top"})
                    ,]),
                # Coordinates
                html.Br(),
                html.Div(id='reference-div', children=[
                    html.Div(id='coordinates-div', children=[
                        html.P(children='Coordinates', style={'display': 'inline-block'}, className='subheader'),
                        dcc.RadioItems(id="coordinates-radio",
                                       options=[
                                           {'label': 'UTM', 'value': 0},
                                           {'label': 'Geographic', 'value': 1},
                                           {'label': 'Relative', 'value': 2},
                                       ],
                                       value=2,
                                       className='legend'
                                       ),
                    ], style={"width": "50%", "height": "100%", "display": "inline-block","vertical-align": "top"}),
                    html.Div(id='exagg-div', children=[
                        html.P(children='Vertical Exaggeration:', className='subheader'),
                        dcc.Slider(id="exag-sl",
                                   min=1, max=5, step=0.1, value=1,
                                   marks={
                                       5: {'label': '0', 'style': {'color': txt_color}},
                                       4: {'label': '', 'style': {'color': txt_color}},
                                       3: {'label': '5', 'style': {'color': txt_color}},
                                       2: {'label': '', 'style': {'color': txt_color}},
                                       1: {'label': '10', 'style': {'color': txt_color}},},
                                   className='legend'
                                   ),
                        html.Br(),
                        html.Button('Load', id='load-params-button-2',style={'float':'right'})
                    ], style={"width": "50%", "height": "100%", "display": "inline-block","vertical-align": "top"}),
                ]),



                # Point Of Interest
                html.P("", style={'font-size': '15px'}),
                html.Div(id='POI-div', children=[
                    html.P(children='Point Of Interest', style={'display': 'inline-block', }, className='subheader'),
                    html.Div(id='ann-POI-div', children=[
                        html.Div(id='ann-POI-list', children=[
                            dcc.RadioItems(id="ann-POI-label-radio",
                                           options=[
                                               {'label': 'All', 'value': '-9999'},
                                               {'label': 'Sonar contact', 'value': '1'},
                                               {'label': 'SBP sonar contact', 'value': '2'},
                                               {'label': 'Magnetic Anomaly', 'value': '3'},
                                               {'label': 'CPT Location', 'value': '4'},
                                               {'label': 'Gravity core Location', 'value': '5'},
                                               #{'label': 'Text', 'value': '6'},
                                               {'label': 'None', 'value': '9999'},
                                           ], value='9999',
                                   className='legend')],
                                 style={"width": "85%", "height": "100%", "display": "inline-block","vertical-align": "top"}),
                        html.Div(id='leg_POI_div', children=[
                            dcc.Graph(
                                id='leg_POI',
                                config=config2d,
                            )
                        ], style={"width": "15%", "height": "100%", "display": "inline-block", "vertical-align": "top"})]
                             ),
                ], ),
                # Polylines
                html.Div(id='polylines-div', children=[
                    html.P(children='Polylines', style={'display': 'inline-block'}, className='subheader'),
                    html.Div(id='poly-div', children=[
                        html.Div(id='poly-list', children=[
                            dcc.RadioItems(id="poly-label-radio",
                                           options=[
                                               {'label': 'All', 'value': '-9999'},
                                               # {'label': 'Seabed depression', 'value': '3'},
                                               {'label': 'Found cable', 'value': '4'},
                                               # {'label': 'Pockmark', 'value': '6'},
                                               {'label': 'Linear target', 'value': '10'},
                                               # {'label': 'MR limit', 'value': '42'},
                                               # {'label': 'Fine Sediment limit', 'value': '51'},
                                               # {'label': 'Biogenic concrection area', 'value': '61'},
                                               # {'label': 'Slumping area', 'value': '211'},
                                               {'label': 'Anchor trawling scars', 'value': '252'},
                                               {'label': 'KP', 'value': '1000'},
                                               {'label': 'None', 'value': '9999'},
                                           ], value='9999')],
                                 style={"width": "70%", "height": "100%", "display": "inline-block",
                                        "vertical-align": "top"}),
                        html.Div(id='leg_polyline_div', children=[
                            dcc.Graph(
                                id='leg_polyline',
                                config=config2d,
                            )],
                                 style={"width": "20%", "height": "100%", "display": "inline-block",
                                        "vertical-align": "top"})
                    ]),
                ], style={'display': 'None'}),#Display Polylines radio button

                # Create Polylines
                html.Div(id='new-poly-div', children=[
                    html.Div(id='new-poly-button', children=[
                        daq.BooleanSwitch(
                            id="poly-radio-sw",
                            label=['', 'Do you want to create polylines?'],
                            color=txt_color,
                            on=False
                        )], style={'display': 'flex', 'align-items': 'left', 'justify-content': 'left'}),

                    html.P(id="poly-out", children='', style={'display': 'inline-block', 'fontSize': '15px'}),

                    html.Div(id="poly-table-div", children=[
                        html.Button('Load Points', id='load_points', n_clicks=0),
                        tb.DataTable(id='table-poly',
                                     columns=([{'id': 'Id', 'name': 'Id'}] + [{'id': p, 'name': p} for p in
                                                                              ['lon', 'lat']]),
                                     editable=False,
                                     style_header={'backgroundColor': '#1D1D1D', 'textAlign': 'center', 'fontSize': 12,
                                                   'font-family': 'sans-serif'},
                                     style_cell={'backgroundColor': '#1D1D1D', 'Align': 'center', 'color': 'white',
                                                 'fontSize': 12, 'font-family': 'sans-serif'},
                                     style_table={
                                         'maxHeight': '50ex',
                                         'width': '90%',
                                         'minWidth': '10%', },
                                     ),

                    ]),
                ], style={'display': 'None'}),#Display Create Polyline section

                # Restart Button


                html.A(html.Button('Restart'), href='/'),
            ]),
        ], className='one-third30 column app__left__section', ),

        # Right Column
        html.Div(id='right-column', children=[
            html.Div(id='3D-model-div',children=[
                dcc.Loading(id='loading-1', color=txt_color, children=[
                    html.Div(id='3D-model-light-canvas', children=[
                        dcc.Graph(
                            id='3D-model-light',
                            figure={
                                'data': [],
                            }, config=config3d, style={"height": "90vh", "display": "Block"})]),
                    html.Br(className='legend'),
                ]),
            ]),
        ], className='two-thirds70 column app__right__section',),

        # Modal
        html.Div([
            dbc.Modal(
                [
                    dbc.ModalHeader(id="modal-2D_header", children="This is the header of the modal"),
                    dbc.ModalBody(id="modal-2D_body", children="This is the content of the modal",
                                  style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                         'justify-content': 'center'}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-2D", className="ml-auto")
                    ),
                ],
                id="modal-2D",
                size="xl",
                centered=True,
            ),
        ]),

        html.Div([
            dbc.Modal(
                [
                    dbc.ModalHeader(id="modal-3D_header", children="This is the header of the modal"),
                    dbc.ModalBody(id="modal-3D_body", children="This is the content of the modal",
                                  style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                         'justify-content': 'center'}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-3D", className="ml-auto")
                    ),
                ],
                id="modal-3D",
                size="xl",
                centered=True,
            ),
        ]),

        # Hidden Div
        html.Div([
            html.P(id="place_holder"),
            html.Button('press to show username', id='button_user'),
            html.P(id='left-section-color', children='#515151'),
            html.P(id='right-section-color', children='#515151'),
            html.P(id='3D-section-color', children='#515151'),
            html.P(id="isMobile"),
            html.P(id="isPortrait"),
            html.P(id="opSyst"),
            html.P(id="wind_width"),
            dcc.Location(id="url"),
            dcc.Graph(id='3D-model-nolight', figure={'data': [], 'layout': init_plot_layout, },config=config3d),
            html.Div(id='colorscale-sel', children=[
                dcc.RadioItems(id="colorscale-radio-selected",
                               options=[
                                   {'label': 'Deep', 'value': 0},
                                   {'label': 'Thermal', 'value': 1},
                                   {'label': 'Haline', 'value': 2},
                                   {'label': 'Terrain', 'value': 3},
                                   {'label': 'Rainbow', 'value': 4},
                                   {'label': 'Spring', 'value': 5},
                                   {'label': 'Autumn', 'value': 6},],
                               value=2,
                               labelStyle={'display': 'inline-block'}
                               ),
            ]),
            html.Div(id='coordinates-sel', children=[
                dcc.RadioItems(id="coordinates-radio-selected",
                               options=[
                                   {'label': 'UTM', 'value': 0},
                                   {'label': 'Geographic', 'value': 1},
                                   {'label': 'Relative', 'value': 2},],
                               value=0,
                               ),
            ]),
            html.Div(children=[
                dcc.RadioItems(id="poly-label-radio-selected",
                               options=[
                                   {'label': 'All', 'value': '-9999'},
                                   {'label': 'Seabed depression', 'value': '1'},
                                   {'label': 'Found cable', 'value': '2'},
                                   {'label': 'Pockmark', 'value': '3'},
                                   {'label': 'Linear Target', 'value': '4'},
                                   {'label': 'MR Limit', 'value': '5'},
                                   {'label': 'FS Limit', 'value': '6'},
                                   {'label': 'Biogenic concrection area', 'value': '7'},
                                   {'label': ' Slumping Area', 'value': '8'},
                                   {'label': 'Anchor Trawling Scars', 'value': '9'},
                                   {'label': 'None', 'value': '9999'},
                               ], value='9999')]),
        ], style={'display': 'none'}, className='container')
    ]),
    html.Div(id='turn', children=[
        html.Div(id='left-column-p', children=[
            html.Div(id='header-p', children=[
                html.Img(src=app.get_asset_url('logo.svg'), style={'width': '80%'}),
                html.H4('Lighthouse 3D Visualization', className='header', ),
                html.H4(version, className='header pb-20', ),
                html.P(children='Please rotate the device', className='header', )
            ]),
        ], className='app__left__section__mobile mobile__left_bg__color' ),

    ])


])



# JavaScript callbacks
# callback to retrieve the windows width
app.clientside_callback(
    '''
    function(href){
        return window.innerWidth;
    }
    ''',
    Output("wind_width", "children"), [Input("url", "href")])

app.clientside_callback(
    '''
        function(href){
        var OSName="Unknown OS";
        if (window.navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
        if (window.navigator.appVersion.indexOf("Mac")!=-1) OSName="MacOS";
        if (window.navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
        if (window.navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";
                return OSName;
    }
    ''',
    Output("opSyst", "children"), [Input("url", "href")])

app.clientside_callback(
    '''
        function(href){
        var isMobile=false;
       
        if ((typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1)) isMobile=true;
                return isMobile;
                
    }
    ''',
    Output("isMobile", "children"), [Input("url", "href")])



app.clientside_callback(
    '''
        function(href){
        var orientation = (screen.orientation || {}).type || screen.mozOrientation || screen.msOrientation;
        return orientation;
    }
    ''',
    Output("isPortrait", "children"), [Input("url", "href")])





app.clientside_callback(
    '''
        function(href){
        var isMobile=false;
        lockAllowed="Niente"
        if (typeof window.orientation !== "portrait") lockAllowed = window.screen.orientation.lock("landscape");
        return 0
        
    }
    ''',
    Output("place_holder", "children"), [Input("url", "href")])



# Python-Dash callback

@app.callback([Output('zoom-button-div', 'style'),
               Output('map', 'style'),
               Output('map-2D-fig', 'style'),
               Output('left-column', 'className'),
               Output('right-column', 'className'),
               Output('left-section-color', 'children'),
               Output('right-section-color', 'children'),
               Output('3D-section-color', 'children')
               ],
              [Input('isMobile', 'children'),
               Input('isPortrait', 'children')])
def style_on_mobile(isMobile, isPortrait):
    classNameLC='one-third column app__left__section'
    classNameRC='two-thirds column app__right__section'
    style_butt={"display":"None"}
    style_maps = {"display":"Block",'height': '22vw', 'width': '22vw', 'marginBttom': '10px'}

    rSecColor="#515151"
    lSecColor="#515151"
    d3Color="#515151"

    if isMobile:
        style_butt= {"display": "block", "vertical-align": "center"}
        style_maps = {'height': '25vw', 'width': '25vw', 'marginBttom': '10px'}
        classNameLC = 'one-third30 column app__left__section mobile__left_bg__color'
        classNameRC = 'two-thirds70 column app__right__section'
        rSecColor = "#515151"
        lSecColor = "#858585"
        d3Color = "#171717"


    return style_butt, style_maps, style_maps, classNameLC, classNameRC, lSecColor, rSecColor, d3Color

# left-column: callback to show the world map with Auth integration
@app.callback(Output('map', 'figure'), [Input('button_user', 'n_clicks')])
def update_world_map(nclicks):
    username = request.authorization['username']
    secur_auth = -1

    sec_table = pd.read_csv('./data/auth/sec_table.csv')
    text_list_hidden = sec_table['Name'].values
    lon_list_hidden = np.array(sec_table['Lon'].values)
    lat_list_hidden = np.array(sec_table['Lat'].values)

    auth_table = pd.read_csv('./data/auth/auth.csv', index_col=0)
    init = int(auth_table.iloc[df[df['User'] == username].index.values]['init'].values[0])
    end = int(auth_table.iloc[df[df['User'] == username].index.values]['end'].values[0])


    lat_list = lat_list_hidden[init:end+1]
    lon_list = lon_list_hidden[init:end+1]
    text_list = text_list_hidden[init:end+1]



    return draw_map(mapbox_access_token, lat_list, lon_list, text_list, txt_color)



#left-column: load the 2d map
@app.callback([Output('model_selected', 'children'),
               Output('map-2D-fig', 'figure'),
               Output('map-2D', 'style'),
               Output('poly-label-radio-selected', 'value')],
              [Input('map', 'clickData'),
               Input('load_points', 'n_clicks'),
               Input('poly-radio-sw', 'on'),
               Input('ann-POI-label-radio', 'value'),
               Input('poly-label-radio', 'value'),
               Input('map-2D-fig', 'relayoutData'),
               ],
              [
               State('model_selected', 'children'),
               State('map-2D-fig', 'figure'),
               State('poly-label-radio-selected', 'value'),
               State('table-poly', 'data'),
               State('wind_width', 'children'), ])
def load_map(click_data,   load_polyd, inv_point_polyd, POI_label_value, poly_label_value, \
             relayoutData, mod_selected, fig_old,   poly_label_sel, table_polyd, width):

    poly_label_value = int(poly_label_value)
    display_str = 'No model selected.'
    fig = go.Figure()
    fig.update_layout(title='', margin=dict(t=0, b=0, l=0, r=0), font=dict(size=12, color='white'),
                      showlegend=False,
                      plot_bgcolor='#515151', paper_bgcolor='#515151',
                      scene=dict(xaxis=axis_template, yaxis=axis_template), )
    display_2D = {'display': 'None'}
    POI_label_value = int(POI_label_value)
    poly_label_sel = int(poly_label_sel)

    if click_data:
        sel_mod = click_data['points'][0]['text']
        zoom = get_2D_zoom(relayoutData)
        ctx = dash.callback_context
        cond1 = (sel_mod != mod_selected)
        cond4 = (poly_label_value != poly_label_sel)
        cond5 = ctx.triggered[0]['prop_id'].split('.')[0] == 'map.clickData'

        new_draw = cond1  or cond4 or cond5


        fig = draw_2D(sel_mod, relayoutData, new_draw, fig_old,  mapbox_access_token, width,
                                 POI_label_value, poly_label_value, zoom, max_zoom, load_polyd, inv_point_polyd, table_polyd)

        display_2D = {'display': 'Block'}
        display_str = sel_mod


    return display_str, fig, display_2D, poly_label_value

#left-column: draw the compass
@app.callback(Output('map-2D-arrow', 'figure'),
              [Input('3D-model-light', 'relayoutData'),
               Input('map', 'clickData'),
               Input('left-section-color', 'children')])
def load_compass(rdata, sel_mod,lColor):
    fig = go.Figure()
    fig.update(layout=init_plot_layout)
    if sel_mod:
        fig = draw_compass(rdata,lColor)
    return fig

#left-column: draw the legends
@app.callback([Output('leg_polyline', 'figure'),
               Output('leg_POI', 'figure')],
              [Input('map', 'clickData'),Input('wind_width', 'children'),Input('left-section-color', 'children')])
def render_legend_content(clickData, width, color):

    fig_pl = get_legend_polyline(width, color)
    fig_POI = get_legend_POI(width, color)
    return fig_pl, fig_POI


#left-column: show the table with the selected points of the drawn polyline
@app.callback([Output('poly-out', 'children'),
               Output('poly-table-div', 'style'),
               Output('table-poly', 'data'), ],
              [Input('map-2D-fig', 'clickData'),
               Input('poly-radio-sw', 'on')],
              [State('table-poly', 'data')])
def display_poly_table(click_data, poly_value, data):
    txt = ""
    style_tab = {'display': 'None'}

    if click_data:
        if poly_value:
            txt = "lon: " + str(click_data['points'][0]['lon']) + " lat: " + str(click_data['points'][0]['lon'])

            d = {'Id': [1],
                 'lon': [click_data['points'][0]['lon']],
                 'lat': [click_data['points'][0]['lat']]}
            style_tab = {'display': 'Block'}
            if data == None:
                df = pd.DataFrame(d, columns=['Id', 'lon', 'lat'])
            else:

                df = pd.DataFrame(data, columns=['Id', 'lon', 'lat'])

                id = int(df.tail(1)['Id'].values[0])

                d = {'Id': [id + 1],
                     'lon': [click_data['points'][0]['lon']],
                     'lat': [click_data['points'][0]['lat']]}

                df_app = pd.DataFrame(d, columns=['Id', 'lon', 'lat'])
                df = pd.concat([df, df_app])

            data = df.to_dict('records')

    return txt, style_tab, data




#right-column: Load the 3d model

@app.callback([Output('3D-model-nolight', 'figure'),
               Output('3D-model-div', 'style')],
              [Input('colorscale-radio', 'value'),
               Input('map-2D-fig', 'relayoutData'),
               Input('map', 'clickData'),
               Input('load_points', 'n_clicks'),
               Input('ann-POI-label-radio', 'value'),
               Input('poly-label-radio', 'value'),
               Input('coordinates-radio', 'value'),
               Input('load-params-button', 'n_clicks'),
               Input('load-params-button-2', 'n_clicks'),
               Input('zoom-button', 'n_clicks')
               ],
              [State('table-poly', 'data'),
               State('exag-sl', 'value'),
               State('3D-model-light', 'relayoutData'),
               State('isMobile', 'children'),
               State('3D-section-color', 'children')
              ])
def load_3D(icolorscale, relayoutData, click_data, load_n_click,label_value, poly_label_value, coord_value,nclicks_load,nclicks_load2,nclicks_zoom,
            table_points,exag_value, rdata_3D_light, isMobile, d3Color):

    colorscale = colorscale_trad(icolorscale)
    label_value = int(label_value)
    poly_label_value = int(poly_label_value)
    display_graph = {'display': 'None'}
    fig = go.Figure()
    resolution = 100



    marks = {
        0: {'label': '0', 'style': {'color': txt_color}},
        100: {'label': '100', 'style': {'color': txt_color}},
        200: {'label': '200', 'style': {'color': txt_color}},
        300: {'label': '300', 'style': {'color': txt_color}},
        400: {'label': '400', 'style': {'color': txt_color}},
        500: {'label': '500', 'style': {'color': txt_color}},
    }

    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id']=="map.clickData":
        relayoutData=dict(autosize=True)
        rdata_3D_light={'scene.camera': {'eye': {'x': 1.25, 'y': 1.25, 'z': 1.25}}}

    if ctx.triggered[0]['prop_id']=="zoom-button.n_clicks":
        x_eye= rdata_3D_light['scene.camera']['eye']['x']
        y_eye = rdata_3D_light['scene.camera']['eye']['y']
        z_eye = rdata_3D_light['scene.camera']['eye']['z']

        d1 = math.sqrt(x_eye * x_eye + y_eye * y_eye + z_eye * z_eye)
        d2 = math.sqrt(1.25 * 1.25 + 1.25 * 1.25 + 1.25 * 1.25)
        fact=d2/d1

        x_eye=fact*x_eye
        y_eye=fact*y_eye
        z_eye=fact*z_eye
        rdata_3D_light={'scene.camera': {'eye': {'x': x_eye, 'y': y_eye, 'z': z_eye}}}

    if click_data:
        sel_mod = click_data['points'][0]['text']
        if sel_mod != 'empty':
            fig = draw_3D(sel_mod, relayoutData, label_value, poly_label_value, table_points, ctx,
                                            exag_value, max_zoom, colorscale, resolution, coord_value, txt_color, isMobile, d3Color)
            display_graph ={ "display": "Block"}
    else:
        fig.update(layout=init_plot_layout)


    if rdata_3D_light != None:
        if 'scene.camera' in rdata_3D_light.keys():
            rdata_3D_light['scene.camera']['eye']['x']=rdata_3D_light['scene.camera']['eye']['x']
            rdata_3D_light['scene.camera']['eye']['y']=rdata_3D_light['scene.camera']['eye']['y']
            rdata_3D_light['scene.camera']['eye']['z']=rdata_3D_light['scene.camera']['eye']['z']
            fig.update_layout(scene=dict(camera=dict(eye=rdata_3D_light['scene.camera']['eye'])))




    return fig, display_graph




#right-column: call back for lighting
@app.callback(Output('3D-model-light', 'figure'),
              [Input('load-params-button', 'n_clicks'),
               Input('load-params-button-2', 'n_clicks'),
               Input('3D-model-nolight', 'figure'),
               ],
              [State('ambient-sl', 'value'),
               State('light-x-input-sl', 'value'),
               State('light-y-input-sl', 'value'),
               State('3D-model-light', 'relayoutData'),
               ])
def lighting_camera(load_params,load_params2, graph_nolight, amb, x_l, y_l, rdata):

    fig = go.Figure(graph_nolight)

    lighting_effects = dict(ambient=amb)
    lightposition = dict(x=x_l, y=y_l)

    fig.update_traces(lighting=lighting_effects, selector=dict(type='surface'))
    fig.update_traces(lightposition=lightposition, selector=dict(type='surface'))




    return fig



#Open the modal when a POI is selected on 2d map
@app.callback([Output("modal-2D", "is_open"),
               Output("modal-2D_body", "children"),
               Output("modal-2D_header", "children")],
              [Input('map-2D-fig', 'clickData'),
               Input("close-2D", "n_clicks"), ],
              [State("modal-2D", "is_open"),
               State('map', 'clickData'),
               State('poly-radio-sw', 'on')])
def display_modal_2D(click_data_2D, n2, is_open, map_data, poly_value):
    # div = html.Video(src='/static/8_POI_9.mp4', controls=True, style={"width": "80%"})
    txt = ""
    if map_data and not poly_value:
        if click_data_2D or n2:
            return modal_display(click_data_2D, is_open)

    return is_open, txt, txt

#Open the modal when a POI is selected on 3d
@app.callback([Output("modal-3D", "is_open"),
               Output("modal-3D_body", "children"),
               Output("modal-3D_header", "children")],
              [Input("3D-model-light", 'clickData'),
               Input("close-3D", "n_clicks"),
               ],
              [State("modal-3D", "is_open"),
               State('map', 'clickData')])
def display_modal_3D(click_data_3D, n2, is_open, map_model):
    txt = ""
    if map_model:
        if click_data_3D or n2:
            return modal_display(click_data_3D, is_open)

    return is_open, txt, txt




if __name__ == '__main__':
    # app.run_server()
    app.run_server(debug=True)