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

class Trade:
    """
    한 건의 매매에 대한 기본정보를 담는 class
    
    2021.09.30
    """
    
    def __init__(self, direction, product):
        
        if direction in ["long", "short"]:
            self.direction = direction
        else:
            raise NameError('Unexpected direction')
            
        self.product = product
        if self.product in ["ktbf", "lktbf"]:
            self.product_multiplier = 100
        elif self.product in ["usdkrw"]:
            self.product_multiplier = 10
        else:
            raise NameError('Unexpected product')
        
        self.is_triggered = False
        self.is_traded = False
        self.trade_price = None
        self.trade_time = None
        self.trade_local_index = None
        
        self.is_timely_closed = False
        
        self.is_losscut_triggered = False
        self.is_losscut_traded = False
        self.losscut_price = None
        self.losscut_time = None
        self.losscut_local_index = None
        
        self.is_pt_triggered = False
        self.is_pt_traded = False
        self.pt_price = None
        self.pt_time = None
        self.pt_local_index = None
        
        self.pl = None
        
        self.max_gain = None
        self.max_gain_price = None
        self.max_gain_time = None
        self.max_gain_local_index = None
        
        # ex) draw_down 20%: max_gain 대비 20% 토해냄
        self.draw_down = None
        
    def updatePl(self, price):
        if self.direction == "long":
            self.pl = round(self.product_multiplier * (price - self.trade_price), 2)
        else:
            self.pl = -round(self.product_multiplier * (price - self.trade_price), 2)
        pass
    
    def __repr__(self):
        return str(self.__dict__)
    

