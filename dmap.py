import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import geopandas
from ipyleaflet import (
    Map,
    Marker,
    TileLayer,Polygon,Polyline
)
import ipyleaflet as il
import matplotlib as mpl

def map_ice_thick(df,m,cols):
    lat = 73.
    lon = 45.748445
    center = [lat, lon]
    zoom = 2
    #m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom)
    for i in range(df.shape[0]):
        bounds=df.geometry.values[i]
        crd=bounds.exterior.coords.array_interface()['data']
        shapes=bounds.exterior.coords.array_interface()['shape']
        crd1=[]
        for j in range(0,shapes[0]*2,2):
            crd1.append((crd[j+1],crd[j]))
        
        #print(i)
        #if i not in [117,120]:
        #if i not in [108]:
        cid=df.loc[df.index==i,'SA'].values[0]
        if cid=='-9':   
            fcolor = mpl.colors.rgb2hex(cols.loc[cols.SA==0,['color1','color2','color3']].values[0]/255.)
        else:
            fcolor = mpl.colors.rgb2hex(cols.loc[cols.SA==np.int(cid),['color1','color2','color3']].values[0]/255.)
        
        pg = il.Polygon(locations=crd1, weight=1,
            color='white', opacity=0.8, fill_opacity=0.5,
            fill_color=fcolor
             )
        m += pg
    

def map_ice_conc(df,m,cols):
    lat = 73.
    lon = 45.748445
    center = [lat, lon]
    zoom = 2
    #m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom)
    for i in range(df.shape[0]):
        bounds=df.geometry.values[i]
        crd=bounds.exterior.coords.array_interface()['data']
        shapes=bounds.exterior.coords.array_interface()['shape']
        crd1=[]
        for j in range(0,shapes[0]*2,2):
            crd1.append((crd[j+1],crd[j]))
        
       
        cid=df.loc[df.index==i,'CT'].values[0]
        if cid=='-9':   
            fcolor = mpl.colors.rgb2hex(cols.loc[cols.CT==0,['color1','color2','color3']].values[0]/255.)
        else:
            fcolor = mpl.colors.rgb2hex(cols.loc[cols.CT==np.int(cid),['color1','color2','color3']].values[0]/255.)
        
        pg = il.Polygon(locations=crd1, weight=1,
            color='white', opacity=0.8, fill_opacity=0.5,
            fill_color=fcolor
            
                       )
        m += pg
    
    
def map_thick(df1,df2,cols):
    lat = 73.
    lon = 45.748445
    center = [lat, lon]
    zoom = 4
    m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom)
    map_ice_thick(df1,m,cols)
    map_ice_thick(df2,m,cols)
    display(m)
    return m
    
def map_conc(df1,df2,cols):
    lat = 73.
    lon = 45.748445
    center = [lat, lon]
    zoom = 4
    m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom)
    map_ice_conc(df1,m,cols)
    map_ice_conc(df2,m,cols)
    display(m)
    return m

def map_line(line,m):
    bounds=line
    crd=bounds.coords.array_interface()['data']
    shapes=bounds.coords.array_interface()['shape']
    crd1=[]
    for j in range(0,shapes[0]*2,2):
        crd1.append((crd[j],crd[j+1]))
    pl = il.Polyline(locations=crd1, weight=1,
            color='black'
                        
                       )
    m += pl
