# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 17:20:12 2020

@author: 61426
"""


import pandas as pd
from tools import date_tools,file_tools

def select_ec_merge_by_month(ID,time,season,predict_day,type,file_path='./data/ob_EC_merge',
                             save_path='./data/last_15_days'):
    file = file_path+'/'+str(predict_day)+'天'+'/'+time+'/'+type+'/'
    save = save_path+'/'+str(predict_day)+'天'+'/'+season+'/'+time+'/'+type+'/'
    
    file_tools.check_dir_and_mkdir(file)
    file_tools.check_dir_and_mkdir(save)
    
    orign_data = pd.read_csv(file+ID+'.csv')
    orign_data = orign_data.loc[orign_data['predict_time'].apply(lambda x :x[5:7] in date_tools.month_list(season))]
    orign_data = orign_data.dropna(axis=0)
    orign_data.to_csv(save+ID+'.csv',index=False)