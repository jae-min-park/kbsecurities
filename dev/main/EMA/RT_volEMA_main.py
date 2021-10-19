import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util
import datetime
from tradeLoi import *


    


"""3선 RT"""
dfmkt_3y = util.setRtData(asset="ktbf3y")
date = dfmkt_3y.date[0]
px_last_3y = dfmkt_3y.price.iloc[-1]

result_ema_3y = tradeEma(date, 'ktbf200vol', plot="Y", execution="vwap", 
                      fast_coeff=0.30,
                      slow_coeff=0.05,
                      margin = 0.5, dfmkt=dfmkt_3y)

sig_3y = result_ema_3y['df'] 

sig_3y['amt'] = 2 
sig_3y.at[sig_3y.index[0], 'amt'] = 1
commission_3y = 0.05 * sig_3y.amt.sum() # 수수료 계약당 500원 가정

pl_3y = sum(100 * sig_3y.direction.values * sig_3y.amt.values * (px_last_3y - sig_3y.price.values))
pl_3y = round(pl_3y - commission_3y, 1)

print(f'현재가: {px_last_3y}  |  PL(틱): {pl_3y}  |  PL(백만원): {pl_3y*2}')

#%%
"""10선 RT"""
dfmkt = util.setRtData()
date = dfmkt.date[0]
px_last = dfmkt.price.iloc[-1]
#%%
result_ema = tradeEma(date, 'lktbf50vol', plot="Y", execution="vwap",
                      fast_coeff=0.20,
                      slow_coeff=0.05,
                      margin = 1.0, dfmkt=dfmkt)

sig = result_ema['df'] 

sig['amt'] = 2 
sig.at[sig.index[0], 'amt'] = 1
commission_10y = 0.05 * sig.amt.sum() # 수수료 계약당 500원 가정

pl = sum(100 * sig.direction.values * sig.amt.values * (px_last - sig.price.values))
pl = round(pl - commission_10y, 1)
print(f'현재가: {px_last}  |  PL(틱): {pl}  |  PL(백만원): {pl*0.5}')

#%%
"""오늘PL 출력"""
pl_today = round(pl_3y*2 + pl*0.5, 1)
print(f'손익계(백만원): {pl_today}')
