# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 12:06:19 2021

@author: infomax
"""

import lktbftick_dataManager as dm

import math
import pymysql
import pandas as pd
import numpy as np

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                          # host = '211.232.156.57',
                          host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

# """
# 일단 기본 ohlc sql통해 날자값 안으로 df받아오기
# """
dfm = dm.DataFrameManager(cursor)
dt_start = pd.Timestamp(year=2020, month = 11, day = 1)
dt_end = pd.Timestamp(year=2020, month = 11, day = 30)
dfm.setDfData(dt_start, dt_end)
df = dfm.df

li = sorted(list(set(df['date'])))
cnt = long_tot = short_tot = tot_cnt = 0

tick_long_take = 0.06
tick_long_cut = 0.04
tick_short_take = 0.06
tick_short_cut = 0.04

forExcel = pd.DataFrame(columns=['date', 'long_earn', 'short_earn','std', 'long sharpe ratio','short sharpe ratio', 'long_day_cnt', 'long_win', 'long_lose', 'long_draw','long_win max', 'long_loss max','long_win avg', 'long_loss avg', 'short_day_cnt', 'short_win', 'short_lose', 'short_draw','short_win max', 'short_loss max','short_win avg', 'short_loss avg'] )
for dt in li :
    
    df_date = df[df['date'] == dt]
    dti = df_date.index

    long_profit = [0] 
    long_loss = [0]
    short_profit = [0]
    short_loss = [0]
    long_win = long_lose = long_draw = long_buy = long_sell = long_buy_cnt = long_day_cnt = _sum = 0
    short_win = short_lose = short_draw = short_buy = short_sell = short_buy_cnt = short_day_cnt = sum_ = 0
    long_pnl = long_sell - long_buy
    short_pnl = short_buy - short_sell
    longState = False
    shortState = False    
    for dti_pre, dti_post in zip(dti, dti[1:]) :
        df_date.loc[dti_post,'v'] = df_date.loc[dti_pre,'vol'] * (df_date.loc[dti_post,'close'] - df_date.loc[dti_pre,'close'])
        df_date.loc[dti_post,'a'] = (df_date.loc[dti_post,'v'] - df_date.loc[dti_pre,'v'])
        
        if dti_post<df_date.index[-1] and (df_date.loc[dti_post, 'v'] < 0 and df_date.loc[dti_post, 'a'] > 0 or (short_buy - short_buy_cnt*df_date.loc[dti_post+1, 'close']) <= -tick_short_cut or (short_buy - short_buy_cnt*df_date.loc[dti_post+1, 'close']) >= tick_short_take) :
            # df_date.loc[dti_post+1, 'buy']  = True
            """
            long 매수
            """
            if df_date.loc[dti_post, 'v'] < 0 and df_date.loc[dti_post, 'a'] > 0 :
                long_buy += round(df_date.loc[dti_post+1, 'close'],2)
                long_buy_cnt += 1
                longState = True
            
            """
            short 매도
            """
            if shortState :
                short_sell = round(short_buy_cnt*df_date.loc[dti_post+1, 'close'],2) 
                short_pnl = round(short_buy-short_sell,2)
                # df_date.loc[dti_post, 'pnl'] = long_pnl
                shortState = False
                if not math.isnan(short_pnl) :
                    if short_pnl > 0 :
                        short_win+=1
                        short_profit.append(short_pnl)
                    elif short_pnl < 0 :
                        short_lose += 1
                        short_loss.append(short_pnl)
                    else :
                        short_draw += 1                  
                    sum_ += short_pnl
                    short_day_cnt+=1
                    tot_cnt+=1
                short_buy_cnt = short_buy = short_sell = 0
                
        elif dti_post < df_date.index[-1] and (df_date.loc[dti_post, 'v'] > 0 and df_date.loc[dti_post, 'a'] < 0 or (long_buy_cnt*df_date.loc[dti_post+1, 'close'] - long_buy) <= -tick_long_cut  or (long_buy_cnt*df_date.loc[dti_post+1, 'close'] - long_buy) >= tick_long_take):
            # df_date.loc[dti_post+1, 'sell'] = True
            """
            long 매도
            """
            if longState :
                long_sell = round(long_buy_cnt*df_date.loc[dti_post+1, 'close'],2) 
                long_pnl = round(long_sell - long_buy,2)
                
                longState = False
                # df_date.loc[dti_post, 'pnl'] = long_pnl
                if not math.isnan(long_pnl) :
                    if long_pnl > 0 :
                        long_win+=1
                        long_profit.append(long_pnl)
                    elif long_pnl < 0 :
                        long_lose += 1
                        long_loss.append(long_pnl)
                    else :
                        long_draw += 1                  
                    _sum += long_pnl
                    long_day_cnt+=1
                    tot_cnt+=1
                long_buy_cnt = long_buy = long_sell = 0
            elif df_date.loc[dti_post, 'v'] > 0 and df_date.loc[dti_post, 'a'] < 0 :
                """
                short 매수
                """
                short_buy += round(df_date.loc[dti_post+1, 'close'],2)
                short_buy_cnt += 1
                shortState = True
            # print(str(df_date.loc[dti_post,'date']) + " " +str(df_date.loc[dti_post,'time']) +" sell:" + str(sell) +"-buy:"+str(buy) +" = "+ str(round(arbitrage,2)))
    _sum = round(sum(long_profit),2) + round(sum(long_loss),2)
    sum_ = round(sum(short_profit),2) + round(sum(short_loss),2)
    long_tot += _sum
    short_tot += sum_
    
    long_profit_avg = 0 
    long_loss_avg = 0
    short_profit_avg = 0
    short_loss_avg = 0
    if len(long_profit) == 1 :
        long_profit_avg = round(sum(long_profit),2)/len(long_profit)
    else :
        long_profit_avg = round(sum(long_profit),2)/(len(long_profit)-1)
    if len(long_loss) == 1 :
        long_loss_avg = round(sum(long_loss),2)/len(long_loss)
    else :
        long_loss_avg = round(sum(long_loss),2)/(len(long_loss)-1)
 
    if len(short_profit) == 1 :
        short_profit_avg = round(sum(short_profit),2)/len(short_profit)
    else :
        short_profit_avg = round(sum(short_profit),2)/(len(short_profit)-1)
    if len(short_loss) == 1 :
        short_loss_avg = round(sum(short_loss),2)/len(short_loss)
    else :
        short_loss_avg = round(sum(short_loss),2)/(len(short_loss)-1)

    long_sharpe_ratio = _sum/long_day_cnt/np.std(df_date['close']) if long_day_cnt > 1 else 0
    short_sharpe_ratio = sum_/short_day_cnt/np.std(df_date['close']) if short_day_cnt > 1 else 0
    # print(str(df_date.loc[dti_post,'date']) + "  long_earn:" + str(_sum) + "  short_earn:"+str(sum_)+"  std:" + str(np.std(df_date['close'])) + "  long_day_cnt:" + str(long_day_cnt) + "  long_win:"+str(long_win) + "  long_lose:"+str(long_lose)+"  long_draw:"+str(long_draw) +"  long win max:"+str(max(long_profit)) + "  long loss max:" + str(min(long_loss)) + "  long win avg:"+str(long_profit_avg) + '  long loss avg:'+str(long_loss_avg) +"  short_day_cnt:" + str(short_day_cnt) + "  short_win:"+str(short_win) + "  short_lose:"+str(short_lose)+"  short_draw:"+str(short_draw) +"  short win max:"+str(max(short_profit)) + "  short loss max:" + str(min(short_loss)) + "  short win avg:"+str(short_profit_avg) + '  short loss avg:'+str(short_loss_avg))
    print(str(df_date.loc[dti_post,'date']) + "  long_earn:" + str(_sum) + "  short_earn:"+str(sum_)+ "  long_day_cnt:" + str(long_day_cnt) + "  long_win:"+str(long_win) + "  long_lose:"+str(long_lose)+"  long_draw:"+str(long_draw) +"  long win max:"+str(max(long_profit)) + "  long loss max:" + str(min(long_loss)) + "  long win avg:"+str(long_profit_avg) + '  long loss avg:'+str(long_loss_avg) +"  short_day_cnt:" + str(short_day_cnt) + "  short_win:"+str(short_win) + "  short_lose:"+str(short_lose)+"  short_draw:"+str(short_draw) +"  short win max:"+str(max(short_profit)) + "  short loss max:" + str(min(short_loss)) + "  short win avg:"+str(short_profit_avg) + '  short loss avg:'+str(short_loss_avg))
    print()
    # print(profit)
    # print(loss)
    
    forExcel.loc[cnt] = [df_date.loc[dti_post,'date'], _sum, sum_, np.std(df_date['close']), long_sharpe_ratio, short_sharpe_ratio, long_day_cnt, long_win, long_lose, long_draw, max(long_profit), min(long_loss), long_profit_avg, long_loss_avg, short_day_cnt, short_win, short_lose, short_draw, max(short_profit), min(short_loss), short_profit_avg, short_loss_avg ]
    cnt+=1


