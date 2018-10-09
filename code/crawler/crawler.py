# -*- coding: utf-8 -*-
# Python3.5
import requests  # 导入requests
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
import os
import pandas as pd
import numpy as np

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
all_url = 'http://tianjin.8684.cn'  # 开始的URL地址
start_html = requests.get(all_url, headers=headers)
# print (start_html.text)
Soup = BeautifulSoup(start_html.text, 'lxml')
all_a = Soup.find('div', class_='bus_kt_r1').find_all('a')
Network_list = pd.DataFrame(
    columns=['line_no', 'line_up', 'station_num', 'station_0'])
temp = 1
for a in all_a:
    href = a['href']  # 取出a标签的href 属性
    html = all_url + href
    second_html = requests.get(html, headers=headers)
    # print (second_html.text)
    Soup2 = BeautifulSoup(second_html.text, 'lxml')
    all_a2 = Soup2.find('div', class_='cc_content').find_all(
        'div')[-1].find_all('a')  # 既有id又有class的div不知道为啥取不出来，只好迂回取了
    for a2 in all_a2:
        title1 = a2.get_text()  # 取出a1标签的文本
        href1 = a2['href']  # 取出a标签的href 属性
        line_no = a2.get_text()
        # print (title1,href1)
        html_bus = all_url + href1
        thrid_html = requests.get(html_bus, headers=headers)
        Soup3 = BeautifulSoup(thrid_html.text, 'lxml')
        bus_name = Soup3.find('div', class_='bus_i_t1').find('h1').get_text()

        # print (bus_name,bus_type,bus_time,bus_cost,bus_company,bus_update)
        all_line = Soup3.find_all('div', class_='bus_line_top')
        all_site = Soup3.find_all('div', class_='bus_line_site')

        for line_up in range(len(all_line)):
            line_x = all_line[line_up].find('div', class_='bus_line_txt').get_text()[
                :-9]+all_line[line_up].find_all('span')[-1].get_text()
            sites_x = all_site[line_up].find_all('a')
            station_num = len(sites_x)
            sites_x_list = dict()
            i = 0
            for site_x in sites_x:
                sites_x_list.update(
                    {'station_{}'.format(i): site_x.get_text()})
                i += 1
            information = {'line_no': line_no,
                           'line_up': line_up, 'station_num': station_num}
            information.update(sites_x_list)
            if station_num > Network_list.columns.size-3:
                while temp != station_num:
                    Network_list['station_{}'.format(temp)] = None
                    temp += 1

            Network_list = Network_list.append(information, ignore_index=True)
# 定义保存函数，将运算结果保存为txt文件


def text_save(content, filename, mode='w'):
    # Try to save a list variable in txt file.
    file = open(filename, mode)
    for i in range(len(content)):
        file.write(str(content[i])+'\n')
    file.close()


# 输出处理后的数据
# text_save(Network_list, 'Network_bus.txt')
Network_list.to_csv('Network_bus.csv')
