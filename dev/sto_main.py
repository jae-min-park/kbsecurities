import utils.util as util
import pandas as pd
from matplotlib import pyplot as plt
import datetime as dt
import numpy as np
import os
from tqdm import tqdm

# """
# 이득, 손해 사이에 선을 그려주는 함수
# """
# def lineDrawer(color,x_list,y_list) :
#     plt.scatter(x_list[0],y_list[0],color=color)
#     plt.scatter(x_list[1],y_list[1],color=color)
#     x = np.array(x_list)
#     y = np.array(y_list)
#     plt.plot(x,y, color=color,linewidth=4)

# """파는 가격을 보수적으로 잡을때"""
# def flr(item):
#     item = item * 100
#     item = math.floor(item)
#     return item / 100

# """사는 가격을 보수적으로 잡을때"""
# def upp(item) :
#     item = item * 100
#     item = math.ceil(item)
#     return item / 100

def writeSummary(df_result, dti_now, time, action, vwap, avg_price, amount, pl, local_index) :
    df_result.loc[dti_now,'time'] = time
    df_result.loc[dti_now,'action'] = action
    df_result.loc[dti_now,'vwap'] = vwap
    df_result.loc[dti_now,'avg_price'] = avg_price
    df_result.loc[dti_now,'left_amount'] = amount
    df_result.loc[dti_now,'pl'] = pl
    df_result.loc[dti_now,'local_index'] = local_index

def getPl(vwap, buy_price, amt, direction=1) :
    return round(amt*(vwap - buy_price)*direction,3)

def stochastic(dfmkt, date, N, m, t, buy_margin=0, sell_margin=0, plot='N'):
    idx = dfmkt.index
    # slow_D = []
    # slow_K = []
    fast_D= []
    fast_K= []
    i = N-1
    
    cols = ['time', 'action', 'vwap', 'avg_price', 'left_amount', 'pl', 'local_index']
    df_result = pd.DataFrame(columns=cols)
    buy_price = 0.0
    amount = 0
    
    for dti_pre ,dti_now, dti_post in zip(idx, idx[N-1:], idx[N:]):

        sto_N = np.array(dfmkt.loc[dti_pre:dti_now]['vwap'])
        _max = np.max(sto_N)
        _min = np.min(sto_N)
        
        sto = 0
        if _max != _min :
            sto = (dfmkt.loc[dti_now, 'vwap']-_min)/(_max-_min)
        elif len(fast_K) > 0 :
            sto = fast_K[-1]
            
        fast_K.append(sto)
        dfmkt.loc[dti_now, 'fast_K'] = sto
    
        if len(fast_K)>=m:
            fd = np.mean(fast_K[-m:])
            fast_D.append(fd)
            dfmkt.loc[dti_now,'fast_D'] = fd
            
        if len(fast_K)>=t:
            sk = np.mean(fast_K[-t:])
            # slow_K.append(sk)
            dfmkt.loc[dti_now,'slow_K'] = sk
            
        if len(fast_D)>=t:
            sd = np.mean(fast_D[-t:])
            # slow_D.append(sd)
            dfmkt.loc[dti_now,'slow_D'] = sd
    
            if dfmkt.iloc[i-1]['slow_K'] - dfmkt.iloc[i-1]['slow_D'] > sell_margin and sell_margin < dfmkt.iloc[i]['slow_D'] - dfmkt.iloc[i]['slow_K']:
            # slow_K가 slow_D밑으로 내려갈때 매도
                if amount > 0 :
                    time = dfmkt.loc[dti_post]['time']
                    vwap = dfmkt.loc[dti_post]['vwap']
                    pl = getPl(vwap=dfmkt.loc[dti_post]['vwap'], buy_price = buy_price, amt = amount)
                    local_index = dfmkt.loc[dti_post]['index']
                    writeSummary(df_result, dti_post, time, 'sell', vwap, buy_price, amount, pl, local_index)
                    amount = 0
                    
            elif buy_margin < dfmkt.iloc[i-1]['slow_D'] - dfmkt.iloc[i-1]['slow_K'] and dfmkt.iloc[i]['slow_K'] - dfmkt.iloc[i]['slow_D'] > buy_margin :
            # slow_K가 slow_D 위로 올라 갈때 매수
                time = dfmkt.loc[dti_post]['time']
                vwap = dfmkt.loc[dti_post]['vwap']
                buy_price = (dfmkt.loc[dti_post]['vwap']+ buy_price*amount) / (amount+1)
                amount+=1
                pl = 0 
                local_index = dfmkt.loc[dti_post]['index']
                writeSummary(df_result, dti_post, time, 'buy', vwap, buy_price, amount, pl, local_index)
        if idx[-2] == i :
            # 마지막에 청산
            if amount > 0 :
                time = dfmkt.loc[dti_post]['time']
                vwap = dfmkt.loc[dti_post]['vwap']
                pl = getPl(vwap=dfmkt.loc[dti_post]['vwap'], buy_price = buy_price, amt = amount)
                local_index = dfmkt.loc[dti_post]['index']
                writeSummary(df_result, dti_post, time, 'sell', vwap, buy_price, amount, pl, local_index)
                amount = 0
        i+=1
    # df_result.dropna(inplace=True)
    
    if not os.path.exists('sto_test.xlsx'):
        with pd.ExcelWriter('sto_test.xlsx', mode = 'w', engine = 'openpyxl') as writer :
            df_result.to_excel(writer, sheet_name=str(date))
    else:
        with pd.ExcelWriter('sto_test.xlsx', mode = 'a', engine = 'openpyxl') as writer :
            df_result.to_excel(writer, sheet_name=str(date))
    
    writer.save()
    return df_result
    # fig, ax1 = plt.subplots()
    # ax1.plot(idx, dfmkt['vwap'])
    # ax2 = ax1.twinx()
    # ax2.plot(idx, dfmkt['slow_K'], color = 'green', linewidth=1)
    # ax3 = ax2.twinx()
    # ax3.plot(idx, dfmkt['slow_D'], color = 'purple', linewidth=1)
    # plt.show()
    
N = 20
m = 30
t = 5
# day = dt.date(2017,12,19)
# dfmkt = util.setDfData(day, day, 'lktbf50vol')
# r = stochastic(dfmkt, day, N, m, t)

total = 0.00
df_summary = pd.DataFrame(columns=['day_pl_sum', 'day_signal_cnt'])
writer = pd.ExcelWriter("summary_sto_test.xlsx",engine="xlsxwriter")

"""복수 일자 """
ld = list(util.getDailyOHLC().index)[:]
ld = [d for d in ld if d.year>=2017 and d.year==2021]

for i, day in tqdm(enumerate(ld)) :    
    dfmkt = util.setDfData(day, day, 'lktbf50vol')
    r = stochastic(dfmkt, day, N, m, t)
    
    daily_pl = r['pl'].sum()
    trade_cnt = len(r.index)
    df_summary.loc[day, 'day_pl_sum'] = daily_pl
    df_summary.loc[day, 'day_signal_cnt'] = trade_cnt
    
    # calDailyPlRangeLoi(r, day)
    print("-------------------------------------------------------------\n"
    f'Day   | {day}    pl= {daily_pl}, {trade_cnt}')
    total += daily_pl
    print(total, "   ",total/(i+1))
    print("-------------------------------------------------------------------------------------\n")
df_summary.to_excel(writer)
writer.save()
    
