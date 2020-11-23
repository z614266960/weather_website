# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 12:12:14 2020

@author: 61426
"""


import os

def check_dir_and_mkdir(dir_path):
    """
    检查文件是否存在，如不存在则创建
    ----------
    dir_path : string
        路径，要检测文件夹路径
    """
    if(os.path.exists(dir_path)):
        print(dir_path,'路径存在')
    else:
        os.makedirs(dir_path);
        print(dir_path,'路径不存在，现已创建')