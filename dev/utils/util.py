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
    sql = "SELECT * FROM "+ table +" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    df = pd.DataFrame(result)
    if datetime_col == "Y":
        df['datetime'] = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
        df.set_index('datetime', inplace=True)
        
    return df

def date_offset(ref_day, n=int):
    """
    parameter
        ref_day : offset시킬 날
        offset : offset
    returns : offset된 날짜
    """
    ld = list(getDailyOHLC().index)
    i = ld.index(ref_day)
    return ld[i+n]

""" table이 param으로 주어지면 해당 table에서 날자 리스트를 오름차순으로 뽑아주는 함수 """
def getDateList(table):
    df = setDfData('2000-10-01','2099-04-30', table)
    li = sorted(list(set(df['date'])))
    return li

def getDailyOHLC():
    """
    returns : 일봉 dataframe
    """
    df = setDfData('2000-10-01','2099-04-30', '`lktb1day`')
    df.index = df.date
    df = df.drop(columns='date')
    
    return df

def getNdayOHLC(candle_end_date, n):
    """
    candle_end_date를 포함한 n일의 OHLC를 구함
    Parameters
    ----------
    candle_end_date : datetime.date
        DESCRIPTION.
    days : 양의정수
        candle_end_date를 포함해서 며칠짜리 캔들인지

    Returns
    -------
    N-day candle

    """
    candle_start_date = date_offset(candle_end_date, -n+1)
    df_ndays = setDfData(candle_start_date, candle_end_date, '`lktb1day`')
    df_ndays.index = df_ndays.date

    return {'open': df_ndays.loc[candle_start_date]['open'],
            'hi': max(df_ndays['hi']),
            'lo': min(df_ndays['lo']),
            'close': df_ndays.loc[candle_end_date]['close']}
    
    
def getYdayOHLC(today=datetime.date, dfmkt=None):
    """
    returns : 전일 OHLC
    """
    if dfmkt == None:
        dfmkt = getDailyOHLC()
    
    yday = date_offset(today, -1)
    
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

