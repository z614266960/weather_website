# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 21:25:37 2020

@author: 86152
"""
import pandas as pd
import ob_func as ob_func
import EC_func as EC_func
import merge_func as merge_func

# 实况原始数据处理
ob_file_path = 'E:\data\OB_raw_data'
ob_save_path = './实况数据'
'''
Process_raw_ob_data(file_path) 处理站点的原始实况数据，保存在指定目录下，并返回需要预测站点ID列表
:param raw_file_path: 原始的实况数据存放路径
:param save_file_path: 处理后的实况数据存放路径
:return: 返回需要预测的站点列表
'''
Station_list = ob_func.Process_raw_ob_data(ob_file_path, ob_save_path)
print(Station_list)
# Station_list = ['F2273', 'F2286']

# EC原始数据处理
EC_file_path = 'E:\data\EC_raw_data'
EC_save_path = './EC_byID'
"""
process_raw_EC_data(raw_file_path, ID_list, file_save_path) 根据提供的站点ID列表，从原始EC的数据中提取相应的数据，处理后得到10UV以及MSL
:param: raw_file_path: 原始EC存放的路径
:param: ID_list: 需要处理的站点ID列表
:param: file_save_path: 处理后的EC数据存放路径
:return: 返回需要预测的日期
"""
datestr = EC_func.process_raw_EC_data(EC_file_path, Station_list, EC_save_path)

#拼接LSTM需要的全部的ob数据
data = merge_func.data_for_LSTM(Station_list, '10FG6', '08')
#拼接SVR模型需要的数据
datestr = '2017-07-14 08:00:00'
# data = merge_func.data_for_SVR(Station_list, '10UV', datestr, '20')
# print(data)




# 创建文件夹
# basic_func.make_dir('./', '实况数据', 'ob_dir', None)
# feature_list = ['10UV', 'MSL','10FG6'] #
# for feature in feature_list:
#     basic_func.make_dir('./', 'EC数据', 'EC_dir', feature)
    # basic_func.make_dir('./', 'EC_byID', 'ECbyID_dir', feature)
    # basic_func.make_dir('./', 'EC_OB_merge', 'merge_dir', feature)

# basic_func.make_dir('./', 'test', 'ECbyID_dir', '10UV')



