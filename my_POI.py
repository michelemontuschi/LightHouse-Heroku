import os
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
import utm

from my_config import get_bool_array_label, get_bool_array_range


import base64



def POI_symbol_converter(label):

    symbols=['','triangle-red', 'triangle-green', 'circle-oran', 'circle-fux', 'circle-blu', 'border-dot']

    return symbols[label]
def POI_symbol3D_converter(label):

    symbols=['','diamond', 'diamond', 'circle', 'circle', 'circle', 'x']

    return symbols[label]

def POI_color_converter(label):

    colors=['', 'red', 'green', 'orange', 'magenta', 'blue', 'black']
    return colors[label]

def import_POI(path, lon_range, lat_range, label=-9999):
    df_POI = pd.read_csv(path, ",")

    lon_array = np.array(df_POI.Lon.values)
    lat_array = np.array(df_POI.Lat.values)
    label_array = np.array(df_POI.Label.values)
    desc_array = np.array(df_POI.Description.values)
    attr_array = np.array(df_POI.Attribute.values)
    ID_array = np.array(df_POI.ID.values)

    lon_log = get_bool_array_range(lon_array, lon_range)
    lat_log = get_bool_array_range(lat_array, lat_range)

    log = (np.logical_and(lon_log, lat_log))

    if label > 0:
        lab_log = get_bool_array_label(label_array, label)
        log = np.logical_and(log, lab_log)

    lon_n = lon_array[log]
    lat_n = lat_array[log]
    label_n = label_array[log]

    f_s = np.vectorize(POI_symbol_converter, otypes=[str])
    symbol_n = f_s(label_n)
    f_c = np.vectorize(POI_color_converter, otypes=[str])
    color_n = f_c(label_n)

    f_s_3d = np.vectorize(POI_symbol3D_converter, otypes=[str])
    symbol3d_n = f_s_3d(label_n)

    attr_n = attr_array[log]
    desc_n = desc_array[log]

    ID_n = ID_array[log]

    df_POI_n = pd.DataFrame()
    df_POI_n['lon'] = lon_n
    df_POI_n['lat'] = lat_n
    df_POI_n['label'] = label_n
    df_POI_n['attr'] = attr_n
    df_POI_n['desc'] = desc_n
    df_POI_n['ID'] = ID_n
    df_POI_n['symbol'] = symbol_n
    df_POI_n['symbol3D'] = symbol3d_n
    df_POI_n['color'] = color_n

    return df_POI_n


def import_annotation(path, lon_range, lat_range, label=-9999):
    df_POI = pd.read_csv(path, ";")

    lon_array = np.array(df_POI.Lon.values)
    lat_array = np.array(df_POI.Lat.values)
    label_array = np.array(df_POI.Label.values)
    attr_array = np.array(df_POI.Annotation.values)

    lon_log = get_bool_array_range(lon_array, lon_range)
    lat_log = get_bool_array_range(lat_array, lat_range)
    log = (np.logical_and(lon_log, lat_log))

    if label > 0:
        lab_log = get_bool_array_label(label_array, label)
        log = np.logical_and(log, lab_log)

    lon_n = lon_array[log]
    lat_n = lat_array[log]
    label_n = label_array[log]

    f_s = np.vectorize(POI_symbol_converter, otypes=[str])
    symbol_n = f_s(label_n)
    f_c = np.vectorize(POI_color_converter, otypes=[str])
    color_n = f_c(label_n)

    f_s_3d = np.vectorize(POI_symbol3D_converter, otypes=[str])
    symbol3d_n = f_s_3d(label_n)

    attr_n = attr_array[log]

    df_POI_n = pd.DataFrame()
    df_POI_n['lon'] = lon_n
    df_POI_n['lat'] = lat_n
    df_POI_n['label'] = label_n
    df_POI_n['attr'] = attr_n
    df_POI_n['symbol'] = symbol_n
    df_POI_n['symbol3D'] = symbol3d_n
    df_POI_n['color'] = color_n

    return df_POI_n

    return 0


def get_modal_body(name):

    div=""
    if 'MALTA'in name:
        if 'T' in name[17:]:
            return modal_POI_T(name)
        elif 'C' in name[17:]:
            return modal_POI_C(name)
        elif 'K' in name[17:]:
            return modal_POI_SB(name)
    if 'T' in name[13:]:
        return modal_POI_T(name)
    elif 'C' in name[13:]:
        return modal_POI_C(name)
    elif 'K' in name[13:]:
        return modal_POI_SB(name)
    else:
        return -1



    return div


def get_lon_lat_POI(name):
    df_POI =  pd.read_csv("./data/POI/Malta_POI.csv", ",")

    row=df_POI.loc[df_POI['ID']==name]
    lon=row['Lon'].values[0]
    lat=row['Lat'].values[0]

    return lon, lat



