# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 12:06:19 2021

@author: infomax
"""
from tqdm import tqdm
import ddt_util
import dataManager 
import datetime
import pymysql
import pandas as pd
import plotManager as pm

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                          # host = '211.232.156.57',
                          host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

"""
일단 기본 ohlc sql통해 날자값 안으로 df받아오기
"""
dfm = dataManager.DataFrameManager(cursor)
dt_start = pd.Timestamp(year=2018, month = 3, day = 2)
dt_end = pd.Timestamp(year=2021, month = 4, day = 6)
dfm.setDfData(dt_start, dt_end)
df = dfm.df

"""
기본 df에 대해 day_ohlc 및 캔들 데이터들 df에 추가로 받아오기
"""
date_set = ddt_util.get_date_list(df)
df_candle = pd.DataFrame(columns=dfm.df.columns)
for date in tqdm(date_set) :
    tempDf = dfm.df[dfm.df['date'] == date]
    tempDf = dfm.getCandleValueDf(tempDf)
    df_candle = df_candle.append(tempDf)

"""
전략을 위한 column 추가한 df 만들기
"""
df_candle['gravePattern'] = False
df_candle['reboundPattern'] = False
df_candle['declinePattern'] = False

df_strategy = pd.DataFrame(columns=df_candle.columns)
for i,date in enumerate(date_set) :
    pre_date_close = 9999
    if i > 0 :
        tmpDf = df_candle[df_candle['date'] == date_set[i-1]]
        pre_date_close = tmpDf.iloc[-1]['close']
        # print(tmpDf.iloc[-1][['date', 'time', 'close']])
    
    tempDf = df_candle[df_candle['date'] == date]
    tempDf = dfm.getGraveStoneAndReboundValueDf(tempDf, pre_date_close)
    df_strategy = df_strategy.append(tempDf)



"""
전략을 만족하는 날자를 확인하기 위한 print
"""
print(df_strategy[df_strategy.gravePattern])
print(df_strategy[df_strategy.reboundPattern])
print(df_strategy[df_strategy.declinePattern])
pm.plot(df, df_strategy[df_strategy.declinePattern].index)


# """
# DB에 백테스트용 데이타들 삽입
# """
# dfm.insertExcelData(cursor)
# test_db.commit()




