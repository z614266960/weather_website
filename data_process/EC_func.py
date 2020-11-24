# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 18:25:31 2020

@author: 86152
处理原始数据函数
1.实况数据的提取
2.EC数据的提取
"""
import meteva
import os
import meteva.base as meb
import numpy as np
import datetime
import xarray as xr
import pandas as pd
from nmc_met_io.read_micaps import read_micaps_4
import matplotlib.pyplot as plt
from meteva.base.tool.plot_tools import add_china_map_2basemap
import copy
from datetime import datetime, date, timedelta

import basic_func as basic_func

#经度 longitude
#纬度 latitude
# 站点的经纬度以及站点ID信息
#经度
Longitude_raw = [117.5000, 117.3600, 117.0900, 117.3200, 117.2100, 118.0100, 118.1153,
                  119.3935, 119.3319, 118.0739, 117.5401, 118.0753, 118.0647, 118.0224,
                 117.4119, 117.4119, 117.4523, 117.3703, 117.3500, 117.1354, 117.2209,
                 117.4226, 117.2900, 117.2748]
#纬度
Latitude_raw = [24.2600, 24.0800, 23.4600, 23.4500, 23.5800, 24.1300, 23.3805,
                 23.1532, 23.3402, 24.1835, 24.0205, 24.1608, 24.1952, 24.2436,
                 23.3159, 23.3159, 23.5614, 23.5004, 23.4300, 23.3605, 23.3409,
                 23.4649, 23.4225, 23.3918]
#站点
Station_ID_list = ['59127','59129','59320','59321','59322','59330','59334',
                  '46730','46735','F2206','F2273','F2286','F6031','F6032',
                  'F6054','F6060','F6084','F6038','F6040','F6118','F6119',
                  'F6127','F6147','F6901']

# Longitude_list = basic_func.process_position(Longitude_raw,8)  #字符串长度为8
# Latitude_list = basic_func.process_position(Latitude_raw,7)  #字符串长度为8

"""
GetPositionDelta(ID_list, Longitude_list, Latitude_list, flag) 根据flag的值将经度或者纬度加或者减一
:param: ID_list: 需要处理的站点列表
:param: Longitude_list: 需要处理的站点的经度列表
:param: Latitude_list: 需要处理的站点的纬度列表
:param: flag: 1 纬度+1; 2 纬度-1; 3 经度-1; 4 经度+1
:return: 返回站点信息的字典， 包含站点ID列表，处理后的经度列表以及处理后的纬度列表
"""
def GetPositionDelta(ID_list, Longitude_list, Latitude_list, flag):
    #经度 longitude
    #纬度 latitude
    if flag == 1: # 纬度+1 A
        Longitude_list = basic_func.process_position(Longitude_list,8)  #字符串长度为8
        Latitude_list = [x + 1 for x in Latitude_list]
        Latitude_list = basic_func.process_position(Latitude_list,7)  #字符串长度为8
    if flag == 2: #纬度-1 B
        Longitude_list = basic_func.process_position(Longitude_list,8)  #字符串长度为8
        Latitude_list = [x - 1 for x in Latitude_list]
        Latitude_list = basic_func.process_position(Latitude_list,7)  #字符串长度为8
    if flag == 3: #经度-1 C
        Latitude_list = basic_func.process_position(Latitude_list,7)  #字符串长度为8
        Longitude_list = [x - 1 for x in Longitude_list]
        Longitude_list = basic_func.process_position(Longitude_list,8)  #字符串长度为8
    if flag == 4: #经度+1 D
        Latitude_list = basic_func.process_position(Latitude_list,7)  #字符串长度为8
        Longitude_list = [x + 1 for x in Longitude_list]
        Longitude_list = basic_func.process_position(Longitude_list,8)  #字符串长度为8
         
    Station_Info = {"Station_ID":ID_list, "Longitude":Longitude_list, "Latitude":Latitude_list}    
    return Station_Info
  
"""
interpolate_func(Station_Info, file_path, feature) 对给定的站点使用插值法 求出对应的特征值
:param: Station_Info: 存放站点信息
:param: file_path: EC原始数据存放路径
:param: feature: feature可取10U 10V MSL等
:return: 返回列名为'time', 'dtime', 'id', 'lon', 'lat', feature的dataframe feature可以为10U、10V、MSL
"""
def interpolate_func(Station_Info, file_path, file_name_list, feature):
    
    df = pd.DataFrame(Station_Info)
    # 将DataFrame格式转化为站点格式
    sta_ID = meb.sta_data(df,columns = ["id","lon","lat"])    
    meb.set_stadata_coords(sta_ID, level = 0,)
    
    print("feature:",feature)
    
    EC_data = pd.DataFrame()
    for file_name in file_name_list:
        time_ymdh = "20"+file_name[0:8]
        dtime_str = file_name[9:12]
        
        datetime1 = meb.all_type_time_to_datetime(time_ymdh)
        meb.set_stadata_coords(sta_ID, time = datetime1, dtime=dtime_str)

        # 读取EC原始文件
        read_path = os.path.join(file_path, file_name)
        grd_data = meb.read_griddata_from_micaps4(read_path)
        sta_data = meb.fun.trans_grd_to_sta(grd_data)
        
        meb.set_stadata_names(sta_ID,[feature])
        meb.set_stadata_names(sta_data,[feature])
        # 将要素的网格信息以站点格式使用反距离权重插值到站点中
        sta_IDW = meb.interp_ss_idw(sta_data ,station = sta_ID,nearNum = 4)
        
        sta_IDW["id"] = df["Station_ID"]           #将id的70改回字符F
        EC_data = EC_data.append(sta_IDW, ignore_index = True)
    EC_data.drop(columns = ['level'],inplace=True) 
    return EC_data

"""
interpolate_other(file_path, feature, ID_list, Longitude_list, Latitude_list) 根据EC原始数据对特征插值，获取未来十天的预测信息
:param: file_path: EC原始文件存放路径
:param: feature: 需要插值的特征 10U或者10V
:param: ID_list: 需要处理的站点对应ID列表
:param: Longitude_list: 需要处理的站点对应的纬度列表
:param: Latitude_list: 需要处理的站点对应的经度列表
:return: dict  {'1天':DataFrame,'2天':DataFrame...,'10天':DataFrame} DataFrame 含time,dtime,id,lon,lat,feature六列 feature可为10U或者10V
"""
def interpolate_other(file_path, feature, ID_list, Longitude_list, Latitude_list):
    Longitude_list = basic_func.process_position(Longitude_list,  8)  #字符串长度为8
    Latitude_list = basic_func.process_position(Latitude_list, 7)  #字符串长度为7
    Station_Info = {"Station_ID":ID_list, "Longitude":Longitude_list, "Latitude":Latitude_list}
    
    file_path = os.path.join(file_path, feature, '999')
    file_name_list = os.listdir(file_path)
    
    suffix = 0
    file_byDay = {}
    for file_name in file_name_list:
        suffix = int(file_name[9:12])
        if suffix == 0:
            continue
        if suffix % 24 == 0:
            day = int(suffix /24)
        else:
            day = int(suffix / 24) + 1
            
        if day < 4:
            index_sub = 15 + (day - 1) * 24
            index_upper = 24 + (day - 1)*24
        else:
            index_sub = 90 + (day - 4) * 24
            index_upper = 96 + (day - 4)*24
        if suffix >= index_sub and suffix <= index_upper:
            if str(day) + '天' not in file_byDay.keys():
                file_byDay[str(day) + '天'] = []
            file_byDay[str(day) + '天'].append(file_name)
    # print(file_byDay)
    data_byDay = {}
    for day_str in file_byDay:
       raw_file_list = file_byDay[day_str] 
       data_feature = interpolate_func(Station_Info, file_path, raw_file_list, feature)
       data_byDay[day_str] = data_feature
    return data_byDay

"""
save_10UV_local(ID_list, _10U_dict, _10V_dict, file_save_path) 对EC预测的未来10天10U和10V数据进行处理，合并为10UV，并且保存到本地指定位置
:param: ID_list: 处理的站点对应的ID列表
:param: _10U_dict: 字典 {'1天':DataFrame, '2天':DataFrame.....}存放未来10天10U预测值
:param: _10V_dict:字典 {'1天':DataFrame, '2天':DataFrame.....}存放未来10天10V预测值
:param: file_save_path: 处理后得到的10UV数据存放路径
:return: 无
"""
def save_10UV_local(ID_list, _10U_dict, _10V_dict, file_save_path):
    basic_func.make_dir('./', 'EC_byID', 'ECbyID_dir', '10UV')
    
    for day_str in _10U_dict.keys():
        _10U_df = _10U_dict[day_str]
        _10V_df = _10V_dict[day_str]
        
        _10UV_df = _10U_df
        _10UV_df = pd.merge(_10UV_df,_10V_df,how='left',on=["time",'dtime','id','lon','lat'])
        _10UV_df['10UV'] = None
        
        for i in range(len(_10U_df)):
            _10V_select = _10V_df.loc[(_10V_df['id'] == _10U_df.iloc[i]['id']) & (_10V_df['time'] == _10U_df.iloc[i]['time']) & (_10V_df['dtime'] == _10U_df.iloc[i]['dtime'])]
            _10V_select = _10V_select['10V'].values
            _10U_select = _10U_df.iloc[i]['10U']
            if len(_10V_select) > 0 :
                _10UV_df.loc[i, '10UV'] = (abs(_10U_select)**2 + abs(_10V_select[0])**2)**0.5
        
        _10UV_max_df = _10UV_df.groupby(by='id', as_index=False).max()
        for ID in ID_list:
            _10UV_select = _10UV_max_df.loc[_10UV_max_df['id'] == ID]
            _10UV_select['time'] = _10UV_select["time"].astype(str)
            if len(_10UV_select) > 0:
                time = _10UV_select['time'].values[0]
                hour_str = time[11:13]
                
                
                save_path = os.path.join(file_save_path, day_str, hour_str, '10UV', ID + '.csv')
                
                day = int(day_str[0:1])
                _10UV_select['predict_time'] = basic_func.get_date_n(_10UV_select['time'], day, hour_str)
                _10UV_select.drop(columns = ['dtime','10U','10V'],inplace=True)
                _10UV_select.rename(columns={'time':'now_time'}, inplace = True)
                
                if basic_func.isFileExist(save_path):
                    df = pd.read_csv(save_path)
                    df = df.append(_10UV_select, ignore_index = True)
                    df = df.sort_values(by = ['now_time','predict_time'])
                    df = df.drop_duplicates(subset = ['predict_time'], keep='first')
                    df.to_csv(save_path, index=False)
                else:
                    cols = _10UV_select.columns
                    cols = ['now_time','predict_time','id','lon','lat','10UV']
                    _10UV_select = _10UV_select.loc[:,cols]
                    # cols.insert(0,cols.pop(cols.index('c')))
                    _10UV_select.to_csv(save_path, index=False)
   
"""
interpolate_MSL(file_path, file_name, ID_list, Longitude_raw, Latitude_raw) 对站点经纬度进行处理，求得A、B、C、D站点经纬度，再进行插值处理，求得最大的差值
:param: file_path: EC原始文件存放路径
:param: file_name: EC原始文件名
:param: ID_list: 需要处理的站点对应ID列表
:param: Longitude_list: 需要处理的站点对应的纬度列表
:param: Latitude_list: 需要处理的站点对应的经度列表
:return: 返回列名为time,dtime,id,lon,lat,MSL六列DataFrame
"""
def interpolate_MSL(file_path, file_name, ID_list, Longitude_raw, Latitude_raw):
    # process_df = copy.deepcopy(MSL_df)
    df=pd.DataFrame()
    # def interpolate_func(Station_Info, file_path, file_name_list, feature):
    A_Info = GetPositionDelta(ID_list, Longitude_raw, Latitude_raw,1)
    A_data = interpolate_func(A_Info, file_path, file_name,'MSL')
    B_Info = GetPositionDelta(ID_list, Longitude_raw, Latitude_raw,2)
    B_data = interpolate_func(B_Info, file_path, file_name, 'MSL')
    C_Info = GetPositionDelta(ID_list, Longitude_raw, Latitude_raw,3)
    C_data = interpolate_func(C_Info, file_path, file_name, 'MSL')
    D_Info = GetPositionDelta(ID_list, Longitude_raw, Latitude_raw,4)
    D_data = interpolate_func(D_Info, file_path, file_name, 'MSL')
    
    Longitude_list = basic_func.process_position(Longitude_raw,8)  #字符串长度为8
    Latitude_list = basic_func.process_position(Latitude_raw,7)  #字符串长度为8
    Station_Info = {"Station_ID":ID_list, "Longitude":Longitude_list, "Latitude":Latitude_list}  
    
    df = pd.DataFrame(Station_Info)
    # 将DataFrame格式转化为站点格式
    MSL_df = meb.sta_data(df,columns = ["id","lon","lat"])    
    meb.set_stadata_names(MSL_df,['MSL'])
    time_ymdh = "20"+file_name[0][0:8]
    dtime_str = file_name[0][9:12]
    datetime1 = meb.all_type_time_to_datetime(time_ymdh)
    meb.set_stadata_coords(MSL_df, time = datetime1, dtime=dtime_str)
    MSL_df.drop(columns = ['level'],inplace=True) 
    MSL_df["id"] = Station_Info["Station_ID"]           #将id的70改回字符F
    A_B = abs(A_data['MSL'] - B_data['MSL'])
    D_C = abs(D_data['MSL'] - C_data['MSL'])
    
    df['A-B']=A_B
    df['D-C']=D_C
    MSL_df['MSL']=df[['A-B','D-C']].max(axis=1)
    print(MSL_df)
    return MSL_df

"""
process_MSL(file_path, feature, ID_list, Longitude_list, Latitude_list) 将EC预测的未来10天的MSL数据存放在字典中
:param: file_path: EC原始文件存放路径
:param: feature: 特征 MSL
:param: ID_list: 需要处理的站点对应ID列表
:param: Longitude_list: 需要处理的站点对应的纬度列表
:param: Latitude_list: 需要处理的站点对应的经度列表
:return: dict  {'1天':DataFrame,'2天':DataFrame...,'10天':DataFrame} DataFrame 含time,dtime,id,lon,lat,MSL六列
"""         
def process_MSL(file_path, feature, ID_list, Longitude_list, Latitude_list):
    
    file_path = os.path.join(file_path, feature, '999')
    file_name_list = os.listdir(file_path)
    
    file_byDay = {}
    for file_name in file_name_list:
        suffix = int(file_name[9:12])
        if suffix == 0:
            continue
        if suffix % 24 == 0:
            day = int(suffix /24)
            day_str = str(day) + '天'
            if day_str not in file_byDay.keys():
                file_byDay[day_str] = []
            file_byDay[str(day) + '天'].append(file_name)
    print(file_byDay)
    data_byDay = {}
    for day_str in file_byDay:
       raw_file_list = file_byDay[day_str] 
       data_feature = interpolate_MSL(file_path, raw_file_list, ID_list, Longitude_list, Latitude_list)
       data_byDay[day_str] = data_feature
    return data_byDay

"""
save_MSL_local(ID_list, MSL_dict, file_save_path) 将EC预测得到未来10天的MSL，保存到本地指定位置
:param: ID_list: 需要处理的站点对应ID列表
:param: MSL_dict: 含EC预测未来10天的MSL
:param: MSL_dict:字典 {'1天':DataFrame, '2天':DataFrame.....}存放未来10天MSL预测值
:param: file_save_path: 处理后得到的MSL数据存放路径
:return: 无
"""
def save_MSL_local(ID_list, MSL_dict, file_save_path):
    basic_func.make_dir('./', 'EC_byID', 'ECbyID_dir', 'MSL')
    
    for day_str in MSL_dict.keys():
        MSL_df = MSL_dict[day_str]
        for ID in ID_list:
            MSL_select = MSL_df.loc[MSL_df['id'] == ID]
            MSL_select['time'] = MSL_select["time"].astype(str)
            if len(MSL_select) > 0:
                time = MSL_select['time'].values[0]
                hour_str = time[11:13]
                save_path = os.path.join(file_save_path, day_str, hour_str,  ID + '.csv')#'MSL',
                # if basic_func.isFileExist(save_path):
                #     df = pd.read_csv(save_path)
                #     df = df.append(MSL_select, ignore_index = True)
                #     df = df.sort_values(by = ['time'])
                #     df = df.drop_duplicates(subset = ['time'], keep='first')
                # MSL_select.to_csv(save_path, index=False)
                print(save_path)


"""
predict_date(file_path) 获取需要预测的日期
:param: file_path: EC原始数据存放路径
:return: 返回需要预测的日期
"""
def predict_date(file_path):
    
    file_path = os.path.join(file_path, '10U', '999')
    file_name_list = os.listdir(file_path)
    if len(file_name_list) == 0:
        print("无法获取需预测的日期")
        return None
    
    file_name = file_name_list[0]
    datestr = '20' + file_name[0:2] + '-' + file_name[2:4] + '-'+  file_name[4:6] + ' ' + file_name[6:8] + ":00:00"
    # str2date = datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")#字符串转化为date形式
    return datestr
    

"""
process_raw_EC_data(raw_file_path, ID_list, file_save_path) 对EC原始数据进行处理，并且存放在指定的本地路径
:param: raw_file_path: EC原始数据存放路径
:param: ID_list: 需要处理的站点对应ID列表
:param: file_save_path: EC数据写入路径
:return: 返回需要预测的日期
"""
def process_raw_EC_data(raw_file_path, ID_list, file_save_path): #,feature
    predict_ID = []
    predict_Longitude_raw = []
    predict_Latitude_raw = []
    for ID in ID_list:
        index = Station_ID_list.index(ID)
        predict_ID.append(ID)
        predict_Longitude_raw.append(Longitude_raw[index])
        predict_Latitude_raw.append(Latitude_raw[index])
    
    Station_Info = {"Station_ID":predict_ID, "Longitude":predict_Longitude_raw, "Latitude":predict_Latitude_raw}

    # _10U_dict = interpolate_other(raw_file_path, '10U', predict_ID, predict_Longitude_raw, predict_Latitude_raw)
    # _10V_dict = interpolate_other(raw_file_path, '10V', predict_ID, predict_Longitude_raw, predict_Latitude_raw)
    # save_10UV_local(ID_list, _10U_dict, _10V_dict, file_save_path)
    
    # MSL_dict = process_MSL(raw_file_path, 'MSL', predict_ID, predict_Longitude_raw, predict_Latitude_raw)    
    # save_MSL_local(ID_list, MSL_dict, file_save_path)
    
    datestr = predict_date(raw_file_path)
    return datestr
    
    
    

    
    

