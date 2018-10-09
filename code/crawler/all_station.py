# -*- coding: utf-8 -*-
# Python3.5
import requests  # 导入requests
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
import os
import pandas as pd
import numpy as np

'''
def get_all_station():
    all_station = pd.DataFrame(columns=['name', 'longitude', 'latitude'])
'''

bus_net = pd.read_csv('Network_bus.csv', index_col=0)
all_station = set()
for i in range(len(bus_net)):
    for j in range(bus_net.loc[i, 'station_num']):
        all_station.add(bus_net.loc[i, 'station_{}'.format(j)])
temp = list(all_station)
temp.sort()
df = pd.DataFrame(columns=['name'])
df['name'] = (temp)
df.to_csv('Station_map.csv')
# print(df)

