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

def afternoonFall(date, db_table, af_config, method="simple", plot="Y"):
    """
    오후 저가 갱신하는 경우 추격매도하는 모멘텀 트레이딩
    
    발동조건
        1. 시간조건, 오후 2pm or ?
        2. 현재가 < 이전 저가
        3. SHORT by ema, 약세분위기 감지용
    

    Parameters
    ----------
    date : datetime.date
        테스트 대상 날짜
    db_table : str
        test하는 db_table명. ex) 'lktbf100vol'
    plot : "Y" 테스트날의 차트 플로팅

    Returns
    -------
    bangla 
   
    """
    
    if db_table[:3] == 'lkt':
        product = 'lktbf'
        product_multiplier = 100
    elif db_table[:3] == 'ktb':
        product = 'ktbf'
        product_multiplier = 100
    elif db_table[:3] == 'usd':
        product = 'usdkrw'
        product_multiplier = 10
    
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
    
    #초기세팅
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    intra_lo = +99999
    intra_hi = -99999
    
    bangla = {'is_triggered': False,
                    'is_traded': False,
                    'trade_price': None,
                    'trade_time': None,
                    'trade_local_index': None,
                    
                    'is_losscut_triggered': False,
                    'is_losscut_traded': False,
                    'losscut_price': None,
                    'losscut_time': None,
                    'losscut_local_index': None,
                    
                    'is_pt_triggered': False,
                    'is_pt_traded': False,
                    'pt_price': None,
                    'pt_time': None,
                    'pt_local_index': None,
                    
                    'pl': None,
                    'max_gain': None,
                    'max_gain_price': None,
                    'draw_down': None,
                    
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
                                     margin=ema_margin)
        
        # 매매정보입력 및 PL 계산
        # 트리거는 됐는데 매매는 아직 실행전
        if bangla['is_triggered'] == True and bangla['is_traded'] == False:
            bangla['trade_price'] = vwap
            bangla['trade_time'] = now
            bangla['trade_local_index'] = dti_now
            bangla['is_traded'] = True
            # max_gain 초기화
            bangla['max_gain'] = -9999
        
        # losscut 발동, losscut 실행전
        elif bangla['is_losscut_triggered'] == True and bangla['is_losscut_traded'] == False:
            bangla['losscut_price'] = vwap
            bangla['losscut_time'] = now
            bangla['losscut_local_index'] = dti_now
            bangla['is_losscut_traded'] = True
            bangla['pl'] = round(product_multiplier*(bangla['trade_price'] - bangla['losscut_price']), 1)
            break
        
        # profit-taking 발동, pt실행전
        elif bangla['is_pt_triggered'] == True and bangla['is_pt_traded'] == False:
            bangla['pt_price'] = vwap
            bangla['pt_time'] = now
            bangla['pt_local_index'] = dti_now
            bangla['is_pt_traded'] = True
            bangla['pl'] = round(product_multiplier*(bangla['trade_price'] - bangla['pt_price']), 1)
            break

        # 매매실행이후 PL 관련 처리, 종가PL도 아래에서 동일하게 처리
        elif bangla['is_triggered'] == True and bangla['is_traded'] == True:
            # 일상적 PL 기록
            bangla['pl'] = round(product_multiplier * (bangla['trade_price'] - close_price), 1)
            
            # max gain 기록
            if bangla['pl'] > bangla['max_gain']:
                bangla['max_gain'] = bangla['pl']
                bangla['max_gain_price'] = close_price
            
            # draw down 기록
            if abs(bangla['max_gain']) > 0:
                bangla['draw_down'] = 1 - bangla['pl'] / bangla['max_gain']
            else:
                bangla['draw_down'] = 0
                
            # print(now, bangla['max_gain'], bangla['pl'], bangla['draw_down'])
            
            # 손절 로직1 : 매매발동전 관찰기간중 고가-저가의 ???% 폭만큼 반등하면 손절 트리거
            # 손절 로직2 : 30틱
            # 1 or 2 만족시 손절
            bool_lc_intra_hilo = bangla['pl'] < -product_multiplier * af_config['lc_hi-lo'] * (intra_hi - intra_lo)
            bool_lc_pl = bangla['pl'] < af_config['lc_pl'] #틱환산 했으므로 product_multiplier 적용안함
            if bool_lc_intra_hilo or bool_lc_pl:
                bangla['is_losscut_triggered'] = True
                
            # 익절 로직1 : max_gain이 ??틱 이상
            # 손절 로직2 : max_gain의 ??%만큼의 draw_down 발생
            # 1 and 2 만족시 손절
            bool_pt_pl = bangla['max_gain'] > af_config['pt_pl'] # (틱)
            bool_draw_down = af_config['pt_draw_down'] < bangla['draw_down']
            if bool_pt_pl and bool_draw_down:
                bangla['is_pt_triggered'] = True
            
                    
        # 매매시간대 이전 장중 저가 및 고가 기록
        if now < trading_begins_after:
            intra_lo = min(intra_lo, vwap)
            intra_hi = max(intra_hi, vwap)
        
        # 매매시간대 진입, 본격 조건 탐색            
        elif now >= trading_begins_after and now < trading_begins_before:
            if trading_begins_after_index == None:
                trading_begins_after_index = dti_now
            
            if vwap < (intra_lo - thru/100) and tested_status == "below":
                bangla['is_triggered'] = True
    """
    test loop 끝
    """
    # test loop break 이후에 trading time zone endline 설정
    til = datetime.datetime.combine(date, trading_begins_before)
    trading_begins_before_index = dfmkt[dfmkt['datetime'] > til].index[0]
    
    """
    PLOT
    """
    if bangla['is_traded'] == True and plot == "Y":
            
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(1,1,1)
        ax.scatter(bangla['trade_local_index'],
                   bangla['trade_price'],
                   color="b", marker="v", s=300)
        
        if bangla['is_losscut_traded'] == True:
            ax.scatter(bangla['losscut_local_index'],
                       bangla['losscut_price'],
                       color="tab:red", marker="^", s=300)
            
        elif bangla['is_pt_traded'] == True:
            ax.scatter(bangla['pt_local_index'],
                       bangla['pt_price'],
                       color="tab:red", marker="^", s=300)
        
        plt.plot(dti, dfmkt['vwap'])
        plt.plot(dti, dfmkt['ema_fast'])
        plt.plot(dti, dfmkt['ema_slow'])
        
        # 매매시간대 V-line
        plt.axvline(x=trading_begins_after_index)
        plt.axvline(x=trading_begins_before_index)

        
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
        
        plot_name = str(date)+ ' |   P&L : ' + str(bangla['pl'])
        ax.set_xlabel(plot_name, fontdict=font)
        plt.show()
    """
    PLOT 끝
    """
    
    return bangla


