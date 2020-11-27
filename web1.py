# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:06:13 2020

@author: 61426
"""

import os
from flask import Flask, flash, request, redirect, url_for, escape,jsonify,make_response
from flask_cors import CORS
from flask import render_template

from build_model import lstm_model,add_lstm,svr_model
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
    data = []
    
    lstm_model.build_lstm(id,time,data)
    return 'ok'

# 进入建立svr页面
@app.route('/build/svr/view')
def build_svr_view():
    return render_template('build_svr_view.html')

# 接收svr参数
@app.route('/build_svr_data')
def build_svr():
    id = request.form['id']
    time = request.form['time']
    type = request.form['type']
    predict_day = request.form['predict_day']
    season = request.form['season']
    dir = request.form['dir']
    
    # TODO 处理数据
    data = []
    
    add_lstm.add_obp(id, season, int(predict_day), time)
    svr_model.build_svr(id, season, int(predict_day), time)  
    return 'ok'

if __name__ == '__main__':
    app.run(threaded=True)