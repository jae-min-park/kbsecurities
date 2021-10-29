# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 10:20:11 2021

@author: infomax
"""

import pandas as pd
import datetime
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util
import emaDynaRisk as edr


#일봉기준 전체 date list
ld = list(util.getDailyOHLC().index)
# ld = [d for d in ld if d.year >= 2016 and d.year < 2019]
# ld = [d for d in ld if d.year == 2021 and d.month ==10]
# ld = [d for d in ld if d == datetime.date(2021, 9, 28) or d == datetime.date(2021, 9, 29) or d == datetime.date(2021, 10, 13)]
ld = [d for d in ld if d == datetime.date(2021, 10, 28)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])

for i, day in enumerate(ld):
    
    result = edr.tradeEmaDynamicRisk(
        day,
        db_table='usdkrw300vol',
        fast_coeff=0.040, 
        slow_coeff=0.015, 
        tick_cross_margin=0.5,
        window_ref=5,
        max_qty=1000,
        max_trade_qty=100,
        method = "linear",
        losscut = "Y"
        )
    
    # result = edr.tradeEmaDynamicRisk(
    # day,
    # db_table='usdkrw300vol',
    # fast_coeff=0.20, 
    # slow_coeff=0.05, 
    # tick_cross_margin=0.5,
    # window_ref=5,
    # max_qty=500,
    # max_trade_qty=80,
    # method = "linear",
    # losscut = "Y"
    # )
    
    dfpl.at[i, 'date'] = day
    
    trade_end_time = str(result.at[result.dropna().index[-1], 'datetime'].time()) 
    
    pl_of_the_day = int(result.net_pl.dropna().iloc[-1])
    dfpl.at[i, 'pl'] = pl_of_the_day
    
    num_trade = result.trade_qty.abs().sum()
    dfpl.at[i, 'num_trade'] = num_trade
    
    #당일의 결과
    print(f'Day   | {day}  {trade_end_time}   pl= {pl_of_the_day:,},  {int(num_trade):,}')
    
    #누적결과
    cumsum = round(dfpl.pl.sum(), 1)
    mean = round(dfpl.pl.mean(), 2)
    std = round(dfpl.pl.std(), 3)
    sr = round(mean / std, 3)
    num_trade_cumul = dfpl.num_trade.sum()
    contracts_per_day = dfpl.num_trade.sum() / dfpl.shape[0]
    print(f'Cumul | cumsum: {cumsum:,}  mean:{mean:,}  SR: {sr}  trades/day: {int(contracts_per_day):,}',
          "\n---------------------------------------------------------------")

# 결과 출력및 저장
# dfpl 수정됨, call by reference
pl_mon, pl_yr = util.reportSummary(dfpl, show_hist="n")