#%% BTST

#일봉기준 전체 date list
ld = list(util.getDailyOHLC().index)
# ld = [d for d in ld if d.year == 2021]
# ld = [d for d in ld if d.year >= 2021 and d.month>=9]
ld = [d for d in ld if d == datetime.date(2021, 10, 6)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])

# ld = list(pd.read_excel("AF_loss_days.xlsx").date)

#장중저가 하향돌파 margin(틱), +2 --> 장중저가보다 2틱 아래를 돌파로 가정
af_config = {'trading_begins_after': datetime.time(12,15,0),
             'trading_begins_before': datetime.time(15,15,0),
             'ema_fast_coeff': 0.20,
             'ema_slow_coeff': 0.05,
             'thru': 0.5,
             'ema_margin': 0.5,
             'lc_hi-lo': 1.0, 
             'lc_pl': -30, 
             'pt_pl': 20,
             'pt_draw_down': 0.50
             }


for i, day in enumerate(ld):
    if str(type(day)) == "<class 'pandas._libs.tslibs.timestamps.Timestamp'>":
        day = day.date()
    
    result = afternoonFall(day, af_config=af_config, db_table='lktbf100vol', plot="Y")
    # result = afternoonFall(day, af_config=af_config, db_table='lktbf100vol', plot="Y")
    
    dfpl.at[i, 'date'] = day
    
    pl_of_the_day = result['pl']
    dfpl.at[i, 'pl'] = pl_of_the_day
    dfpl.at[i, 'max_gain'] = result['max_gain']
    
    num_trade = 1 if result['is_traded'] == True else 0
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

