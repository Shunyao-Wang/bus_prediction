import pandas as pd
import numpy as np
import gc
df2 = pd.read_csv('../bus_data/stationmap/location_corrected.csv')
df1 = pd.read_csv('../bus_data/stationmap/train_amap_correct.csv')

a_x = np.ones((len(df2),len(df1)))
ttt = np.array(df1.longitude_amap)
a_x = ttt * a_x
a_x = a_x.T

b_x = np.ones((len(df1),len(df2)))
ttt = np.array(df2.longitude)
b_x = ttt * b_x

delta_x = (1000*a_x - 1000*b_x)**2
del [a_x,b_x]

##计算y差值
a_y = np.ones((len(df2),len(df1)))
ttt = np.array(df1.latitude_amap)
a_y = a_y * ttt
a_y = a_y.T
b_y = np.ones((len(df1),len(df2)))
ttt = np.array(df2.latitude)
delta_y = (1000*a_y - 1000*b_y)**2
del [a_y,b_y]

print(delta_x)
print(delta_y)