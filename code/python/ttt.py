# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import time
df_train = pd.read_csv('../bus_data/stationmap/train_amap_correct.csv')
df_train['station_id'] = None
df_train['name'] = None
df_train['real_longitude'] = np.NaN
df_train['real_latitude'] = np.NaN
df_real = pd.read_csv('../bus_data/stationmap/location_corrected.csv')
a = time.time()
for i in range(len(df_train)):
    train_x = df_train.loc[i,'longitude_amap']
    train_y = df_train.loc[i,'latitude_amap']
    df_temp = df_real.copy()
    df_temp['distance'] = np.NaN
    for j in range(len(df_real)):
        real_x = df_real.loc[j,'longitude']
        real_y = df_real.loc[j,'latitude']
        distance = (train_x*1000 - real_x*1000)**2 + (train_y*1000 - real_y*1000)**2
        df_temp.loc[j,'distance'] = distance
    df_temp.sort_values(by=['distance'],inplace=True)
    index = df_temp.index[0]
    df_train.loc[i,'station_id'] = df_real.loc[index,'station_id']
    df_train.loc[i,'name'] = df_real.loc[index,'name']
    df_train.loc[i,'real_longitude'] = df_real.loc[index,'longitude']
    df_train.loc[i,'real_latitude'] = df_real.loc[index,'latitude']
    if i % 10 == 9:
        b = time.time()
        print('complete {},cost {}s.'.format(i+1,b-a))
   
df_train.to_csv('../bus_data/stationmap/match_result.csv',index=False)