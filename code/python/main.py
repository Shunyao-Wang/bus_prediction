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
        '../bus_data/traveltime_records/traveltime_record_2017{}.csv'.format(a))
    del [df_temp['O_LINENO_START'], df_temp['O_TERMINALNO_START'], df_temp['O_UP_START'], df_temp['DATE_TIME_START'], df_temp['ARRIV_STATION_START'],
         df_temp['O_LONGITUDE_START'], df_temp['O_LATITUDE_START'], df_temp['O_SPEED_START'], df_temp['O_LONGITUDE_END'], df_temp['O_LATITUDE_END'],
         df_temp['O_SPEED_END'], df_temp['AVER_SPEED']]
    df_temp['DATE_TIME_END'] = pd.to_datetime(df_temp['DATE_TIME_END'])
    df_temp['TRAVEL_TIME'] = pd.to_timedelta(df_temp['TRAVEL_TIME'])
    df_train = df_train.append(df_temp, ignore_index=True)
    timeb = time.time()
    print('\'2017{}.csv\'has read, cost {} seconds.'.format(a, timeb-timea))


start_time = time.time()
all_result = []
match_time = 0
matched_time = 0
for i in range(len(df_test.index)):
    # for i in range(200):
    result = []
    total = 0
    startid = df_test.loc[i, 'pred_start_stop_ID']
    endid = df_test.loc[i, 'pred_end_stop_ID']
    hour_temp = df_test.loc[i, 'TIME'].hour
    df_temp = df_train[(df_train.O_LINENO_END == df_test.loc[i, 'O_LINENO'])]
    df_temp = df_temp[(df_temp.O_UP_END == df_test.loc[i, 'O_UP'])]
    df_temp = df_temp[(df_temp.ARRIV_STATION_END.between(startid, endid))]
    df_temp = df_temp[(df_temp.DATE_TIME_END.dt.weekday ==
                       df_test.loc[i, 'TIME'].weekday())]
    df_temp = df_temp[(df_temp.DATE_TIME_END.dt.hour.between(
        hour_temp-1, hour_temp))]
    # print(df_temp.groupby('ARRIV_STATION_END')['TRAVEL_TIME'])

    for j in range(startid, endid+1):
        df_temp2 = df_temp[(df_temp['ARRIV_STATION_END'] == j)]
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
