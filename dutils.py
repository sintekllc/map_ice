import requests
import zipfile
import re
import os
import itertools
import geopandas
import datetime
now = datetime.datetime.now()
print(now.year, now.month, now.day, now.hour, now.minute, now.second)
import xarray as xr
from metpy.cbook import get_test_data
import ftplib

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename="(.+)"', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_file(url,path_to=''):
    #url = 'http://google.com/favicon.ico'
    if is_downloadable(url):
        r = requests.get(url, allow_redirects=True)
        filename = get_filename_from_cd(r.headers.get('content-disposition'))
        open(os.path.join(path_to,filename), 'wb').write(r.content)
        return filename
    else:
        return ''

def unzip_file(path_to_zip_file,directory_to_extract_to):
    if path_to_zip_file =='':
        return ''
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()
    filename=path_to_zip_file.split('/')[-1]
    return filename.split('.')[0]

URL_BASE='http://ocean8x.aari.ru/item6/data/aarires/d0004/index.php?dir='

def get_url(sea='B',letter='a',
            fdate=datetime.date(2018,1,2)
             
            ):
    #Sea = 'B' or 'K'
    year  = fdate.strftime("%Y")
    month = fdate.strftime("%m")
    day   = fdate.strftime("%d")

    sea1=sea.lower()
    #letter=['a','b','c','d','e']

    
    URL='{}{}ar%2Fsigrid%2F{}%2F&download=aari_{}ar_{}{}{}_pl_{}.zip'.format(URL_BASE,sea,year,sea1,year,month,day,letter)
    return URL

def get_letter(ffdate,sea='B',path_to=''):
    fn=''
    for l in ['a','b','c','d','e']:
        fn=download_file(get_url(sea=sea,fdate=ffdate,letter=l),path_to=path_to)
        if fn != '':
            return fn
    return fn

def download_last(now=datetime.datetime.now()):
    firstdate = datetime.date(2018, 1, 2)
    nextdate = datetime.date(2018, 1, 9)
    # Кол-во времени между датами.
    delta = nextdate - firstdate
    print(delta.days)
    while nextdate.month <= now.month:
        nextdate = nextdate + delta
    fn=''
    for i in range(10):
        fn=get_letter(nextdate)
        if fn=='':
            nextdate = nextdate - delta 
    if fn=='':
        return 'Error: Maps not found'
    fname = unzip_file(fn,'')
    if fname=='':
        return 'Error:Bar Maps not found'
    df_bar=geopandas.read_file(fname+'.dbf')
    #print(fname)
    fname = unzip_file(get_letter(nextdate,'K'),'')
    if fname=='':
        return 'Error:Kar Maps not found'
    df_kar=geopandas.read_file(fname+'.dbf')
    #print(fname)
    return df_bar,df_kar

def download_year(year=2018,path_to=''):
    firstdate = datetime.date(2018, 1, 2)
    nextdate = datetime.date(2018, 1, 9)
    # Кол-во времени между датами.
    delta = nextdate - firstdate
    
    sdate=datetime.date(year, 1, 1)
    main_dir = [path_to+sdate.strftime("%Y")] 
    common_dir = ["Bar", "Kar"]
    for dir1, dir2 in itertools.product(main_dir, common_dir):
        try: os.makedirs(os.path.join(dir1,dir2))
        except OSError: pass
    if firstdate.year>year:
        while nextdate.year > year-1:
            nextdate = nextdate - delta
        nextdate = nextdate + delta
    if firstdate.year<year:
        while nextdate.year < year:
            nextdate = nextdate + delta
    while nextdate.year == year:
        fn=get_letter(nextdate,'B',path_to=os.path.join(main_dir[0],common_dir[0]))
        if fn=='':
            print(nextdate)
        fn=get_letter(nextdate,'K',path_to=os.path.join(main_dir[0],common_dir[1]))
        nextdate = nextdate + delta
    return

def down_w(fname,INPUT=''):
    if not os.path.exists(INPUT+fname):
        #url = 'ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/surface_gauss/tmax.2m.gauss.2018.nc'
        url = 'ftp.cdc.noaa.gov'
        
        ftp = ftplib.FTP(url)
        ftp.login()
        ftp.cwd('/Datasets/ncep.reanalysis/surface_gauss/')
        with open(INPUT+fname, 'wb') as f:
            ftp.retrbinary('RETR ' + fname, f.write)

def get_data_w(fname,INPUT=''):
    
    down_w(fname)
    ds3 = xr.open_dataset(get_test_data(INPUT+fname, False))
    
    return ds3

def get_wind_data():
    fname='new_uwnd.nc'
    #'uwnd.10m.gauss.2018.nc'
    ds3=get_data_w(fname)
    fname='new_vwnd.nc'
    #fname='vwnd.10m.gauss.2018.nc'
    ds4=get_data_w(fname)
    ds5=xr.merge([ds3,ds4])
    return ds5

def get_temp_data():
    fname='tmp.0-10cm.gauss.2018.nc'
    ds3=get_data_w(fname)
    return ds3

def get_bath_data():
    fname="new_bath.nc"
    ds = get_data_w(fname)
    return ds
    
