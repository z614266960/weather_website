# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:43:36 2020

@author: 86152
"""
from process_data import merge_func
from process_data import word_func


# lstm模型所用数据
def data_for_LSTM_model(Station_ID, hour, feature, ob_raw_file_path):
    lstm_df = merge_func.data_for_LSTM_model(Station_ID, hour, feature, ob_raw_file_path)
    return lstm_df


# SVR模型所用数据
def data_for_SVR_model(Station_ID, hour, feature, ob_raw_file_path, ec_raw_file_path):
    merge_func.data_for_SVR_model(Station_ID, hour, feature, ob_raw_file_path, ec_raw_file_path)


# 预测风速所用数据
def data_for_predict(Station_ID, hour, feature, nowtime, predict_day, ob_raw_file_path, ec_raw_file_path):
    svr_df, season = merge_func.data_for_predict(Station_ID, hour, feature, nowtime, predict_day, ob_raw_file_path,
                                                 ec_raw_file_path)
    return svr_df, season


# 生成本地word报文
def generate_word9(predict_df):
    word_func.generate_word_local(predict_df)