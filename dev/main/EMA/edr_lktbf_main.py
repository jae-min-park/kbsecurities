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
import emaDynaRisk as edr


#일봉기준 전체 date list
ld = list(util.getDailyOHLC().index)
ld = [d for d in ld if d.year >= 2019]
# ld = [d for d in ld if d.year == 2020 and d.month == 5]
# ld = [d for d in ld if d == datetime.date(2021, 9, 28) or d == datetime.date(2021, 9, 29) or d == datetime.date(2021, 10, 13)]

#일간 PL을 기록하는 dataframe
dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])

# config = {'trading_begins_after': datetime.time(12,15,0),
#              'trading_begins_before': datetime.time(15,15,0),
#              'ema_fast_coeff': 0.20,
#              'ema_slow_coeff': 0.05,
#              'thru': 0.5,
#              'ema_margin': 0.5,
#              'lc_hi-lo': 1.0, 
#              'lc_pl': -20, 
#              'pt_pl': 20,
#              'pt_draw_down': 0.3
#              }

for i, day in enumerate(ld):
    
    result = edr.tradeEmaDynamicRisk(
        day,
        db_table='lktbf200vol',
        fast_coeff=0.30, 
        slow_coeff=0.05, 
        tick_cross_margin=0.5,
        window_ref=5,
        max_qty=300,
        max_trade_qty=50,
        method = "linear"
        )
        
    dfpl.at[i, 'date'] = day
    
    pl_of_the_day = int(result.net_pl.iloc[-1])
    dfpl.at[i, 'pl'] = pl_of_the_day
    
    num_trade = result.trade_qty.abs().sum()
    dfpl.at[i, 'num_trade'] = num_trade
    
    #당일의 결과
    print(f'Day   | {day}    pl= {pl_of_the_day:,},  {num_trade}')
    
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

