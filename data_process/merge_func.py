# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 21:15:25 2020

@author: 86152
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime
from datetime import datetime, date, timedelta
import os

hour_list = ['08','20']
FILE_PATH = './EC_byID'

'''
get_date_before(date_today, index, space) 求某个字符格式日期前推space或者后推space的日期
:param date_today: 当前日期
:param index: 前推或者后推的日期长度
:param space:  前推或者后推间隔
:return: 所求的日期队列
'''
#计算前7天的日期
def get_date_before(date_today, index, space):   #dataType EC ob
    newDayList = []

    for i in range(index,0,1):  # -7 0 1
        str2date = datetime.strptime(date_today, "%Y-%m-%d %H:%M:%S")
        index = i - space + 1
        today_before = (str2date + timedelta(days = index)).strftime("%Y-%m-%d %H:%M:%S")  
        newDayList.append(today_before)
    
    return newDayList
'''
get_day_data_dict(path, feature, hour, Station_ID) 根据特征读取对应数据，并将EC预测的未来10天的数据存放在字典中
:param path: 文件存放路径
:param feature: 可取10UV 10FG6 MSL等
:param hour: 08时或者20时
:param Station_ID: 站点的ID
:return: dict {'1天':DataFrame, '2天':DataFrame.....} DataFrame为某时刻(08或者20时)EC预测的10UV或10FG6或MSL
'''
def get_day_data_dict(path, feature, hour, Station_ID):
    # D:\WorkSpace_Spyder\气象局项目\total_Code\EC_byID\1天\08\MSL
    _data_dict = {}
    for day in range(1,11):
        _10Feature_path = os.path.join(path, str(day) + '天\\', hour, feature, Station_ID + '.csv')
        original = pd.read_csv(_10Feature_path) 
        _data_dict[str(day)+'天'] = original 
    return _data_dict

"""
read_file_real(path, hour, feature) 读取实况数据，选取对应数据列，返回的数据存在dataframe中
:param: path: 处理后的实况数据存放路径
:param: hour: 08时或者20时
:param: feature: 10UV对应2_min_wind_force 10FG6对应great_wind_force 
:return: 返回含有'id', 'time', 'ob'列的DataFrame
"""
def read_file_real(path, hour, feature):
    # 2_min_wind_force great_wind_force
    if feature == '10UV':
        feature_select = '2_min_wind_force'
        feature_drop = 'great_wind_force'
    elif feature == '10FG6':
        feature_select = 'great_wind_force'
        feature_drop = '2_min_wind_force'
    else:
        print("feature error!")
        return pd.DataFrame()
    
    data = pd.DataFrame(columns=["台站号", "年月日", feature_select])

    original = pd.read_csv(path)
    data = data.append(original, ignore_index=True)#, index_col=0

    # 日期格式校正
    # 先转化为字符串类型
    data["年月日"] = data["年月日"].astype(str)
    date_list = data["年月日"].astype(str)
    minutes = '00'
    seconds = '00'

    data["年月日"] = data["年月日"].apply(
        lambda x: datetime.
            strptime(x[:4] + "-" + x[4:6] + "-" + x[6:8] + " " + hour + ":" + minutes + ":" + seconds,
                     "%Y-%m-%d %H:%M:%S"))
    # 确保EC资料数据和实况数据time和id 的数据类型一致
    data["年月日"] = data["年月日"].astype(str)
    data["台站号"] = data["台站号"].astype(str)
        
    data.drop(columns=['小时', feature_drop, '2_Min_Wind_Force', 'Great_Wind_Force'], inplace=True)
    data.rename(columns={'台站号': 'id', '年月日': 'time', feature_select: 'ob'}, inplace=True)
    return data


