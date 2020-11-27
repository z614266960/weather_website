# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 21:36:42 2020

@author: 61426
"""
import pandas as pd
from build_model import add_lstm,svr_model
def forecast(ID,predict_day,time,season,data,type):
    '''
    Parameters
    ----------
    ID : string
        要建模的站点
    predict_day : int
        要预测的天数
    time : string
        起报时间
    season : String
        季节
    -------
    Returns : dataframe
    预测结果
    '''
    
    
    obp_data = add_lstm.add_obp_by_one(ID,data,predict_day,time,type)
    predictions = svr_model.svr_predict(ID,obp_data,season,
                              predict_day,'08',type)
    
    return predictions[0]
    