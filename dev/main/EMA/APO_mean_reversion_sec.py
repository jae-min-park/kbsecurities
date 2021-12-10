# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 10:20:11 2021

@author: infomax
"""

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import gridspec
import numpy as np
import math
import datetime
import os
from tqdm import tqdm
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util
from DayTradeBook import DayTradeBook

               
def tradeMRbyAPO(
    date, 
    yesterday = None,
    db_table='lktbf50vol', 
    dfmkt = None,
    fast_coeff=0.20, 
    slow_coeff=0.05, 
    window_ref=5,
    threshold_apo_coeff = 2.0,
    max_qty=200,
    qty_per_trade=5,
    min_profit = 3*10**6,
    lc_pt_ratio = 3.0,
    min_price_move_from_last_trade=0.05,
    losscut="Y",
    ):

    
    """
    -. fast ema - slow ema인 APO(tick_diff)를 mean reversion에 활용
    -. negative skew 전략
    -. 최근 N일 장중 stdev의 평균을 기준점으로 stdev factor 도입
    
    Parameters
    ----------
    date : datetime.date
        테스트하고자 하는 날짜
        
    db_table : str
        몇개짜리 볼륨봉을 쓸 것인지 = DB의 table명과 동일하게
        
    fast_coeff, slow_coeff : ema용 Coefficient
    
    tick_cross_margin : fast가 slow의 ??틱 위에서 long을 시작할 것인지
    
    window_ref : 며칠간의 window로 diff의 max값을 세팅할 것인지
    
    Returns
    -------
    result = ?????????????????????
    
    """
    db_table='lktbf_10sec'
    fast_coeff=0.050
    slow_coeff=0.008
    window_ref=5
    threshold_apo_coeff = 1.3
    max_qty=100
    qty_per_trade=50
    min_profit = 5*10**6
    lc_pt_ratio = 3
    min_price_move_from_last_trade=0.03
    dfmkt=None
    
    # date = datetime.date(2021, 11, 19)
    
    K_FAST=fast_coeff
    K_SLOW=slow_coeff
    
    MAX_QTY=max_qty
    QTY_PER_TRADE=qty_per_trade
    
    rw = 6*15
    
    losscut = "n"
    dti_cut = 9999999   
    trading_time_start=None
    
    dt = DayTradeBook(date, db_table)
    
    TICK_VALUE = dt.tick_value
    KRW_COMMISSION_PER_CONTRACT = dt.krw_commission_per_contract
    KRW_VALUE_1PT = dt.krw_value_1pt
    
    TICK_CONVERSION = dt.tick_conversion
    
    
    
    #%% CONFIGURATION 
    # look back period 및 트레이딩을 위한 설정값들 정의
    
    apo_std_recent = util.apoStdRecent(date, db_table, fast_coeff, slow_coeff,
                                       look_back_days=10)
    
    se_std_table = util.stdTimeTable(date, db_table, look_back_days=20)
    
    """
    최근 N일의 diff 분포에서 N sigma에 해당하는 diff에 도달하면 진입
    2.0 sigma로 설정하여 전체 trading time에서 4.6%의 극단값에 진입
    1.5 sigma -> 13.4%
    1.0 sigma -> 31.7%
    """
    THRESHOLD_APO_COEFF = threshold_apo_coeff
    ENTRY_THRESHOLD_APO = THRESHOLD_APO_COEFF * apo_std_recent * TICK_CONVERSION
    print(f'APO {THRESHOLD_APO_COEFF} sigma : {ENTRY_THRESHOLD_APO:.3f}')
    
    WATCH_VOL_DURATION = pd.Timedelta(hours=0.5, minutes=0)
    TRADING_ENDS = pd.Timestamp.combine(date, datetime.time(15,0))
    
    # 익절기준 손익 : look back window 일간std의 50%
    # MIN_KRW_PROFIT_TO_CLOSE = KRW_VALUE_1PT * 0.5 * timely_std_list[-1] * QTY_PER_TRADE 
    MIN_KRW_PROFIT_TO_CLOSE = min_profit 
    
    LOSSCUT_KRW = -lc_pt_ratio * MIN_KRW_PROFIT_TO_CLOSE # 익절금액의 ??배
    # LOSSCUT_KRW = -10**7
    
    # MIN_PRICE_MOVE_FROM_LAST_TRADE = 0.3 * timely_std_list[-1] # look back window 일간std의 20%
    MIN_PRICE_MOVE_FROM_LAST_TRADE = min_price_move_from_last_trade # look back window 일간std의 20%
    
    
    
    #%% main test
    
    # 테스트를 위한 해당일의 시장 data load
    if dfmkt is None or dfmkt.empty == True:
        dfmkt = util.setDfData(date, date, db_table)
    
    # local index
    dti = dfmkt.index
    
    # 시작점 boundary condition 정의
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'close']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'close']
    dfmkt.at[dti[0], 'tick_apo'] = 0
    dfmkt.at[dti[0], 'std_factor'] = 1
    
    # 시가시간, 장 초반 변동성 파악하기 위한 시간 정의 필요
    siga_time = pd.Timestamp.combine(date, dt.siga_time)
    WATCH_VOL_UNTIL = siga_time + WATCH_VOL_DURATION # pd.Timedelta
    
    
    """10초 단위의 close(또는 H L)기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        
        last_prc = dfmkt.loc[dti_now,'close']
        
        # 현재시간
        now = dfmkt.at[dti_now, 'datetime'] # pd.Timestamp
                
        # std factor update
        std_tilnow = dfmkt[:dti_now]['close'].expanding(2).std().iloc[-1]
        std_tilnow_ref = se_std_table[:now.time()].iloc[-1]
        std_factor = std_tilnow / std_tilnow_ref
        if std_factor == 0 or np.isnan(std_factor):
            std_factor = 1
        
        dfmkt.at[dti_now, 'std_factor'] = std_factor
        dfmkt.at[dti_now, 'sell_entry'] = ENTRY_THRESHOLD_APO * std_factor
        dfmkt.at[dti_now, 'buy_entry'] = -ENTRY_THRESHOLD_APO * std_factor
        
        # last_prc 기준으로 ema update
        # 즉, volume봉 내에서 last가 최신이므로 거래는 vwap, 시그널은 last prc로 정의
        dfmkt.at[dti_now, 'ema_fast'] = K_FAST * std_factor * last_prc \
            + (1 - K_FAST * std_factor) * dfmkt.at[dti_pre, 'ema_fast']
        
        dfmkt.at[dti_now, 'ema_slow'] = K_SLOW * std_factor * last_prc \
            + (1 - K_SLOW * std_factor) * dfmkt.at[dti_pre, 'ema_slow']
        
        tick_apo = TICK_CONVERSION * (dfmkt.at[dti_now, 'ema_fast'] - dfmkt.at[dti_now, 'ema_slow'])
        dfmkt.at[dti_now, 'tick_apo'] = tick_apo
        tick_apo_chg = tick_apo - dfmkt.at[dti_pre, 'tick_apo']
        
        # last_prc 기준으로 pl 계산, 현재까지의 누적 pl을 기록함
        net_pl = dt.getCumPl(last_prc)
        
        dfmkt.at[dti_now, 'net_pl'] = net_pl
        
        if now.time() >= (TRADING_ENDS + pd.Timedelta(minutes=10)).time():
            # open_qty = dt.getOpenPositionQty()
                
            # 포지션 청산
            if dt.getOpenPositionQty() != 0:
                dt.exitOpenPosition(trade_time=now, 
                                    mid_price=last_prc,
                                    remark='by_time')
            
        
        # 장 초반 vol watch로 트레이딩 미실시, 장 막판 트레이딩 진입 안함
        elif now > WATCH_VOL_UNTIL and now < TRADING_ENDS :
    
            # open_position_qty 를 기준으로 조건 탐색
            
            # 현재 포지션 없음
            if dt.getOpenPositionQty() == 0:
                # 진입 test
                # threshold 조건 & apo가 이전가격대비 반대방향으로 진행 (꺾이는 경우)
                # & last_trade_price 대비 충분히 움직임
                
                # 롱 진입
                b1 = tick_apo < -ENTRY_THRESHOLD_APO * std_factor
                b2 = tick_apo_chg > 0
                b3 = dt.isMovedEnoughFromLastTrade(last_prc, MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor)
    
                # 숏 진입
                if (tick_apo > ENTRY_THRESHOLD_APO * std_factor) \
                    and (tick_apo_chg < 0) \
                    and dt.isMovedEnoughFromLastTrade(
                        last_prc,
                        MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor
                        ):
                    dt.logTrade(trade_time=now, 
                                trade_price=last_prc - 0.5 * TICK_VALUE,
                                trade_qty=-QTY_PER_TRADE,
                                trade_type='ini')
                
                elif (tick_apo < -ENTRY_THRESHOLD_APO * std_factor) \
                    and (tick_apo_chg > 0) \
                    and dt.isMovedEnoughFromLastTrade(
                        last_prc,
                        MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor
                        ):
                    # print("!!!!")
                    dt.logTrade(trade_time=now, 
                                trade_price=last_prc + 0.5 * TICK_VALUE,
                                trade_qty=QTY_PER_TRADE,
                                trade_type='ini')
            
            # Open Position 있음
            else: 
                open_pnl = dt.getOpenPnl(last_prc)
                open_qty = dt.getOpenPositionQty()
                
                # 포지션 익절 or 손절, 이유는 다르지만 수량 방향 같으므로 한번에 처리
                bool_profit_taking = open_pnl > MIN_KRW_PROFIT_TO_CLOSE / std_factor
                bool_loss_cut = open_pnl < LOSSCUT_KRW / std_factor
                
                if bool_profit_taking or bool_loss_cut:
                    dt.exitOpenPosition(trade_time=now,
                                        mid_price=last_prc,
                                        remark='PT' if bool_profit_taking else 'LC')
                        
                    
                # 손익으로는 청산 조건에 해당 없으므로 포지션 추가 또는 apo 기준 청산 또는 nothing
                else:
                    # apo조건 청산, apo 꺾이는 것 확인 후 청산
                    if (tick_apo <= 0 and open_qty < 0 and tick_apo_chg > 0) \
                        or (tick_apo >= 0 and open_qty > 0 and tick_apo_chg <0):
                        dt.exitOpenPosition(trade_time=now,
                                            mid_price=last_prc,
                                            remark='apo_change')
                    
                    # add 조건 만족하면 포지션 add
                    # entry조건 만족 & max 수량 이내 & 마지막거래대비 충분히 움직임 & APO 꺾임
                    
                    # 숏 애드
                    elif (tick_apo > ENTRY_THRESHOLD_APO * std_factor) \
                        and (abs(open_qty) < MAX_QTY) \
                        and dt.isMovedEnoughFromLastTrade(
                            last_prc,
                            MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor) \
                        and (tick_apo < dfmkt.loc[dti_pre, 'tick_apo']): 
    
                        dt.logTrade(trade_time=now, 
                                    trade_price=last_prc - 0.5 * TICK_VALUE,
                                    trade_qty=-QTY_PER_TRADE,
                                    trade_type='add')
                        
                    # 롱 애드
                    elif (tick_apo < -ENTRY_THRESHOLD_APO * std_factor) \
                        and (abs(open_qty) < MAX_QTY) \
                        and dt.isMovedEnoughFromLastTrade(
                            last_prc,
                            MIN_PRICE_MOVE_FROM_LAST_TRADE * std_factor) \
                        and (tick_apo > dfmkt.loc[dti_pre, 'tick_apo']): 
    
                        dt.logTrade(trade_time=now, 
                                    trade_price=last_prc + 0.5 * TICK_VALUE,
                                    trade_qty=QTY_PER_TRADE,
                                    trade_type='add')
               
      
            
    """index기준 test loop종료"""       
            
    
    print(f'net_pl : {net_pl:,}')
    print(f'trade qty sum : {int(dt.book.trade_qty.abs().sum()):,}')
    
    
    #%% PLOT
    
    # dfmkt = dfmkt[dfmkt['datetime'] < pd.Timestamp(2021,1,14,12,0,0)]
    # dfmkt = dfmkt[dfmkt['datetime'] < pd.Timestamp.combine(date, datetime.time(13,15))]
    
    fig = plt.figure(figsize=(10,10))
    
    spec = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2,1])
    
    ax = fig.add_subplot(spec[0])
    
    # dft = dfmkt.set_index(dfmkt.time)
    ax.plot(dfmkt.datetime, dfmkt['close'], linewidth=0.5)
    ax.plot(dfmkt.datetime, dfmkt['ema_fast'])
    ax.plot(dfmkt.datetime, dfmkt['ema_slow'])
    
    
    # 전일종가 H-line
    ax.axhline(y=dt.yday_close, color='black', linestyle='dashed')
    
    # ax2 = ax.twinx()
    # ax2.fill_between(dfmkt.datetime, dfmkt['net_pl'], 0, alpha=0.3, color="gray")
    # ax2.scatter(dfmkt.index[-1], 
    #             dfmkt['net_pl'].iloc[-1],
    #             color="tab:red" if dfmkt['net_pl'].iloc[-1] > 0 else "b", 
    #             marker="o", s=50)
    
    # ax3 = ax.twinx()
    # ax3.spines["right"].set_position(("axes", 1.05)) ## 오른쪽 옆에 y축 추가
    # ax3.fill_between(dfmkt.datetime, dfmkt['actual_qty'], 
    #                  where= dfmkt['actual_qty']>0, alpha=0.1, color="red")
    # ax3.fill_between(dfmkt.datetime, dfmkt['actual_qty'], 
    #                  where= dfmkt['actual_qty']<0, alpha=0.1, color="b")
    # ax3.scatter(dfmkt.index[-1], 
    #             dfmkt['actual_qty'].iloc[-1],
    #             color="tab:red" if dfmkt['actual_qty'].iloc[-1] > 0 else "b", 
    #             marker="^" if dfmkt['actual_qty'].iloc[-1] > 0 else "v",
    #             s=50)
    
    ax4 = ax.twinx()
    ax4.spines["right"].set_position(("axes", 1.1)) ## 오른쪽 옆에 y축 추가
    ax4.plot(dfmkt.datetime, dfmkt['std_factor'], color="r", linewidth=0.5)
    ax4.plot(dfmkt.datetime, dfmkt['std_factor'].rolling(6*10).mean(), color="grey", linewidth=0.5)
    
    ax_below = fig.add_subplot(spec[1])
    ax_below.fill_between(dfmkt.datetime, dfmkt['tick_apo'], 0, alpha=0.3, color="blue")
    ax_below.plot(dfmkt.datetime, dfmkt['sell_entry'])
    ax_below.plot(dfmkt.datetime, dfmkt['buy_entry'])
    
    # dt.addDatetimeColumn()
    for i in dt.book.index:
        marker = "^" if dt.book.loc[i]['trade_qty'] > 0 else "v"
        color = "tab:red" if marker == "^" else "b"
        x = dt.book.loc[i]['trade_time']
        y = dt.book.loc[i]['trade_price']
        y_below = dfmkt.loc[dfmkt['datetime']==x]['tick_apo']
        ax.scatter(x, y, color=color, marker=marker, s=200)
        ax_below.scatter(x, y_below, color=color, marker=marker, s = 50)
    
    # ax_below2 = ax_below.twinx() # rolling std
    # ax_below2.spines["right"].set_position(("axes", 1.1)) ## 오른쪽 옆에 y축 추가
    
    # ax_below3 = ax_below.twinx() # rolling std
    # ax_below3.spines["right"].set_position(("axes", 1.2)) ## 오른쪽 옆에 y축 추가
    # dfmkt['rolling_std'] = dfmkt.close.rolling(rw).std()
    # ax_below3.plot(dfmkt.datetime, dfmkt['rolling_std'], color="b")
    
    # dfmkt['rolling_mean'] = dfmkt.close.rolling(rw).mean().shift(1)
    # dfmkt['zs'] = (dfmkt['close'] - dfmkt['rolling_mean']) / dfmkt['rolling_std']
    # ax5 = ax.twinx()
    # ax5.spines["right"].set_position(("axes", 1.2)) ## 오른쪽 옆에 y축 추가
    # ax5.plot(dfmkt.datetime, dfmkt['zs'], color="purple", linewidth=0.3)
    
    
    from scipy.signal import argrelextrema 
    # ba_peak_max = argrelextrema(dfmkt['rolling_std'].values, np.greater_equal, 
    #                             order=rw)[0]
    # dfmkt['max_std'] = dfmkt.iloc[ba_peak_max]['rolling_std']
    # dfmkt['max_close'] = dfmkt.iloc[ba_peak_max]['close']
    # ax_below3.scatter(dfmkt.datetime, dfmkt['max_std'], color="b")
    # ax.scatter(dfmkt.datetime, dfmkt['max_close'], color="b")
    
    ba_peak_fast = argrelextrema(dfmkt['ema_fast'].values, 
                                     np.greater_equal, order=6*10)[0]
    ba_valy_fast = argrelextrema(dfmkt['ema_fast'].values, 
                                     np.less_equal, order=6*10)[0]
    dfmkt['fast_peak'] = dfmkt.iloc[ba_peak_fast]['ema_fast']
    dfmkt['fast_valy'] = dfmkt.iloc[ba_valy_fast]['ema_fast']
    # dfmkt['max_close'] = dfmkt.iloc[ba_peak_max]['close']
    # ax_below3.scatter(dfmkt.datetime, dfmkt['max_std'], color="b")
    ax.scatter(dfmkt.datetime, dfmkt['fast_peak'], color="r")
    ax.scatter(dfmkt.datetime, dfmkt['fast_valy'], color="b")
    
    
    base = 5
    y_absmax = dfmkt['tick_apo'].abs().max()
    y_abxmax_adj = int(base * math.ceil(y_absmax/base))
    y_major_ticks = np.arange(-y_abxmax_adj, y_abxmax_adj, 2*base)
    y_minor_ticks = np.arange(-y_abxmax_adj, y_abxmax_adj, base)
    
    ax_below.set_yticks(y_major_ticks)
    ax_below.set_yticks(y_minor_ticks, minor=True)
    
    ax_below.grid(which='major', color='grey', linewidth=0.6,linestyle='-')
    ax_below.grid(which='minor', color='grey', linewidth=0.4,linestyle=':')
    ax_below.yaxis.set_ticks_position('left')
    
    
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


    return dfmkt


