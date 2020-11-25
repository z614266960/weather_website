# -*- coding: utf-8 -*-
# from tools import json_tools

# 创建json
# =============================================================================
# json = {'ID_list' : ['F2286'],
#       'seasons' : ['3-4'],
#       'predict_days' : [1],
#       'times' : ['08']
#       }
# 
# json_tools.create_json(json)
# =============================================================================

# 读取json
# data = json_tools.read_json()

# ID_list = data['ID_list']
# seasons = data['seasons']
# predict_days = data['predict_days']
# times = data['times']

from process_data import data_process_func, merge_func, EC_func

# json = json_tools.read_json('config/record_wlf.json')
# ob_file_path = json['ob_file_path'][0]
# EC_file_path = json['EC_file_path'][0]

ob_file_path = './data\OB_raw_data'
EC_file_path = './data\EC_raw_data'
# Station_list, datestr = data_process_func.Start_process_raw_data(ob_file_path,EC_file_path)

# Station_list = ob_func.Process_raw_ob_data(ob_file_path)
# print(Station_list)
Station_list = ['F2273']#, 'F2286'
# EC_file_path = "./data/EC_raw_data"
# datestr = EC_func.process_raw_EC_data(EC_file_path, Station_list)

#拼接LSTM需要的全部的ob数据
# data = merge_func.data_for_LSTM(Station_list, '10FG6', '08')
#拼接SVR模型需要的数据
datestr = '2017-07-14 08:00:00'
datestr = '2015-07-14'
# merge_func.merge_data_for_SVR(Station_list, '10UV', datestr, '08')
# print(data)

from process_data import merge_func
data = merge_func.data_for_SVR(Station_list[0], '10UV', datestr, '08', str(2))
print(data)

# from build_model import lstm_model,add_lstm,svr_model
# # 创建lstm模型
# for ID in ID_list:
#     lstm_model.build_lstm(ID)

# # 添加obp
# for ID in ID_list:
#     for season in seasons:
#         for predict_day in predict_days:
#             for time in times:
#                 add_lstm.add_obp(ID, season, predict_day, time)
#                 svr_model.build_svr(ID, season, predict_day, time)

