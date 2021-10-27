# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 10:20:11 2021

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

def calTargetQty(
        max_qty, 
        tick_diff_now,
        tick_cross_margin, 
        tick_diff_of_max_qty, 
        method="linear"
        ):
    
    # # linear 증감을 위한 1차함수 계수
    # qty_per_tick_diff_overmargin = max_qty / (tick_diff_of_max_qty - tick_cross_margin)
    
    if abs(tick_diff_now) <= tick_cross_margin:
        target_qty = 0
        
    elif tick_diff_now > tick_cross_margin:
        if method == "linear":
            target_qty_raw = max_qty * tick_diff_now / tick_diff_of_max_qty
            target_qty = target_qty_raw if target_qty_raw < max_qty else max_qty
        elif method == "power":
            target_qty_raw = max_qty * (tick_diff_now / tick_diff_of_max_qty)**2
            target_qty = target_qty_raw if target_qty_raw < max_qty else max_qty
        else:
            ValueError("Wrong method")
        
    elif tick_diff_now < -tick_cross_margin:
        if method == "linear":
            target_qty_raw = max_qty * tick_diff_now / tick_diff_of_max_qty
            target_qty = target_qty_raw if -target_qty_raw < max_qty else -max_qty
        elif method == "power":
            # 제곱하니까 - 부호 붙여줌
            target_qty_raw = -max_qty * (tick_diff_now / tick_diff_of_max_qty)**2
            target_qty = target_qty_raw if -target_qty_raw < max_qty else -max_qty
        else:
            ValueError("Wrong method")
        
    else:
        raise ValueError("Unexpected tick_diff_now status")
    
    return int(target_qty)


