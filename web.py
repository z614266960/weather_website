# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:06:13 2020

@author: 61426
"""

import os
from flask import Flask, flash, request, redirect, url_for, escape

from flask import render_template

app = Flask(__name__)
    
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

# 进入处理Ob数据页面
@app.route('/process/ob')
def process_ob():
    return render_template('process_ob.html')

# 获取处理ob数据的路径
@app.route('/process/ob/get_dir', methods=['GET', 'POST'])
def process_ob_get_dir():
    ob_dir = request.form['ob_dir']
    ec_dir = request.form['ec_dir']
    return ob_dir,ec_dir

# 进入建立模型页面
@app.route('/build/models/view')
def build_models_view():
    return render_template('build_models.html')

# 进入建立模型页面
@app.route('/build', methods=['GET', 'POST'])
def build_models():
    id = request.form['id']
    time = request.form['time']
    season = request.form['season']
    predict_day = request.form['predict_day']
    model = request.form['model']
    
    from build_model import lstm_model,add_lstm,svr_model
    if model=='all' or model=='lstm':
        lstm_model.build_lstm(id)
    if model=='all' or model=='svr':
        add_lstm.add_obp(id, season, predict_day, time)
        svr_model.build_svr(id, season, predict_day, time)   
    return ''+id+time+predict_day+model




if __name__ == '__main__':
    app.run()