# def intraLow

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
    uno, dos, .. 
   
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
    
    # ema coeffs
    fast_coeff = af_config['ema_fast_coeff']
    slow_coeff = af_config['ema_slow_coeff']
    ema_margin = af_config['ema_margin']
    
    # 장중저가 하향돌파 margin(틱), +2 --> 장중저가보다 2틱 아래를 돌파로 가정
    thru = af_config['thru']
    
    # vwap 시장 data 불러오기
    dfmkt = util.setDfData(date, date, db_table)
    
    # local index
    dti = dfmkt.index
    
    # trading time zone 설정
    trading_begins_after = af_config['trading_begins_after']
    trading_begins_after_index = None
    
    trading_begins_before = af_config['trading_begins_before']
    trading_begins_before_index = None
    
    # 종가시간 설정
    trading_hour_ends = dfmkt.iloc[-1].datetime.time()
    
    # ema 초기세팅
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    
    # intra hi lo 초기세팅
    intra_lo = +99999
    intra_hi = -99999
    
    # 1st trade 객체 생성
    uno = Trade("short", product)
    dos = Trade("short", product)
    
    # 1st trade test loop 시작
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
        # 트리거는 됐는데, 매매는 실행전 --> 최초진입실행
        if uno.is_triggered and not uno.is_traded:
            uno.trade_price = vwap
            uno.trade_time = now
            uno.trade_local_index = dti_now
            uno.is_traded = True
            # max_gain 초기화
            uno.max_gain = 0
            uno.max_gain_price = vwap
            uno.max_gain_time = now
            uno.max_gain_local_index = dti_now
        
        # losscut 발동, losscut 실행전 --> losscut실행
        elif uno.is_losscut_triggered and not uno.is_losscut_traded:
            uno.losscut_price = vwap
            uno.losscut_time = now
            uno.losscut_local_index = dti_now
            uno.is_losscut_traded = True
            uno.updatePl(vwap)
            break
        
        # profit-taking 발동, pt실행전 --> pt 실행
        elif uno.is_pt_triggered and not uno.is_pt_traded:
            uno.pt_price = vwap
            uno.pt_time = now
            uno.pt_local_index = dti_now
            uno.is_pt_traded = True
            uno.updatePl(vwap)
            break

        # 매매실행이후 PL 업데이트하여 LC, PT 처리, 종가PL도 아래에서 동일하게 처리
        elif uno.is_triggered and uno.is_traded:
            # 일상적 PL 기록
            uno.updatePl(vwap)
            
            # max gain 기록
            if uno.pl > uno.max_gain:
                uno.max_gain = uno.pl
                uno.max_gain_price = close_price
                uno.max_gain_time = now
                uno.max_gain_local_index = dti_now
            
            # draw down 기록, max_gain 0 인 경우 예외처리
            if uno.max_gain !=0:
                uno.draw_down = 1 - uno.pl / uno.max_gain 
            else: 
                uno.draw_down = 0
            
            # 중간 검증용 uno 프린트
            # print(now, uno.draw_down)
            
            # 손절 로직1 : 매매발동전 관찰기간중 고가-저가의 ???% 폭만큼 손실발생시 손절 트리거
            # 손절 로직2 : af_config['lc_pl'] 틱 만큼 터지면
            bool_lc_intra_hilo = uno.pl < -product_multiplier * af_config['lc_hi-lo'] * (intra_hi - intra_lo)
            bool_lc_pl = uno.pl < af_config['lc_pl'] #틱환산 했으므로 product_multiplier 적용안함
            # 1 or 2 만족시 손절
            if bool_lc_intra_hilo or bool_lc_pl:
                uno.is_losscut_triggered = True
                
            # 익절 로직1 : max_gain이 ??틱 이상
            # 익절 로직2 : draw_down %% 이상 발생
            bool_pt_pl = uno.max_gain > af_config['pt_pl'] # (틱)
            bool_draw_down = uno.draw_down > af_config['pt_draw_down']
            # 1 and 2 만족시 익절
            if bool_pt_pl and bool_draw_down:
                uno.is_pt_triggered = True
                
            # 종가청산 기록
            if now == trading_hour_ends:
                uno.is_timely_closed = True
                break
                    
        # 매매시간대 이전 장중 저가 및 고가 기록
        if now < trading_begins_after:
            intra_lo = min(intra_lo, vwap)
            intra_hi = max(intra_hi, vwap)
        
        # 매매시간대 진입, 본격 조건 탐색            
        elif now >= trading_begins_after and now < trading_begins_before:
            if trading_begins_after_index == None:
                trading_begins_after_index = dti_now
            
            if vwap < (intra_lo - thru/uno.product_multiplier) and tested_status == "below":
                uno.is_triggered = True
                
    dti_break = dti_now
    time_break = now
    # 1st trade test loop 끝
    
    
    # 2nd trade test loop 시작
    # 1st trade가 종가청산이 아닌 경우에 아래 실행
    if time_break < trading_begins_before and (uno.is_losscut_traded or uno.is_pt_traded):
        
        # 2nd trade 진입가격
        dos_entry = uno.max_gain_price 
        
        for dti_pre, dti_now in zip(dti[dti_break:], dti[dti_break+1:]):
            # 현재시간
            now = dfmkt.at[dti_now, 'datetime'].time()
            
            # 현재가
            vwap = dfmkt.loc[dti_now,'vwap']
            close_price = dfmkt.loc[dti_now,'close']
            
            # ema 기록
            dfmkt.at[dti_now, 'ema_fast'] = fast_coeff * vwap + \
                (1-fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
            
            dfmkt.at[dti_now, 'ema_slow'] = slow_coeff * vwap + \
                (1-slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
            
            # cross test 결과 
            tested_status = tl.crossTest(
                dfmkt.at[dti_now, 'ema_fast'], 
                dfmkt.at[dti_now, 'ema_slow'], 
                margin=ema_margin
                )
            
            # 트리거는 됐는데, 매매는 실행전 --> 진입실행
            if dos.is_triggered and not dos.is_traded:
                dos.trade_price = vwap
                dos.trade_time = now
                dos.trade_local_index = dti_now
                dos.is_traded = True
                # max_gain 초기화
                dos.max_gain = 0
                dos.max_gain_time = now
                dos.max_gain_local_index = dti_now
                
            # losscut 발동, losscut 실행전 --> losscut실행
            elif dos.is_losscut_triggered and not dos.is_losscut_traded:
                dos.losscut_price = vwap
                dos.losscut_time = now
                dos.losscut_local_index = dti_now
                dos.is_losscut_traded = True
                dos.updatePl(vwap)
                break
            
            # profit-taking 발동, pt실행전 --> pt 실행
            elif dos.is_pt_triggered and not dos.is_pt_traded:
                dos.pt_price = vwap
                dos.pt_time = now
                dos.pt_local_index = dti_now
                dos.is_pt_traded = True
                dos.updatePl(vwap)
                break
            
            # 트리거 & 실행 후
            elif dos.is_triggered and dos.is_traded:
                # 일상적 PL 기록
                dos.updatePl(vwap)
                # print(dos.pl)
                
                # max gain 기록
                if dos.pl > dos.max_gain:
                    dos.max_gain = dos.pl
                    dos.max_gain_price = close_price
                    dos.max_gain_time = now
                    dos.max_gain_local_index = dti_now
                
                # draw down 기록, max_gain 0 인 경우 예외처리
                if dos.max_gain !=0:
                    dos.draw_down = 1 - dos.pl / dos.max_gain 
                else: 
                    dos.draw_down = 0
            
                # 손절 로직 : uno의 lc의 50%만큼 손실나면
                bool_lc_pl_dos = dos.pl < 0.5 * af_config['lc_pl'] #틱환산 했으므로 product_multiplier 적용안함
                if bool_lc_pl_dos:
                    dos.is_losscut_triggered = True
                    
                # 익절 로직1 : max_gain이 ??틱 이상 --> uno의 50%
                # 익절 로직2 : draw_down %% 이상 발생 --> uno 비율의 1.5배
                bool_pt_pl_dos = dos.max_gain > 0.5 * af_config['pt_pl'] # (틱)
                bool_draw_down_dos = dos.draw_down > 1.5 * af_config['pt_draw_down']
                # 1 and 2 만족시 익절
                if bool_pt_pl_dos and bool_draw_down_dos:
                    dos.is_pt_triggered = True
                
            # 매매 조건 탐색
            if vwap < dos_entry and tested_status == "below":
                dos.is_triggered = True
                
            # 종가청산 기록
            if now == trading_hour_ends:
                dos.is_timely_closed = True
                break
    
                
    # if dos.is_traded:
    #     uno.pl = uno.pl + dos.pl
    
    
    # test loop break 이후에 trading time zone endline 설정, Plotting용
    til = datetime.datetime.combine(date, trading_begins_before)
    trading_begins_before_index = dfmkt[dfmkt['datetime'] > til].index[0]
    
    """
    PLOT
    """
    if uno.is_traded and plot == "Y":
            
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(1,1,1)
        ax.scatter(uno.trade_local_index,
                   uno.trade_price,
                   color="b", marker="v", s=300)
        
        if uno.is_losscut_traded:
            ax.scatter(uno.losscut_local_index,
                       uno.losscut_price,
                       color="tab:red", marker="^", s=300)
            
        if uno.is_pt_traded:
            ax.scatter(uno.pt_local_index,
                       uno.pt_price,
                       color="tab:red", marker="^", s=300)
            
        if dos.is_traded:
            ax.scatter(dos.trade_local_index,
                       dos.trade_price,
                       color="b", marker="v", s=200)
            
        if dos.is_losscut_traded:
            ax.scatter(dos.losscut_local_index,
                       dos.losscut_price,
                       color="tab:red", marker="^", s=200)
        
        if dos.is_pt_traded:
            ax.scatter(dos.pt_local_index,
                       dos.pt_price,
                       color="tab:red", marker="^", s=200)
            
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
                'size': 14}
        
        pl = uno.pl + dos.pl if dos.is_traded else uno.pl
        
        plot_name = str(date)+ ' |   P&L : ' + str(round(pl, 1))
        ax.set_xlabel(plot_name, fontdict=font)
        plt.show()
    """
    PLOT 끝
    """

    
    return uno, dos


#%% BTST

#일봉기준 전체 date list
ld = list(util.getDailyOHLC().index)
# ld = [d for d in ld if d.year in [2015, 2016, ]]
# ld = [d for d in ld if d.year >= 2019 ]
ld = [d for d in ld if d == datetime.date(2021, 11, 8)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])

