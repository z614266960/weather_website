# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:43:36 2020

@author: 86152
"""
from process_data import ob_func, EC_func

def Start_process_raw_data(ob_file_path, EC_file_path, Station_ID = None):
        
    if Station_ID is None:
        #为预测风速处理数据
        Station_list = ob_func.Process_raw_ob_data(ob_file_path) #ob_save_path
        date_list = EC_func.process_raw_EC_data(EC_file_path, Station_list) #EC_save_path
    else:
        #为跑SVR模型处理数据
        Station_list = ob_func.Process_raw_ob_data(ob_file_path) #ob_save_path
        Station_list = []
        Station_list.append(Station_ID)
        date_list = EC_func.process_raw_EC_data(EC_file_path,Station_list) #EC_save_path
    return Station_list, date_list