# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
# from sklearn.externals import joblib
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score  # 交叉检验
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from tools import file_tools
# 中文显示
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']


def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def build_svr(ID,season,predict_day,time,type,data_path='data/obp/',
               models_save_path='models/svr/',
               images_save_path='images/svr/'):
    '''
    Parameters
    ----------
    ID : string
        要建模的站点
    season : string
        要建模的季节（3-4）
    predict_day : int
        要预测的天数
    time : string
        要预测的小时(08)
    data_path : string
        路径，用来训练svr的文件路径，包含10UV,msl,obp等特征
    models_save_path : string
        svr模型的保存路径
    images_save_path : string
        图片的保存路径
    Returns
    -------
    None.
    '''
    FILE_PATH = data_path+str(predict_day)+'天/'+season+'/'+time+'/'+type+'/'+ID+'_p.csv'
    
    orgin_data = pd.read_csv(FILE_PATH)
    
    # 分trian,test
    index = int(len(orgin_data)*0.9)
    columns_list = ['MSL',type,'ob_p']
    # x_train, x_test, y_train, y_test = train_test_split(orgin_data[columns_list], orgin_data['ob'], test_size=0.2,random_state=113)
    x_train = orgin_data[columns_list][:index]
    x_test = orgin_data[columns_list][index:]
    y_train = orgin_data['ob'][:index]
    y_test = orgin_data['ob'][index:]
    
    # 归一化
    min_max_scaler = MinMaxScaler()
    x_train_scaler = min_max_scaler.fit_transform(x_train)
    x_test_scaler = min_max_scaler.fit_transform(x_test)
    
    # 训练模型，并保存
    model = SVR(kernel='rbf')
    model.fit(x_train_scaler, y_train)
    model_save_path = models_save_path+season+'/'+str(predict_day)+'天/'+time+'/'+type+'/'
    file_tools.check_dir_and_mkdir(model_save_path)
    joblib.dump(model, model_save_path+ID+'.pkl')
    
    # 绘制训练Loss图
    # plot_learning_curves(model,x_train_scaler,y_train)
    
    predictions = model.predict(x_test_scaler)
    
    
    # 检查文件夹路径
    dir_path = images_save_path+ID+'/'
    file_tools.check_dir_and_mkdir(dir_path)
    
    # 画图
    X_label = []
    for i in range(predictions.shape[0]):
        X_label.append(i)
    plt.figure(figsize=(10,3))
    plt.plot(X_label, predictions,'r',label='预测结果')
    plt.plot(X_label, y_test,'black',label='理想结果')
    plt.plot(X_label, x_test[type],'g--',label='ec')
    plt.title(ID+' '+season+' '+str(predict_day))
    plt.legend()
    plt.savefig(dir_path+ID+'_'+season+'_'+str(predict_day)+'.png')
    # plt.show()

    
def svr_predict(ID,data,season,predict_day,time,type,models_save_path='models/svr/'):
    '''
    Parameters
    ----------
    ID : string
        要建模的站点
    data : dataframe
        成型的obp文件
    season : string
        要建模的季节（3-4）
    predict_day : int
        要预测的天数
    time : string
        要预测的小时(08)
    models_save_path : string
        svr模型的保存路径
    -------
    Returns : dataframe
    预测结果
    '''
    
    orgin_data = data
    
    columns_list = ['MSL',type,'ob_p']
    # x_train, x_test, y_train, y_test = train_test_split(orgin_data[columns_list], orgin_data['ob'], test_size=0.2,random_state=113)
    x = orgin_data[columns_list]
    
    # 归一化
    min_max_scaler = MinMaxScaler()
    x_train_scaler = min_max_scaler.fit_transform(x)
    
    # 加载模型
    model_save_path = models_save_path+season+'/'+str(predict_day)+'天/'+time+'/'+type+'/'+ID+'.pkl'
    model = joblib.load(model_save_path)
    
    predictions = model.predict(x)
    
    return predictions