#%% TEST PLOT

#일봉기준 전체 date list
ld = list(util.getDailyOHLC().index)
# ld = [d for d in ld if d.year in [2015, 2016, ]]
# ld = [d for d in ld if d.year >= 2021 ]
ld = [d for d in ld if d == datetime.date(2021, 1, 6)]
# ld = [d for d in ld if d == datetime.date(2021, 7, 21)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])


for i, day in enumerate(ld):
        
    dfmkt = tradeMRbyAPO(
        day, 
        yesterday = None,
        db_table='lktbf_10sec', 
        dfmkt = None,
        fast_coeff=0.05, 
        slow_coeff=0.015, 
        window_ref=5,
        threshold_apo_coeff = 1.5,
        max_qty=160,
        qty_per_trade=20,
        min_profit=5*10**6,
        lc_pt_ratio=10,
        losscut="Y"
        )
    
    pl_of_the_day = dfmkt.net_pl.dropna().iloc[-1]
    
    print(f'pl : {pl_of_the_day:,}')
    # print(f'trade volume : {dfmkt.trade_qty.abs().sum():,}')
    
    dfpl.at[i, 'date'] = day
    
    dfpl.at[i, 'pl'] = pl_of_the_day
    
    
    #누적결과
    cumsum = round(dfpl.pl.sum(), 1)
    mean = round(dfpl.pl.mean(), 2)
    std = round(dfpl.pl.std(), 3)
    sr = round(mean / std, 3)
    num_trade_cumul = dfpl.num_trade.sum()
    print(f'Cumul | cumsum: {int(cumsum):,}  mean:{int(mean):,}  SR: {sr}  trades: {num_trade_cumul}',
          "\n---------------------------------------------------------------")

# 결과 출력및 저장
# dfpl 수정됨, call by reference
pl_mon, pl_yr = util.reportSummary(dfpl, show_hist="n")










