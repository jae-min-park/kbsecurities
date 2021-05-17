# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:19:35 2021

@author: infomax
"""

import pandas as pd
import pymysql
import datetime

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

# df_sample = pd.read_excel('reshape_real_1d.xlsx')


def setDfData(date_start, date_end, table, datetime_col="N") :
    sql = "SELECT * FROM "+ table +"where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    df = pd.DataFrame(result)
    if datetime_col == "Y":
        df['datetime'] = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
        
    return df

def date_offset(ld, ref_day, n=int):
    """
    parameter
        ld : 시장 영업일 리스트
    returns : n만큼 offset 날짜
    """
    i = ld.index(ref_day)
    return ld[i+n]

def getDailyOHLC():
    """
    returns : 일봉 dataframe
    """
    df = setDfData('2000-10-01','2099-04-30', '`lktb1day`')
    df.index = df.date
    df = df.drop(columns='date')
    
    return df

    
def getYdayOHLC(today=datetime.date, dfmkt=None):
    """
    returns : 전일 OHLC
    """
    if dfmkt == None:
        dfmkt = getDailyOHLC()
    
    ld = list(dfmkt.index)
    yday = date_offset(ld, today, -1)
    
    return {'open': dfmkt.loc[yday]['open'],
            'hi': dfmkt.loc[yday]['hi'],
            'lo': dfmkt.loc[yday]['lo'],
            'close': dfmkt.loc[yday]['close']}


def getPriceYdayMostTraded(dfmkt, today):
    
    """
    returns : 어제의 최빈도 거래가격
    """
    pass

def getPriceTodayMostTraded(dfmkt, today):
    
    """
    returns : 오늘 현재까지의 최빈도 거래가격
    """
    pass