def modal_POI_T(name):
    image_filename = "./data/POI/SCR/Images/" + name + ".jpg"
    div=''
    if os.path.isfile(image_filename):
        encoded_image = base64.b64encode(open(image_filename, 'rb').read())
        div = html.Div(children=[
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                     style={"width": "50%", "height": "100%", "display": "inline-block", "vertical-align": "top"}),
            html.P(children=[" "],
                   style={'white-space':'pre-line', "width": "10%", "height": "100%", "display": "inline-block", "vertical-align": "top",
                          'align-items': 'right', 'justify-content': 'right'}),
            html.P(children=get_text_T(name),
                   style={'white-space':'pre-line', "width": "40%", "height": "100%", "display": "inline-block", "vertical-align": "top"})
        ],)

    return div
def modal_POI_all(name):

    div = html.Div(children=[
        html.P(children=get_text_all(name),
               style={'white-space':'pre-line', "width": "40%", "height": "100%", "display": "inline-block", "vertical-align": "top"})
    ],)

    return div
def modal_POI_C(name):

    image_filename_1 = "./data/POI/CPT/Images/" + name + "_1.jpg"
    image_filename_2 = "./data/POI/CPT/Images/" + name + "_2.jpg"
    div=''
    if os.path.isfile(image_filename_1) and os.path.isfile(image_filename_2):

        encoded_image_1 = base64.b64encode(open(image_filename_1, 'rb').read())
        encoded_image_2 = base64.b64encode(open(image_filename_2, 'rb').read())
        div = html.Div(children=[
            html.Img(src='data:image/png;base64,{}'.format(encoded_image_1.decode()),
                     style={"width": "97%"}),
            html.Img(src='data:image/png;base64,{}'.format(encoded_image_2.decode()),
                     style={"width": "97%"}),

        ],)

    return div

def get_text_T(name):
    txt=''
    with open('./data/POI/SCR/Text/' + name + '.txt', 'r') as f:
        txt=f.readlines()
    return txt

def get_text_all(name):

    POI = pd.read_csv("./data/POI/Malta_POI.csv", ",")
    txt=POI.loc[POI['ID'] == name]['Attribute']

    return txt


def modal_POI_SB(name):

    mimetype = "application/pdf"

    div = ''
    filename='./data/POI/SB/PDF/' + name + '.pdf'
    if os.path.isfile(filename) :
        data = base64.b64encode(open(filename, "rb").read()).decode("utf-8")
        pdf_string = f"data:{mimetype};base64,{data}"

        div=dcc.Loading(html.A(
            id="download",
            href=pdf_string,
            children=[html.Button("Download", id="download-btn")],
            target="_blank",
            download=name+'.pdf'
        )),

    return div




def get_new_POI_DB():

    df_POI = pd.read_csv("./data/POI/Malta_morph_POI.csv", ";")
    df_CPT = pd.read_csv("./data/POI/CPT_Text.csv", ";")
    df_SB = pd.read_csv("./data/POI/SB_Text.csv", ";")
    df_SC = pd.read_csv("./data/POI/SC_Text.csv", ";")

    add_attrs=[]

    for row in df_POI.iterrows():
        POI_name=row[1][0]
        POI_name=POI_name[8:]
        POI_label=int(row[1][3])

        text=""

        if ('MALTA_' in POI_name):
            POI_name=POI_name[POI_name.find("MALTA_")+6:]


        #T=1, C=4, K=5

        if POI_label == 1 :
            desc=df_SC.loc[df_SC['ID'] == POI_name].Description.values
            if len(desc) == 0:
                text = " "
            else:
                n_desc = ""
                for d in desc:
                    n_desc = n_desc + d + " "
                text = row[1][4] + " - " + n_desc

        if POI_label == 4:
            desc = df_CPT.loc[df_CPT['ID'] == POI_name].Description.values
            penet = df_CPT.loc[df_CPT['ID'] == POI_name].Penetration.values

            if len(desc)==0:
                text=" "
            else:
                n_desc=""
                n_penet = ""
                for d in desc:
                    n_desc= n_desc+d+" "
                for p in penet:
                    n_penet= n_penet+str(p)+ " "
                text = n_desc + " at " + n_penet
        if POI_label== 5:

            desc = df_SB.loc[df_SB['ID'] == POI_name].Description.values

            if len(desc) == 0:
                text = " "
            else:
                n_desc = ""
                for d in desc:
                    n_desc = n_desc + d + " "
                text = n_desc
        add_attrs.append(text)

    df_POI['Description']=add_attrs
    df_POI.to_csv("Malta_POI.csv")

    return 0

def modal_display(click_data, is_open):

    if 'text' in click_data['points'][0]:
        txt = (click_data['points'][0]['text'])
        txt = txt[:txt.find('\n\r')]
        div = get_modal_body(txt)
        lon, lat = (get_lon_lat_POI(txt))
        xy_UTM = utm.from_latlon(lat, lon)
        header = txt + " - UTM proj coordinates: " + str(xy_UTM)

        if div != -1:
            return not is_open, div, header

    return is_open, "", ""