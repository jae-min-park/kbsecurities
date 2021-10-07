# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 13:19:48 2021

@author: infomax
"""

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import datetime
import os
from tqdm import tqdm
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util
import tradeLoi as tl


def afternoonFall_ema(date, db_table, af_config, plot="Y"):
    """
    오후 저가 갱신하는 경우 추격매도하는 모멘텀 트레이딩
    
    발동조건
        1. 시간조건, 오후 2pm or ?
        2. 현재가 < 이전 저가
        3. SHORT by ema, 약세분위기 감지용
        
    진입후 매매조건
        1. 최초 SHORT진입 후 ema 방식을 따름
        2. 반대시그널에 청산, 숏시그널 재진입, 종가까지

    Parameters
    ----------
    date : datetime.date
        테스트 대상 날짜
    db_table : str
        test하는 db_table명. ex) 'lktbf100vol'
    plot : "Y" 테스트날의 차트 플로팅

    Returns
    -------
    bangla = {'is_triggered': False,
              'is_traded': False,
              'trade_price': None,
              'trade_time': None,
              'trade_local_index': None,
              'pl': None}
   
    """
    
    if db_table[:3] == 'lkt':
        product = 'lktbf'
    elif db_table[:3] == 'ktb':
        product = 'ktbf'
    elif db_table[:3] == 'usd':
        product = 'usdkrw'
        
    day_table = product + '_day'
    
        
        
    trading_begins_after = af_config['trading_begins_after']
    trading_begins_after_index = None
    trading_begins_before = af_config['trading_begins_before']
    
    #ema coeffs
    fast_coeff = af_config['ema_fast_coeff']
    slow_coeff = af_config['ema_slow_coeff']
    ema_margin = af_config['ema_margin']
    
    #장중저가 하향돌파 margin(틱), +2 --> 장중저가보다 2틱 아래를 돌파로 가정
    thru = af_config['thru']
        
    dfmkt = util.setDfData(date, date, db_table)
    
    #local index
    dti = dfmkt.index
    
    #종가시간 정의
    close_time = dfmkt['datetime'].iloc[-1].time()
    
    #초기세팅
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    intra_lo = +99999
    intra_hi = -99999
    
    max_gain = -9999
    max_loss = 9999
    
    bangla = {'is_triggered': False,
              'trade_list': [],
              'trade_direction_list': [],
              'trade_price_list': [],
              'trade_time_list': [],
              'trade_local_index_list': [],
              'pl_list': []
              }
    
    #초기상태에 대한 정의 필요
    prev_status = "attached"
    
    """
    vwap index기준 test loop시작
    """
    for dti_pre, dti_now in zip(dti, dti[1:]):
        
        # 현재시간
        now = dfmkt.at[dti_now, 'datetime'].time()
        
        # 현재가
        vwap = dfmkt.loc[dti_now,'vwap']
        close_price = dfmkt.loc[dti_now,'close']
        
        # ema 기록
        dfmkt.at[dti_now, 'ema_fast'] = fast_coeff * vwap + (1-fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
        dfmkt.at[dti_now, 'ema_slow'] = slow_coeff * vwap + (1-slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
        
        # cross test 결과 
        tested_status = tl.crossTest(dfmkt.at[dti_now, 'ema_fast'], 
                                     dfmkt.at[dti_now, 'ema_slow'], 
                                     margin = ema_margin)
        
        
               
        # 트리거는 됐는데 매매는 아직 실행전이면 최초 매매(short) data 저장
        if bangla['is_triggered'] == True and len(bangla['trade_list']) == 0:
            # 최초 매매니까 'short'를 추가해줌
            bangla['trade_list'].append('short')
            bangla['trade_direction_list'].append(-1)
            bangla['trade_price_list'].append(vwap)
            bangla['trade_time_list'].append(now)
            bangla['trade_local_index_list'].append(dti_now)
            bangla['pl_list'].append(0)
        
        # 트리거되고 최초매매도 기록한 이후의 본격적인 매매 영역
        elif len(bangla['trade_list']) != 0:
            
            # cross 상태가 above 또는 below에서 attached로 바뀌면 이전상태 attached로 변경
            if (prev_status == "above" or prev_status == "below") and tested_status == "attached":
                prev_status = tested_status
            
            # cross 상태 변화 없으면 아무것도 안하고 pass
            elif prev_status == tested_status:
                pass
            
            # cross 상태가 유의미하게 변화
            # 즉, attahced -> above/below 또는 below/above -> above/below
            # 이 조건은 위의 두 경우를 제외한 나머지 이므로 else 사용 가능
            else: 
                # print(prev_status, tested_status)
                prev_status = tested_status
                
                # last trade가 short & 현재가 > intra_lo & long signal 나온 경우 -> cover
                if bangla['trade_list'][-1] == 'short' and tested_status == 'above':
                    if product == 'ktbf' or product == 'lktbf':
                        #틱단위 표시
                        pl_from_last = round(100*(bangla['trade_price_list'][-1] - vwap), 1)
                    elif product == 'usdkrw':
                        #틱단위 표시
                        pl_from_last = round(10*(bangla['trade_price_list'][-1] - vwap), 1)
                    else:
                        raise NameError('Unexpected product')
                    
                    bangla['trade_list'].append('covered')
                    bangla['trade_direction_list'].append(1)
                    bangla['trade_price_list'].append(vwap)
                    bangla['trade_time_list'].append(now)
                    bangla['trade_local_index_list'].append(dti_now)
                    bangla['pl_list'].append(pl_from_last)
                    
                # last trade가 covered 인데 short signal 나온 경우 -> 매매기록, PL은 0 기록
                elif bangla['trade_list'][-1] == 'covered' and tested_status == 'below':
                    
                    bangla['trade_list'].append('short')
                    bangla['trade_direction_list'].append(-1)
                    bangla['trade_price_list'].append(vwap)
                    bangla['trade_time_list'].append(now)
                    bangla['trade_local_index_list'].append(dti_now)
                    bangla['pl_list'].append(0)
                
        # timely 체크하는 것들
        # 매매시간대 이전 준비단계
        # 장중 저가 및 고가 기록
        if now < trading_begins_after:
            intra_lo = min(intra_lo, vwap)
            intra_hi = max(intra_hi, vwap)
        
        # 매매시간대 들어감, 최초 진입조건 탐색
        elif now >= trading_begins_after and now < trading_begins_before:
            # 매매시간대 시작점 local index 기록
            if trading_begins_after_index == None:
                trading_begins_after_index = dti_now
            # 최초진입조건 만족시 trigger상태만 변경해줌
            if vwap < (intra_lo - thru/100) and tested_status == "below":
                bangla['is_triggered'] = True
        
        # 종가청산 only if (trading 있다) and (포지션이 열린)
        elif now >= close_time and len(bangla['trade_list']) != 0:
            if bangla['trade_list'][-1] == 'short':
                if product == 'ktbf' or product == 'lktbf':
                    # 틱단위 표시
                    pl_from_last = round(100*(bangla['trade_price_list'][-1] - vwap), 1)
                elif product == 'usdkrw':
                    #틱단위 표시
                    pl_from_last = round(10*(bangla['trade_price_list'][-1] - vwap), 1)
                else:
                    raise NameError('Unexpected product')
                    
                bangla['trade_list'].append('covered')
                bangla['trade_direction_list'].append(1)
                bangla['trade_price_list'].append(vwap)
                bangla['trade_time_list'].append(now)
                bangla['trade_local_index_list'].append(dti_now)
                bangla['pl_list'].append(pl_from_last)
                
    """
    test loop 끝
    """
    
    
    """
    PLOT
    """
    if len(bangla['trade_list']) !=0 and plot == "Y":
            
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(1,1,1)
        
        for i, trade_index in enumerate(bangla['trade_local_index_list']):
            marker = "v" if bangla['trade_list'][i] == 'short' else "^"
            color = "b" if marker == "v" else "tab:red"
                    
            ax.scatter(trade_index,
                       bangla['trade_price_list'][i],
                       color=color, 
                       marker=marker, 
                       s=300)
        
        plt.plot(dti, dfmkt['vwap'])
        plt.plot(dti, dfmkt['ema_fast'])
        plt.plot(dti, dfmkt['ema_slow'])
        
        # 매매시작시간 V-line
        plt.axvline(x=trading_begins_after_index)
        
        # 장중 저가 H-line
        plt.axhline(y=intra_lo, color='r', linestyle='dashed')
        
        # 전일종가 H-line
        yday_close = util.getYdayOHLC(date, table=day_table)['close']
        plt.axhline(y=yday_close, color='black', linestyle='dashed')
        
        # 20일이평 H-line
        # ma_20 = util.getNdayMovingAverage(date, 20, asset=product)
        # plt.axhline(y=ma_20, color='black', linestyle='-')

        font = {'family': 'verdana',
                'color':  'darkblue',
                'weight': 'bold',
                'size': 16}
        
        plot_name = str(date)+ ' |   P&L : ' + str(bangla['pl_list']) + str(round(sum(bangla['pl_list']),1))
        ax.set_xlabel(plot_name, fontdict=font)
        plt.show()
    """
    PLOT 끝
    """
    
    return bangla


#%% BTST

#일봉기준 전체 date list
ld = list(util.getDailyOHLC().index)
# ld = [d for d in ld if d.year == 2021 and d.month == 3]
# ld = [d for d in ld if d.year>=2017]
ld = [d for d in ld if d == datetime.date(2021,10,6)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])

# ld = list(pd.read_excel("AF_loss_days.xlsx").date)

#장중저가 하향돌파 margin(틱), +2 --> 장중저가보다 2틱 아래를 돌파로 가정
af_config = {'trading_begins_after': datetime.time(12,15,0),
             'trading_begins_before': datetime.time(15,15,0),
             'ema_fast_coeff': 0.30,
             'ema_slow_coeff': 0.10,
             'thru': 0.5,
             'ema_margin': 0.5
             }


for i, day in enumerate(ld):
    if str(type(day)) == "<class 'pandas._libs.tslibs.timestamps.Timestamp'>":
        day = day.date()
    
    bangla = afternoonFall_ema(day, af_config=af_config, db_table='lktbf100vol', plot="Y")
    
    dfpl.at[i, 'date'] = day
    
    pl_of_the_day = round(sum(bangla['pl_list']),1)
    dfpl.at[i, 'pl'] = pl_of_the_day
    
    num_trade = 1 if len(bangla['trade_list']) != 0 else 0
    dfpl.at[i, 'num_trade'] = num_trade
    
    #당일의 결과
    print(f'Day   | {day}    pl= {pl_of_the_day},  {num_trade}')
    
    #누적결과
    cumsum = round(dfpl.pl.sum(), 1)
    mean = round(dfpl.pl.mean(), 2)
    std = round(dfpl.pl.std(), 3)
    sr = round(mean / std, 3)
    num_trade_cumul = dfpl.num_trade.sum()
    print(f'Cumul | cumsum: {cumsum}  mean:{mean}  SR: {sr}  trades: {num_trade_cumul}',
          "\n---------------------------------------------------------------")

#결과 출력및 저장
pl_mon, pl_yr = util.reportSummary(dfpl)

