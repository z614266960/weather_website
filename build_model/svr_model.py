# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.externals import joblib
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


def build_svr(ID,season,predict_day,time,data_path='data/obp/',
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
    FILE_PATH = data_path+str(predict_day)+'天/'+season+'/'+time+'/'+ID+'_p.csv'
    
    orgin_data = pd.read_csv(FILE_PATH)
    
    # 相关矩阵
    # corr_matrix = orgin_data.corr()
    # print(corr_matrix["ob"].sort_values(ascending=False))
    
    # 分trian,test
    index = int(len(orgin_data)*0.8)
    columns_list = ['MSL','10UV','ob_p']
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
    model_save_path = models_save_path+season+'/'+str(predict_day)+'天/'+time+'/'
    file_tools.check_dir_and_mkdir(model_save_path)
    joblib.dump(model, model_save_path+ID+'.pkl')
    
    # 绘制训练Loss图
    # plot_learning_curves(model,x_train_scaler,y_train)
    
    predictions = model.predict(x_test_scaler)
    
    # 评估
    from sklearn.metrics import mean_absolute_error
    my_mae = mean_absolute_error(predictions,y_test)
    my_rmse = rmse(predictions,y_test)
    print('---------------'+str(predict_day)+'---------------')
    print('my_mae:'+str(round(my_mae,2)))
    print('my_rmse:'+str(round(my_rmse,2)))
    ec_mae = mean_absolute_error(x_test['10UV'],y_test)
    ec_rmse = rmse(x_test['10UV'],y_test)
    print('ec_mae:'+str(round(ec_mae,2)))
    print('ec_rmse:'+str(round(ec_rmse,2)))
    print('样本数量：'+str(len(orgin_data)))
    print('模型提升率:'+str(round((ec_rmse-my_rmse)/ec_rmse*100,4))+'%')
    
    
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
    plt.plot(X_label, x_test['10UV'],'g--',label='ec')
    plt.title(ID+' '+season+' '+str(predict_day))
    plt.legend()
    plt.savefig(dir_path+ID+'_'+season+'_'+str(predict_day)+'.png')
    plt.show()

    