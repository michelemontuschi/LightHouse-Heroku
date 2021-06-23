#from app.py
'''
@server.route('/static/<path:path>')
def serve_static(path):
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'static'), path)
'''

#from my_model_2D.py
'''
#show polygon on 2D map
def polygon_mapping2D(lon_subaxis, lat_subaxis, z, img):


    index_vec=[30,31,32,40,42,43,51,61,211]
    color_vec=['rgb(0, 0, 0)', 'rgb(255, 191, 127)', 'rgb(255, 193, 5)', 'rgb(221, 165, 0)', 'rgb(221, 193, 110)',
               'rgb(255, 255, 127)', '#ffff7f', 'rgb(159, 255, 127)', 'rgb(255, 112, 255)']

    pl_colors=get_colorscale_from_vec(index_vec, color_vec, 256)


    lat=np.append([0],lat_subaxis)
    lat=np.array(lat)
    img=np.array(img)
    lon_subaxis=np.array(lon_subaxis)
    img_=np.column_stack((lon_subaxis, img))
    img_=np.vstack((lat, img_))
    lat, lon, img = [], [], []

    for i, y in enumerate(img_[0][1:], 1):
        for z in img_[1:]:
            lon.append(z[0])
            lat.append(y)
            img.append(z[i])


    surf = go.Densitymapbox(lat=lat, lon=lon, z=img,
                            radius=10, below='',
                            colorscale=pl_colors,
                            zmin=0,
                            zmax=255)
    return surf
'''

