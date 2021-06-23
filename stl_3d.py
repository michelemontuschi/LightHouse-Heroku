import meshio
import pandas as pd


def get_stl(path):
    mesh_in = meshio.read(path)
    df_points=pd.DataFrame(mesh_in.points, columns=["x", "y", "z"])
    df_faces=pd.DataFrame(mesh_in.cells_dict['triangle'], columns=["i", "j", "k"])

    #df_points.to_csv('points.txt')
    #df_points.to_csv('faces.txt')

    return df_points, df_faces


