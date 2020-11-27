# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:06:13 2020

@author: 61426
"""

import os
from flask import Flask, flash, request, redirect, url_for, escape,jsonify,make_response
from flask_cors import CORS
from flask import render_template

from build_model import lstm_model
app = Flask(__name__)
# 设置跨域
CORS(app, resources=r'/*')
# app.debug = True



# 进入建立lstm页面
@app.route('/build/lstm/view')
def build_lstm_view():
    return render_template('build_lstm_view.html')


# 接收lstm页面
@app.route('/build_lstm_data',methods=['POST'])
def build_lstm():
    id = request.form['id']
    time = request.form['time']
    type = request.form['type']
    dir = request.form['dir']
    
    # TODO 处理数据
    from process_data import merge_func
    lstm_df = merge_func.data_for_LSTM(id, time, type, dir)
    print(lstm_df)
    data = []
    
    lstm_model.build_lstm(id,time)
    return 'ok'

if __name__ == '__main__':
    app.run(threaded=True)