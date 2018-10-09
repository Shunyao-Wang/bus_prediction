import numpy as np
import pandas as pd
import datetime
import time
df_test = pd.read_csv('../bus_data/toBePredicted_forUser.csv')
df_test['TIME'] = pd.to_datetime(
    '2017'+'-'+df_test['O_DATA']+' '+df_test['predHour'])
df_test['pred_timeStamps'] = None
df_train = pd.DataFrame()
timea = time.time()
for i in range(8, 9):
    a = ''
    if i < 10:
        a = '0'
    a += str(i)
    df_temp = pd.read_csv(
        '../bus_data/traveltime_records/traveltime_record_201710{}.csv'.format(a))
    del [df_temp['O_LINENO_START'], df_temp['O_TERMINALNO_START'], df_temp['O_UP_START'], df_temp['DATE_TIME_START'], df_temp['ARRIV_STATION_START'],
         df_temp['O_LONGITUDE_START'], df_temp['O_LATITUDE_START'], df_temp['O_SPEED_START'], df_temp['O_LONGITUDE_END'], df_temp['O_LATITUDE_END'],
         df_temp['O_SPEED_END'], df_temp['AVER_SPEED']]
    df_temp['DATE_TIME_END'] = pd.to_datetime(df_temp['DATE_TIME_END'])
    df_temp['TRAVEL_TIME'] = pd.to_timedelta(df_temp['TRAVEL_TIME'])
    df_train = df_train.append(df_temp, ignore_index=True)
    timeb = time.time()
    print('\'201710{}.csv\'has read, cost {} seconds.'.format(a, timeb-timea))
item = 0
start_time = time.time()
# for i in range(df_test.index.size):
for i in range(200):
    result = ''
    total = 0
    startid = df_test.loc[i, 'pred_start_stop_ID']
    endid = df_test.loc[i, 'pred_end_stop_ID']
    df_temp = df_train[(df_train.O_LINENO_END == df_test.loc[i, 'O_LINENO'])
                       & (df_train.O_UP_END == df_test.loc[i, 'O_UP'])]
    for j in range(startid, endid+1):
        costlist = []
        df_temp2 = df_temp[(df_temp['ARRIV_STATION_END'] == j)]
        time_a = df_test.loc[i, 'TIME']
        time_a_hour = time_a.hour
        time_a_minute = time_a.minute
        for k in range(df_temp2.index.size):
            time_b = df_temp2.iloc[k, 3]
            time_b_hour = time_b.hour
            time_b_minute = time_b.minute
            if time_a_hour == time_b_hour:
                costlist.append(df_temp2.iloc[k, 5].seconds)
            elif time_a_hour == time_b_hour + 1:
                costlist.append(df_temp2.iloc[k, 5].seconds)
        if len(costlist) != 0:
            costlist.sort()
            total += costlist[len(costlist)//2]  # 中位数
        else:
            total += 125
        result += str(total)
        if j != endid:
            result += ';'
    df_test.loc[i, 'pred_timeStamps'] = result
    item += 1
    if item % 100 == 0:
        end_time = time.time()
        print('{} complete!    {} seconds.'.format(item, end_time-start_time))
        df_result = df_test.copy()
del [df_result['O_UP'], df_result['TIME']]
df_result.to_csv('../bus_data/result_test.csv', index=False)
