item = 0
start_time = time.time()
#for i in range(df_test.index.size):
for i in range(200):
    result = ''
    total = 0
    startid = df_test.loc[i, 'pred_start_stop_ID']
    endid = df_test.loc[i, 'pred_end_stop_ID']
    time_temp = df_test.loc[i, 'TIME']
    time_tempa = datetime.datetime(2017, 10, 8, time_temp.hour-1, 0, 0)
    time_tempb = datetime.datetime(2017, 10, 8, time_temp.hour+1, 0, 0)
    df_temp = df_train[(df_train.O_LINENO_END == df_test.loc[i, 'O_LINENO'])
                       & (df_train.O_UP_END == df_test.loc[i, 'O_UP'])
                       & (df_train.DATE_TIME_END < time_tempb)
                       & (df_train.DATE_TIME_END > time_tempa)]
    for j in range(startid, endid+1):
        costlist = []
        df_temp2 = df_temp[(df_temp['ARRIV_STATION_END'] == j)]
        for k in range(df_temp2.index.size):
            costlist.append(df_temp2.iloc[k,5].seconds)
        if len(costlist) != 0:
            costlist.sort()
            total += costlist[len(costlist)//2]  #中位数
        else:
            total += 125
        result += str(total)
        if j != endid:
            result  += ';'
    df_test.loc[i, 'pred_timeStamps'] = result
    item += 1
    if item % 100 == 0:
        end_time = time.time()
        print('{} complete!    {} seconds.'.format(item,end_time-start_time))