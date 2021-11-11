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

date = datetime.date(2021, 9, 6)
db_table = 'lktbf_10sec'

config = {
    'trading_ends_at': datetime.time(11,30,0),
    'position_build_until': datetime.time(9,30,0),
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
position_build_until = config['position_build_until']

#local index
dti = dfmkt.index

#초기세팅
dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'open']
dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'open']
dfmkt.at[dti[0], 'tick_apo'] = 0
dfmkt.at[dti[0], 'trade_price'] = 0
dfmkt.at[dti[0], 'trade_qty'] = 0
dfmkt.at[dti[0], 'actual_qty'] = 0

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

prev_status = "attached"

last_move = "standby"

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
#%% look back period 및 트레이딩을 위한 설정값들 정의
    
    # ar_diff_window = np.array([])
    # refmkt_list = []
    # apo_std_list = []
    
    # for i in range(1, window_ref+1):
    #     if yesterday != None:
    #         d = yesterday
    #     else:
    #         d = util.date_offset(date, -i)
    #     # print(i, d)
    #     refmkt = util.setDfData(d, d, db_table)
    #     refdti = refmkt.index
        
    #     refmkt.at[refdti[0], 'ema_fast'] = refmkt.at[refdti[0], 'vwap']
    #     refmkt.at[refdti[0], 'ema_slow'] = refmkt.at[refdti[0], 'vwap']
        
    #     for refdti_pre, refdti_now in zip(refdti, refdti[1:]):
    #         last_prc = refmkt.loc[refdti_now,'close']
            
    #         refmkt.at[refdti_now, 'ema_fast'] = K_FAST * last_prc \
    #             + (1 - K_FAST) * refmkt.at[refdti_pre, 'ema_fast']
            
    #         refmkt.at[refdti_now, 'ema_slow'] = K_SLOW * last_prc \
    #             + (1 - K_SLOW) * refmkt.at[refdti_pre, 'ema_slow']
        
    #     ar_diff_day = np.array(refmkt['ema_fast']) - np.array(refmkt['ema_slow'])
        
    #     print(f'{d}  {ar_diff_day.mean()*100:.1f}  {ar_diff_day.std()*100:.1f}  {refmkt.close.std()*100:.1f}')
        
    #     refmkt['cum_std'] = refmkt['close'].expanding(2).std()
        
    #     apo_std_list.append(np.std(ar_diff_day))
        
    #     refmkt_list.append(refmkt)
    
    # # look back window의 시간대별 평균 변동성(cum std) 기록, 분단위
    # timely_std_list = []
    
    # for ti in pd.timedelta_range(start='9:00:00', end='15:45:00', freq='1min', closed='right'):
    #     # print(ti)
    #     std_til_ti = []
    #     for refmkt in refmkt_list:
    #         if refmkt['time'].iloc[0] == pd.Timedelta(hours=9):
    #             std_til_ti.append(refmkt[refmkt['time'] <= ti]['cum_std'].iloc[-1])
    #         else:
    #             pass
    #     timely_std_list.append(np.mean(std_til_ti))


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
        if (open_position_qty != 0) \
            and ((now >= trading_ends_at) \
                 or (max_gain > MIN_KRW_PROFIT_TO_CLOSE and draw_down > DRAWDOWN_TO_CLOSE)):
                
            trade_qty = -open_position_qty
            trade_price = last_prc - TICK_VALUE * 0.5 if open_position_qty > 0 else last_prc + TICK_VALUE * 0.5
            open_position_qty = 0
            open_position_trade_price_list = []
            open_position_trade_qty_list = []
            last_trade_price = trade_price
            last_move = "position_closed"
            print(now, last_move)
            
            # break
        
        
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
            
        tested_status = tl.crossTest(dfmkt.at[dti_now, 'ema_fast'], 
                                     dfmkt.at[dti_now, 'ema_slow'], 
                                     margin=EMA_MARGIN)
        
        # 기본수량 매수하고 시작
        if dti_now == dti[1]:
            trade_qty = QTY_PER_TRADE
            trade_price = siga + TICK_VALUE * 0.5 # dti_pre가 시가 indexing하므로 siga로 강제지정
            open_position_qty += trade_qty
            # 시가매수이므로 최초 dti 입력
            dfmkt.at[dti_pre, 'trade_price'] = trade_price
            dfmkt.at[dti_pre, 'trade_qty'] = trade_qty
            dfmkt.at[dti_pre, 'actual_qty'] = trade_qty + dfmkt.at[dti_pre, 'actual_qty']
            open_position_trade_price_list.append(trade_price)
            open_position_trade_qty_list.append(trade_qty)
            last_trade_price = trade_price
            last_move = "initial_long_entered"
            print(now, last_move)
        
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
        
        # 방향성 탐색 & 포지션 쌓기
        if now < position_build_until:
            
            # 롱 add하는 경우
            if (open_position_qty > 0) \
                and (open_position_qty < MAX_QTY) \
                and (last_prc - last_trade_price < -MIN_PRICE_MOVE_FROM_LAST_TRADE) \
                and (open_pnl_krw > LOSSCUT_KRW) \
                and (last_prc > siga - 0.05):
                    
                trade_qty = QTY_PER_TRADE
                trade_price = last_prc + TICK_VALUE * 0.5
                open_position_qty += trade_qty
                open_position_trade_price_list.append(trade_price)
                open_position_trade_qty_list.append(trade_qty)
                last_trade_price = trade_price
                last_move = "long_added"
                print(now, last_move)
            
            # 롱 손절, 로스컷 손익 이하일때
            elif (open_position_qty > 0) and (open_pnl_krw <= LOSSCUT_KRW):
                trade_qty = -open_position_qty
                trade_price = last_prc - TICK_VALUE * 0.5
                open_position_qty = 0
                open_position_trade_price_list = []
                open_position_trade_qty_list = []
                last_trade_price = trade_price
                last_move = "long_losscut"
                print(now, last_move)
            
            # 숏 진입, 장중 저가 깨졌을 때
            elif  last_move == "long_losscut" and last_prc <= intra_lo:
                trade_qty = -QTY_PER_TRADE
                trade_price = last_prc - TICK_VALUE * 0.5
                open_position_qty += trade_qty
                open_position_trade_price_list.append(trade_price)
                open_position_trade_qty_list.append(trade_qty)
                last_trade_price = trade_price
                last_move = "short_entered"
                print(now, last_move)
                    
            # 숏 애드, 숏포지션이고 tick apo가 직전보다 심화될 때
            elif (open_position_qty < 0) \
                and (abs(open_position_qty) < MAX_QTY) \
                and (last_prc - last_trade_price < -MIN_PRICE_MOVE_FROM_LAST_TRADE) \
                and (open_pnl_krw > LOSSCUT_KRW) \
                and (tick_apo < dfmkt.loc[dti_pre]['tick_apo']): # 숏 강도가 심화
                
                trade_qty = -QTY_PER_TRADE
                trade_price = last_prc - TICK_VALUE * 0.5
                open_position_qty += trade_qty
                open_position_trade_price_list.append(trade_price)
                open_position_trade_qty_list.append(trade_qty)
                last_trade_price = trade_price
                last_move = "short_added"
                print(last_move)
            
            else:
                trade_qty = 0
                trade_price = 0
        
        # if dti_now != dti[1]:
        dfmkt.at[dti_now, 'trade_price'] = trade_price
        dfmkt.at[dti_now, 'trade_qty'] = trade_qty
        dfmkt.at[dti_now, 'actual_qty'] = trade_qty + dfmkt.at[dti_pre, 'actual_qty']
            
        trade_qty = 0
        trade_price = 0
            
        # last_prc 기준으로 pl 계산, 현재까지의 누적 pl을 기록함
        dftemp = dfmkt[:dti_now]
        gross_pl = KRW_VALUE_1PT * sum(np.array(dftemp['trade_qty']) \
                                       * (last_prc - np.array(dftemp['trade_price'])))
        commission = KRW_COMMISSION_PER_CONTRACT * abs(np.array(dftemp['trade_qty'])).sum()
        net_pl = int(gross_pl - commission)
        dfmkt.at[dti_now, 'net_pl'] = net_pl
            
            
            
            # # open position data들 print
            # print(f' {open_position_trade_qty_list}')
            # print(f' {open_position_trade_price_list}')
            
            # # 상기 trade로 포지션 flat이 된 경우 data 초기화
            # if open_position_qty == 0:
            #     open_position_trade_price_list = []
            #     open_position_trade_qty_list = []
            
        
        
            # 절대금액 손절 로직 추가
            # if losscut == "Y" and net_pl < -30*(10**6):
            #     break
            
    """index기준 test loop종료"""       
            
    
    print(f'net_pl : {net_pl:,}')
    print(f'trade qty sum : {int(dfmkt.trade_qty.abs().sum()):,}')
    print(f'commission sum : {int(commission):,}')
    