"""
merge_Feature_OB_data(_10Feature_dict, MSL_dict, ob_data, date_str, day, Feature) 拼接SVR模型所需数据，存在DataFrame中
:param: _10Feature_dict: dict 存放EC预测的未来10天的10UV或者10FG6数据
:param: MSL_dict: dict 存放EC预测的未来10天的MSL数据
:param: ob_data: 存放某站点全部的实况数据
:param: date_str: 预测的日期 例如2015-07-14
:param: day: 1-10 分别表示1天到10天
:param: Feature: 10UV或者10FG6
:return: 返回SVR模型所需数据
"""
# Feature 10UV 10FG6
def merge_Feature_OB_data(_10Feature_dict, MSL_dict, ob_data, date_str, day, Feature):
    _10Feature_data = _10Feature_dict[str(day)+'天']
    MSL_data = MSL_dict[str(day) + '天']
    MSL_data.drop(columns = ['predict_time'],inplace=True)
    select_data = _10Feature_data.loc[_10Feature_data['now_time'] == date_str]
    merge_data = pd.merge(select_data,MSL_data,how='left',on=["now_time","id","lon","lat"])
    merge_data['ob'] = None
    for i in range(1,day):
        merge_data[Feature + '_-'+str(i)] = None
        
    for i in range(1,16):
        merge_data['ob_-'+str(i)] = None
    
    for index, row in merge_data.iterrows():
        ob_date_list = get_date_before(row['predict_time'], -15, day)
        
        ob_select = ob_data[ob_data['time'] == row['predict_time']]
        ob_select = ob_select['ob'].values
        if len(ob_select) > 0:
            row['ob'] = ob_select[0]
        
        for sub_index in range(1,day):
            Feature_data = _10Feature_dict[str(day - sub_index)+'天']
            Feature_select = Feature_data[Feature_data['now_time'] == row['now_time']]
            Feature_select = Feature_select[Feature].values
            if len(Feature_select) != 0:
                row[ Feature + '_-'+str(sub_index)] = Feature_select[0]

            
        for sub_index in range(1,16):
            ob_select = ob_data[ob_data['time'] == ob_date_list[15-sub_index]]
            ob_select = ob_select['ob'].values
            if len(ob_select) > 0:
                row['ob_-'+str(sub_index)] = ob_select[0]
        merge_data.loc[index] = row
    return merge_data

"""
data_for_LSTM(ID_list, feature) 根据所需预测站点的ID信息，查找各个站点所有年份的实况数据
:param: ID_list: 需要拼接数据的站点对应ID列表
:param: feature: 10UV或者10FG6 分别对应实况的2_min_wind_force和great_wind_force
:return: dict  {'F2273':DataFrame,'F2286':DataFrame} DataFrame 含id,time,ob三列
"""
def data_for_LSTM(ID_list, feature, hour):
    data_byID = {}
    # for hour in hour_list:
    for ID in ID_list:
        if hour == '08':
            real_path = './实况数据\\012(08-20)\\' + ID + '.csv'
        if hour == '20':
            real_path = './实况数据\\012(20-08)\\' + ID + '.csv'
        real_data = read_file_real(real_path,hour,feature)
        # real_data_Total = real_data_Total.append(real_data,ignore_index=False)
        # real_data_Total = real_data_Total.reset_index(drop = True)
        data_byID[ID] = real_data   
    return data_byID

"""
data_for_SVR(ID_list, feature, datestr, hour) 拼接SVR模型预测时所需的数据
:param: ID_list: 需要拼接数据的站点对应ID列表
:param: feature: 10UV或者10FG6 分别对应实况的2_min_wind_force和great_wind_force
:param: hour: 08时或者20时
:return: dict  {'1天':DataFrame, '2天':DataFrame.....} DataFrame 含SVR模型所需特征值
""" 
# feature 10UV 10FG6
def data_for_SVR(ID_list, feature, datestr, hour):
    date = datestr[0:10]

    data_byID = {}
    for ID in ID_list:
        Feature_path = os.path.join(FILE_PATH)
        
        _10Feature_data_dic = get_day_data_dict(Feature_path, feature,  hour, ID)
        _MSL_data_dic = get_day_data_dict(Feature_path, 'MSL', hour, ID)
        
        real_path = ''
        if hour == '08':
            real_path = os.path.join('./实况数据', '012(20-08)', ID + '.csv')
            hour_ob = '20'
        if hour == '20':
            real_path = os.path.join('./实况数据', '012(08-20)', ID + '.csv')
            hour_ob = '08'
        real_data = read_file_real(real_path, hour_ob, feature)

        data_byDay = {}
        for day in range(1,11):
            date_str = date + ' ' + hour + ':00:00'
            merge_data = merge_Feature_OB_data(_10Feature_data_dic, _MSL_data_dic, real_data, date_str, day, feature)
            day_str = str(day) + '天'
            data_byDay[day_str] = merge_data
        data_byID[ID] = data_byDay
    return data_byID

 
    
    
    
    
    
    
    
    