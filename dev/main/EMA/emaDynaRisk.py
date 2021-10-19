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
                        dti_cut = 9999999
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
        krw_commission_per_contract = 250 #원래 248.95원/계약
        krw_value_1pt = 10**6
    
    elif db_table[:3] == 'ktb':
        product = 'ktbf'
        tick_value = 0.01
        krw_commission_per_contract = 170 #원래 168.97원/계약
        krw_value_1pt = 10**6
    
    elif db_table[:3] == 'usd':
        product = 'usdkrw'
        tick_value = 0.1
        krw_commission_per_contract = 100
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
    
    # 최근 N일의 diff 분포에서 1.5 sigma에 해당하는 diff에 도달하면 max qty가 되도록 수량 설정
    # 2 sigma로 설정하여 전체 trading time에서 5%의 시간에 max_qty를 보유하는 것으로 설정
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
        if dfmkt.ema_slow.count() > siga_count + (1 / slow_coeff):
            
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
            
            
    """index기준 test loop종료"""       
            
    
    # print(f'net_pl : {net_pl:,}')
    # print(f'trade qty sum : {int(dfmkt.trade_qty.abs().sum()):,}')
    print(f'commission sum : {int(commission):,}')
    
    # ratio of max_qty (actual based)
    max_risk_ratio = dfmkt[dfmkt.actual_qty.abs() == max_qty].shape[0] / dfmkt.shape[0]
    print(f'max risk ratio : {round(100*max_risk_ratio, 1)}%')
    
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    # for result_i in df_result.index:
    #     marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
    #     color = "tab:red" if marker == "^" else "b"
    #     x = result_i
    #     y = df_result.loc[result_i]['price']
    #     ax.scatter(x, y, color=color, marker=marker, s=300)
    plt.plot(dfmkt.index, dfmkt['vwap'])
    plt.plot(dfmkt.index, dfmkt['ema_fast'])
    plt.plot(dfmkt.index, dfmkt['ema_slow'])
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 12,
            }
    plot_name = '{3}, Fast_coef: {0}, Slow_coef: {1}, max qty: {2}'
    plot_name = plot_name.format(fast_coeff,
                                 slow_coeff,
                                 max_qty,
                                 date
                                 )
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    
    return dfmkt

