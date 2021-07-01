# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 07:55:22 2020

@author: infomax
"""

import pandas as pd
import sys
sys.path.append('c:/pywork/DDT_lib')
sys.path.append('d:/pywork/DDT_lib')
sys.path.append('d:/pywork/DDT(4)PR')
import ddt_util as du
import pr_util as pu
import loadmkt

""""""""""""""""""""""""""""""""""""""""""""""""
"""AUCTION"""
""""""""""""""""""""""""""""""""""""""""""""""""
df10 = loadmkt.read_ktb10y()
df3 = loadmkt.read_ktb3y()

dfktbsp = loadmkt.read_ktbsp()
# dfhanmi = loadmkt.read_hanmi()

ld_all = du.get_date_list(df10)

#%%
from datetime import datetime
timenote = datetime.now().strftime("%Y/%m/%d, %H:%M")

CASE = "AUCT30"

PREV_NUM = -5
NEXT_NUM = 5
OFFSET = 1
NUMPLOT = 6

df10 = loadmkt.update_futures_rt(df10, fut_name='10y')
df3 = loadmkt.update_futures_rt(df3, fut_name='3y')
dfktbsp = loadmkt.update_futures_rt(dfktbsp, fut_name='sp')


# dates = du.read_casedates(CASE, "KR", nth_in_year=[1] )[:7] #매년 첫 입찰
dates = du.read_casedates(CASE, "KR", )[:NUMPLOT] #최근 입찰


dates = du.date_offset_list(ld_all, dates, OFFSET)
# dates += [pd.Timestamp(2021,4,19)]
dates = du.remove_yyyymm(dates, [202002, 202003, 202004,]) #코로나 변동월 제거
# dates = du.select_months(dates, [1,2,3,4])
# dates = dates[:7] + du.select_months(dates, [1])[1:]
# dates = du.select_years(dates, [2015, 2016, 2017, 2019, 2020])

# dates = dates[:5]

pu.plot_multly(df10, dates, CASE+" LKTB "+timenote, PREV_NUM, NEXT_NUM, shift=0)

pu.plot_multly(df3, dates, CASE+" KTBF3Y "+timenote, PREV_NUM, NEXT_NUM)
pu.plot_multly(dfktbsp, dates, CASE+" SP "+timenote, PREV_NUM, NEXT_NUM)
# pu.plot_multly(dfhanmi, dates, CASE+" HANMI "+timenote, PREV_NUM, NEXT_NUM)
