# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 21:36:42 2020

@author: 61426
"""
import pandas as pd
import datetime
from build_model import add_lstm,svr_model
from tools import date_tools
def forecast(ID,predict_day):
    '''
    Parameters
    ----------
    ID : string
        要建模的站点
    predict_day : int
        要预测的天数
    -------
    Returns : dataframe
    预测结果
    '''
    # 假装有数据
    data = pd.read_csv('E:\F2273.csv');
    data = data[0:1]
    
    obp_data = add_lstm.add_obp_by_one(ID,data,predict_day)
    predictions = svr_model.svr_predict(ID,obp_data,date_tools.choose_season_by_month(datetime.datetime.now().month),
                              predict_day,'08')
    
    return predictions[0]
    