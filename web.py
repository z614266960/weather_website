# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:06:13 2020

@author: 61426
"""

import os
from flask import Flask, flash, request, redirect, url_for, escape,jsonify,make_response
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)
# 设置跨域
CORS(app, resources=r'/*')


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

# 进入处理Ob数据页面
@app.route('/process/ob')
def process_ob():
    return render_template('process_ob.html')

param_dict = {}
# 获取处理ob数据的路径
@app.route('/process/ob/get_dir', methods=['GET', 'POST'])
def process_ob_get_dir():
    ob_dir = request.form['ob_dir']
    ec_dir = request.form['ec_dir']
    
    #处理ob EC原始数据
    from process_data import data_process_func
    Station_list, predict_date = data_process_func.Start_process_raw_data(ob_dir, ec_dir)

    global param_dict
    param_dict['Station_list'] = Station_list
    param_dict['predict_date'] = predict_date

    # return param_dict
    return render_template('build_models.html', param_dict = param_dict)

# 进入建立模型页面
@app.route('/build/models/view')
def build_models_view():
    return render_template('build_models.html', param_dict = param_dict)  #param_list = Station_list, param_date = predict_date

# 进入建立模型页面
@app.route('/build', methods=['POST'])
def build_models():
    id = request.form['id']
    time = request.form['time']
    season = request.form['season']
    predict_day = request.form['predict_day']
    model = request.form['model']
    
    # from process_data import merge_func
    # #id 预测的站点ID
    # #10UV 2分钟风速 10FG6 极大风速
    # #输入08 预测的是20时风速
    # #predict_day 1-10天
    # df_SVR = merge_func.data_for_SVR(id, '10UV', param_dict['predict_date'], '08', predict_day)
    # print(df_SVR)
    
    from build_model import lstm_model,add_lstm,svr_model
    if model=='all' or model=='lstm':
        lstm_model.build_lstm(id,time)
    if model=='all' or model=='svr':
        add_lstm.add_obp(id, season, int(predict_day), time)
        svr_model.build_svr(id, season, int(predict_day), time)   
    res = make_response('ok')
    return res


# 进入建立预测页面
@app.route('/forecast/view')
def forecast_view():
    return render_template('forecast.html')

@app.route('/forecast',methods=['POST'])
def forecast():
    id = request.form['id']
    time = request.form['time']
    predict_day = request.form['predict_day']
    print(id,time,predict_day)
    
    from build_model import forecast
    # TODO 测试季节先写死
    predict = forecast.forecast(id,int(predict_day),time,'3-4')
    json_data = jsonify(predict)
    res = make_response(json_data)
    return res


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/test/post',methods=['POST'])
def test_post():
    id = request.form['id']
    time = request.form['time']
    season = request.form['season']
    print(id,time,season)
    
    json_data = jsonify('ok')
    res = make_response(json_data)
    return res


if __name__ == '__main__':
    app.run(threaded=True)