forExcel.to_excel('test.xls')
# std = np.std(df['close'])
# tot_avg = tot/tot_cnt
# print("tot:"+str(tot))
# print('num:' + str(tot_cnt))
# print("std:"+str(std))
# print("sharpe ratio:" + str(tot_avg/std))
# print("win:"+str(win) + ", lose:"+str(lose)+', draw:'+str(draw))
# print("win max : "+ str(max(profit)) + ", loss max :" + str(min(loss)) + ", win avg : " + str(sum(profit)/len(profit)) + "loss avg :" + str(sum(loss)/len(loss)) + "  winmax:" + str(max(profit)) +"  lossmax"+str(min(loss)) +"  winavg:" + str(sum(profit)/len(profit)) + "  lossavg:" + str(sum(loss)/len(loss)))


# forExcel = pd.DataFrame(columns=['date', 'tot', 'num', 'std', 'sharpe ratio', 'win', 'lose', 'draw','win max', 'loss max','win avg', 'loss avg'] )
# forExcel.loc[1] = [dt_start, tot, tot_cnt, std, tot_avg/std, win, lose, draw, max(profit), min(loss), sum(profit)/len(profit), sum(loss)/len(loss) ]
# forExcel.to_excel('test.xls')
    # df_date['reboundPattern'] = df_date['reboundPattern'].fillna(False)
    
    #     # dti = paramDf.index
    #     dti = paramDf[paramDf['time'] <= pd.Timedelta("10:00:10")].index
    #     if paramDf.loc[dti[0],'open'] - pre_close < 0 :
    #         paramDf['gravePattern'] = False
    #         paramDf['reboundPattern'] = False
    #         paramDf['declinePattern'] = False
    #         return paramDf
        
    #     for dti_pre, dti_post in zip(dti, dti[1:]) :
    #         if round(abs(paramDf.loc[dti_pre,'body']),2) <= grvStn_max_body and round(paramDf.loc[dti_pre, 'u_tail'],2) >= grvStn_min_utail and round(paramDf.loc[dti_pre, 'l_tail'],2) <= grvStn_max_ltail :
    #             paramDf.loc[dti_pre, 'gravePattern'] = True
    #             if paramDf.loc[dti_post, 'body'] >= rebound_min_body :
    #                 paramDf.loc[dti_post, "reboundPattern"] = True
    #             elif paramDf.loc[dti_post, 'body'] <= decline_max_body : 
    #                 paramDf.loc[dti_post, "declinePattern"] = True
    #             else:
    #                 paramDf.loc[dti_post, "reboundPattern"] = False
    #                 paramDf.loc[dti_post, "declinePattern"] = False
    #         else :
    #             paramDf.loc[dti_pre, 'gravePattern'] = False
    #             paramDf.loc[dti_post, 'reboundPattern'] = False
    #             paramDf.loc[dti_post, "declinePattern"] = False
    #     paramDf['gravePattern'] = paramDf['gravePattern'].fillna(False)
    #     paramDf['reboundPattern'] = paramDf['reboundPattern'].fillna(False)
    #     paramDf['declinePattern'] = paramDf['declinePattern'].fillna(False)
    #     return paramDf
    
