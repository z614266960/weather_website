# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 23:30:04 2020

@author: 61426
"""


from build_model import forecast,svr_model,add_lstm

# add_lstm.add_obp('F2273','3-4',1,'08')
# svr_model.build_svr('F2273','3-4',1,'08')

data = forecast.forecast('F2273',1)
# print(data)