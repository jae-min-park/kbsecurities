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

def calTargetQty(
        max_qty,
        abs_max_short_qty,
        tick_diff_now,
        tick_cross_margin, 
        tick_diff_of_max_qty, 
        method="linear"
        ):
    
    # linear 증감을 위한 1차함수 계수
    # qty_per_tick_diff_overmargin = max_qty / (tick_diff_of_max_qty - tick_cross_margin)
    
    # cross_margin 이내의 경우
    if abs(tick_diff_now) <= tick_cross_margin:
        target_qty = 0
    
    # 롱 시그널
    elif tick_diff_now > tick_cross_margin:
        if method == "linear":
            target_qty_raw = max_qty * tick_diff_now / tick_diff_of_max_qty
            target_qty = target_qty_raw if target_qty_raw < max_qty else max_qty
        elif method == "power":
            target_qty_raw = max_qty * (tick_diff_now / tick_diff_of_max_qty)**2
            target_qty = target_qty_raw if target_qty_raw < max_qty else max_qty
        else:
            ValueError("Wrong method")
    
    # 숏 시그널
    elif tick_diff_now < -tick_cross_margin:
        if method == "linear":
            target_qty_raw = abs_max_short_qty * tick_diff_now / tick_diff_of_max_qty
            target_qty = target_qty_raw if -target_qty_raw < abs_max_short_qty else -abs_max_short_qty
        elif method == "power":
            # 제곱하니까 - 부호 붙여줌
            target_qty_raw = -abs_max_short_qty * (tick_diff_now / tick_diff_of_max_qty)**2
            target_qty = target_qty_raw if -target_qty_raw < abs_max_short_qty else -abs_max_short_qty
        else:
            ValueError("Wrong method")
        
    else:
        raise ValueError("Unexpected tick_diff_now status")
    
    return int(target_qty)


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
    # date = datetime.date(2021, 8, 17)
    
    yesterday = None
    db_table='lktbf100vol'
    dfmkt = None
    K_FAST=fast_coeff
    K_SLOW=slow_coeff
    
    # window_ref=window_ref
    
    MAX_QTY=max_qty
    QTY_PER_TRADE=qty_per_trade
    
    losscut = "n"
    dti_cut = 9999999   
    trading_time_start=None
    
    
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
    
    print(product)
    
    #%% CONFIGURATION 
    # look back period 및 트레이딩을 위한 설정값들 정의
    
    ar_diff_window = np.array([])
    refmkt_list = []
    apo_std_list = []
    
    for i in range(1, window_ref+1):
        if yesterday != None:
            d = yesterday
        else:
            d = util.date_offset(date, -i)
        # print(i, d)
        refmkt = util.setDfData(d, d, db_table)
        refdti = refmkt.index
        
        refmkt.at[refdti[0], 'ema_fast'] = refmkt.at[refdti[0], 'vwap']
        refmkt.at[refdti[0], 'ema_slow'] = refmkt.at[refdti[0], 'vwap']
        
        for refdti_pre, refdti_now in zip(refdti, refdti[1:]):
            last_prc = refmkt.loc[refdti_now,'close']
            
            refmkt.at[refdti_now, 'ema_fast'] = K_FAST * last_prc \
                + (1 - K_FAST) * refmkt.at[refdti_pre, 'ema_fast']
            
            refmkt.at[refdti_now, 'ema_slow'] = K_SLOW * last_prc \
                + (1 - K_SLOW) * refmkt.at[refdti_pre, 'ema_slow']
        
        ar_diff_day = np.array(refmkt['ema_fast']) - np.array(refmkt['ema_slow'])
        
        print(f'{d}  {ar_diff_day.mean()*100:.1f}  {ar_diff_day.std()*100:.1f}  {refmkt.close.std()*100:.1f}')
        
        refmkt['cum_std'] = refmkt['close'].expanding(2).std()
        
        apo_std_list.append(np.std(ar_diff_day))
        
        refmkt_list.append(refmkt)
    
    # look back window의 시간대별 평균 변동성(cum std) 기록, 분단위
    timely_std_list = []
    
    for ti in pd.timedelta_range(start='9:00:00', end='15:45:00', freq='1min', closed='right'):
        # print(ti)
        std_til_ti = []
        for refmkt in refmkt_list:
            if refmkt['time'].iloc[0] == pd.Timedelta(hours=9):
                std_til_ti.append(refmkt[refmkt['time'] <= ti]['cum_std'].iloc[-1])
            else:
                pass
        timely_std_list.append(np.mean(std_til_ti))
        
    # print(timely_std_list)
    # pd.Series(timely_std_list).plot()
    
    """
    최근 N일의 diff 분포에서 N sigma에 해당하는 diff에 도달하면 진입
    2.0 sigma로 설정하여 전체 trading time에서 4.6%의 극단값에 진입
    1.5 sigma -> 13.4%
    1.0 sigma -> 31.7%
    """
    THRESHOLD_APO_COEFF = threshold_apo_coeff
    ENTRY_THRESHOLD_APO = THRESHOLD_APO_COEFF * np.mean(apo_std_list) * TICK_CONVERSION
    print(f'APO {THRESHOLD_APO_COEFF} sigma : {ENTRY_THRESHOLD_APO:.3f}')
    
    WATCH_VOL_UNTIL = datetime.time(9,30)
    TRADING_ENDS = datetime.time(15,00)
    
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
    # dfmkt = dfmkt[:400]
    
    # dfmkt = dfmkt[:dti_cut]
    
    # local index
    dti = dfmkt.index
    
    # 시작점 boundary condition 정의
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'tick_apo'] = 0
    dfmkt.at[dti[0], 'std_factor'] = 1
    
    dfmkt.at[dti[0], 'trade_price'] = 0
    dfmkt.at[dti[0], 'trade_qty'] = 0
    dfmkt.at[dti[0], 'actual_qty'] = 0
    
    trade_qty = 0
    
    # 시가거래 volume봉 개수, 장 시작후 초기값 세팅 전까지 trade 유보 위해 사용
    siga_time = dfmkt.at[dti[0], 'datetime']
    siga_count = dfmkt[dfmkt['datetime'] == siga_time].shape[0]
    
    
    # open_position에 대한 전역변수들
    open_position_qty = 0
    open_position_trade_qty_list = []
    open_position_trade_price_list = []
    open_pnl_krw = 0
    last_trade_price = 0
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        
        # 실제 운용시 vwap이 last보다 빠른 정보일 것
        vwap = dfmkt.loc[dti_now,'vwap']
        last_prc = dfmkt.loc[dti_now,'close']
        
        # 현재시간
        now = dfmkt.at[dti_now, 'datetime']
        # 장 시작후 몇분이 경과했는지
        now_n_min = max(1, int((now - siga_time).seconds / 60))
        
        # std factor update
        std_tilnow = dfmkt[:dti_now]['close'].expanding(10).std().iloc[-1]
        std_tilnow_ref = timely_std_list[now_n_min-1]
        std_factor = std_tilnow / std_tilnow_ref
        if std_factor == 0 or np.isnan(std_factor):
            std_factor = 1
        
        dfmkt.at[dti_now, 'std_factor'] = std_factor
        dfmkt.at[dti_now, 'sell_entry'] = ENTRY_THRESHOLD_APO * std_factor
        dfmkt.at[dti_now, 'buy_entry'] = -ENTRY_THRESHOLD_APO * std_factor
        
        # trading_time_start 조건이 있을 경우 trade_qty 강제로 reset
        # AF같은 타 전략에서 edr 조건 차용시 사용할 수 있음
        if trading_time_start != None:
            if now < trading_time_start:
                trade_qty = 0
        
        # dti_pre에서 trade 요청 발생한 경우 dti_now에서 실행
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
        
        # last_prc 기준으로 ema update
        # 즉, volume봉 내에서 last가 최신이므로 거래는 vwap, 시그널은 last prc로 정의
        dfmkt.at[dti_now, 'ema_fast'] = K_FAST * std_factor * last_prc \
            + (1 - K_FAST * std_factor) * dfmkt.at[dti_pre, 'ema_fast']
        
        dfmkt.at[dti_now, 'ema_slow'] = K_SLOW * std_factor * last_prc \
            + (1 - K_SLOW * std_factor) * dfmkt.at[dti_pre, 'ema_slow']
        
        diff_now = dfmkt.at[dti_now, 'ema_fast'] - dfmkt.at[dti_now, 'ema_slow']
        
        tick_apo = TICK_CONVERSION * diff_now
        
        dfmkt.at[dti_now, 'tick_apo'] = tick_apo
        
        # 장 초반 vol watch로 트레이딩 미실시, 장 막판 트레이딩 미실시
        if now.time() > WATCH_VOL_UNTIL and now.time() < TRADING_ENDS :
            
            # last_prc 기준으로 pl 계산, 현재까지의 누적 pl을 기록함
            dftemp = dfmkt[:dti_now+1]
            gross_pl = KRW_VALUE_1PT * sum(np.array(dftemp['trade_qty']) \
                                           * (last_prc - np.array(dftemp['trade_price'])))
            commission = KRW_COMMISSION_PER_CONTRACT * abs(np.array(dftemp['trade_qty'])).sum()
            net_pl = int(gross_pl - commission)
            dfmkt.at[dti_now, 'net_pl'] = net_pl
            
            # open_pnl 계산
            if open_position_qty != 0:
                open_pnl_krw = KRW_VALUE_1PT * sum(
                    np.array(open_position_trade_qty_list) \
                        * (last_prc - np.array(open_position_trade_price_list))
                        )
                
            
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
        
            # 절대금액 손절 로직 추가
            # if losscut == "Y" and net_pl < -30*(10**6):
            #     break
            
            
    """index기준 test loop종료"""       
            
    
    print(f'net_pl : {net_pl:,}')
    print(f'trade qty sum : {int(dfmkt.trade_qty.abs().sum()):,}')
    print(f'commission sum : {int(commission):,}')
    
    
    
    #%% PLOT
    
    fig = plt.figure(figsize=(10,10))
    
    spec = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3,1])
    
    ax = fig.add_subplot(spec[0])
    ax.plot(dfmkt.index, dfmkt['vwap'], linewidth=0.5)
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
    # ax3.fill_between(dfmkt.index, dfmkt['actual_qty'], 0, alpha=0.1, color="red")
    ax3.fill_between(dfmkt.index, dfmkt['actual_qty'], where= dfmkt['actual_qty']>0, alpha=0.1, color="red")
    ax3.fill_between(dfmkt.index, dfmkt['actual_qty'], where= dfmkt['actual_qty']<0, alpha=0.1, color="b")
    ax3.scatter(dfmkt.index[-1], 
                dfmkt['actual_qty'].iloc[-1],
                color="tab:red" if dfmkt['actual_qty'].iloc[-1] > 0 else "b", 
                marker="^" if dfmkt['actual_qty'].iloc[-1] > 0 else "v",
                s=50)
    
    ax4 = ax.twinx()
    ax4.spines["right"].set_position(("axes", 1.1)) ## 오른쪽 옆에 y축 추가
    ax4.plot(dfmkt.index, dfmkt['std_factor'], color="r")
    
    ax_below = fig.add_subplot(spec[1])
    ax_below.fill_between(dfmkt.index, dfmkt['tick_apo'], 0, alpha=0.3, color="blue")
    ax_below.plot(dfmkt.index, dfmkt['sell_entry'])
    ax_below.plot(dfmkt.index, dfmkt['buy_entry'])
    
    
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
ld = [d for d in ld if d == datetime.date(2021, 1, 14)]
# ld = [d for d in ld if d == datetime.date(2021, 7, 21)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])


for i, day in enumerate(ld):
        
    dfmkt = tradeMRbyAPO(
        day, 
        yesterday = None,
        db_table='lktbf100vol', 
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
    print(f'trade volume : {dfmkt.trade_qty.abs().sum():,}')
    
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










