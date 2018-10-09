# -*- coding: utf-8 -*-
# Python3.5
import requests  # 导入requests
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
import os
import pandas as pd
import numpy as np

df = pd.read_csv('Station_map.csv', index_col=0)
df['longitude'] = None
df['latitude'] = None
# print(df)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
for i in range(len(df)):

    address = df.loc[i,'name']
    url = 'https://restapi.amap.com/v3/place/text?keywords=' + address +\
        '(公交站)&city=天津&output=XML&key=8325164e247e15eea68b59e89200988b'  # 开始的URL地址
    start_html = requests.get(url, headers=headers)
    Soup = BeautifulSoup(start_html.text, 'lxml')
    all_a = Soup.find('location')
    if all_a == None:
        continue
    location = all_a.get_text()
    location = location.split(',')
    df.loc[i,'longitude'] = location[0]
    df.loc[i,'latitude'] = location[1]

df.to_csv('location.csv')
