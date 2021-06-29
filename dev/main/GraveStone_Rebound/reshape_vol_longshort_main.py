import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
from utils.util import *

df_sample = setDfData('2019-04-12','2019-04-12', '`lktb200vol`')


"""
이득, 손해 사이에 선을 그려주는 함수
"""
def lineDrawer(color,x1,y1,x2,y2) :
    plt.scatter(x1,y1,color=color)
    plt.scatter(x2,y2,color=color)
    x = np.array([x1, x2])
    y = np.array([y1, y2])
    plt.plot(x,y, color=color,linewidth=4)

"""
파는 가격을 보수적으로 잡을때
"""
def flr(item):
    item = item * 100
    item = math.floor(item)
    return item / 100

"""
사는 가격을 보수적으로 잡을때
"""
def upp(item) :
    item = item * 100
    item = math.ceil(item)
    return item / 100

"""
long 혹은 short position 진입조건
"""
def longTest(long, vwap, opn,a, v, v2) :
    return not long and round(abs(vwap - opn),2) <= 0.01 and a > 0 and v > 0  and v2 >= 0

def shortTest(short, vwap, opn, a, v, v2):
    return not short and round(abs(vwap - opn),2) <= 0.01 and a < 0 and v < 0 and v2 <= 0 

"""
mode : "preday_close", "preday_max", "open"
"""
def strategy(df_sample,mode) :
    """
    dt는 각 날자이고, df_today는 날자를 만족시키는 dataframe이다.
    """
    pt = 0.1
    lc = -0.05
    # vol_term = 35
    preday_close = 0
    preday_max = 0
    
    
    for dt in li :
        df_today = df_sample[df_sample['date'] == dt]
    
        dti = df_today.index
        long = False
        long_win = long_lose = long_price = long_index = 0
        long_profit = []
        short = False
        short_win = short_lose = short_price = short_index = 0
        short_profit=[]
        
        if mode == 'preday_close' :
            loi = df_today.iloc[0]['open'] if (preday_close == 0) else preday_close # line of interest : loi
        elif mode =='preday_max' :
            loi = df_today.iloc[0]['open'] if (preday_max == 0) else preday_max # line of interest : loi
        elif mode == 'open' :
            loi = df_today.iloc[0]['open']
    
        preday_max = 1
        vol_start = 0
        vol_end = 0
        
        for dti_pre, dti_mid, dti_post in zip(dti, dti[1:], dti[2:]):
            vwap = df_today.loc[dti_mid,'vwap']
            close = df_today.loc[dti_mid,'price']
            high = df_today.loc[dti_mid,'high']
            low = df_today.loc[dti_mid,'low']
    
            if preday_max < close :
                preday_max = close
            
        # 매수조건
            # if df_today.loc[i-1, 'rbPattern'] == True:
            #     df_today.loc[i, 'buy'] = df_today.loc[i, 'price']
            
            # REBOUND 이기 위한 조건
            # if df_today.at[i-1,'gvsPattern'] == True and close <= opn  :
            #     df_today.at[i,'rbPattern'] = True
            #     df_today.at[i,'rbPattern2'] = 'Y'
    
            v = df_today.at[dti_mid,'v'] = close - vwap
            pre_v = df_today.at[dti_pre,'v'] = df_today.at[dti_pre, 'price'] - df_today.at[dti_pre,'vwap'] 
            v2 = df_today.at[dti_mid, 'price'] - df_today.at[dti_pre,'vwap']
            a = df_today.at[dti_mid,'a'] = v - pre_v
            
            # 오전에만 돌릴까 말까 고민
            # if df_today.at[dti_mid,'time'] <= pd.Timedelta("12:00:00") :
                
            # 롱진입, 숏진입 초입부
            if not short and longTest(long, vwap, loi, a, v, v2):
                long = True
                long_index=dti_post
                long_price = df_today.loc[dti_post,'price']
            elif not long and shortTest(short, vwap, loi, a, v, v2) :
                short = True
                short_index = dti_post
                short_price = df_today.loc[dti_post,'price']
            # 롱 익절
            if long and upp(df_today.loc[dti_mid,'vwap']) > long_price + pt:
                win = pt
                lineDrawer("red",long_index,long_price,dti_post,df_today.loc[dti_post,'vwap'])
                
                long_win+=1
                long_profit.append(win)
                long=False
            # 롱 손절후 숏으로 전환
            elif long and upp(df_today.loc[dti_mid,'vwap']) <= long_price +lc or shortTest(short, vwap, loi,a, v, v2):
            # elif long and upp(df_today.loc[dti_mid,'vwap']) <= long_price +lc or shortTest(short, vwap, loi,a, v, v2) and dti_mid - short_index >= vol_term:
                if upp(df_today.loc[dti_mid,'price']) > long_price :
                    win = upp(df_today.loc[dti_post,'vwap']) - long_price
                    lineDrawer("red",long_index,long_price,dti_post, upp(df_today.loc[dti_post,'vwap']))
                    
                    long_win+=1
                    long_profit.append(win)
                    long=False
                else:
                    lineDrawer("blue",long_index,long_price,dti_post,flr(df_today.loc[dti_post,'vwap']))
                
                    lose = lc
                    long = False
                    long_profit.append(lose)
                    long_lose+=1
                # if shortTest(short, vwap, loi,a, v, v2) and dti_mid - short_index >= vol_term :
                if shortTest(short, vwap, loi,a, v, v2) :
                    short = True
                    short_index = dti_post
                    short_price = df_today.loc[dti_post,'price']
            # 숏 익절 
            elif short and flr(df_today.loc[dti_mid,'vwap']) <= short_price - pt:
                win = pt
                lineDrawer("orange",short_index,short_price,dti_post,df_today.loc[dti_post,'price'])
                short_profit.append(win)
                short_win+=1
                short=False
            # 숏 손절후 롱으로 전환
            elif short and flr(df_today.loc[dti_mid,'vwap']) >= short_price -lc or longTest(long, vwap, loi,a, v, v2):
            # elif short and flr(df_today.loc[dti_mid,'vwap']) >= short_price -lc or longTest(long, vwap, loi,a, v, v2) and dti_mid - long_index >= vol_term:
                if short_price > df_today.loc[dti_mid,'price'] :
                    
                    win = short_price - flr(df_today.loc[dti_mid,'vwap'])
                    lineDrawer("orange",short_index,short_price,dti_post,flr(df_today.loc[dti_post,'vwap']))
                    
                    short_win+=1
                    short_profit.append(win)
                    short=False
                else :
                    lineDrawer("purple",short_index,short_price,dti_post,upp(df_today.loc[dti_post,'vwap']))
                    lose = lc
                    short = False
                    short_lose+=1
                    short_profit.append(lose)
                if longTest(long, vwap, loi,a, v, v2) :
                # if longTest(long, vwap, loi,a, v, v2) and dti_mid - long_index >= vol_term:
                    long = True
                    long_index = dti_post
                    long_price = df_today.loc[dti_post,'price']
            # 마지막 인덱스에서 처분    
            elif long and dti_post == dti[-1]:
                last = round(df_today.loc[dti_post,'price'] - long_price,2)
                if last > 0 :
                    lineDrawer("red",long_index,long_price,dti_post,df_today.loc[dti_post,'price'])
                    long_win += 1 
                else:
                    lineDrawer("blue",long_index,long_price,dti_post,df_today.loc[dti_post,'price'])
                    long_lose += 1  
                long_profit.append(last)
                long = False
            elif short and dti_post == dti[-1]:
                last = round(short_price - df_today.loc[dti_post,'price'],2)
                if last > 0 :
                    lineDrawer("orange",short_index,short_price,dti_post,df_today.loc[dti_post,'price'])
                    short_win +=1  
                else:
                    lineDrawer("purple",short_index,short_price,dti_post,df_today.loc[dti_post,'price'])
                    short_lose +=1
                short_profit.append(last)
                short = False
            
                
            # GRAVE STONE 이면 패턴 체크
            if round(abs(close - loi),2) <= 0.01 and round(min(loi,close)-low,2) <= 0.01 and round(high-max(loi,close),2) >= 0.04:
                df_today.at[dti_post, 'gvsPattern'] = True
        
        
        preday_close = df_today.iloc[-1]['price']
        
        longProfit = np.array(long_profit)
        shortProfit = np.array(short_profit)
        print("long:"+str(long_profit)+ str(sum(long_profit))+ ", " + str(len(long_profit))+ " " + str(np.average(longProfit)))
        print("short:"+str(short_profit)+ str(sum(short_profit))+ ", " + str(len(short_profit))+ " " + str(np.average(shortProfit)))
    
        df_tag.loc[dt] = [sum(long_profit), len(long_profit), np.average(longProfit), sum(short_profit), len(short_profit), np.average(shortProfit), (sum(long_profit)+sum(short_profit)), long_win, long_lose, short_win, short_lose]
        df_tag.to_excel(writer,sheet_name=mode)
        
        plt.plot(dti,df_today['price'])
        plt.show()
   
"""
엑셀에 요약본 작성하려고 만드는 dataframe
"""
tag_list = "long_sum", "long_len", "long_avg", "short_sum", "short_len", "short_avg", "total", "long_win", "long_lose", "short_win","short_lose"
df_tag = pd.DataFrame(columns=tag_list)

"""
li는 setDfData의 param으로 준 날자들의 집합을 오름차순으로 정렬해 놓은 값이다.
"""
li = sorted(list(set(df_sample['date'])))

"""
소스코드의 경로에 result.xlsx 파일로 결과가 정리되고 날자별로 시트가 나온다.
"""
writer = pd.ExcelWriter('precise.xlsx', engine='xlsxwriter')

strategy(df_sample, 'preday_close')
strategy(df_sample, 'preday_max')
strategy(df_sample, 'open')
    
writer.save()



