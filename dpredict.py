#
# Predict Utilites for Map Ice
# https://github.com/sintekllc/map_ice
# Author Shtekhin S.
# 2018
#
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
import datetime

INPUT='g:/neft/test2/'
INPUT=''
def load_model(filename='m2017_2018_2715_1706.mdl',INPUT=''):
    model=CatBoostClassifier(iterations=100, depth=5, learning_rate=0.3, loss_function='MultiClass', logging_level='Verbose')
    model.load_model(INPUT+filename)
    return model

def load_data(filename='sf6_g2b_prep2017_2018_ocean.csv',INPUT=''):
    df=pd.read_csv(INPUT+filename)
    return df

def prepare_data(df):
    df['bath']=df['bath'].fillna(0.)
    df['lat_s']=df.lat.astype('str')
    df['lon_s']=df.lon.astype('str')
    df['CT_pred']=-9
    return df

def init_data(model_name='m2017_2018_2715_1706.mdl',
              data_name='sf6_g2b_prep2017_2018_ocean.csv',INPUT=''):
    model=load_model(model_name,INPUT)
    df=load_data(data_name,INPUT)
    df=prepare_data(df)
    return model,df

def map_predict_con(df,model,sdate='20170110',map_dt=datetime.date(2017,1,10),name_col='CT_pred'):
    cols=['lat_s', 'lon_s', 'year', 'week', 'uwnd', 'vwnd', 'tmp',  'pres', 'skt',
       'air', 'bath'   ]
    cl=[0,12,13,20,23,30,40,45,46,50,56,60,70,78,80,90,91,92]
    ddf=df.loc[
       (df.CT!=-9)]
    pweek=pd.to_datetime(sdate).week
    pyear=pd.to_datetime(sdate).year
    #test_data=ddf.loc[(ddf.dat==map_dt),cols]
    test_data=df.loc[(df.year==pyear)&
                      (df.week==pweek),cols]
    preds_class = model.predict(test_data)
    for i in range(test_data.shape[0]):
        lat_s=test_data.lat_s.values[i]
        lon_s=test_data.lon_s.values[i]
        df.loc[(df.year==pyear)&
                (df.week==pweek)&
            #(df.dat==map_dt)&
                   (df.lat_s==lat_s)&
                   (df.lon_s==lon_s),
                   name_col]= cl[np.int(preds_class[i][0])]
    return df