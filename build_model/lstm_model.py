# -*- coding: utf-8 -*-

import pandas as pd
import numpy

import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM

from tools import file_tools

def create_dataset(dataset, look_back, look_after):
    """
    这里的look_back与timestep相同
    训练数据太少 look_back并不能过大
    ----------
    dataset : list
        数据集，要求只有一列真实值，即shape=(-1,1)
    look_back : int
        用过去多少个数据做参数
    look_after : int
        预测未来多少个数据
    ----------
        return:返回二维的两个数组
    """
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-look_after):
        a = dataset[i:(i+look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back:i + look_back+ look_after])
    return numpy.array(dataX),numpy.array(dataY)
    

def build_lstm(ID,data_path='data/lstm/',
               look_back=15,look_after=1,
               models_save_path='models/lstm/',
               images_save_path='images/lstm/'):
    """
    lstm建模
    ----------
    ID : string
        要建模的站点
    data_path : string
        路径，以站点为划分的所有ob数据，按日期排序
    look_back : int
        用过去多少个数据做参数
    look_after : int
        预测未来多少个数据
    models_save_path : string
        路径，lstm模型存放地点
    images_save_path : string
        路径，lstm模型，建模的图像存放地点
    ----------
    return:
        
    """
    FILE_PATH = data_path+ID+'.csv'
    MODEL_SAVE_PATH = models_save_path+ID+'_'+str(look_after)+'.h5'
    
    dataframe = pd.read_csv(FILE_PATH)
    dataframe.dropna(axis=0,inplace=True)
    dataset = dataframe['ob'].values
    # 将整型变为float
    dataset = dataset.astype('float64').reshape(-1,1)
    
    #归一化
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    
    train_size = int(len(dataset) * 0.8)
    trainlist = dataset[:train_size]
    testlist = dataset[train_size:]
    
    # 创建数据集
    trainX,trainY  = create_dataset(trainlist,look_back,look_after)
    testX,testY = create_dataset(testlist,look_back,look_after)
    
    #结果反归一化
    trainY[:,:,0] = scaler.inverse_transform(trainY[:,:,0])
    testY[:,:,0] = scaler.inverse_transform(testY[:,:,0])
    
    trainX = numpy.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
    testX = numpy.reshape(testX, (testX.shape[0], testX.shape[1] ,1 ))
    
    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(4, input_shape=(None,1)))
    model.add(Dense(look_after))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=16)
    file_tools.check_dir_and_mkdir(models_save_path)
    model.save(MODEL_SAVE_PATH)
    
    # make predictions
    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)
    
    # 保存图像
    file_tools.check_dir_and_mkdir(images_save_path)
    plt.figure(figsize=(10,3))
    plt.plot(trainY[:,look_after-1,0],'r')
    plt.plot(trainPredict[:,0],'g')
    plt.title(ID+'_train')
    plt.savefig(images_save_path+ID+'_train'+'.png')
    plt.show()
    plt.figure(figsize=(10,3))
    plt.plot(testY[:,look_after-1,0],'r')
    plt.plot(testPredict[:,0],'g')
    plt.title(ID+'test')
    plt.savefig(images_save_path+ID+'_test'+'.png')
    plt.show()
    
    # 评估
    from sklearn.metrics import mean_absolute_error
    my_mae = mean_absolute_error(testPredict[:,0],testY[:,look_after-1,0])
    print(ID+' '+'my_mae:'+str(my_mae))
    
    return 
    




