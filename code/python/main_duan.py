#工作日、周末
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
for i in range(1009, 1032):
    a = str(i)
    df_temp = pd.read_csv(
        '../bus_data/traveltime_records_correct/2017{}.csv'.format(a))
    del [df_temp['O_LINENO_START'],
         df_temp['O_TERMINALNO_START'], df_temp['O_UP_START']]
    df_temp['DATE_TIME_END'] = pd.to_datetime(df_temp['DATE_TIME_END'])
    df_temp['TRAVEL_TIME'] = pd.to_timedelta(df_temp['TRAVEL_TIME'])
    df_train = df_train.append(df_temp, ignore_index=True)
    timeb = time.time()
    print('\'2017{}.csv\'has read, cost {} seconds.'.format(a, timeb-timea))

df_idmap = pd.read_csv('../bus_data/stationmap/match_result.csv')

start_time = time.time()
all_result = []
match_time = 0
matched_time = 0
for i in range(len(df_test.index)):
    # for i in range(50):
    result = []
    total = 0
    startid = df_test.loc[i, 'pred_start_stop_ID']
    endid = df_test.loc[i, 'pred_end_stop_ID']
    temp_dt = df_test.loc[i, 'TIME']
    weekday = df_test.loc[i, 'TIME'].weekday()
    lineno = df_test.loc[i, 'O_LINENO']
    up = df_test.loc[i, 'O_UP']
    #df_temp = df_train[(df_train.O_LINENO_END == df_test.loc[i, 'O_LINENO'])]
    #df_temp = df_temp[(df_temp.O_UP_END == df_test.loc[i, 'O_UP'])]
    #df_temp = df_temp[(df_temp.ARRIV_STATION_END.between(startid,endid))]

    ''' 工作日、周末 '''
    
    if weekday in range(5):
        df_temp = df_train[(df_train.DATE_TIME_END.dt.weekday.between(0,4))]
    else:
        df_temp = df_train[(df_train.DATE_TIME_END.dt.weekday.between(5,6))]
    
    #df_temp = df_train[(df_train.DATE_TIME_END.dt.weekday == df_test.loc[i, 'TIME'].weekday())]

    for j in range(startid, endid+1):
        df_aaa = df_idmap[df_idmap.O_LINENO == lineno]
        df_aaa = df_aaa[df_aaa.O_UP == up]
        df_aaa1 = df_aaa[df_aaa.STATION == j-1]
        df_aaa2 = df_aaa[df_aaa.STATION == j]
        start_real_id = -1
        end_real_id = -1
        if ((len(df_aaa1.index) != 0) & (len(df_aaa2.index) != 0)):
            start_real_id = list(df_aaa1['station_id'])[0]
        # if len(df_aaa2.index) != 0:
            end_real_id = list(df_aaa2['station_id'])[0]

        df_temp2 = df_temp[df_temp.STATION_ID_START == start_real_id]
        df_temp2 = df_temp2[df_temp2.STATION_ID_END == end_real_id]

        ''' 动态时间范围 '''
        fromtime = (temp_dt - datetime.timedelta(seconds=2400) +
                    datetime.timedelta(seconds=total)).time()
        totime = (temp_dt + datetime.timedelta(seconds=2400) +
                  datetime.timedelta(seconds=total)).time()
        df_temp2 = df_temp2[(
            df_temp2.DATE_TIME_END.dt.time.between(fromtime, totime))]
        if len(df_temp2.index) != 0:
            total += df_temp2['TRAVEL_TIME'].dt.seconds.median()  # 中位数
            matched_time += 1
        else:
            total += 120
        result.append(str(total))
        match_time += 1
    result = ";".join(result)
    all_result.append(result)
    #df_test.loc[i, 'pred_timeStamps'] = result

    if i % 100 == 99:
        end_time = time.time()
        print('{} complete!    {} seconds.'.format(i + 1, end_time-start_time))
print('All compulted! Matched {}/{}'.format(matched_time, match_time))
df_test['pred_timeStamps'] = all_result

df_result = df_test.copy()
del [df_result['O_UP'], df_result['TIME']]
a = str(datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d_%H%M%S'))
df_result.to_csv('../bus_data/result/result_{}.csv'.format(a), index=False)
print(a)
