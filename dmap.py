import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import geopandas
from ipyleaflet import (
    Map,
    Marker,
    Velocity,
    basemaps,
    ImageOverlay,
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

def init_map():
    lat = 73.
    lon = 45.748445
    center = [lat, lon]
    zoom = 4
    m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom)
    return m

def map_conc(df1,df2,cols):
    m = init_map()
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

def map_wind(ds,m,fdate='2018-07-24T06:00:00'):
    display_options = {
    'velocityType': 'Global Wind',
    'displayPosition': 'bottomleft',
    'displayEmptyString': 'No wind data'
    }
    import numpy as np
    import datetime
    if ((ds['time'][-1].values > np.datetime64(fdate))&
        (ds['time'][0].values < np.datetime64(fdate))):
        wind = Velocity(
            data=ds.sel(time=fdate), 
            #zonal_speed='u_wind', meridional_speed='v_wind', 
            zonal_speed='uwnd', meridional_speed='vwnd', 
            latitude_dimension='lat', longitude_dimension='lon', 
            velocity_scale=0.01, max_velocity=20, 
            display_options=display_options
            )
        m.add_layer(wind)
    else:
        print('Нет данных на данную дату')


def get_png(acc_web):       
    acc_norm = acc_web - np.nanmin(acc_web)
    acc_norm = acc_norm / np.nanmax(acc_norm)
    acc_norm = np.where(np.isfinite(acc_web), acc_norm, 0)
    import PIL
    from base64 import b64encode
    try:
        from StringIO import StringIO
        py3 = False
    except ImportError:
        from io import StringIO, BytesIO
        py3 = True
    
    acc_im = PIL.Image.fromarray(np.uint8(plt.cm.Blues(acc_norm)*255))
                                      #YlOrRd(acc_norm)*255))
                                      #jet
    acc_mask = np.where(np.isfinite(acc_web), 255, 0)
    mask = PIL.Image.fromarray(np.uint8(acc_mask), mode='L')
    im = PIL.Image.new('RGBA', acc_norm.shape[::-1], color=None)
    im.paste(acc_im, mask=mask)
    if py3:
        f = BytesIO()
    else:
        f = StringIO()
    im.save(f, 'png')
    data = b64encode(f.getvalue())
    if py3:
        data = data.decode('ascii')
    imgurl = 'data:image/png;base64,' + data
    return imgurl 
        
def get_png_temp(ds,fdate='2018-07-04T12:00:00'):
    if ((ds['time'][-1].values > np.datetime64(fdate))&
        (ds['time'][0].values < np.datetime64(fdate))):
        lons=ds.sel(time=fdate)['lon']
        ind_lons=np.where((lons>18.)&(lons<100.))

        lats=ds.sel(time=fdate)['lat']
        ind_lats=np.where(lats>65.)

        lon_2d, lat_2d = np.meshgrid(lons[ind_lons], lats[ind_lats])
    
        surface_temp = ds.sel(time=fdate)['tmp'][ind_lats[0],ind_lons[0]]
        surface_temp.metpy.convert_units('degC')
        acc_web=surface_temp
        return get_png(acc_web)
    else:
        print('Нет данных на данную дату')
        return ''
        
    
        
def map_temp(ds,m,fdate='2018-07-24T06:00:00'):
    bounds = [(88., 18), (65., 100.)]
    imgurl=get_png_temp(ds,fdate)
    if imgurl != '':
    #bounds = [(18., 68), (100., 85.)]
        io = ImageOverlay(url=imgurl, bounds=bounds, opacity=0.3)
        m.add_layer(io)

def get_png_bath(ds):
    bath = ds['z']
    acc_web=np.flip(bath,axis=0)
    return get_png(acc_web)
        
def map_bath(ds,m):
    bounds = [(81.5, 18.5), (64.5, 99.)]
    imgurl=get_png_bath(ds)
    if imgurl != '':
    #bounds = [(18., 68), (100., 85.)]
        io = ImageOverlay(url=imgurl, bounds=bounds, opacity=0.75)
        m.add_layer(io)