
import plotly.graph_objects as go

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

font_size_big_str = "20px"
font_size_small_str = "15px"
font_size_big = 20
font_size_small = 15



def get_legend(color_arr, symbol_arr, text_arr, title='', width=1500, bg_color='#606060'):

    h=24
    if width:
        if width<1010:
            h=20
    fig = go.Figure(data=[go.Table(
        columnwidth=[10],
        header=dict(values=[''],
                    line_color=bg_color,
                    fill_color=bg_color,
                    align='right',
                    font=dict(color=[color_arr], size=[font_size_big]),
                    height=h),
        cells=dict(values=[symbol_arr],  # 3rd column
                   line_color=bg_color,
                   fill_color=bg_color,
                   align='right',
                   font=dict(color=[color_arr], size=[font_size_big]),
                   height=h),

    )
    ],)

    fig.update_layout(title='', margin=dict(t=0, b=0, l=0, r=0), font=dict(size=font_size_small, color='white'),
                      showlegend=False,
                      plot_bgcolor=bg_color, paper_bgcolor=bg_color, height=250)

    return fig





def get_legend_polygon(bg_color):
    Rock = ['CS', 'Boulder', 'RS', 'R', 'SR', 'FS', 'Bio', 'Slumping area']
    Color = ['rgb(255, 191, 127)', 'rgb(255, 193, 5)', 'rgb(221, 165, 0)', 'rgb(221, 193, 110)', 'rgb(255, 255, 127)',
             '#ffff7f', 'rgb(159, 255, 127)', 'rgb(255, 112, 255)']

    quad_leg=[]
    for i in range(len(Rock)):
        quad_leg.append('\u25A0')

    fig=get_legend(Color, quad_leg, Rock, 'Polygon Legend')

    fig = go.Figure(data=[go.Table(
        columnwidth=[10],
        header=dict(values=['', 'Polygon Legend'],
                    line_color=bg_color,
                    fill_color=bg_color,
                    align='right',
                    font=dict(color=['white', 'white'], size=[font_size_small,font_size_small]),
                    height=24),
        cells=dict(values=[quad_leg, Rock],  # 3rd column
                   line_color=bg_color,
                   fill=dict(color=[bg_color,bg_color]),
                   align='right',
                   font=dict(color=[Color, "white"], size=[font_size_small,font_size_small]),
                   height=24),

    )
    ], )

    fig.update_layout(title='', margin=dict(t=0, b=0, l=0, r=0), font=dict(size=font_size_small, color='white'),
                      showlegend=False,
                      plot_bgcolor=bg_color, paper_bgcolor=bg_color, height=250)

    return fig




    return fig

def get_legend_polyline(width, bg_color):

    Rock = ['Found cable', 'Linear Target',  'Anchor Trawling Scars']
    Color = [ 'orange',  'red',  'brown']

    quad_leg=[]
    for i in range(len(Rock)):
        quad_leg.append('\u2014')

    fig=get_legend(Color, quad_leg, Rock, 'Polyline Legend', width, bg_color)

    return fig

def get_legend_POI(width, color):

    POI = ['sonar contact', 'SBP sonar contact', 'magnetic anomaly', 'CPT location', 'gravity core', 'text']
    Color = ['red', 'green', 'orange', 'magenta', 'blue','white']
    symbol =['\u25B2','\u25B2', '\u25CF','\u25CF', '\u25CF', '\u2022']

    fig=get_legend(Color, symbol, POI, 'POI Legend', width, color)

    return fig
