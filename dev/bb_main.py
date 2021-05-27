import utils.util as util
import tradeLoi as tl
import pandas as pd
from matplotlib import pyplot as plt
import datetime as dt
import numpy as np
import math


"""
이득, 손해 사이에 선을 그려주는 함수
"""
def lineDrawer(color,x_list,y_list) :
    plt.scatter(x_list[0],y_list[0],color=color)
    plt.scatter(x_list[1],y_list[1],color=color)
    x = np.array(x_list)
    y = np.array(y_list)
    plt.plot(x,y, color=color,linewidth=4)

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

def recordProfile(df_pf, time, position, pl, status, vwap) :
    df_pf.at[post_i,'time'] = time
    df_pf.at[post_i,'position'] = position
    df_pf.at[post_i,'pl'] = pl
    df_pf.at[post_i,'status'] = status
    df_pf.at[post_i,'vwap'] = vwap
    
date = dt.date(2017,9,19)
date2 = dt.date(2021,4,26)
# date = dt.date(2020,3,20)
df = util.setDfData(str(date), str(date2), 'lktb100vol')
li = sorted(list(set(df['date'])))

writer = pd.ExcelWriter("result.xlsx",engine="xlsxwriter")
df_summary = pd.DataFrame(columns=['pl','sr'])

for dt in li :
    df_today = df[df['date'] == dt]
    
    dti = df_today.index
    pl_today = np.array([])
    
    margin = 0.01
    loss_cut = 0.02
    
    #엑셀 요약만 보고 그림 안보여주고 싶으면 주석
    # fig = plt.figure(figsize=(8,8))
    x=[]
    y=[]
    long_num = 0
    short_num = 0
    long_price = 0
    short_price = 0
    status = 'none'
    position = 'none'
    
    df_pf = pd.DataFrame(columns=['date','time','position','pl','status', 'vwap'])
    df_pf.loc[:]['date']=str(dt)
    
    for pre_i, post_i in zip(dti, dti[80:]) :
        ul = df_today.loc[post_i,'bb_ul'] = np.mean(df_today.loc[pre_i:post_i,'vwap'])+1.5*np.std(df_today.loc[pre_i:post_i,'vwap'])
        ml = df_today.loc[post_i,'bb_ml'] = np.mean(df_today.loc[pre_i:post_i,'vwap'])
        ll = df_today.loc[post_i,'bb_ll'] = np.mean(df_today.loc[pre_i:post_i,'vwap'])-1.5*np.std(df_today.loc[pre_i:post_i,'vwap'])
        sd = np.std(df_today.loc[pre_i:post_i,'vwap'])
        margin = sd/8
        loss_cut = sd/2
        price = df_today.loc[post_i, 'price']
        
            
        #마지막 시각에서 다 팔기
        if post_i == dti[-1]:
            pl = df_today.loc[post_i,'vwap']*long_num - long_price  if position == 'long ' else short_price - df_today.loc[post_i,'vwap'] * short_num
            df_today.loc[post_i,'pl'] = pl
            long_price = 0
            long_num = 0
            short_price = 0
            long_num = 0
            status = 'none'
            pl_today = np.append(pl_today,pl)
            
            recordProfile(df_pf,df_today.at[post_i,'time'], position, pl, 'sell', df_today.loc[post_i,'vwap'])
        
        # 포지션이 없을때 진입을 포지션 롱으로 하나 결정(롱에서 loss cut 했으면 진입 롱 안함)
        elif position =='none' and status != 'long_lc' and abs(round(ll-price,2)) <= margin:
            position = 'long';
            long_price += df_today.loc[post_i,'vwap']
            long_num += 1
            status = 'buy'
            pl = df_today.loc[post_i,'vwap']*long_num - long_price
            recordProfile(df_pf,df_today.at[post_i,'time'], position, pl, 'buy', df_today.loc[post_i,'vwap'])
            x.append(post_i)
            y.append(df_today.loc[post_i,'price'])
            
        # 포지션이 없을때 진입을 포지션 숏으로 하나 결정(숏에서 loss cut 했으면 진입 숏 안함)
        elif position =='none' and status != 'short_lc' and abs(round(ul-price,2)) <= margin:        
            position = 'short';
            short_price += df_today.loc[post_i,'vwap']
            short_num += 1
            status = 'buy'
            pl = short_price -df_today.loc[post_i,'vwap'] * short_num
            recordProfile(df_pf,df_today.at[post_i,'time'], position, pl, 'buy', df_today.loc[post_i,'vwap'])
            x.append(post_i)
            y.append(df_today.loc[post_i,'price'])
            
        # 다 청산하고 pl 0 에다가 hold 상태
        elif position =='none':
            recordProfile(df_pf, df_today.at[post_i,'time'], 'none', 0, 'hold', df_today.loc[post_i,'vwap'])
        
        # long 일때 손절처리.
        elif status == 'hold' and position =='long' and round(ll-price,2) > loss_cut:
            pl = df_today.loc[post_i,'vwap'] * long_num - long_price
            long_price = 0
            long_num = 0
            status = 'long_lc'
            recordProfile(df_pf, df_today.at[post_i,'time'], position, pl, 'cut sell', df_today.loc[post_i,'vwap'])
            x.append(post_i)
            y.append(df_today.loc[post_i,'price'])
            lineDrawer("blue",x,y)
            x=[]
            y=[]
            pl_today = np.append(pl_today,pl)
            
        # short 일때 손절처리
        elif status =='hold' and position == 'short' and round(price - ul, 2) > loss_cut:
            pl = short_price - df_today.loc[post_i,'vwap'] * short_num
            short_price = 0
            short_num = 0
            status = 'short_lc'
            recordProfile(df_pf, df_today.at[post_i,'time'], position, pl, 'cut sell', df_today.loc[post_i,'vwap'])
            x.append(post_i)
            y.append(df_today.loc[post_i,'price'])
            lineDrawer("blue",x,y)
            x=[]
            y=[]
            pl_today = np.append(pl_today,pl)
            
        # 홀드하고 있던것 청산
        # elif position =='long' and (status =='hold' or status == 'buy') and round(price-ul,2) >= -margin :
        elif position =='long' and (status =='hold' or status == 'buy') and round(price-ml,2) >= -margin :
            pl = df_today.loc[post_i,'vwap'] * long_num - long_price
            long_price = 0
            long_num = 0
            status = 'sell'
            recordProfile(df_pf, df_today.at[post_i,'time'], position, pl, status,  df_today.loc[post_i,'vwap'])

            x.append(post_i)
            y.append(df_today.loc[post_i,'price'])
            lineDrawer("red",x,y)
            x=[]
            y=[]
            pl_today = np.append(pl_today,pl)
            
        # elif position == 'short' and (status =='hold' or status == 'buy') and round(ll-price,2) >= -margin:
        elif position == 'short' and (status =='hold' or status == 'buy') and round(ml-price,2) >= -margin:
            pl = short_price - df_today.loc[post_i,'vwap'] * short_num
            short_price = 0
            short_num = 0
            status = 'sell' 
            recordProfile(df_pf, df_today.at[post_i,'time'], position, pl, status,  df_today.loc[post_i,'vwap'])
            
            x.append(post_i)
            y.append(df_today.loc[post_i,'price'])
            lineDrawer("red",x,y)
            x=[]
            y=[]
            pl_today = np.append(pl_today,pl)
            
        # 청산 후에 일반구간.(pl=0이 되는 구간) position을 none으로 하여 언제나 어떤 포지션을 진입가능하도록 함
        elif long_num == 0 and short_num==0:
            recordProfile(df_pf, df_today.at[post_i,'time'], 'none', 0, 'hold', df_today.loc[post_i,'vwap'])
            position = 'none'
    
        # 0이아닌 PL값을 갖고 홀딩하는 일반구간
        else :
            status = 'hold'
            if position == 'long' :
                recordProfile(df_pf, df_today.at[post_i,'time'], position, df_today.loc[post_i,'vwap'] * long_num - long_price, 'hold',df_today.loc[post_i,'vwap'])
            elif position == 'short':
                recordProfile(df_pf, df_today.at[post_i,'time'], position, short_price - df_today.loc[post_i,'vwap'] * short_num, 'hold',df_today.loc[post_i,'vwap'])
            else :
                print("wtf!")
    
    # for result_i in dti:
        # marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
        # color = "tab:red" if marker == "^" else "b"
    # for i in result.index:
    #     marker = "^" if result.loc[i]['direction'] == 1 else "v"
    #     color = "tab:red" if marker == "^" else "b"
    #     x = str(i)[11:]
    #     y = result.loc[i]['price']
    #     ax.scatter(x, y, color=color, marker=marker, s=100) #s=마커사이즈    
        
    df_summary.loc[dt,'pl'] = np.sum(pl_today)
    df_summary.loc[dt,'sr'] = np.mean(pl_today)/np.std(pl_today)
    
    df_summary.to_excel(writer, sheet_name='summary')
    
    plt.plot(df_today.index, df_today['price'])
    plt.plot(df_today.index, df_today['bb_ul'])
    plt.plot(df_today.index, df_today['bb_ml'])
    plt.plot(df_today.index, df_today['bb_ll'])
        
    # plt.plot(dti, df_today['price'])
    df_pf.to_excel(writer, sheet_name=str(dt))
writer.save()