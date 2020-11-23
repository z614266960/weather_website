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
    return ob_dir+'   '+ec_dir
