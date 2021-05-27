# -*- coding: utf-8 -*-
"""
Created on Tue May 25 21:24:16 2021

@author: infomax
"""
import tradeLoi as tl
import datetime
import pandas as pd
import utils.util as util
import matplotlib.pyplot as plt

ld = list(util.getDailyOHLC().index)

date = datetime.date(2018,2,2)

timebin = "1min"

df1min = util.setDfData(date, date, '`lktb1min`', datetime_col="Y")
df = df1min.resample(timebin, label='right', closed='right').agg({'close': 'last'})

dfplot = pd.DataFrame(index=df.index.time)

daylen = len(df.index)

bad_days = pd.read_excel("EMA경향분석.xlsx").bad
good_days = pd.read_excel("EMA경향분석.xlsx").good

for day in good_days:
    
    r = tl.tradeEma(day, vol_option='lktb50vol', plot="N", execution="vwap", 
                    fast_coeff=0.3, slow_coeff=0.05, margin = 1.0)
    dfpl = tl.calPlEmaTimely(r, timebin=timebin)
    
    print(day, round(dfpl.pl[-1], 1))
    
    if len(dfpl) != daylen:
        print("skipped")
        pass
    else:
        dfplot[day] = dfpl.pl.values
    
    
dfplot.plot()
plt.legend(loc='upper left', ncol=2, bbox_to_anchor=(0,-0.1))
plt.figure(figsize=(15,15))
plt.show()

date = datetime.date(2020,3,20)
def showChartNStd(date):
    df = util.setDfData(date, date, '`lktb50vol`', datetime_col="Y")
    px = df.vwap
    
    for i in df.index:
        df.at[i, 'std'] =