#from my_model_3D.py
'''

def draw_scale(lon_subaxis, lat_subaxis, data_table):


    df_points, df_faces=get_stl('Scala.stl')

    lon_max = np.amax(lon_subaxis)
    lat_max = np.amax(lat_subaxis)
    lon_min = np.amin(lon_subaxis)
    lat_min = np.amin(lat_subaxis)

    z_arr = np.nanmax(data_table)


    x = (0.1+df_points.z.values * 0.005) * (lat_max - lat_min) + lat_min
    y = (0.75+df_points.x.values * 0.005) * (lon_max - lon_min) + lon_min
    z = z_arr+14+(df_points.y.values)*0.5


    dist_lon=calc_dist(lat_min, lat_min, lon_min, lon_max)*(np.amax(df_points.z.values * 0.005)-np.amin(df_points.z.values * 0.005))
    dist_lat=calc_dist(lat_min, lat_max, lon_min, lon_min)*(np.amax(df_points.x.values * 0.005)-np.amin(df_points.x.values * 0.005))


    label_min=[np.amin(x), np.amin(y), np.amin(z)]
    label_max=[np.amax(x), np.amax(y), np.amin(z)]


    color=['#e74610' for i in df_faces.j]

    data = go.Mesh3d(
        x=x, y=y, z=z,
        i=df_faces.i, j=df_faces.j, k=df_faces.k,
        facecolor=color,
        hoverinfo = "none",
    )



    return data, dist_lon,dist_lat, label_min, label_max


def get_close(axis, value, cellsize):

    for i in range(len(axis)):
        if (abs(axis[i]-value)<=cellsize):
            return i+1


def draw_model_img(lon_subaxis, lat_subaxis, z, img, coord_value):
    pl_grey = [[0.0, 'rgb(0, 0, 0)'],
               [0.05, 'rgb(13, 13, 13)'],
               [0.1, 'rgb(29, 29, 29)'],
               [0.15, 'rgb(45, 45, 45)'],
               [0.2, 'rgb(64, 64, 64)'],
               [0.25, 'rgb(82, 82, 82)'],
               [0.3, 'rgb(94, 94, 94)'],
               [0.35, 'rgb(108, 108, 108)'],
               [0.4, 'rgb(122, 122, 122)'],
               [0.45, 'rgb(136, 136, 136)'],
               [0.5, 'rgb(150, 150, 150)'],
               [0.55, 'rgb(165, 165, 165)'],
               [0.6, 'rgb(181, 181, 181)'],
               [0.65, 'rgb(194, 194, 194)'],
               [0.7, 'rgb(206, 206, 206)'],
               [0.75, 'rgb(217, 217, 217)'],
               [0.8, 'rgb(226, 226, 226)'],
               [0.85, 'rgb(235, 235, 235)'],
               [0.9, 'rgb(243, 243, 243)'],
               [0.95, 'rgb(249, 249, 249)'],
               [1.0, 'rgb(255, 255, 255)']]

    lat_subaxis, lon_subaxis = set_axis_coord(lat_subaxis, lon_subaxis, np.nanmin(lat_subaxis), np.nanmin(lon_subaxis), coord_value)

    surf = go.Surface(x=lat_subaxis, y=lon_subaxis, z=z,
                      surfacecolor=img,
                      colorscale=pl_grey,
                      showscale=False)
    return surf


def polygon_mapping(lon_subaxis, lat_subaxis, z, img, coord_value):
    lat_subaxis, lon_subaxis = set_axis_coord(lat_subaxis, lon_subaxis, np.nanmin(lat_subaxis), np.nanmin(lon_subaxis), coord_value)
    index_vec=[30,31,32,40,42,43,51,61,211]
    color_vec=['rgb(0, 0, 0)', 'rgb(255, 191, 127)', 'rgb(255, 193, 5)', 'rgb(221, 165, 0)', 'rgb(221, 193, 110)',
               'rgb(255, 255, 127)', '#ffff7f', 'rgb(159, 255, 127)', 'rgb(255, 112, 255)']

    pl_colors=get_colorscale_from_vec(index_vec, color_vec, 256)

    surf = go.Surface(x=lat_subaxis, y=lon_subaxis, z=z,
                      surfacecolor=img,
                      colorscale=pl_colors,
                      showscale=False,
                      cmin=0,
                      cmax=255)
    return surf


def scale_annotation(fig, label_min, label_max, scale_lon, scale_lat):

    fig=go.Figure(fig)
    fig.update_layout(
        scene=dict(
            annotations=[
                dict(
                    showarrow=False,
                    x=label_min[0],
                    y=label_min[1],
                    z=label_min[2],
                    text="{:.0f} km".format(scale_lon),
                    xanchor="left",
                    xshift=-50,
                    yshift=-10),
                dict(
                    showarrow=False,
                    x=label_max[0],
                    y=label_max[1],
                    z=label_max[2],
                    text="{:.0f} km".format(scale_lat),
                    xanchor="left",
                    xshift=10),
                dict(
                    showarrow=False,
                    x=label_min[0],
                    y=label_max[1],
                    z=label_min[2],
                    text='0',
                    xanchor="left",
                    xshift=10,
                    yshift=-10),
            ])),


    return fig

'''
'''
.app__left__section {
    background-color: #303030;
    color: #e74610;
    min-height: 100vh;
    max-height: 100vh;
    max-width: 100vw;
    overflow-y: scroll;
    overflow: scroll;
    padding: 25px;
    border-left: black solid 5px;
}
.app__right__section {
    background-color: #303030;
    min-height: 100vh;
    max-height: 100vh;
    overflow-y: scroll;
    overflow: scroll;
    padding: 25px;
    border-right: black solid 5px;

}

.app__left__section::-webkit-scrollbar-thumb {
    border-radius: 5px;
    background-color: #e74610;
    --webkit-box-shadow: 0 0 1px #e74610;
}

.app__left__section::-webkit-scrollbar {
    --webkit-appearance: none;
    width: 10px;
}

.app__left__section::-webkit-scrollbar-corner {
    background: rgba(0,0,0,0);
}


.app__right__section::-webkit-scrollbar-thumb {
    border-radius: 5px;
    background-color: #e74610;
    --webkit-box-shadow: 0 0 1px #e74610;
}

.app__right__section__section::-webkit-scrollbar {
    --webkit-appearance: none;
    width: 10px;
}

.app__right__section::-webkit-scrollbar-corner {
    background: rgba(0,0,0,0);
}
'''