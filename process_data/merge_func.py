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
from process_data import basic_func, ob_func, EC_func
from tools import date_tools

'''
get_date_before(date_today, index, space) 求某个字符格式日期前推space或者后推space的日期
:param date_today: 当前日期
:param index: 前推或者后推的日期长度
:param space:  前推或者后推间隔
:return: 所求的日期队列
'''


# 计算前7天的日期
def get_date_before(date_today, index, space):  # dataType EC ob
    newDayList = []

    for i in range(index, 0, 1):  # -7 0 1
        str2date = datetime.strptime(date_today, "%Y-%m-%d %H:%M:%S")
        index = i - space + 1
        today_before = (str2date + timedelta(days=index)).strftime("%Y-%m-%d %H:%M:%S")
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
    for day in range(1, 11):
        _10Feature_path = os.path.join(path, str(day) + '天\\', hour, feature, Station_ID + '.csv')

        isExist = os.path.exists(_10Feature_path)
        if not isExist:
            original = pd.DataFrame()
        else:
            original = pd.read_csv(_10Feature_path)
        _data_dict[str(day) + '天'] = original
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

    isExist = os.path.exists(path)
    if not isExist:
        return pd.DataFrame()

    data = pd.DataFrame(columns=["台站号", "年月日", feature_select])
    original = pd.read_csv(path)
    data = data.append(original, ignore_index=True)  # , index_col=0
    data = data.loc[(data[feature_select] > 0)]

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


def fill_func(df_row, feature, index, day):
    if index >= day:
        return 'nan'
    if df_row.loc[feature + '_-' + str(index)] is 'nan':
        index = index + 1
        return fill_func(df_row, feature, index, day)
    else:
        return df_row.loc[feature + '_-' + str(index)]