# ld = list(pd.read_excel("AF_loss_days.xlsx").date)

#장중저가 하향돌파 margin(틱), +2 --> 장중저가보다 2틱 아래를 돌파로 가정
af_config = {'trading_begins_after': datetime.time(12,00,0),
             'trading_begins_before': datetime.time(15,00,0),
             'ema_fast_coeff': 0.20,
             'ema_slow_coeff': 0.05,
             'thru': 0.5,
             'ema_margin': 0.5,
             'lc_hi-lo': 1.0, 
             'lc_pl': -25, 
             'pt_pl': 25,
             'pt_draw_down': 0.3
             }

# af_config_3y = {'trading_begins_after': datetime.time(12,00,0),
#              'trading_begins_before': datetime.time(15,00,0),
#              'ema_fast_coeff': 0.20,
#              'ema_slow_coeff': 0.05,
#              'thru': 0.5,
#              'ema_margin': 0.5,
#              'lc_hi-lo': 1.0, 
#              'lc_pl': -7, 
#              'pt_pl': 7,
#              'pt_draw_down': 0.3
#              }


for i, day in enumerate(ld):
    if str(type(day)) == "<class 'pandas._libs.tslibs.timestamps.Timestamp'>":
        day = day.date()
    
    uno, dos = afternoonFall(day, af_config=af_config, db_table='lktbf100vol', plot="Y")
    # uno, dos = afternoonFall(day, af_config=af_config_3y, db_table='ktbf200vol', plot="Y")
    
    dfpl.at[i, 'date'] = day
    
    pl_of_the_day = uno.pl + dos.pl if dos.is_traded else uno.pl
    dfpl.at[i, 'pl'] = pl_of_the_day
    dfpl.at[i, 'dos_pl'] = dos.pl
    
    num_trade = 1 if uno.is_traded == True else 0
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

# 결과 출력및 저장
# dfpl 수정됨, call by reference
pl_mon, pl_yr = util.reportSummary(dfpl, show_hist="n")

