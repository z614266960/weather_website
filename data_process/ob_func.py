# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 21:48:33 2020

@author: 86152
"""

import pandas as pd
import os
import numpy as np
import datetime

import basic_func as basic_func

# ob_columns = ['台站号','年月日','小时','2分钟风向','2分钟风速','极大风速风向','极大风速'] #
# 2_min_wind_force  10UV风速
# great_wind_force  10FG3风速 
# 2_Min_Wind_Force  10UV风力
# Great_Wind_Force  10FG3风力
ob_columns = ['台站号','年月日','小时','2_min_wind_force','great_wind_force','2_Min_Wind_Force','Great_Wind_Force'] #


'''
preprocess_raw_ob(ob_row_df) 预处理ob的原始数据,剔除掉无用的数据，并将按照年月日和小时排序
:param ob_row_df: 存放ob原始数据的DataFrame
:return: dataframe 处理后的ob数据
'''
def preprocess_raw_ob(ob_row_df):
    ob_row_df = ob_row_df.dropna(axis=0, how='any')
    # ob_row_df['2分钟风速'] = ob_row_df['2分钟风速'].astype(int)
    # ob_row_df['极大风速'] = ob_row_df['极大风速'].astype(int)
    # ob_row_df = ob_row_df.loc[(ob_row_df['2分钟风速']>0) & (ob_row_df['极大风速']>0)]
    ob_row_df['小时'] = ob_row_df['小时'].astype(int)
    ob_row_df = ob_row_df.sort_values(by = ['年月日','小时'], ascending=['True','True'])
    return ob_row_df

'''
txt2csv(file_path, file_name) 提取txt格式ob原始数据中有用的数据，并将txt格式转化为csv格式
:param file_path: txt格式数据存放路径
:param file_name: txt格式数据文件名称
:return: 返回处理之后列名为'台站号', '年月日', '小时', '2_min_wind_force', 'great_wind_force'的dataframe格式的数据 
'''
def txt2csv(file_path, file_name):
    txt_path = os.path.join(file_path, file_name)
    with open(txt_path, 'r') as f:
        rows = f.read()
    rows = rows.splitlines()
    
    datas = []
    for row in rows:
        datas.append(row.split())
    
    useful_data = []
    for data in datas:
        temp = data[0:3] + data[4:5] +  data[-2:-1]
        useful_data.append(temp)
    
    df = pd.DataFrame(useful_data)
    
    df.columns = ob_columns[0:5]
    df = preprocess_raw_ob(df)
    # =====================================================
    # save_path = 'D:\\WorkSpace_Spyder\\气象局项目\\total_Code\\test_data\\test_save\\实况数据\\txt2csv\\'
    # df.to_csv(save_path + file_name[0:5] + ".csv", index=None, encoding= 'gbk')
    # print(save_path + file_name[0:5] + ".csv")
    # =====================================================
    return df

'''
data_20_isExist(ob_df, date) 查找某个日期是否存在20时的实况数据
:param ob_df: 某个站点所有时间段的实况数据
:param date: 需要查找的日期
:return: 若存在返回日期，若不存在返回None
'''
def data_20_isExist(ob_df, date):

    data = ob_df.loc[ob_df["年月日"] == date]
    data["小时"] = data["小时"].astype(int)
    # 当前日期
    data_temp = data[data["小时"] >= 20]
    if len(data_temp) > 0:
        return date
    else:
        day_after = basic_func.get_date_step(date, 1, "%Y%m%d")
        data = ob_df.loc[ob_df["年月日"] == day_after]
        data_temp = data[data["小时"] >= 0]
        data_temp = data_temp[data["小时"] <= 7]
        if len(data_temp) > 0:
            return date
    return None

'''
find_max_data(ob_part, Station_ID, date, hour) 某个站点某个时间段数值的最大值
:param ob_part: 某个站点某天的实况数据
:param Station_ID: 站点ID
:param date: 查找的日期
:param hour: 08时或者20时
:return: 若成功，返回列名为'台站号', '年月日', '小时', '2_min_wind_force', 'great_wind_force','2_Min_Wind_Force', 'Great_Wind_Force'的dataframe数据 
         否则返回空的dataframe
'''
def find_max_data(ob_part, Station_ID, date, hour):
    # 2_min_wind_force  10UV风速  OK
    # great_wind_force  10FG3风速 
    # 2_Min_Wind_Force  10UV风力
    # Great_Wind_Force  10FG3风力
    _10UV_Speed = []
    _10FG3_Speed = []   
        
    for index in range(len(ob_part)):
        _10UV_Speed.append(int(ob_part.iloc[index]["2_min_wind_force"]))
        _10FG3_Speed.append(int(ob_part.iloc[index]["great_wind_force"]))
    if ((len(_10UV_Speed) != 0) & (len(_10FG3_Speed) != 0)):
        # 2分钟风速最大值 2_min_wind_force
        _10UV_Speed_max = max(_10UV_Speed)
        _10UV_Speed_max = int(_10UV_Speed_max)/10
        _10UV_Power_max = Wind_SpeedtoPower(_10UV_Speed_max)
        # 极大风速最大值 great_wind_force
        _10FG3_Speed_max = max(_10FG3_Speed)
        _10FG3_Speed_max = int(_10FG3_Speed_max)/10
        _10FG3_Power_max = Wind_SpeedtoPower(_10FG3_Speed_max)
        
        row_list = [Station_ID, date, hour, _10UV_Speed_max, _10FG3_Speed_max,_10UV_Power_max,_10FG3_Power_max]#, max_angle2, max_angle
        arr = np.array(row_list).reshape(1, len(ob_columns))
        row_ob_df = pd.DataFrame(arr, columns = ['台站号','年月日','小时','2_min_wind_force','great_wind_force','2_Min_Wind_Force','Great_Wind_Force'])#,'2分钟风向','极大风速风向'
        return row_ob_df
    return pd.DataFrame()

'''
Wind_SpeedtoPower(_Speed_max)
:param _Speed_max: 10UV或者10FG6某个时间段风速最大值
:return: 返回转换后的10UV或者10FG6风力
'''
def Wind_SpeedtoPower(_Speed_max):    
    if _Speed_max == 0:
        return 0
    if _Speed_max < 1.6:
        return 1 + (_Speed_max -0)/(1.6-0)
    elif _Speed_max < 3.4:
        return 2 + (_Speed_max -1.6)/(3.4-1.6)
    elif _Speed_max < 5.5:
        return 3 + (_Speed_max -3.4)/(5.5-3.4)
    elif _Speed_max < 8:
        return 4 + (_Speed_max -5.5)/(8-5.5)
    elif _Speed_max < 10.8:
        return 5 + (_Speed_max -8)/(10.8-8)
    elif _Speed_max < 13.9:
        return 6 + (_Speed_max -10.8)/(13.9-10.8)
    elif _Speed_max < 17.2:
        return 7 + (_Speed_max -13.9)/(17.2-13.9)
    elif _Speed_max < 20.8:
        return 8 + (_Speed_max -17.2)/(20.8-17.2)
    elif _Speed_max < 24.5:
        return 9 + (_Speed_max -20.8)/(24.5-20.8)
    elif _Speed_max < 28.5:
        return 10 + (_Speed_max -24.5)/(28.5-24.5)
    elif _Speed_max < 32.7:
        return 11 + (_Speed_max -28.5)/(32.7-28.5)
    elif _Speed_max < 37:
        return 12 + (_Speed_max -32.7)/(37-32.7)
    elif _Speed_max < 41.5:
        return 13 + (_Speed_max -37)/(41.5-37)
    elif _Speed_max < 46.2:
        return 14 + (_Speed_max -41.5)/(46.2-41.5)
    elif _Speed_max < 51:
        return 15 + (_Speed_max -46.2)/(51-46.2)
    elif _Speed_max < 56.1:
        return 16 + (_Speed_max -51)/(56.1-51)
    else:
        return 17

'''
ob_12h_max(ob_raw_df):查找12小时中ob中2分钟风速，极大风速的最大值
:param ob_raw_df: ob的原始数据
:return: 返回筛选出的列名为'台站号', '年月日', '小时', '2_min_wind_force', 'great_wind_force',
       '2_Min_Wind_Force', 'Great_Wind_Force'的dataframe
'''
def ob_12h_max(ob_raw_df):
    print("12h寻找最大值")
    
    ID_list = []
    ID_group = ob_raw_df.groupby("台站号").groups
    ID_list = list(ID_group.keys())
    
    times_list = []
    times_group = ob_raw_df.groupby("年月日").groups
    times_list = list(times_group.keys())
    
    process_ob_df = pd.DataFrame()
    
    for ID in ID_list:
        for time in times_list:
            ob_part = ob_raw_df.loc[ob_raw_df['台站号'] == ID] 
            # 筛选08时的实况数据
            ob_part_08 = ob_part.loc[ob_part['年月日'] == time] 
            ob_part_08["小时"] = ob_part_08["小时"].astype(int)
            ob_part_08 = ob_part_08.loc[(ob_part_08['小时']> 8) & (ob_part_08['小时']< 21)]  #8-19   9-20 

            # 查找12小时内的最大值
            df = find_max_data(ob_part_08,  ID, time, '08')
            
            if len(df) != 0:
                process_ob_df = process_ob_df.append(df, ignore_index = True)
            
            ob_20_date = data_20_isExist(ob_part, time)
            if ob_20_date != None:
                #筛选20时的实况数据
                ob_part_20 = ob_part.loc[ob_part['年月日'] == ob_20_date]
                ob_part_20["小时"] = ob_part_20["小时"].astype(int)
                ob_part_20 = ob_part_20.loc[ob_part_20['小时']>20] # 20- 21-
                
                data = ob_part.loc[ob_part['年月日'] == basic_func.get_date_step(ob_20_date, 1, "%Y%m%d")]
                data["小时"] = data["小时"].astype(int)
                data = data.loc[(data['小时']>=0)&(data['小时']<=8)] # 0-7  0- 8
                ob_part_20 = ob_part_20.append(data, ignore_index= False)
                # 查找12小时内的最大值
                df = find_max_data(ob_part_20, ID, ob_20_date, '20')
                if len(df) != 0:
                    process_ob_df = process_ob_df.append(df, ignore_index = True)                
    process_ob_df = process_ob_df.drop_duplicates()
    return process_ob_df


'''
save_ob_local(ob_df, save_path)
:param ob_df: 存放处理后实况数据的dataframe
:param save_path: 处理后的实况数据存放位置
:return: 返回若成功实况数据中包含的站点列表
            否则返回None
'''
def save_ob_local(ob_df, save_path):
    basic_func.make_dir('./', '实况数据', 'ob_dir', None)
    hour_list = []
    hour_group = ob_df.groupby("小时").groups
    hour_list = list(hour_group.keys())
    
    ID = ob_df['台站号']
    if len(ID) == 0:
        return None
    ID = ID[0]
    
    for hour in hour_list:

        if hour == '08':
            hour_str = '012(08-20)'
        if hour == '20':
            hour_str = '012(20-08)'
            
        row_add = ob_df.loc[(ob_df['台站号'] == ID) & (ob_df['小时'] == hour)]
        row_add['小时'] = str(0)
        
        ID_str = ID + '.csv'
        read_path = os.path.join(save_path, hour_str, ID_str)
        if basic_func.isFileExist(read_path):
            df = pd.read_csv(read_path)           
            df = df.append(row_add, ignore_index = True)
            df['年月日'] = df['年月日'].astype(int)
            df = df.sort_values(by = ['年月日'])
            # df["年月日"] = df["年月日"].astype(str)
            df = df.drop_duplicates(subset = ['年月日'], keep='first')
            df.to_csv(read_path, index=False)
        else:
            row_add.to_csv(read_path, index=False)
    return ID

'''
Process_raw_ob_data(raw_file_path,save_file_path) 处理站点的原始实况数据，保存在指定目录下，并返回需要预测站点ID列表
:param raw_file_path: 原始的实况数据存放路径
:param save_file_path: 处理后的实况数据存放路径
:return: 返回需要预测的站点列表
'''
def Process_raw_ob_data(raw_file_path, save_file_path):
    file_name_list = os.listdir(raw_file_path)
    ID_list = []
    for file_name in file_name_list:
        df_temp = txt2csv(raw_file_path, file_name)
        ob_max_df = ob_12h_max(df_temp)
        ID = save_ob_local(ob_max_df,save_file_path)
        if ID != None:  
            ID_list.append(ID)
    return ID_list