def fill_empty_cell(df_row, feature, day):
    # 实况数据为空
    if df_row.loc['ob'] is 'nan':
        data = fill_func(df_row, 'ob', 1, 15)
        # 空值处理
        if data is 'nan':
            return False
        else:
            df_row['ob'] = data

    for sub_index in range(1, day):
        if df_row.loc[feature + '_-' + str(sub_index)] is 'nan':
            data = fill_func(df_row, feature, sub_index + 1, day)
            if data is 'nan':
                data = df_row.loc[feature]
            df_row[feature + '_-' + str(sub_index)] = data

    for sub_index in range(1, 16):
        if df_row.loc['ob_-' + str(sub_index)] is 'nan':
            data = fill_func(df_row, 'ob', sub_index + 1, 15)
            if data is 'nan':
                data = df_row.loc['ob']
            df_row['ob_-' + str(sub_index)] = data
    return df_row


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
# def merge_Feature_OB_data(_10Feature_dict, MSL_dict, ob_data, date_list, hour, day, ID, Feature):
def merge_Feature_OB_data(_10Feature_dict, MSL_dict, ob_data, date_str, hour, day, ID, Feature):
    merge_file_path = os.path.join('./', 'data', 'ob_EC_merge')
    basic_func.make_dir(merge_file_path, '', 'merge_dir', Feature)

    _10Feature_data = _10Feature_dict[str(day) + '天']
    MSL_data = MSL_dict[str(day) + '天']
    # date_str = date + ' ' + hour + ':00:00'

    merge_file_path = os.path.join('./', 'data', 'ob_EC_merge', str(day) + '天', hour, Feature, ID + '.csv')
    isExist = os.path.exists(merge_file_path)
    if isExist:
        if not _10Feature_data.empty and not MSL_data.empty:
            select_10Feature = pd.DataFrame()
            select_MSL = pd.DataFrame()
            # for nowtime in date_list:
            #     date = nowtime[0:10]
            #     date_str = date + ' ' + hour + ':00:00'
            df_10Feature = _10Feature_data.loc[_10Feature_data['now_time'] == date_str]
            df_msl = MSL_data.loc[MSL_data['now_time'] == date_str]
            if not df_10Feature.empty:
                select_10Feature = select_10Feature.append(df_10Feature, ignore_index=True)
            if not df_msl.empty:
                select_MSL = select_MSL.append(df_msl, ignore_index=True)

            # merge_data = df.append(merge_data, ignore_index = True)
            # select_10Feature = _10Feature_data.loc[_10Feature_data['now_time'] == date_str]
            # select_MSL = MSL_data.loc[MSL_data['now_time'] == date_str]
        elif not MSL_data.empty:
            select_MSL = MSL_data.loc[MSL_data['now_time'] == date_str]
            select_10Feature = pd.DataFrame()
        elif not _10Feature_data.empty:
            select_10Feature = _10Feature_data.loc[_10Feature_data['now_time'] == date_str]
            select_MSL = pd.DataFrame()
    else:
        select_10Feature = _10Feature_data
        select_MSL = MSL_data

    if not select_10Feature.empty and not select_MSL.empty:
        select_MSL.drop(columns=['predict_time'], inplace=True)
        merge_data = pd.merge(select_10Feature, select_MSL, how='left', on=["now_time", "id", "lon", "lat"])
    elif not select_MSL.empty:
        merge_data = select_MSL
        merge_data.loc[:, Feature] = 'nan'
    elif not select_10Feature.empty:
        merge_data = select_10Feature
        merge_data.loc[:, 'MSL'] = 'nan'
    else:
        return

    merge_data.loc[:, 'ob'] = 'nan'
    for i in range(1, day):
        merge_data.loc[:, Feature + '_-' + str(i)] = 'nan'

    for i in range(1, 16):
        merge_data.loc[:, 'ob_-' + str(i)] = 'nan'

    for index, row in merge_data.iterrows():
        ob_date_list = get_date_before(row['predict_time'], -15, day)

        ob_select = ob_data[ob_data['time'] == row['predict_time']]
        ob_select = ob_select['ob'].values
        if len(ob_select) > 0:
            row['ob'] = ob_select[0]

        for sub_index in range(1, day):
            Feature_data = _10Feature_dict[str(day - sub_index) + '天']
            Feature_select = Feature_data[Feature_data['now_time'] == row['now_time']]
            Feature_select = Feature_select[Feature].values
            if len(Feature_select) != 0:
                row[Feature + '_-' + str(sub_index)] = Feature_select[0]

        for sub_index in range(1, 16):
            ob_select = ob_data[ob_data['time'] == ob_date_list[15 - sub_index]]
            ob_select = ob_select['ob'].values
            if len(ob_select) > 0:
                row['ob_-' + str(sub_index)] = ob_select[0]

        row = fill_empty_cell(row, '10UV', day)
        if row is False:
            continue
        merge_data.loc[index] = row
    if isExist:
        df = pd.read_csv(merge_file_path)
        merge_data = df.append(merge_data, ignore_index=True)
        merge_data = merge_data.sort_values(by=['now_time', 'predict_time'])
        merge_data = merge_data.drop_duplicates(subset=['predict_time'], keep='first')
    merge_data.to_csv(merge_file_path, index=False)


FILE_PATH = './data'


def merge_data_for_SVR(ID, feature, date_list, hour):  # ID_list
    print("SVR模型所需数据拼接中........")
    Feature_path = os.path.join(FILE_PATH, 'EC_byID')

    _10Feature_data_dic = get_day_data_dict(Feature_path, feature, hour, ID)
    _MSL_data_dic = get_day_data_dict(Feature_path, 'MSL', hour, ID)

    real_path = ''
    if hour == '08':
        real_path = os.path.join('./', 'data', 'ob', '012(20-08)', ID + '.csv')
        hour_ob = '20'
    if hour == '20':
        real_path = os.path.join('./', 'data', 'ob', '012(08-20)', ID + '.csv')
        hour_ob = '08'
    real_data = read_file_real(real_path, hour_ob, feature)

    # for nowtime in date_list:
    #     date = nowtime[0:10]
    #     date_str = date + ' ' + hour + ':00:00'
    for day in range(1, 11):
        for nowtime in date_list:
            date = nowtime[0:10]
            date_str = date + ' ' + hour + ':00:00'
            merge_Feature_OB_data(_10Feature_data_dic, _MSL_data_dic, real_data, date_str, hour, day, ID, feature)
            # merge_Feature_OB_data(_10Feature_data_dic, _MSL_data_dic, real_data, date_list, hour, day, ID, feature)
    print("SVR模型所需数据拼接完成")


"""
data_for_LSTM(ID_list, feature) 根据所需预测站点的ID信息，查找各个站点所有年份的实况数据
:param: ID_list: 需要拼接数据的站点对应ID列表
:param: feature: 10UV或者10FG6 分别对应实况的2_min_wind_force和great_wind_force
:return: dict  {'F2273':DataFrame,'F2286':DataFrame} DataFrame 含id,time,ob三列
"""


