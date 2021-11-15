# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:19:35 2021

@author: infomax
"""

import pandas as pd
import pymysql
import datetime
import numpy as np
from tqdm import tqdm

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)


""" 만기일들 db에서 array안에 datetime이 들어가 있는 자료구조로 불러와 주는 함수"""
def getMaturityDays(date_start='2017-01-01', date_end=str(datetime.datetime.now())[:10], table='ktbf_lktbf_maturityday'):
    sql = "SELECT * FROM "+ table +" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    res =[]
    for item in result :
        res.append(item['date'])
    arr = np.array(res)
    return arr

def setDfData(date_start, date_end, table, skip_datetime_col="N") :
    sql = "SELECT * FROM "+ table +" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    df = pd.DataFrame(result)
    
    if skip_datetime_col == "Y":
        return df
    
    else:
        df['datetime'] = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
        
    #     df['datetime'] = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
    #     df.set_index('datetime', inplace=True)
    return df

def setRtData(asset="lktbf", dtype="vol", vol=100):
    if asset == "lktbf" and dtype == "vol":
        dftick = pd.read_excel("lktbf_rt.xlsx", header=3, usecols="A,B,C,D")
        dfrt = convertRtTickToVol(dftick, vol)
    elif asset == "ktbf3y" and dtype == "vol":
        dftick = pd.read_excel("ktbf3y_rt.xlsx", header=3, usecols="A,B,C,D")
        dfrt = convertRtTickToVol(dftick, vol)
        
    dfrt['datetime'] = pd.to_datetime(dfrt.date.astype(str) + ' ' + dfrt.time.astype(str))
    dfrt['close'] = dfrt['price']
        
    return dfrt

def convertRtTickToVol(dftick, vol_bin):
    
    dfbinned = pd.DataFrame(columns=['date','time','vwap','price'])
        
    vol_list = []
    prc_list = []
    
    i_resampled = 0
    
    for i in dftick.index:
        vol = dftick.at[i, '거래량']
        prc = dftick.at[i, '현재가']
            
        vol_list.append(vol)
        prc_list.append(prc)
        
        cumsum_vol = sum(vol_list)
        
        if cumsum_vol >= vol_bin:
            bins_made = int(cumsum_vol / vol_bin)
            leftover = cumsum_vol % vol_bin
            vol_list[-1] = vol_list[-1] - leftover
            vwap = sum(np.array(prc_list) * np.array(vol_list)) / (bins_made * vol_bin)
            
            for n in range(bins_made):
                dfbinned.at[i_resampled, 'vwap'] = vwap
                dfbinned.at[i_resampled, 'date'] = dftick.at[i, '일자']
                dfbinned.at[i_resampled, 'time'] = dftick.at[i, '시간']
                dfbinned.at[i_resampled, 'price'] = dftick.at[i, '현재가']
                i_resampled += 1
            
            vol_list = [leftover] #[0]이어도 무관
            prc_list = [prc]
        
        else:
            pass
        
    return dfbinned
    


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

def getDailyOHLC(start_date='2000-10-01',
                 end_date='2099-12-31',
                 market_table_name='lktbf_day'):
    """
    returns : 일봉 dataframe
    """
    df = setDfData(start_date, end_date, market_table_name, skip_datetime_col="Y")
    df.index = df.date
    df = df.drop(columns='date')
    
    return df

def getNdayOHLC(candle_end_date, n, table='lktbf_day'):
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
    df_ndays = setDfData(candle_start_date, candle_end_date, table)
    df_ndays.index = df_ndays.date

    return {'open': df_ndays.loc[candle_start_date]['open'],
            'high': max(df_ndays['high']),
            'low': min(df_ndays['low']),
            'close': df_ndays.loc[candle_end_date]['close']}
    
def getDdayOHLC(today=datetime.date, table='lktbf_day', dfmkt=None):
    """
    returns : 당일 OHLC dict
    """
    if dfmkt == None:
        dfmkt = getDailyOHLC(market_table_name=table)
    
    return {'open': dfmkt.loc[today]['open'],
            'high': dfmkt.loc[today]['high'],
            'low': dfmkt.loc[today]['low'],
            'close': dfmkt.loc[today]['close']}

def getYdayOHLC(today=datetime.date, table='lktbf_day', dfmkt=None):
    """
    returns : 전일 OHLC dict
    """
    if dfmkt == None:
        dfmkt = getDailyOHLC(market_table_name=table)
    
    yday = date_offset(today, -1)
    
    return {'open': dfmkt.loc[yday]['open'],
            'high': dfmkt.loc[yday]['high'],
            'low': dfmkt.loc[yday]['low'],
            'close': dfmkt.loc[yday]['close']}

def getMktTime(date=datetime.date):
    """
    returns : 장 시작시간 및 종료시간 리턴
    """
    dfmkt = setDfData(date,date,'lktbf_min')
    
    return {'start': datetime.time(dfmkt.datetime.iloc[0].time().hour, 0),
            'end': dfmkt.datetime.iloc[-1].time()}

def getNdayMovingAverage(today, n, asset='lktbf', option="close"):
    """

    Parameters
    ----------
    today : datetime.date
        전일종가까지로 계산한 n일의 이동평균을 계산하기 위한 관찰일
    n : 이동평균 window
    option : 
        "close" : 일반적인 이동평균가격
        "volume" : 평균거래량
        "hi_lo" : 고가저가 차이
        "open_close" : 시가종가 차이 절대값
        
    Returns
    -------
    n_day_average = {option}의 관찰일 이전 n일 평균

    """
    ma_start_date = date_offset(today, -n)
    df_daily = getDailyOHLC(ma_start_date, today, market_table_name=asset+'_day')
    
    if option == "close":
        ma = round(df_daily.close[:-1].mean(), 2)
    elif option == "volume":
        ma = int(df_daily.volume[:-1].mean())
    elif option == "hi_lo":
        ma = round((df_daily.high - df_daily.low)[:-1].mean(), 2)
    elif option == "open_close":
        ma = round((df_daily.close - df_daily.open).abs()[:-1].mean(), 2)
    
    return ma
    
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

def reportSummary(dfpl, show_hist="n"):
    """
    일별 손익('pl'컬럼)을 담고 있는 dataframe을 받아서 
     1. 요약 보고서를 출력 (히스토그램 포함)
     2. 월/연 손익 dataframe 리턴

    Parameters
    ----------
    dfpl : 일별 손익('pl'컬럼)을 담고 있는 dataframe
        
    Returns
    -------
    월별손익 dataframe
    연별손익 dataframe

    """
    
    # 히스토그램 출력
    if show_hist == "Y":
        dfpl.pl.hist(bins=int(max(0.25*len(dfpl.pl), 1)))
        
    dfpl.pl.fillna(value=0, inplace=True)
    # Annualized SR 출력
    annSR = round( dfpl.pl.mean() / dfpl.pl.std() * 250 / (250 ** 0.5), 2)
    print(f'Annualized SR : {annSR}')
    
    # dfpl의 index가 datetimeindex가 아니고 date 컬럼이 있으면
    if str(type(dfpl.index)) != "<class 'pandas.core.indexes.datetimes.DatetimeIndex'>" :
        if 'date' in dfpl.columns:
            dfpl.set_index(pd.to_datetime(dfpl.date), inplace=True)
            dfpl.drop(columns='date', inplace=True)
        else: 
            raise NameError('date column missing')
    # dfpl의 index가 datetimeindex인데, date column이 있으면 제거
    else:
        if 'date' in dfpl.columns:
            dfpl.drop(columns='date', inplace=True)
    
    
    # 월손익, 연손익 PL 자료 출력
    dfpl_mon = dfpl.groupby(by=[dfpl.index.year, dfpl.index.month]).agg({'pl':'sum', 'num_trade':'sum'})
    print(dfpl_mon)
    dfpl_yr = dfpl.groupby(by=[dfpl.index.year]).agg({'pl':'sum', 'num_trade':'sum'})
    print(dfpl_yr)
    
    return dfpl_mon, dfpl_yr
    
def stdTimeTable(date, db_table, look_back_days=20, yesterday=None):
    """
    look_back_days 기간동안의 시간대별 평균 cum_std를 담고 있는 table을 리턴
    freq : '10sec' or 'min'
    
    Returns
    -------
    freq 시간대별 cum_std Series
    
    """
    
    dfstd = pd.DataFrame(index=range(2430))
    
    print("Calculating std table")
    for i in tqdm(range(1, look_back_days+1)):
        if yesterday != None:
            d = yesterday
        else:
            d = date_offset(date, -i)
        refmkt = setDfData(d, d, db_table)
        if refmkt['time'].iloc[0] <= pd.Timedelta(hours=9, minutes=10):
            dfstd.loc[:, d] = refmkt['close'].expanding(1).std()
        
    init = pd.Timedelta(hours=9)
    t = []
    for i in range(2430) :
        init+=pd.Timedelta(seconds=10)
        t.append(init)
    T = pd.TimedeltaIndex(t)
    # T = pd.to_datetime(T.astype(np.int64)).time
    
    dfstd.set_index(T, inplace=True)
    
    return dfstd.mean(axis=1)


def apoStdRecent(date, db_table, K_FAST, K_SLOW, look_back_days=5, yesterday=None):
    
    apo_std_list = []
    print("Calculating recent APO std")
    for i in tqdm(range(1, look_back_days+1)):
        if yesterday != None:
            d = yesterday
        else:
            d = date_offset(date, -i)
        refmkt = setDfData(d, d, db_table)
        refdti = refmkt.index
        
        refmkt.at[refdti[0], 'ema_fast'] = refmkt.at[refdti[0], 'close']
        refmkt.at[refdti[0], 'ema_slow'] = refmkt.at[refdti[0], 'close']
        
        for refdti_pre, refdti_now in zip(refdti, refdti[1:]):
            last_prc = refmkt.loc[refdti_now,'close']
            
            refmkt.at[refdti_now, 'ema_fast'] = K_FAST * last_prc \
                + (1 - K_FAST) * refmkt.at[refdti_pre, 'ema_fast']
            
            refmkt.at[refdti_now, 'ema_slow'] = K_SLOW * last_prc \
                + (1 - K_SLOW) * refmkt.at[refdti_pre, 'ema_slow']
        
        diff_day = np.array(refmkt['ema_fast']) - np.array(refmkt['ema_slow'])
        
    apo_std_list.append(np.std(diff_day))
            
    return np.mean(apo_std_list)