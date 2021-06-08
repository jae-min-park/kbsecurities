import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import utils.util as util
import datetime
from tradeLoi import *


def main():
    
    print("Running main function\n")
    
    #일봉기준 전체 date list
    # ld = list(util.getDailyOHLC().index)[:-26]
    # ld = [d for d in ld if d.year==2021 and d.month==3]
    # ld = [d for d in ld if d.year==2021 ]
    ld = [datetime.date(2021,5,28)]
    
    #일간 PL을 기록하는 dataframe
    dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])
    
    for i, day in enumerate(ld):
        result_ema = tradeEma(day, 'lktbf50vol', plot="Y", execution="vwap", 
                              fast_coeff=0.2,
                              slow_coeff=0.01,
                              margin = 0.5)
        
        timelyPl = calPlEmaTimely(result_ema, timebin="1min", losscut="Y")
        
        dfpl.at[i, 'date'] = day
        
        pl_of_the_day = round(timelyPl.pl[-1], 2)
        dfpl.at[i, 'pl'] = pl_of_the_day
        
        num_trade = timelyPl.num_trade[-1]
        dfpl.at[i, 'num_trade'] = num_trade
        
        trade_ended_at = str(timelyPl.index[-1])[-8:]
        
        #당일의 결과
        #print(day, "    ", pl_of_the_day, str(timelyPl.index[-1])[-8:])
        print(f'Day   | {day}    pl= {pl_of_the_day},  {trade_ended_at},   {num_trade}')
        
        #누적결과
        cumsum = round(dfpl.pl.sum(), 1)
        mean = round(dfpl.pl.mean(), 2)
        std = round(dfpl.pl.std(), 3)
        sr = round(mean / std, 3)
        num_trade_avg = round(dfpl.num_trade.mean(), 1)
        print(f'Cumul | cumsum: {cumsum}  mean:{mean}  SR: {sr}  trades/day: {num_trade_avg}',
              "\n---------------------------------------------------------------")
    
    dfpl.set_index(pd.to_datetime(dfpl.date), inplace=True)
    
    return dfpl

if __name__ == "__main__":
    dfpl = main()