def data_for_LSTM_model(Station_ID, hour, feature, ob_raw_file_path):
    # 处理原始实况数据
    ob_func.Process_raw_ob_data(ob_raw_file_path)

    # 选取实况数据
    if hour == '08':
        real_path = os.path.join('./', 'data', 'ob', '012(08-20)', Station_ID + '.csv')
    if hour == '20':
        real_path = os.path.join('./', 'data', 'ob', '012(20-08)', Station_ID + '.csv')

    real_data = read_file_real(real_path, hour, feature)
    return real_data


"""
data_for_SVR_model(Station_ID, hour, feature, ob_raw_file_path, ec_raw_file_path) 拼接SVR模型所需的数据
:param: Station_ID: 需要拼接数据的站点ID
:param: hour: 起报时间 08或者20
:param: feature: 10UV或者10FG6 分别对应实况的2_min_wind_force和great_wind_force

:return: None
"""


def data_for_SVR_model(Station_ID, hour, feature, ob_raw_file_path, ec_raw_file_path):
    # 处理原始实况数据 文件夹形式
    ob_func.Process_raw_ob_data(ob_raw_file_path)
    # 处理原始EC数据
    ID_list = [Station_ID]
    date_list = EC_func.process_raw_EC_data(ec_raw_file_path, ID_list)
    # 拼接SVR模型所需数据
    merge_data_for_SVR(Station_ID, feature, date_list, hour)


def data_for_predict(Station_ID, hour, feature, nowtime, predict_day, ob_raw_file_path, ec_raw_file_path):
    # 处理原始实况数据 文件夹形式
    ob_func.Process_raw_ob_data(ob_raw_file_path, file_type='file')
    # 处理原始EC数据
    ID_list = [Station_ID]
    date_list = EC_func.process_raw_EC_data(ec_raw_file_path, ID_list)
    # 拼接SVR模型所需数据
    merge_data_for_SVR(Station_ID, feature, date_list, hour)
    # 筛选指定日期数据
    datestr = nowtime + ' ' + hour + ':00:00'
    season = int(datestr[5:7])
    season = date_tools.choose_season_by_month(season)

    file_path = os.path.join(FILE_PATH, 'ob_EC_merge', predict_day + '天', hour, feature, Station_ID + '.csv')
    isExist = os.path.exists(file_path)
    if isExist:
        df_for_SVR = pd.read_csv(file_path)
    else:
        return pd.DataFrame(), None
    if not df_for_SVR.empty:
        select_SVR = df_for_SVR.loc[df_for_SVR['now_time'] == datestr]
    else:
        return pd.DataFrame(), None
    return select_SVR, season


def data_for_SVR(ID, feature, nowtime, hour, predict_day):  # ID_list

    date_list = [nowtime]
    merge_data_for_SVR(ID, feature, date_list, hour)

    SVR_dict = {}
    print(nowtime[0])
    datestr = nowtime + ' ' + hour + ':00:00'
    season = int(datestr[5:7])
    season = date_tools.choose_season_by_month(season)
    # for ID in ID_list:
    file_path = os.path.join(FILE_PATH, 'ob_EC_merge', predict_day + '天', hour, feature, ID + '.csv')
    isExist = os.path.exists(file_path)
    if isExist:
        df_for_SVR = pd.read_csv(file_path)
    else:
        return pd.DataFrame()

    if not df_for_SVR.empty:
        select_SVR = df_for_SVR.loc[df_for_SVR['now_time'] == datestr]
    else:
        select_SVR = pd.DataFrame()
    SVR_dict[ID] = select_SVR

    return SVR_dict, season


def data_for_LSTM_old(ID_list, feature, hour):
    data_byID = {}
    for ID in ID_list:
        if hour == '08':
            real_path = os.path.join('./', 'data', 'ob', '012(08-20)', ID + '.csv')
        if hour == '20':
            real_path = os.path.join('./', 'data', 'ob', '012(20-08)', ID + '.csv')
        real_data = read_file_real(real_path, hour, feature)
        # real_data_Total = real_data_Total.append(real_data,ignore_index=False)
        # real_data_Total = real_data_Total.reset_index(drop = True)
        data_byID[ID] = real_data
    return data_byID
