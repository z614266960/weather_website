# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 23:30:04 2020

@author: 61426
"""


from build_model import forecast,svr_model,add_lstm

# add_lstm.add_obp('F2273','3-4',1,'08')
# svr_model.build_svr('F2273','3-4',1,'08')

# data = forecast.forecast('F2273',1)
# print(data)


id = 'F2273'
time = '08'
type = '10UV'
predict_day = '1'
season = '3-4'
ec_dir = '/Users/xiaoyilei/Desktop/EC_raw_data'
ob_dir = '/Users/xiaoyilei/Desktop/ob_raw_data'
from process_data import data_process
# TODO 处理数据
# 调用改函数 处理ob EC原始数据
data_process.data_for_SVR_model(id, time, type, ob_dir, ec_dir)