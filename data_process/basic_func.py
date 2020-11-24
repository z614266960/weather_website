# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 19:15:01 2020

@author: 86152

基本的函数定义
基本的变量定义

"""
import os
from datetime import datetime, date, timedelta
'''
sta_data() 对数据进行格式化成为固定格式
:param df: dataframe的站点数据
:param columns: 文件内包含的数据的列名
:return: 包含‘level', 'time', 'dtime', 'id', 'lon', 'lat',  列的一个dataframe
'''

"""
parseLocation(inVal) 单个经度或者纬度字符串转化
:param inVal: 未处理前的经度或者纬度
:return: 转换后的单个经度或者纬度
"""
def parseLocation(inVal):   
    ss = inVal[-2:]
    mm = inVal[-4:-2]
    hh = inVal[:-4]
    position = ""          
    try:
        s = float(ss)/3600
        m = float(mm)/60
        h = float(hh)      
        position = "{:.3f}".format(h + m + s)        
    except ValueError as ex:
         print("Invalid location value: " + inVal + ", " + str(ex))   
    return position

"""
函 数 名: process_position(position_data, data_length)
函数功能: 处理经纬度位置信息
输入参数: 
    position_data:为转换前的经度或者纬度位置
    data_length:经度或者纬度的数据长度
输出参数: 无
返 回 值: 转换后的经度或者纬度列表
"""
def process_position(position_data, data_length):
    tran_positions = []
    str_positions = [str(item) for item in position_data]

    for str_position in str_positions:
        str_position = str_position.ljust(data_length,"0")   #ljust左对齐，不足的用0填充，补充字符串长度
        tran_positions.append(parseLocation(str_position))   #将得出的数据添加进列表
        
    tran_positions = [ float(x) for x in tran_positions ]      #转为浮点数，小数点后的0丢失
    
    return tran_positions

'''
get_date_step(datestr, step, format_str) 求某个字符格式日期前推step或者后退step的日期
:param datestr: 字符串格式的日期
:param step: 前推或者后推的日期长度
:param format_str: 转换的日期格式
:return: 返回所求的日期
'''
# "%Y-%m-%d %H:%M:%S"
def get_date_step(datestr, step, format_str):
    str2date = datetime.strptime(datestr,format_str)#字符串转化为date形式
    date2str = (str2date + timedelta(days = step)).strftime(format_str)    # 昨天日期  
    return date2str

'''
get_date_n(datelist, day, hour) 求某日期前几天的日期列表
:param datelist: 字符格式的日期列表
:param day: 前推或者后推的日期长度
:param hour: 日期后面添加的小时 08或者20时
:return: 返回所求的日期列表
'''
# 求前n天的日期
def get_date_n(datelist, day, hour):
    i = 0
    newlist = []
    for datestr in datelist:
        str2date = datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")#字符串转化为date形式
        if hour == '08':
            index = day -1
            hour_predict = '20'
        if hour == '20':
            index = day
            hour_predict = '08'
        yesterday = (str2date + timedelta(days = index)).strftime("%Y-%m-%d %H:%M:%S")    # 昨天日期
        yesterday = yesterday[:11] + hour_predict + ':00:00'
        newlist.append(yesterday)
    return newlist

'''
make_dir(file_path, dir_name, dir_type, feature) 创建所需的文件夹
:param file_path: 文件夹存放的路径
:param dir_name: 文件夹名字
:param dir_type: 文件夹类型 ob_dir 实况数据存放路径  ECbyID_dir EC数据存放路径
:param feature: 特征名称 10UV 10FG6 MSL
:return: 无
'''
def make_dir(file_path, dir_name, dir_type, feature):
    half_list = ['012(08-20)','012(20-08)']
    hour_list = ['08','20']
    season_list = ['3-4','5-6','7-9','10-11','12-2']
    
    if dir_type == 'ob_dir':      
        for half_str in half_list:
            dir_path = os.path.join(file_path, dir_name, half_str)
            isExists = os.path.exists(dir_path)
            if not isExists:
                os.makedirs(dir_path)
                print(dir_path + ' 创建成功')
            else:
                print(dir_path + ' 目录已存在')
    if dir_type == 'EC_dir':
        for day in range(1, 11):
            for season in season_list:
                for hour in hour_list:
                    day_str = str(day) + '天'
                    dir_path = os.path.join(file_path, dir_name, day_str, season, hour)#, feature
                    isExists = os.path.exists(dir_path)
                    if not isExists:
                        os.makedirs(dir_path)
                        print(dir_path + ' 创建成功')
                    else:
                        print(dir_path + ' 目录已存在')
    if dir_type == 'ECbyID_dir' or dir_type == 'merge_dir':
        for day in range(1, 11):
            for hour in hour_list:
                    day_str = str(day) + '天'
                    dir_path = os.path.join(file_path, dir_name, day_str, hour, feature)
                    isExists = os.path.exists(dir_path)
                    if not isExists:
                        os.makedirs(dir_path)
                        print(dir_path + ' 创建成功')
                    else:
                        print(dir_path + ' 目录已存在')

'''
isFileExist(path, file_name) 检查文件是否存在
:param file_path: 文件存储路径
:return: False 文件不存在; True 文件存在
'''
def isFileExist(file_path):
    # file_path = os.path.join(path, file_name)
    isExist = os.path.exists(file_path)
    if not isExist:
        return False
    else:
        return True