# """
# 기본 df에 대해 day_ohlc 및 캔들 데이터들 df에 추가로 받아오기
# """
# date_set = ddt_util.get_date_list(df)
# df_candle = pd.DataFrame(columns=dfm.df.columns)
# for date in tqdm(date_set) :
#     tempDf = dfm.df[dfm.df['date'] == date]
#     tempDf = dfm.getCandleValueDf(tempDf)
#     df_candle = df_candle.append(tempDf)

# """
# 전략을 위한 column 추가한 df 만들기
# """
# df_candle['gravePattern'] = False
# df_candle['reboundPattern'] = False
# df_candle['declinePattern'] = False

# df_strategy = pd.DataFrame(columns=df_candle.columns)
# for i,date in enumerate(date_set) :
#     pre_date_close = 9999
#     if i > 0 :
#         tmpDf = df_candle[df_candle['date'] == date_set[i-1]]
#         pre_date_close = tmpDf.iloc[-1]['close']
#         # print(tmpDf.iloc[-1][['date', 'time', 'close']])
    
#     tempDf = df_candle[df_candle['date'] == date]
#     tempDf = dfm.getGraveStoneAndReboundValueDf(tempDf, pre_date_close)
#     df_strategy = df_strategy.append(tempDf)



# """
# 전략을 만족하는 날자를 확인하기 위한 print
# """
# print(df_strategy[df_strategy.gravePattern])
# print(df_strategy[df_strategy.reboundPattern])
# print(df_strategy[df_strategy.declinePattern])
# pm.plot(df, df_strategy[df_strategy.declinePattern].index)


# """
# DB에 백테스트용 데이타들 삽입
# """
# dfm.insertExcelData(cursor)
# test_db.commit()
