# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:06:13 2020

@author: 61426
"""

import os
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, escape, jsonify, make_response
from flask_cors import CORS
from flask import render_template

from build_model import lstm_model, add_lstm, svr_model, forecast
from process_data import data_process

app = Flask(__name__)
# 设置跨域
CORS(app, resources=r'/*')
@app.route('/index')
def index():
    return render_template('index.html')

# app.debug = True
@app.route('/build/lstm/view')
def build_lstm_view():
    return render_template('build_lstm_view.html')


# 接收lstm页面
@app.route('/build_lstm_data', methods=['POST'])
def build_lstm():
    id = request.form['id']
    time = request.form['time']
    type = request.form['type']
    dir = request.form['dir']
    # TODO 处理数据
    lstm_df = data_process.data_for_LSTM_model(id, time, type, dir)
    print(lstm_df)

    lstm_model.build_lstm(id, time, lstm_df)
    return 'ok'


# 进入建立svr页面
@app.route('/build/svr/view')
def build_svr_view():
    return render_template('build_svr_view.html')


# 接收svr参数
@app.route('/build_svr_data', methods=['POST'])
def build_svr():
    time = request.form['time']
    type = request.form['type']
    predict_day = request.form['predict_day']
    season = request.form['season']
    ec_dir = request.form['ec_dir']
    ob_dir = request.form['ob_dir']

    # TODO 处理数据
    # 调用改函数 处理ob EC原始数据
    data_process.data_for_SVR_model(id, time, type, ob_dir, ec_dir)
    # from process_data import merge_func
    # # dateslist = data_process_func.Start_process_raw_data(ob_dir, ec_dir,id)
    # # merge_func.merge_data_for_SVR(id, type, dateslist, time)
    # # SVR模型所需数据
    # merge_func.data_for_SVR_model(id, time, type, ob_dir, ec_dir)

    # 处理季节
    from process_data import obp
    obp.select_ec_merge_by_month(id, time, season, int(predict_day), type)

    add_lstm.add_obp(id, season, int(predict_day), time, type)
    svr_model.build_svr(id, season, int(predict_day), time, type)
    return 'ok'


# 进入预测页面
@app.route('/predict/view')
def predict_view():
    return render_template('forecast_new.html')


# 接收预测数据
@app.route('/predict', methods=['POST'])
def predict():
    id = request.form['id']
    time = request.form['time']
    type = request.form['type']
    predict_day = request.form['predict_day']
    ec_dir = request.form['ec_dir']
    ob_dir = request.form['ob_dir']
    # predict_date = request.form['predict_date']
    predict_date = '2015-07-14'
    predict_date = request.form['predict_date']
    svr_df, season = data_process.data_for_predict(id, time, type, predict_date, predict_day, ob_dir, ec_dir)

    print(svr_df)
    lstm_path = 'models/lstm' + '/' + time + '/' + id + '_1.h5'
    svr_path = 'models/svr' + '/' + season + '/' + str(
        predict_day) + '天' + '/' + time + '/' + type + '/' + id + '.pkl'
    if not os.path.exists(lstm_path):
        return jsonify('lstm模型为空')
    if not os.path.exists(svr_path):
        return jsonify('svr模型为空')

    predict = forecast.forecast(id, int(predict_day), time, season, svr_df, type)
    return jsonify(predict)


if __name__ == '__main__':
    app.run(threaded=True)
