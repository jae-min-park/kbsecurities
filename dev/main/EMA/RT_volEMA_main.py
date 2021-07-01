import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import utils.util as util
import datetime
from tradeLoi import *


# def main():
    
#     print("Running RT main function\n")
    
dfmkt = util.setRtData()
date = dfmkt.date[0]
px_last = dfmkt.price.iloc[-1]

result_ema = tradeEma(date, 'lktbf50vol', plot="Y", execution="vwap", 
                      fast_coeff=0.2,
                      slow_coeff=0.05,
                      margin = 0.5, dfmkt=dfmkt)

sig = result_ema['df'] 

sig['amt'] = 2 
sig.at[sig.index[0], 'amt'] = 1

pl = sum(100 * sig.direction.values * sig.amt.values * (px_last - sig.price.values))
print(px_last, pl)

""""""
dfmkt_3y = util.setRtData(asset="ktbf3y")
date = dfmkt_3y.date[0]
px_last_3y = dfmkt_3y.price.iloc[-1]

result_ema_3y = tradeEma(date, 'ktbf200vol', plot="Y", execution="vwap", 
                      fast_coeff=0.5,
                      slow_coeff=0.1,
                      margin = 0.5, dfmkt=dfmkt_3y)

sig_3y = result_ema_3y['df'] 

sig_3y['amt'] = 2 
sig_3y.at[sig_3y.index[0], 'amt'] = 1

pl_3y = sum(100 * sig_3y.direction.values * sig_3y.amt.values * (px_last_3y - sig_3y.price.values))
print(px_last_3y, pl_3y)
# 
# num_trade = ts.amt.sum()
# df.at[t, 'num_trade'] = num_trade
    
    # #당일의 결과
    # #print(day, "    ", pl_of_the_day, str(timelyPl.index[-1])[-8:])
    # print(f'Day   | {day}    pl= {pl_of_the_day},  {trade_ended_at},   {num_trade}')
    
    # #누적결과
    # cumsum = round(dfpl.pl.sum(), 1)
    # mean = round(dfpl.pl.mean(), 2)
    # std = round(dfpl.pl.std(), 3)
    # sr = round(mean / std, 3)
    # num_trade_avg = round(dfpl.num_trade.mean(), 1)
    # print(f'Cumul | cumsum: {cumsum}  mean:{mean}  SR: {sr}  trades/day: {num_trade_avg}',
    #       "\n---------------------------------------------------------------")
    
    # pass

# if __name__ == "__main__":
#     main()