def tradeEmaDynamicRisk(date, 
                        db_table='lktbf50vol', 
                        plot="N", 
                        fast_coeff=0.20, 
                        slow_coeff=0.05, 
                        tick_cross_margin=0.5,
                        window_ref=5,
                        max_qty=200,
                        max_trade_qty=5,
                        method = "power",
                        dti_cut = 9999999,
                        losscut="Y"
                        ):
    """
    tradeEma는 장중 한방향 트렌드가 지속될 때 많은 수익을 추구
    필연적으로 방향전환이 많은 날은 손실 발생 가능
    
    2021.10.13 - DynamicRisk 기능 추가
        fast와 slow의 ema diff에 비례하여 수량조절 
    
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
    
    
    if db_table[:3] == 'lkt':
        product = 'lktbf'
        tick_value = 0.01
        krw_commission_per_contract = 250 # 원래 248.95원/계약
        krw_value_1pt = 10**6
    
    elif db_table[:3] == 'ktb':
        product = 'ktbf'
        tick_value = 0.01
        krw_commission_per_contract = 250 # 원래 225.5원/계약
        krw_value_1pt = 10**6
    
    elif db_table[:3] == 'usd':
        product = 'usdkrw'
        tick_value = 0.1
        krw_commission_per_contract = 60 # 원래 57.9원/계약
        krw_value_1pt = 10**4
    
    tick_conversion = 1 / tick_value
    
    print(product)
    
    # ref window 내의 diff 분포를 구한다. 
    ar_diff_window = np.array([])
    
    for i in range(1, window_ref+1):
        d = util.date_offset(date, -i)
        # print(i, d)
        refmkt = util.setDfData(d, d, db_table)
        refdti = refmkt.index
        
        refmkt.at[refdti[0], 'ema_fast'] = refmkt.at[refdti[0], 'vwap']
        refmkt.at[refdti[0], 'ema_slow'] = refmkt.at[refdti[0], 'vwap']
        
        for refdti_pre, refdti_now in zip(refdti, refdti[1:]):
            vwap = refmkt.loc[refdti_now,'vwap']
            
            refmkt.at[refdti_now, 'ema_fast'] = fast_coeff * vwap + (1-fast_coeff) * refmkt.at[refdti_pre, 'ema_fast']
            refmkt.at[refdti_now, 'ema_slow'] = slow_coeff * vwap + (1-slow_coeff) * refmkt.at[refdti_pre, 'ema_slow']
        
        ar_diff_day = np.array(refmkt['ema_fast']) - np.array(refmkt['ema_slow'])
        
        # print(ar_diff_day.mean(), 2*ar_diff_day.std())
        
        # ar_diff_day = np.abs(ar_diff_day)
        
        ar_diff_window = np.append(ar_diff_window, ar_diff_day)
        
    diff_std = np.std(ar_diff_window)
    # print(ar_diff_window.mean(), 2*ar_diff_window.std())
    
    # 최근 N일의 diff 분포에서 N sigma에 해당하는 diff에 도달하면 max qty가 되도록 수량 설정
    # 2.0 sigma로 설정하여 전체 trading time에서 4.6%의 빈도로 max_qty를 보유하는 것으로 설정
    # 1.5 sigma -> 13.4%
    # 1.0 sigma -> 31.7%
    # linear하게 수량 증감 한다 
    # --> 2021.10.15 linear가 아닌 x^2 모델링으로 작은 diff의 경우 수량을 적게 세팅 
    # --> 1) trade수량 줄이기 2) 
    tick_diff_of_max_qty = 1.5 * diff_std * tick_conversion
    print(f'tick_diff_of_max_qty : {round(tick_diff_of_max_qty, 3)}')
    
    
    # 테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, db_table)
    # dfmkt = dfmkt[:200]
    
    dfmkt = dfmkt[:dti_cut]
    
    # local index
    dti = dfmkt.index
    
    # 시작점 boundary condition 정의
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'tick_diff'] = 0
    
    dfmkt.at[dti[0], 'trade_price'] = 0
    dfmkt.at[dti[0], 'trade_qty'] = 0
    dfmkt.at[dti[0], 'actual_qty'] = 0
    dfmkt.at[dti[0], 'target_qty'] = 0
    
    trade_qty = 0
    
    # 시가거래 volume봉 개수, 장 시작후 초기값 세팅 전까지 trade 유보 위해 사용
    siga_time = dfmkt.at[dti[0], 'datetime']
    siga_count = dfmkt[dfmkt['datetime'] == siga_time].shape[0]
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        # 실제 운용시 vwap이 last보다 빠른 정보일 것
        vwap = dfmkt.loc[dti_now,'vwap']
        last_prc = dfmkt.loc[dti_now,'close']
        
        # 현재시간
        now = dfmkt.at[dti_now, 'datetime'].time()
        
        # dti_pre에서 trade 요청 발생한 경우 dti_now에서 실행
        if trade_qty != 0:
        # if dfmkt.loc[dti_pre]['trade_price'] == 'TBD':
            dfmkt.at[dti_now, 'trade_price'] = vwap
        else:
            dfmkt.at[dti_now, 'trade_price'] = 0
            
        dfmkt.at[dti_now, 'trade_qty'] = trade_qty
        dfmkt.at[dti_now, 'actual_qty'] = trade_qty + dfmkt.at[dti_pre, 'actual_qty']
        
        # reset
        trade_qty = 0
        
        # last_prc 기준으로 ema update
        # 즉, volume봉 내에서 last가 최신이므로 거래는 vwap, 시그널은 last prc로 정의
        dfmkt.at[dti_now, 'ema_fast'] = fast_coeff * last_prc + (1-fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
        dfmkt.at[dti_now, 'ema_slow'] = slow_coeff * last_prc + (1-slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
        
        diff_now = dfmkt.at[dti_now, 'ema_fast'] - dfmkt.at[dti_now, 'ema_slow']
        
        tick_diff_now = tick_conversion * diff_now
        
        if abs(tick_diff_now) > tick_diff_of_max_qty:
            # print("tick_diff_of_max_qty revised!!!!!!", now)
            tick_diff_of_max_qty = abs(tick_diff_now)
        
        dfmkt.at[dti_now, 'tick_diff'] = tick_diff_now
        
        target_qty = calTargetQty(
            max_qty, 
            tick_diff_now, 
            tick_cross_margin, 
            tick_diff_of_max_qty, 
            method=method
            )
        
        dfmkt.at[dti_now, 'target_qty'] = target_qty
        
        # slow ema 형성시까지(=slow ema가 적정수량이 생길때까지) trade하지 않음
        # if dfmkt.ema_slow.count() > siga_count + (1 / slow_coeff):
        if dfmkt.ema_slow.count() > siga_count:
            
            trade_qty_raw = int(target_qty - dfmkt.at[dti_now, 'actual_qty'])
            if trade_qty_raw >= 0:
                trade_qty = min(max_trade_qty, trade_qty_raw)
            else:
                trade_qty = -min(max_trade_qty, -trade_qty_raw)
            
            # last_prc 기준으로 pl 계산, 현재까지의 누적 pl을 기록함
            dftemp = dfmkt[:dti_now+1]
            gross_pl = krw_value_1pt * sum(np.array(dftemp['trade_qty']) * (last_prc - np.array(dftemp['trade_price'])))
            commission = krw_commission_per_contract * abs(np.array(dftemp['trade_qty'])).sum()
            net_pl = int(gross_pl - commission)
            dfmkt.at[dti_now, 'net_pl'] = net_pl
        
            # 절대금액 손절 로직 추가
            if losscut == "Y" and net_pl < -30*(10**6):
                break
            
            
    """index기준 test loop종료"""       
            
    
    # print(f'net_pl : {net_pl:,}')
    # print(f'trade qty sum : {int(dfmkt.trade_qty.abs().sum()):,}')
    print(f'commission sum : {int(commission):,}')
    
    # ratio of max_qty (actual based)
    max_risk_ratio = dfmkt[dfmkt.actual_qty.abs() == max_qty].shape[0] / dfmkt.shape[0]
    print(f'max risk ratio : {round(100*max_risk_ratio, 1)}%')
    
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    ax2 = ax.twinx()
    ax2.fill_between(dfmkt.index, dfmkt['net_pl'], 0, alpha=0.3, color="gray")
    
    ax3 = ax.twinx()
    ax3.spines["right"].set_position(("axes", 1.1)) ## 오른쪽 옆에 y축 추가
    ax3.fill_between(dfmkt.index, dfmkt['actual_qty'], 0, alpha=0.1, color="red")


    ax.plot(dfmkt.index, dfmkt['vwap'], linewidth=0.5)
    ax.plot(dfmkt.index, dfmkt['ema_fast'])
    ax.plot(dfmkt.index, dfmkt['ema_slow'])
    
    
    # ax.set_ylim(108, 109)
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 11,
            }
    plot_name = '{3}, F_co: {0}, S_co: {1}, maxq: {2}, pl: {4:,}'
    plot_name = plot_name.format(fast_coeff,
                                 slow_coeff,
                                 max_qty,
                                 date,
                                 net_pl
                                 )
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    
    return dfmkt


def calTargetQty_LS(
        max_long_qty, 
        abs_max_short_qty,
        tick_diff_now,
        tick_cross_margin, 
        tick_diff_of_max_long_qty, 
        abs_tick_diff_of_max_short_qty, 
        method="linear"
        ):
    
    # # linear 증감을 위한 1차함수 계수
    # qty_per_tick_diff_overmargin = max_qty / (tick_diff_of_max_qty - tick_cross_margin)
    
    if abs(tick_diff_now) <= tick_cross_margin:
        target_qty = 0
        
    elif tick_diff_now > tick_cross_margin:
        if method == "linear":
            target_qty_raw = max_long_qty * tick_diff_now / tick_diff_of_max_long_qty
            target_qty = target_qty_raw if target_qty_raw < max_long_qty else max_long_qty
        elif method == "power":
            target_qty_raw = max_long_qty * (tick_diff_now / tick_diff_of_max_long_qty)**2
            target_qty = target_qty_raw if target_qty_raw < max_long_qty else max_long_qty
        else:
            ValueError("Wrong method")
        
    elif tick_diff_now < -tick_cross_margin:
        if method == "linear":
            target_qty_raw = abs_max_short_qty * tick_diff_now / abs_tick_diff_of_max_short_qty
            target_qty = target_qty_raw if -target_qty_raw < abs_max_short_qty else -abs_max_short_qty
        elif method == "power":
            # 제곱 세제곱 등 부호 예측이 어려우므로 abs후 마지막에 - 붙임
            target_qty_raw = -abs(abs_max_short_qty * (tick_diff_now / abs_tick_diff_of_max_short_qty)**2)
            target_qty = target_qty_raw if -target_qty_raw < abs_max_short_qty else -abs_max_short_qty
        else:
            ValueError("Wrong method")
        
    else:
        raise ValueError("Unexpected tick_diff_now status")
    
    return int(target_qty)


def tradeEmaDynamicRisk_varMaxqty(
        date, 
        db_table='lktbf50vol', 
        plot="N", 
        fast_coeff=0.20, 
        slow_coeff=0.05, 
        tick_cross_margin=0.5,
        window_ref=5,
        max_long_qty=200,
        abs_max_short_qty=200,
        max_trade_qty=5,
        var_max="Y",
        method = "power",
        dti_cut = 9999999,
        losscut="Y"
        ):
    
    """
    max_qty를 long / short 이원화
    max_qty를 현재 pl에 따라 변화
    
    """
    
    
    if db_table[:3] == 'lkt':
        product = 'lktbf'
        tick_value = 0.01
        krw_commission_per_contract = 250 # 원래 248.95원/계약
        krw_value_1pt = 10**6
    
    elif db_table[:3] == 'ktb':
        product = 'ktbf'
        tick_value = 0.01
        krw_commission_per_contract = 250 # 원래 225.5원/계약
        krw_value_1pt = 10**6
    
    elif db_table[:3] == 'usd':
        product = 'usdkrw'
        tick_value = 0.1
        krw_commission_per_contract = 60 # 원래 57.9원/계약
        krw_value_1pt = 10**4
    
    tick_conversion = 1 / tick_value
    
    print(product)
    
    # ref window 내의 diff 분포를 구한다. 
    ar_diff_window = np.array([])
    
    for i in range(1, window_ref+1):
        d = util.date_offset(date, -i)
        # print(i, d)
        refmkt = util.setDfData(d, d, db_table)
        refdti = refmkt.index
        
        refmkt.at[refdti[0], 'ema_fast'] = refmkt.at[refdti[0], 'vwap']
        refmkt.at[refdti[0], 'ema_slow'] = refmkt.at[refdti[0], 'vwap']
        
        for refdti_pre, refdti_now in zip(refdti, refdti[1:]):
            vwap = refmkt.loc[refdti_now,'vwap']
            
            refmkt.at[refdti_now, 'ema_fast'] = fast_coeff * vwap + (1-fast_coeff) * refmkt.at[refdti_pre, 'ema_fast']
            refmkt.at[refdti_now, 'ema_slow'] = slow_coeff * vwap + (1-slow_coeff) * refmkt.at[refdti_pre, 'ema_slow']
        
        ar_diff_day = np.array(refmkt['ema_fast']) - np.array(refmkt['ema_slow'])
        
        # print(ar_diff_day.mean(), 2*ar_diff_day.std())
        
        # ar_diff_day = np.abs(ar_diff_day)
        
        ar_diff_window = np.append(ar_diff_window, ar_diff_day)
        
    diff_std = np.std(ar_diff_window)
    # print(ar_diff_window.mean(), 2*ar_diff_window.std())
    
    # 최근 N일의 diff 분포에서 N sigma에 해당하는 diff에 도달하면 max qty가 되도록 수량 설정
    # 2.0 sigma로 설정하여 전체 trading time에서 4.6%의 빈도로 max_qty를 보유하는 것으로 설정
    # 1.5 sigma -> 13.4%
    # 1.0 sigma -> 31.7%
    # linear하게 수량 증감 한다 
    # --> 2021.10.15 linear가 아닌 x^2 모델링으로 작은 diff의 경우 수량을 적게 세팅하는 옵션 추가
    tick_diff_of_max_qty = 1.0 * diff_std * tick_conversion
    print(f'tick_diff_of_max_qty : {round(tick_diff_of_max_qty, 3)}')
    
    # 최대 포지션을 잡는 tick_diff를 long short 별도로 저장
    tick_diff_of_max_long_qty = tick_diff_of_max_qty
    abs_tick_diff_of_max_short_qty = tick_diff_of_max_qty
    
    
    # 테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, db_table)
    # dfmkt = dfmkt[:200]
    
    dfmkt = dfmkt[:dti_cut]
    
    # local index
    dti = dfmkt.index
    
    # 시작점 boundary condition 정의
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'tick_diff'] = 0
    
    dfmkt.at[dti[0], 'trade_price'] = 0
    dfmkt.at[dti[0], 'trade_qty'] = 0
    dfmkt.at[dti[0], 'actual_qty'] = 0
    dfmkt.at[dti[0], 'target_qty'] = 0
    
    trade_qty = 0
    
    # 시가거래 volume봉 개수, 장 시작후 초기값 세팅 전까지 trade 유보 위해 사용
    siga_time = dfmkt.at[dti[0], 'datetime']
    siga_count = dfmkt[dfmkt['datetime'] == siga_time].shape[0]
    
    # pl_status 초기값 지정, 추후 분위기가 좋으면 max 수량을 늘리는 지표로 사용
    pl_status = "neutral"    
    
    # max qty limit 값 저장 : parameter로 주어진 max값은 어떤 경우에도 초과하지 않는다
    limit_max_long_qty = max_long_qty
    abs_limit_max_short_qty = abs_max_short_qty
    
    # 최초 시작시 맥스를 50%로 제한하고 상황에 따라 변경
    max_long_qty = 0.5 * limit_max_long_qty
    abs_max_short_qty = 0.5 * abs_limit_max_short_qty
    
    dfmkt.at[dti[0], 'max_long_qty'] = max_long_qty
    dfmkt.at[dti[0], 'max_short_qty'] = -abs_max_short_qty
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        # 실제 운용시 vwap이 last보다 빠른 정보일 것
        vwap = dfmkt.loc[dti_now,'vwap']
        last_prc = dfmkt.loc[dti_now,'close']
        
        # 현재시간
        now = dfmkt.at[dti_now, 'datetime'].time()
        
        # dti_pre에서 trade 요청 발생한 경우 dti_now에서 실행
        if trade_qty != 0:
        # if dfmkt.loc[dti_pre]['trade_price'] == 'TBD':
            dfmkt.at[dti_now, 'trade_price'] = vwap
        else:
            dfmkt.at[dti_now, 'trade_price'] = 0
            
        dfmkt.at[dti_now, 'trade_qty'] = trade_qty
        dfmkt.at[dti_now, 'actual_qty'] = trade_qty + dfmkt.at[dti_pre, 'actual_qty']
        
        # reset
        trade_qty = 0
        
        # last_prc 기준으로 ema update
        # 즉, volume봉 내에서 last가 최신이므로 거래는 vwap, 시그널은 last prc로 정의
        dfmkt.at[dti_now, 'ema_fast'] = fast_coeff * last_prc + (1-fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
        dfmkt.at[dti_now, 'ema_slow'] = slow_coeff * last_prc + (1-slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
        
        diff_now = dfmkt.at[dti_now, 'ema_fast'] - dfmkt.at[dti_now, 'ema_slow']
        
        tick_diff_now = tick_conversion * diff_now
        
        # tick_diff가 max치를 넘으면 리스크한도 조정해주고 tick diff of max도 조정 
        if tick_diff_now > tick_diff_of_max_long_qty:
            # print("tick_diff_of_max_long_qty revised!!!!!!", now)
            max_long_qty = int(min(limit_max_long_qty, 
                                   tick_diff_now / tick_diff_of_max_long_qty * max_long_qty
                                   ))
            dfmkt.at[dti_now, 'max_long_qty'] = max_long_qty
            tick_diff_of_max_long_qty = tick_diff_now
            
        elif tick_diff_now < -abs_tick_diff_of_max_short_qty:
            # print("tick_diff_of_max_short_qty revised!!!!!!", now)
            abs_max_short_qty = int(min(abs_limit_max_short_qty,
                                        abs(tick_diff_now / abs_tick_diff_of_max_short_qty * abs_max_short_qty)
                                        ))
            dfmkt.at[dti_now, 'max_short_qty'] = -abs_max_short_qty
            abs_tick_diff_of_max_short_qty = -tick_diff_now
            
        dfmkt.at[dti_now, 'tick_diff'] = tick_diff_now
        
        target_qty = calTargetQty_LS(
            max_long_qty, 
            abs_max_short_qty,
            tick_diff_now, 
            tick_cross_margin, 
            tick_diff_of_max_long_qty, 
            abs_tick_diff_of_max_short_qty, 
            method=method
            )
        
        dfmkt.at[dti_now, 'target_qty'] = target_qty
        
        # slow ema 형성시까지(=slow ema가 적정수량이 생길때까지) trade하지 않음
        # if dfmkt.ema_slow.count() > siga_count + (1 / slow_coeff):
        if dfmkt.ema_slow.count() > siga_count:
            
            trade_qty_raw = int(target_qty - dfmkt.at[dti_now, 'actual_qty'])
            
            if trade_qty_raw >= 0:
                trade_qty = min(max_trade_qty, trade_qty_raw)
            else:
                trade_qty = -min(max_trade_qty, -trade_qty_raw)
            
            # last_prc 기준으로 pl 계산, 현재까지의 누적 pl을 기록함
            dftemp = dfmkt[:dti_now+1]
            dftemp_long = dftemp[dftemp['trade_qty'] > 0]
            dftemp_short = dftemp[dftemp['trade_qty'] < 0]
            
            # 현재까지 long trade로 
            gross_pl_long = krw_value_1pt * sum(
                np.array(dftemp_long['trade_qty']) \
                    * (last_prc - np.array(dftemp_long['trade_price']))
                )
            gross_pl_short = krw_value_1pt * sum(
                np.array(dftemp_short['trade_qty']) \
                    * (last_prc - np.array(dftemp_short['trade_price']))
                )
            
            gross_pl = gross_pl_long + gross_pl_short
                        
            commission = krw_commission_per_contract * abs(np.array(dftemp['trade_qty'])).sum()
            net_pl = int(gross_pl - commission)
            dfmkt.at[dti_now, 'net_pl'] = net_pl
        
            # 절대금액 손절 로직 추가
            if losscut == "Y" and net_pl < -30*(10**6):
                break
            
            # 손익상황에 따라 리스크한도 조정 로직
            # if var_max == "Y":
            #     # net_pl 천만원이 넘으면 max 수량 증대
            #     if net_pl > 10*(10**6) and net_pl > dfmkt.at[dti_pre, "net_pl"] and pl_status == "neutral":
            #         pl_status = "gazua"
            #         print("gazua")
            #         if gross_pl_long > gross_pl_short:
            #             max_long_qty = limit_max_long_qty
            #         else:
            #             abs_max_short_qty = abs_limit_max_short_qty
                
            #     # net_pl ??백만원 아래이고 gazua상태였으면 원복시킴
            #     elif net_pl < 5*(10**6) and pl_status == "gazua":
            #         pl_status = "neutral"
            #         print("gazua cancel")
            #         max_long_qty = limit_max_long_qty
            #         abs_max_short_qty = abs_limit_max_short_qty
                    
            #     elif net_pl < -5*(10**6) and pl_status == "neutral":
            #         pl_status = "sosim"
            #         print("sosim")
            #         if gross_pl_long > gross_pl_short:
            #             max_long_qty = 0.5 * limit_max_long_qty
            #         else:
            #             abs_max_short_qty = 0.5 * abs_limit_max_short_qty
                        
            #     elif net_pl > 0 and pl_status == "sosim":
            #         pl_status = "neutral"
            #         print("sosim cancel")
            #         max_long_qty = limit_max_long_qty
            #         abs_max_short_qty = abs_limit_max_short_qty
                    
                    
                
            
    """index기준 test loop종료"""       
    
    # print(f'net_pl : {net_pl:,}')
    # print(f'trade qty sum : {int(dfmkt.trade_qty.abs().sum()):,}')
    print(f'commission sum : {int(commission):,}')
    
    # ratio of max_qty (actual based)
    num_vol = dfmkt.shape[0]
    
    max_long_occurences = dfmkt[dfmkt.actual_qty == max_long_qty].shape[0]
    max_long_ratio = max_long_occurences / num_vol
    print(f'max long occur ratio : {round(100*max_long_ratio, 1)}%')
    
    max_short_occurences = dfmkt[dfmkt.actual_qty == -abs_max_short_qty].shape[0]
    max_short_ratio = max_short_occurences / num_vol
    print(f'max short occur ratio : {round(100*max_short_ratio, 1)}%')
    
    max_risk_ratio = max_long_ratio + max_short_ratio
    print(f'max risk ratio : {round(100*max_risk_ratio, 1)}%')
    
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    plt.plot(dfmkt.index, dfmkt['vwap'], linewidth=0.5)
    plt.plot(dfmkt.index, dfmkt['ema_fast'])
    plt.plot(dfmkt.index, dfmkt['ema_slow'])
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 12,
            }
    plot_name = '{3}, Fast_coef: {0}, Slow_coef: {1}, net PL: {2:,}'
    plot_name = plot_name.format(fast_coeff,
                                 slow_coeff,
                                 net_pl,
                                 date
                                 )
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    
    return dfmkt

#%% TEST PLOT

# day = datetime.date(2021, 5, 31)

# # result = tradeEmaDynamicRisk(
# #         day,
# #         db_table='lktbf100vol',
# #         fast_coeff=0.100, 
# #         slow_coeff=0.015, 
# #         tick_cross_margin=0.5,
# #         window_ref=5,
# #         max_qty=200,
# #         max_trade_qty=30,
# #         method = "linear",
# #         losscut = "n"
# #         )

# result = tradeEmaDynamicRisk_varMaxqty(
#     day,
#         db_table='lktbf50vol', 
#         plot="Y", 
#         fast_coeff=0.025, 
#         slow_coeff=0.005, 
#         tick_cross_margin=0.5,
#         window_ref=5,
#         max_long_qty=100,
#         abs_max_short_qty=100,
#         max_trade_qty=10,
#         var_max="Y",
#         method = "linear",
#         dti_cut = 9999999,
#         losscut="Y"
#         )

# print(f'pl : {result.net_pl.dropna().iloc[-1]:,}')
# print(f'trade volume : {result.trade_qty.abs().sum():,}')
