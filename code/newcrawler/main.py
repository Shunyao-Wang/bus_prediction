# -*- coding: utf-8 -*-
# Python3.5
import requests  # 导入requests
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
import os
import pandas as pd
import numpy as np

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
all_url = 'http://wuzhong.8684.cn'  # 开始的URL地址
start_html = requests.get(all_url, headers=headers)
# print (start_html.text)
Soup = BeautifulSoup(start_html.text, 'lxml')
all_a = Soup.find_all('div', class_='bus_layer_r')[2].find_all('a')
Network_list = pd.DataFrame(
    columns=['line_no', 'line_up', 'station_num', 'station_0', 'name_0'])
station = []  # list保存唯一站点名和编号
station_id = -1  # 唯一编号
temp = 1
for a in all_a:  # A-Z
    href = a['href']  # 取出a标签的href 属性
    html = all_url + href
    second_html = requests.get(html, headers=headers)
    # print (second_html.text)
    Soup2 = BeautifulSoup(second_html.text, 'lxml')
    all_a2 = Soup2.find('div', class_='cc_content').find_all(
        'div')[-1].find_all('a')  # 既有id又有class的div不知道为啥取不出来，只好迂回取了
    for a2 in all_a2:
        # title1 = a2.get_text()  # 取出a1标签的文本
        href1 = a2['href']  # 取出a标签的href 属性
        station_name = a2.get_text()
        station.append(station_name)
        station_id += 1
        # print (title1,href1)
        html_bus = all_url + href1
        thrid_html = requests.get(html_bus, headers=headers)
        Soup3 = BeautifulSoup(thrid_html.text, 'lxml')
        #bus_name = Soup3.find('div', class_='bus_i_t1').find('h1').get_text()
        # print (bus_name,bus_type,bus_time,bus_cost,bus_company,bus_update)

        ''' 获取线路站点位置  '''
        allline = Soup3.find_all('a', class_='bus_i_span')
        for line in allline:
            line_name = line.get_text()  # '5路'
            href2 = line['href']  # 5路的url 'x_b1c60aa8'
            html_line = all_url + href2
            fourth_html = requests.get(html_line, headers=headers)
            Soup4 = BeautifulSoup(fourth_html.text, 'lxml')

            all_line = Soup4.find_all('div', class_='bus_line_top')  # 上下行
            all_site = Soup4.find_all('div', class_='bus_line_site')

            for line_up in range(len(all_line)):
                line_x = all_line[line_up].find('div', class_='bus_line_txt').get_text()[
                    :-9]+all_line[line_up].find_all('span')[-1].get_text()
                sites_x = all_site[line_up].find_all('a')
                station_num = len(sites_x)
                if station_num > (Network_list.columns.size-3)/2:
                    while temp != station_num:
                        Network_list['station_{}'.format(temp)] = None
                        Network_list['name_{}'.format(temp)] = None
                        temp += 1
                i = 0
                for site_x in sites_x:
                    if str(site_x).find(href1) != -1:
                        if len(Network_list[(Network_list.line_no == line_name) & (Network_list.line_up == line_up)]) != 0:
                            index = Network_list[(Network_list.line_no == line_name) & (
                                Network_list.line_up == line_up)].index[0]
                            Network_list.loc[index, 'station_{}'.format(
                                i)] = station_id
                            Network_list.loc[index, 'name_{}'.format(
                                i)] = site_x.get_text()

                        else:
                            sites_x_list = dict()  # 字典是为了往Dataframe按行存
                            sites_x_list.update(
                                {'station_{}'.format(i): station_id, 'name_{}'.format(i): site_x.get_text()})
                            information = {'line_no': line_name,
                                           'line_up': line_up, 'station_num': station_num}
                            information.update(sites_x_list)
                            Network_list = Network_list.append(
                                information, ignore_index=True)
                    i += 1
print('crawler success!')


def text_save(content, filename, mode='w'):
    # Try to save a list variable in txt file.
    file = open(filename, mode)
    for i in range(len(content)):
        file.write(str(content[i])+'\n')
    file.close()


# 输出处理后的数据
# text_save(Network_list, 'Network_bus.txt')
Se = pd.Series(station)
Se.to_csv('station_dict.csv')
Network_list.to_csv('Network_bus.csv', index=False)
