# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 11:52:04 2021

@author: infomax
"""

import pandas as pd
import numpy as np
import math
import datetime
import os
from tqdm import tqdm
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util
from DayTradeBook import DayTradeBook

#%% slope test
def calSlope(data, fast_win, slow_win):
    # 마지막 data부터 win size만큼만 slicing하여 slope 계산
    # 단순 end_point를 연결한 직선의 slope 계산
    x_fast = data[-fast_win:]
    x_slow = data[-slow_win:]
    
    slope_fast = (x_fast[-1] - x_fast[0]) / fast_win
    slope_slow = (x_slow[-1] - x_slow[0]) / slow_win
    
    return slope_fast, slope_slow

from scipy import stats
x = np.random.random(10)
y = np.random.random(10)
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

from matplotlib import pyplot as plt

fig = plt.figure(figsize=(8,8))

# ax = fig.add_subplot(1,1,1)
# ax.scatter(x,y)

print(slope, r_value**2)



#%% main BTST
def crossTest(ema_fast, ema_slow, margin=0.5):
    """
    ema_fast와 ema_slow를 비교
    
    Returns
    -------
        "attached" / "above" / "below" 중에 하나를 리턴
    """
    if 100*abs(ema_fast - ema_slow) <= margin:
        cross_status = "attached"
    elif ema_fast > ema_slow:
        cross_status = "above"
    elif ema_fast < ema_slow:
        cross_status = "below"
    else:
        raise NameError("Unexpected! Check margin value!")
        
    return cross_status
    

# def tes(date, db_table='lktbf_10sec',
#         fast_coeff=0.3, slow_coeff=0.1, margin=0.5, dfmkt=None):
    """
    tradeEma는 장중 한방향 트렌드가 지속될 때 많은 수익을 추구
    필연적으로 방향전환이 많은 날은 손실 발생 가능
    
    Parameters
    ----------
    date : datetime.date
        테스트하고자 하는 날짜
        
    vol_option : str
        몇개짜리 볼륨봉을 쓸 것인지 = DB의 table명과 동일하게
        
    execution :
        "adjusted" --> upp/flr 활용하여 보수적 진입가격
        "vwap" --> dti_next의 vwap 그대로 활용
    
    fast_coeff, slow_coeff : ema용 Coefficient
    Returns
    -------
    result = {'df' : df_result, 
              'dfmkt': dfmkt,
              'config': (fast_coeff, slow_coeff, margin)}
    """
    
date = datetime.date(2021, 11, 18)
db_table='lktbf_10sec'
fast_coeff=0.05
slow_coeff=0.01
margin=0.5

#테스트를 위한 시장 data load
# if dfmkt == None or dfmkt.empty == True:
dfmkt = util.setDfData(date, date, db_table)
dfmkt = util.dropDonghoTime(dfmkt)
dti_cut = 9999999
dfmkt = dfmkt[:dti_cut]

dt = DayTradeBook(date=date, db_table=db_table)

#필요시 비교를 위한 어제의 dfmkt
yday = dt.yday
dfmkt_yday = util.setDfData(yday, yday, db_table)
dfmkt_yday = util.dropDonghoTime(dfmkt_yday)

# 과거 변동성 data load
std_ref_table = util.stdTimeTable(date, db_table, look_back_days=120)
STD_DIFF_CAL_WINDOW = 6*15

#local index
dti = dfmkt.index

#초기상태에 대한 정의 필요
prev_status = "attached"

#현재의 signal 상태를 저장
signal_before = 0
signal_now = 0

# vol 변동을 대기하는 상태 변수, long or short or None
wait_for_vol_signal = 0 

# vol_diff threshold
STD_DIFF_THRESHOLD = 0.0

# 단위 매매 수량
QTY_PER_TRADE = 50

# vol db인지 sec db인지
if db_table[-3:] == 'vol':
    price_col = 'vwap'
elif db_table[-3:] == 'sec':
    price_col = 'close'
else:
    raise ValueError("Unexpected db_table name")


#ema_fast, ema_slow 시작점 정의, ema는 dfmkt에 저장한다
dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], price_col]
dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], price_col]
dfmkt.at[dti[0], 'tick_apo'] = 0
dfmkt.at[dti[0], 'std_factor'] = np.nan


"""vwap index기준 test loop시작"""
for dti_pre, dti_now in zip(dti, dti[1:]):
    # dfmkt_tilnow = dfmkt[:dti_now+1] 
    prc = dfmkt.loc[dti_now, price_col]
    
    # 현재시간
    now = dfmkt.at[dti_now, 'datetime'] # pd.Timestamp
            
    if dti_now >= STD_DIFF_CAL_WINDOW:
        # std factor update
        std_tilnow = dfmkt[:dti_now+1]['close'].std() # dti_now+1로 슬라이싱 해야 dti_now 포함
        std_tilnow_ref = std_ref_table[:now.time()].iloc[-1]
        std_factor = std_tilnow / std_tilnow_ref
        # if std_factor == 0 or np.isnan(std_factor):
        #     std_factor = 1
        dfmkt.at[dti_now, 'std_factor'] = std_factor
        std_factor_rm = dfmkt[:dti_now+1]['std_factor'].values[-STD_DIFF_CAL_WINDOW:].mean()
        std_diff = std_factor - std_factor_rm
        
        # 당일 현재의 Z-score 정의        
        dfmkt.at[dti_now, 'zs'] = (prc - dfmkt[:dti_now+1]['close'].mean()) / std_tilnow
        # 어제부터 이어오는 Z-score 정의
        dfmkt.at[dti_now, 'zs'] = (prc - dfmkt[:dti_now+1]['close'].mean()) / std_tilnow
        
    else:
        std_factor_rm = std_diff = np.nan
    
    dfmkt.at[dti_now, 'std_factor_rm'] = std_factor_rm
    dfmkt.at[dti_now, 'std_diff'] = std_diff
        
    # ema update    
    # ema_fast = fast_coeff * prc + (1-fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
    # ema_slow = slow_coeff * prc + (1-slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
    ema_fast = std_factor*fast_coeff * prc + (1-std_factor*fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
    ema_slow = std_factor*slow_coeff * prc + (1-std_factor*slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
    tick_apo = dt.tick_conversion * (ema_fast - ema_slow)
    dfmkt.at[dti_now, 'ema_fast'] = ema_fast
    dfmkt.at[dti_now, 'ema_slow'] = ema_slow
    dfmkt.at[dti_now, 'tick_apo'] = tick_apo
    
    # std_factor slope
    slop_f, slop_s = calSlope(dfmkt[:dti_now+1]['std_factor'].values, 10, 100)
    dfmkt.at[dti_now, 'slop_f'] = slop_f
    dfmkt.at[dti_now, 'slop_s'] = slop_s
    
    # cross status update
    tested_status = crossTest(dfmkt.at[dti_now, 'ema_fast'], 
                              dfmkt.at[dti_now, 'ema_slow'], 
                              margin=margin)
    
    # 장종료시 청산
    if (dti_now == dti[-1]) and (dt.getOpenPositionQty() != 0):
        dt.exitOpenPosition(trade_time=now,
                            mid_price=prc,
                            remark='close_by_time')
        break
        
    # 시그널 탐색
    if not np.isnan(std_diff):
        
        if (prev_status == "above" or prev_status == "below") \
            and (tested_status == "attached"):
            prev_status = tested_status
            
            # # 대기신호 처리
            # if (wait_for_vol_signal != 0) \
            #     and (std_diff > STD_DIFF_THRESHOLD) \
            #     and (dt.getOpenPositionQty() == 0):
            #         dt.logTrade(trade_time=now,
            #                     trade_price=prc + signal_now * 0.5 * dt.tick_value,
            #                     trade_qty=signal_now * int(QTY_PER_TRADE * std_factor),
            #                     trade_type='ini',
            #                     signal_price=prc,
            #                     remark='delayed ini')
                
        
        elif prev_status == tested_status:
            # # 대기신호 처리
            # if (wait_for_vol_signal != 0) \
            #     and (std_diff > STD_DIFF_THRESHOLD) \
            #     and (dt.getOpenPositionQty() == 0):
            #         dt.logTrade(trade_time=now,
            #                     trade_price=prc + signal_now * 0.5 * dt.tick_value,
            #                     trade_qty=signal_now * int(QTY_PER_TRADE * std_factor),
            #                     trade_type='ini',
            #                     signal_price=prc,
            #                     remark='delayed ini')
            pass
            
        # below -> above or above -> below or attahced -> above/below
        else: 
            prev_status = tested_status
            signal_now = 1 if tested_status == "above" else -1
            #!!!이 경우에만 시그널 발생
            if signal_before != signal_now: 
                print(now.time(), "signal", prc, round(std_diff, 3), signal_now)
                
                signal_before = signal_now
                
                if std_diff > STD_DIFF_THRESHOLD: 
                    # 청산, 진입 다 실행
                    if dt.getOpenPositionQty() == 0:
                        dt.logTrade(trade_time=now,
                                    trade_price=prc + signal_now * 0.5 * dt.tick_value,
                                    trade_qty=signal_now * int(QTY_PER_TRADE * std_factor),
                                    signal_price=prc,
                                    trade_type='ini')
                    else:
                        if signal_now * dt.getOpenPositionQty() > 0: 
                            # 롱시그널인데 이미 롱이 있음, 숏시그널인데 이미 숏이 있음
                            print("check logic, something went wrong")
                            print(signal_now, dt.getOpenPositionQty())
                        else:
                            dt.exitOpenPosition(trade_time=now,
                                                mid_price=prc,
                                                remark='hi_vol, signal')
                            dt.logTrade(trade_time=now,
                                        trade_price=prc + signal_now * 0.5 * dt.tick_value,
                                        trade_qty=signal_now * int(QTY_PER_TRADE * std_factor),
                                        signal_price=prc,
                                        trade_type='ini')
                else:
                    # std_diff가 threshold 아래인 경우
                    # 청산은 실행, 진입은 안하고 대기 신호만 남김
                    if dt.getOpenPositionQty() == 0:
                        wait_for_vol_signal = signal_now
                        print("wait signal marked")
                    else:
                        if signal_now * dt.getOpenPositionQty() > 0: 
                            # 롱시그널인데 이미 롱이 있음, 숏시그널인데 이미 숏이 있음
                            print("check logic, something went wrong")
                            print(signal_now, dt.getOpenPositionQty())
                        else:
                            dt.exitOpenPosition(trade_time=now,
                                                mid_price=prc,
                                                signal_price=prc,
                                                remark='lo_vol, signal')
                    
                
                
            # dt.logTrade(trade_time, trade_price, trade_qty, trade_type)
            # df_result.at[dti_now, 'direction'] = signal_now
            # signal_before = signal_now
            
            # #timedelta --> datetime.time형식으로 변환
            # df_result.at[dti_now, 'signal_time'] = dfmkt.loc[dti_now,'datetime']
                
            # df_result.at[dti_now, 'signal_vwap'] = prc
            # df_result.at[dti_now, 'price'] = 'TBD'
            # df_result.at[dti_now, 'ema_fast'] = dfmkt.at[dti_now, 'ema_fast']
            # df_result.at[dti_now, 'ema_slow'] = dfmkt.at[dti_now, 'ema_slow']
            # df_result.at[dti_now, 'local_index'] = dti_now
"""index기준 test loop종료"""       
print(dt.book)

#%% PLOT

from matplotlib import pyplot as plt
from matplotlib import gridspec

fig = plt.figure(figsize=(8,8))

spec = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2,1])

ax = fig.add_subplot(spec[0])

for i in dt.book.index:
    marker = "^" if dt.book.loc[i]['trade_qty'] > 0 else "v"
    color = "tab:red" if marker == "^" else "b"
    x = dt.book.loc[i]['trade_time']
    y = dt.book.loc[i]['trade_price']
    ax.scatter(x, y, color=color, marker=marker, s=200)

ax.plot(dfmkt.datetime, dfmkt[price_col], linewidth=0.5)
ax.plot(dfmkt.datetime, dfmkt['ema_fast'])
ax.plot(dfmkt.datetime, dfmkt['ema_slow'])

ax.axhline(y=dt.yday_close, color='black', linestyle='dashed')
ax.axhline(y=dt.yday_lo, color='blue', linestyle='dashed', linewidth=0.5)
ax.axhline(y=dt.yday_hi, color='red', linestyle='dashed', linewidth=0.5)

ax2 = ax.twinx()
ax2.spines["right"].set_position(("axes", 1.05)) ## 오른쪽 옆에 y축 추가

ax2.plot(dfmkt.datetime, dfmkt['std_factor'], color="violet", linewidth=0.7)
ax2.plot(dfmkt.datetime, dfmkt['std_factor'].expanding().mean(), color="skyblue", linewidth=1.7)
ax2.plot(dfmkt.datetime, dfmkt['std_factor_rm'], color="skyblue", linewidth=0.7)


# ax25 = ax.twinx()
# ax25.spines["right"].set_position(("axes", 1.15)) ## 오른쪽 옆에 y축 추가
# ax25.plot(dfmkt.datetime, dfmkt['close'].expanding(6*15).std(), 
#           color="black", linewidth=0.7)
# ax25.fill_between(dfmkt.datetime, dfmkt['close'].rolling(6*30).std(), 0, 
#                     color="orange", alpha=0.3)
# ax25.plot(dfmkt.datetime, std_ref_table, color="grey", linewidth=0.7)
# ax25.plot(dfmkt.datetime, dfmkt['std_factor_rm'], color="skyblue", linewidth=0.7)

ax3 = ax.twinx()
ax3.spines["right"].set_position(("axes", 1.1)) ## 오른쪽 옆에 y축 추가
ax3.fill_between(dfmkt.datetime, dfmkt['std_diff'], 0, alpha=0.3)

# ax_zs = ax.twinx()
# ax_zs.spines["right"].set_position(("axes", 1.2)) ## 오른쪽 옆에 y축 추가
# ax_zs.fill_between(dfmkt.datetime, dfmkt['zs'], 0, alpha=0.3)

bx = fig.add_subplot(spec[1])
bx.fill_between(dfmkt.datetime, dfmkt.tick_apo, 0, alpha=0.2)

bx2 = bx.twinx()
bx2.spines["right"].set_position(("axes", 1.1)) ## 오른쪽 옆에 y축 추가
bx2.fill_between(dfmkt.datetime, dfmkt['slop_f'], 0, alpha=0.7 ) # 당일 일누적 변동성
bx2.fill_between(dfmkt.datetime, dfmkt['slop_s'], 0, alpha=0.3 ) # 당일 일누적 변동성 롤링 평
# bx2.plot(dfmkt.datetime, dfmkt.close.rolling(6*20).std(), ) # 당일 롤링


# Set plot name as xlabel
font = {'family': 'verdana',
        'color': 'darkblue',
        'weight': 'bold',
        'size': 12,
        }
pl = int(dt.getCumPl(dfmkt.close.iloc[-1]))
num_pos = 0 if dt.book.empty else dt.book.pos_id.iloc[-1]
plot_name = f'{date}   Qty: {QTY_PER_TRADE}  SDTHRE: {STD_DIFF_THRESHOLD}   PL: {pl:,}   num_pos: {num_pos}'
ax.set_xlabel(plot_name, fontdict=font)
plt.show()

    # return dt


#%% BTST

# ld = list(util.getDailyOHLC().index)
# # ld = [d for d in ld if d.year in [2015, 2016, ]]
# ld = [d for d in ld if d.year >= 2021 ]
# # ld = [d for d in ld if d == datetime.date(2021, 2, 16)]
# # ld = [d for d in ld if d == datetime.date(2021, 2, 5)]

# #일간 PL을 기록하는 dataframe
# dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])


# for i, day in enumerate(ld):
        
#     dt = tes(day)
    
#     pl_of_the_day = dt.getCumPl()
    
#     print(f'pl : {dt.getCumPl():,}')
#     print(f'trade volume : {dt.book.trade_qty.abs().sum():,}')
    
#     dfpl.at[i, 'date'] = day
    
#     dfpl.at[i, 'pl'] = pl_of_the_day
    
    
#     #누적결과
#     cumsum = round(dfpl.pl.sum(), 1)
#     mean = round(dfpl.pl.mean(), 2)
#     std = round(dfpl.pl.std(), 3)
#     sr = round(mean / std, 3)
#     num_trade_cumul = dfpl.num_trade.sum()
#     print(f'Cumul | cumsum: {int(cumsum):,}  mean:{int(mean):,}  SR: {sr}  trades: {num_trade_cumul}',
#           "\n---------------------------------------------------------------")

# # 결과 출력및 저장
# # dfpl 수정됨, call by reference
# pl_mon, pl_yr = util.reportSummary(dfpl, show_hist="n")
  