#%%PLOT

fig = plt.figure(figsize=(10,10))
    
ax = fig.add_subplot(1,1,1
                     )
ax.plot(dfmkt.index, dfmkt['close'], linewidth=0.5)
ax.plot(dfmkt.index, dfmkt['ema_fast'])
ax.plot(dfmkt.index, dfmkt['ema_slow'])

dftrd = dfmkt[dfmkt['trade_qty'] != 0]
for i in dftrd.index:
    marker = "^" if dftrd.loc[i]['trade_qty'] > 0 else "v" 
    color = "tab:red" if marker == "^" else "b" 
    x = i
    y = dftrd.loc[i]['close']
    ax.scatter(x, y, color=color, marker=marker, s=300)

# 전일종가 H-line
day_table = product + '_day'
yday_close = util.getYdayOHLC(date, table=day_table)['close']
ax.axhline(y=yday_close, color='black', linestyle='dashed')

ax2 = ax.twinx()
ax2.fill_between(dfmkt.index, dfmkt['net_pl'], 0, alpha=0.3, color="gray")
ax2.scatter(dfmkt.index[-1], 
            dfmkt['net_pl'].iloc[-1],
            color="tab:red" if dfmkt['net_pl'].iloc[-1] > 0 else "b", 
            marker="o", s=50)

ax3 = ax.twinx()
ax3.spines["right"].set_position(("axes", 1.05)) ## 오른쪽 옆에 y축 추가
ax3.fill_between(dfmkt.index, dfmkt['actual_qty'], 0, alpha=0.1, color="red")
ax3.scatter(dfmkt.index[-1], 
            dfmkt['actual_qty'].iloc[-1],
            color="tab:red" if dfmkt['actual_qty'].iloc[-1] > 0 else "b", 
            marker="^" if dfmkt['actual_qty'].iloc[-1] > 0 else "v",
            s=50)


# Set plot name as xlabel
font = {'family': 'verdana',
        'color':  'darkblue',
        'weight': 'bold',
        'size': 11,
        }
plot_name = '{3}, F_co: {0}, S_co: {1}, maxq: {2}, pl: {4:,}'
plot_name = plot_name.format(K_FAST,
                             K_SLOW,
                             MAX_QTY,
                             date,
                             net_pl
                             )
ax.set_xlabel(plot_name, fontdict=font)
plt.show()

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








