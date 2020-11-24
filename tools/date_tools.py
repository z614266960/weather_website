# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 23:24:26 2020

@author: 61426
"""

def month_list(season):
    list = []
    if season=='3-4':
        list = ['03','04']
    elif season=='5-6':
        list = ['05','06']
    elif season=='7-9':
        list = ['07','09']
    elif season=='10-11':
        list = ['10','11']
    else:
        list = ['01','02','12']
    return list

def choose_season_by_month(month):
    if month>=3 and month<=4:
        return '3-4'
    elif month>=5 and month<=6:
        return '5-6'
    elif month>=7 and month<=9:
        return '7-9'
    elif month>=10 and month<=11:
        return '10-11'
    else:
        return '12-2'