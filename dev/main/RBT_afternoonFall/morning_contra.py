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


# def olga(date, db_table, config, plot="Y"):

"""
- 전일비 시가갭 발생시 contrarian 접근
- 물타기까지 동원하여 가급적 이익실현을 목표
- 손실금액이 이익금액보다 클 수 있으나 목적상 hit% 높이는 데에 주력
- 빠른 시간 내에 이익실현후 엑싯을 목표로함
    
발동조건
    1. 시가가 전일비 ?? 이상일때 처음부터 매도
    2. 손실발생시 물타기 ?? 회
    
진입후 매매조건
    1. cover는 이익 얼마 이상에서 즉각 실행 --> 모멘텀 기대 없음!!
    2. 손절은 절대금액으로 

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



date = datetime.date(2021, 9, 16)
db_table = 'lktbf_min'

config = {
    'trading_ends_at': datetime.time(11,30,0),
    'ema_fast_coeff': 0.20,
    'ema_slow_coeff': 0.05,
    'thru': 0.5,
    'ema_margin': 0.5,
    'lc_hi-lo': 1.0, 
    'lc_pl': -30, 
    'pt_pl': 20,
    'pt_draw_down': 0.3,
    }

if db_table[:3] == 'lkt':
    product = 'lktbf'
    TICK_VALUE = 0.01
    KRW_COMMISSION_PER_CONTRACT = 250 # 원래 248.95원/계약
    KRW_VALUE_1PT = 10**6
    
elif db_table[:3] == 'ktb':
    product = 'ktbf'
    TICK_VALUE = 0.01
    KRW_COMMISSION_PER_CONTRACT = 250 # 원래 225.5원/계약
    KRW_VALUE_1PT = 10**6

elif db_table[:3] == 'usd':
    product = 'usdkrw'
    TICK_VALUE = 0.1
    KRW_COMMISSION_PER_CONTRACT = 60 # 원래 57.9원/계약
    KRW_VALUE_1PT = 10**4

TICK_CONVERSION = 1 / TICK_VALUE

day_table = product + '_day'

dfmkt = util.setDfData(date, date, db_table)

yday_close = util.getYdayOHLC(date, table=day_table)['close']
siga = dfmkt.close[0]
siga_chg = siga - yday_close

#ema coeffs
K_FAST = config['ema_fast_coeff']
K_SLOW = config['ema_slow_coeff']
EMA_MARGIN = config['ema_margin']

 # trading time zone 설정
trading_ends_at = config['trading_ends_at']
trading_begins_before_index = None

#local index
dti = dfmkt.index

#초기세팅
dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'open']
dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'open']

max_gain = -10**10
max_loss = 10**10
draw_down = 0
DRAWDOWN_TO_CLOSE = 0.3 # 30% draw down 생기면 청산

open_position_qty = 0
open_position_trade_price_list = []
open_position_trade_qty_list = []
open_pnl_krw = 0
last_trade_price = 0

QTY_PER_TRADE = 50
MAX_QTY = 200

#초기상태에 대한 정의 필요
prev_status = "attached"

#현재의 signal 상태를 저장
signal_before = 0
signal_now = 0

# intra_hi, intra_lo 리스트 저장
intra_lo = +99999
intra_lo_list = []
intra_lo_time_list = []

intra_hi = -99999
intra_hi_list = []
intra_hi_time_list = []

LOSSCUT_KRW = -10**7 # -천만원
MIN_KRW_PROFIT_TO_CLOSE = 10**7 # 천만원
MIN_PRICE_MOVE_FROM_LAST_TRADE = 0.03 # 3틱 이상 바뀌었을때만 add

#%% TEST LOOP

    
"""test loop시작"""
# 시가 전일비 갭다운 시작의 경우

if siga_chg < -0.10:
    
    for dti_pre, dti_now in zip(dti, dti[1:]):
        
        # 실제 운용시 vwap이 last보다 빠른 정보일 것
        # vwap = dfmkt.loc[dti_now,'vwap']
        last_prc = dfmkt.loc[dti_now,'close']
        
        # 현재시간
        now = dfmkt.at[dti_now, 'datetime'].time()
        
        # 종료시간 내에 현재 포지션 청산
        # 롱 or 숏 똑같이 처리
        if (now >= trading_ends_at) \
            or (open_pnl_krw > MIN_KRW_PROFIT_TO_CLOSE and draw_down > DRAWDOWN_TO_CLOSE):
                
            trade_qty = -open_position_qty
            trade_price = last_prc - TICK_VALUE * 0.5 if open_position_qty > 0 else last_prc + TICK_VALUE * 0.5
            open_position_qty = 0
            open_position_trade_price_list = []
            open_position_trade_qty_list = []
            last_trade_price = trade_price
        
        
        # 장 시작후 몇분이 경과했는지
        # now_n_min = max(1, int((now - siga_time).seconds / 60))
        
        # std factor update
        # std_tilnow = dfmkt[:dti_now]['close'].expanding(10).std().iloc[-1]
        # std_tilnow_ref = timely_std_list[now_n_min-1]
        # std_factor = std_tilnow / std_tilnow_ref
        # if std_factor == 0 or np.isnan(std_factor):
        #     std_factor = 1
        
        # dfmkt.at[dti_now, 'std_factor'] = std_factor
        
        # last_prc 기준으로 ema update
        # dfmkt.at[dti_now, 'ema_fast'] = K_FAST * std_factor * last_prc \
        #     + (1 - K_FAST * std_factor) * dfmkt.at[dti_pre, 'ema_fast']
        # dfmkt.at[dti_now, 'ema_slow'] = K_SLOW * std_factor * last`_prc \
        #     + (1 - K_SLOW * std_factor) * dfmkt.at[dti_pre, 'ema_slow']
        dfmkt.at[dti_now, 'ema_fast'] = K_FAST * last_prc + (1 - K_FAST) * dfmkt.at[dti_pre, 'ema_fast']
        dfmkt.at[dti_now, 'ema_slow'] = K_SLOW * last_prc + (1 - K_SLOW) * dfmkt.at[dti_pre, 'ema_slow']
            
        diff_now = dfmkt.at[dti_now, 'ema_fast'] - dfmkt.at[dti_now, 'ema_slow']
        tick_apo = TICK_CONVERSION * diff_now
        dfmkt.at[dti_now, 'tick_apo'] = tick_apo
        
        # intra hi, lo 기록
        if last_prc < intra_lo:
            intra_lo = last_prc
            intra_lo_list.append(last_prc)
            intra_lo_time_list.append(now)
            
        elif last_prc > intra_hi:
            intra_hi = last_prc
            intra_hi_list.append(last_prc)
            intra_hi_time_list.append(now)
            
        # 트레이딩 시간 정의
        if  now < trading_ends_at:
            
            tested_status = tl.crossTest(dfmkt.at[dti_now, 'ema_fast'], 
                                         dfmkt.at[dti_now, 'ema_slow'], 
                                         margin=EMA_MARGIN)
            
            # 기본수량 매수하고 시작
            if dti_now == dti[1]:
                trade_qty = QTY_PER_TRADE
                trade_price = last_prc + TICK_VALUE * 0.5
                open_position_qty += trade_qty
                open_position_trade_price_list.append(trade_price)
                open_position_trade_qty_list.append(trade_qty)
                last_trade_price = trade_price
            
            # open position pl 계산
            if open_position_qty != 0:
                open_pnl_krw = KRW_VALUE_1PT * sum(
                    np.array(open_position_trade_qty_list) \
                        * (last_prc - np.array(open_position_trade_price_list))
                        )
                
                if max_gain < open_pnl_krw :
                    max_gain = open_pnl_krw 
                
                if max_gain > 0:
                    draw_down = 1 - open_pnl_krw / max_gain
            
            # 방향성 탐색 시간 (9:30 이전) - 포지션 쌓기
            elif now < dfmkt.loc[dti[29]]['datetime'].time():
                
                # 롱 add하는 경우
                if (open_position_qty > 0) \
                    and (open_position_qty < MAX_QTY) \
                    and (last_prc - last_trade_price < -MIN_PRICE_MOVE_FROM_LAST_TRADE) \
                    and (open_pnl_krw > LOSSCUT_KRW):
                        
                    trade_qty = QTY_PER_TRADE
                    trade_price = last_prc + TICK_VALUE * 0.5
                    open_position_qty += trade_qty
                    open_position_trade_price_list.append(trade_price)
                    open_position_trade_qty_list.append(trade_qty)
                    last_trade_price = trade_price
                
                # 롱 손절하고 숏 전환
                elif (open_position_qty > 0) \
                    and (last_prc <= intra_lo) \
                    and (open_pnl_krw <= LOSSCUT_KRW)
                        
                # 숏 애드
                
                        
            
                
            
            
            # last_prc 기준으로 pl 계산, 현재까지의 누적 pl을 기록함
            dftemp = dfmkt[:dti_now+1]
            gross_pl = KRW_VALUE_1PT * sum(np.array(dftemp['trade_qty']) \
                                           * (last_prc - np.array(dftemp['trade_price'])))
            commission = KRW_COMMISSION_PER_CONTRACT * abs(np.array(dftemp['trade_qty'])).sum()
            net_pl = int(gross_pl - commission)
            dfmkt.at[dti_now, 'net_pl'] = net_pl
            
            
                
            
            # open_position_qty 를 기준으로 조건 탐색
            
            # 현재 포지션 없음
            if open_position_qty == 0:
                # 진입 test
                # threshold 조건 & apo가 이전가격대비 반대방향으로 진행 (꺾이는 경우)
                # & last_trade_price 대비 충분히 움직임
                if (tick_apo > ENTRY_THRESHOLD_APO * std_factor) \
                    and (tick_apo < dfmkt.loc[dti_pre, 'tick_apo']) \
                    and (abs(last_prc - last_trade_price) \
                         > MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor):
                    trade_qty = -QTY_PER_TRADE
                    print("SHORT to be initiated")
                
                elif tick_apo < -ENTRY_THRESHOLD_APO * std_factor \
                    and (tick_apo > dfmkt.loc[dti_pre, 'tick_apo']) \
                    and (abs(last_prc - last_trade_price) \
                         > MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor):
                    trade_qty = QTY_PER_TRADE
                    print("LONG to be initiated")
            
            # 현재 숏포지션
            elif open_position_qty < 0:
                # 포지션 익절
                if open_pnl_krw > MIN_KRW_PROFIT_TO_CLOSE / std_factor:
                    trade_qty = abs(open_position_qty) # 숏이었으므로 양수의 수량
                    print("SHORT profit to be taken.", f'{open_pnl_krw:,}')
                    
                # 포지션 손절
                elif open_pnl_krw < LOSSCUT_KRW / std_factor:
                    trade_qty = abs(open_position_qty) # 숏이었으므로 양수의 수량
                    print("SHORT Loss to be realized")
                    
                # 손익으로는 청산 조건에 해당 없으므로 포지션 추가 또는 apo 기준 청산 또는 nothing
                else:
                    # apo조건 청산
                    if tick_apo <= 0:
                        trade_qty = abs(open_position_qty) # 숏이었으므로 양수의 수량
                        print("Quit SHORT by apo condition")
                    
                    # add 조건 만족하면 포지션 add
                    # entry조건 만족 & max 수량 이내 & 마지막거래대비 충분히 움직임 & APO 꺾임
                    elif (tick_apo > ENTRY_THRESHOLD_APO * std_factor) \
                        and (abs(open_position_qty) < MAX_QTY) \
                        and (abs(last_prc - open_position_trade_price_list[-1]) \
                             > MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor) \
                        and (tick_apo < dfmkt.loc[dti_pre, 'tick_apo']): 
                        trade_qty = -QTY_PER_TRADE
                        print("SHORT Position to be added")
            
            # 현재 롱포지션
            elif open_position_qty > 0:
                # 포지션 익절
                if open_pnl_krw > MIN_KRW_PROFIT_TO_CLOSE / std_factor:
                    trade_qty = -abs(open_position_qty)
                    print("LONG profit to be taken")
                    
                # 포지션 손절
                elif open_pnl_krw < LOSSCUT_KRW / std_factor:
                    trade_qty = -abs(open_position_qty) 
                    print("LONG Loss to be realized")
                    
                # 손익으로는 청산 조건에 해당 없으므로 포지션 추가 또는 apo 기준 청산 또는 nothing
                else:
                    # apo조건 청산
                    if tick_apo >= 0:
                        trade_qty = -abs(open_position_qty) 
                        print("Quit LONG by apo condition")
                    
                    # add 조건 만족하면 포지션 add
                    # entry조건 만족 & max 수량 이내 & 마지막거래대비 충분히 움직임 & APO 꺾임
                    elif (tick_apo < -ENTRY_THRESHOLD_APO * std_factor) \
                        and (abs(open_position_qty) < MAX_QTY) \
                        and (abs(last_prc - open_position_trade_price_list[-1]) \
                             > MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor) \
                        and (tick_apo > dfmkt.loc[dti_pre, 'tick_apo']):
                        trade_qty = QTY_PER_TRADE
                        print("LONG Position to be added")
            
            # qty_to_trade 컬럼 추가
            dfmkt.at[dti_now, 'qty_to_trade'] = trade_qty    
        
        
        if trade_qty != 0:
            dfmkt.at[dti_now, 'trade_price'] = vwap
            last_trade_price = vwap
            
            # open position data들 정리
            open_position_trade_price_list.append(vwap)
            open_position_trade_qty_list.append(trade_qty)
            open_position_qty += trade_qty
            print(f' {dti_now} {now.time()}   {trade_qty} Traded @ {vwap}')
            print(f' {open_position_trade_qty_list}')
            print(f' {open_position_trade_price_list}')
            
            # 상기 trade로 포지션 flat이 된 경우 data 초기화
            if open_position_qty == 0:
                open_position_trade_price_list = []
                open_position_trade_qty_list = []
            
        else:
            dfmkt.at[dti_now, 'trade_price'] = 0
            
        dfmkt.at[dti_now, 'trade_qty'] = trade_qty
        dfmkt.at[dti_now, 'actual_qty'] = trade_qty + dfmkt.at[dti_pre, 'actual_qty']
        
        # reset
        trade_qty = 0
        
        
        
            # 절대금액 손절 로직 추가
            # if losscut == "Y" and net_pl < -30*(10**6):
            #     break
            
            
    """index기준 test loop종료"""       
            
    
    print(f'net_pl : {net_pl:,}')
    print(f'trade qty sum : {int(dfmkt.trade_qty.abs().sum()):,}')
    print(f'commission sum : {int(commission):,}')

#%% temp

# # cross test에 따른 결과로 시그널 처리
#                 if (prev_status == "above" or prev_status == "below") and tested_status == "attached":
#                     prev_status = tested_status
                
#                 elif prev_status == tested_status:
#                     pass
                
#                 #below -> above or above -> below or attahced -> above/below
#                 else: 
#                     # print(prev_status, tested_status)
#                     prev_status = tested_status
                    
#                     signal_now = 1 if tested_status == "above" else -1
                    
#                     # !!!이 경우에만 시그널 발생
#                     # 시그널이 롱인 경우
#                     if signal_before != signal_now and signal_now == 1: 
#                         signal_before = signal_now # signal_before reset
#                         # print("signal detected : ", signal_now)
    
#                         if open_position_qty < MAX_QTY:
#                             trade_price = last_prc + TICK_VALUE * 0.5
#                             trade_qty = QTY_PER_TRADE
                            
#                             dfmkt.at[dti_now, 'trade_price'] = trade_price
#                             dfmkt.at[dti_now, 'trade_qty'] = trade_qty
    
#                             open_position_qty += trade_qty
#                             open_position_trade_price_list.append(trade_price)
#                             open_position_trade_qty_list.append(trade_qty)
                    
#                     # 시그널이 숏인데, PL이 LC보다  경우
#                     elif signal_before != signal_now and signal_now == -1:
#                         signal_before = signal_now # signal_before reset
                        
                        
#                         # 롱포지션 청산
#                         if open_position_qty > 0:
#                             trade_price = last_prc - TICK_VALUE * 0.5
#                             trade_qty = -open_position_qty
                            
#                             dfmkt.at[dti_now, 'trade_price'] = trade_price
#                             dfmkt.at[dti_now, 'trade_qty'] = trade_qty
    
#                             open_position_qty += trade_qty
#                             open_position_trade_price_list.append(trade_price)
#                             open_position_trade_qty_list.append(trade_qty)
                        
                        
#                         # 숏포지션 진입
#                         if open_position_qty < MAX_QTY:
#                             trade_price = last_prc + TICK_VALUE * 0.5
#                             trade_qty = QTY_PER_TRADE
                            
#                             dfmkt.at[dti_now, 'trade_price'] = trade_price
#                             dfmkt.at[dti_now, 'trade_qty'] = trade_qty
    
#                             open_position_qty += trade_qty
#                             open_position_trade_price_list.append(trade_price)
#                             open_position_trade_qty_list.append(trade_qty)








