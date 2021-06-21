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

def writeSummary(df_result, dti, time, pre_status, post_status, pre_position, post_position, action, vwap, avg_price, amount, pl, cause, local_index) :
    df_result.loc[dti,'time'] = time
    df_result.loc[dti,'pre_status'] = pre_status
    df_result.loc[dti,'post_status'] = post_status
    # df_result.loc[dti,'slow_K'] = slow_k
    # df_result.loc[dti,'slow_D'] = slow_d
    df_result.loc[dti,'pre_position'] = pre_position
    df_result.loc[dti,'post_position'] = post_position
    df_result.loc[dti,'action'] = action
    df_result.loc[dti,'vwap'] = vwap
    df_result.loc[dti,'avg_price'] = avg_price
    df_result.loc[dti,'left_amount'] = amount
    df_result.loc[dti,'pl'] = pl
    df_result.loc[dti,'cause'] = cause
    df_result.loc[dti,'local_index'] = local_index

def getPl(vwap, buy_price, amt, direction=1) :
    return round(amt*(vwap - buy_price)*direction,3)


def crossTest(sto_fast, sto_slow, margin=0.05):
    """
    sto_fast와 sto_slow를 비교
    
    Returns
    -------
        "attached" / "above" / "below" 중에 하나를 리턴
    """
    if np.isnan(sto_fast) or np.isnan(sto_slow):
        return 'None'
    if abs(sto_fast - sto_slow) <= margin:
        cross_status = "attached"
    elif sto_fast > sto_slow:
        cross_status = "above"
    elif sto_fast < sto_slow:
        cross_status = "below"
    else:
        raise NameError("Unexpected!!!")
        
    return cross_status
    

def stochastic(dfmkt, date, N, m, t, pt=0.08, lc=-0.15, below_margin=0.1, above_margin=0.9, plot='N'):
    idx = dfmkt.index
    # slow_D = []
    # slow_K = []
    fast_D= []
    fast_K= []
    i = N-1
    
    cols = ['time', 'pre_status', 'post_status', 'pre_position', 'post_position','action', 'vwap', 'avg_price', 'left_amount', 'pl', 'cause', 'local_index']
    df_result = pd.DataFrame(columns=cols)
    buy_price = 0.0
    amount = 0
    
    # pre_position ='None'
    position = 'None'
    status = 'None'
    
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
    
        # if len(fast_K)>=m:
        #     fd = np.mean(fast_K[-m:])
        #     fast_D.append(fd)
        #     dfmkt.loc[dti_now,'fast_D'] = fd
            
        if len(fast_K)>=t:
            sk = np.mean(fast_K[-t:])
            # slow_K.append(sk)
            dfmkt.loc[dti_now,'slow_K'] = sk
            
        # if len(fast_D)>=t:
        #     sd = np.mean(fast_D[-t:])
        #     # slow_D.append(sd)
        #     dfmkt.loc[dti_now,'slow_D'] = sd

            pl = 0.0
            vwap = dfmkt.loc[dti_post]['vwap']
            pre_position = position
            pre_status = status
            time = dfmkt.loc[dti_post]['time']
            local_index = dfmkt.loc[dti_post]['index']
            if position == 'long':
                pl = getPl(vwap, buy_price, amount, 1)
            elif position =='short':
                pl = getPl(vwap, buy_price, amount, -1)
                
            # long이거나 short이면서 pl 이 pt 초과면 익절청산, pl이 lc 미만이면 손절청산            
            if (position == 'long' or position =='short') and (pl > pt or pl < lc):
                position = 'None'
                
                cause = 'pt'
                cause = 'lc' if pl<lc else 'pt'
                writeSummary(df_result, dti_now, time, pre_status, status, pre_position, position, 'close', vwap, buy_price, amount, pl, cause, local_index)
                buy_price = 0
                amount = 0
                
            # slow_K가 below_margin(0.3)밑으로 내려갈때 short 청산하고 
            elif (status == 'above' or status == 'None' or status == 'mid') and crossTest(dfmkt.loc[dti_now,'slow_K'], below_margin) == 'below' :
                if position == 'short' and amount > 0 :
                    status = 'below'
                    position = 'None'
                    cause = 'below margin'
                    writeSummary(df_result, dti_now, time, pre_status, status, pre_position, position, 'close', vwap, buy_price, amount, pl, cause, local_index)
                    buy_price = 0
                    amount = 0
            # long 으로 포지션 잡기
                status = 'below'
                position = 'long'
                buy_price = (vwap + buy_price*amount) / (amount+1)
                amount+=1
                pl = 0
                writeSummary(df_result, dti_post, time, pre_status, status, pre_position, position, 'open', vwap, buy_price, amount, pl, 'None', local_index)

            # slow_K가 above_margin(0.7)위로 올라갈때 long 청산하고             
            elif (status == 'below' or status == 'None' or status == 'mid') and crossTest(dfmkt.loc[dti_now,'slow_K'], above_margin) == 'above' :
                if position == 'long' and amount > 0 :
                    status = 'above'
                    position = 'None'
                    writeSummary(df_result, dti_now, time, pre_status, status, pre_position, position, 'close', vwap, buy_price, amount, pl, 'above margin', local_index)
                    buy_price = 0
                    amount = 0
            # short 으로 포지션 잡기
                status = 'above'
                position = 'short'
                buy_price = (vwap + buy_price*amount) / (amount+1)
                amount+=1
                pl = 0
                writeSummary(df_result, dti_post, time, pre_status, status, pre_position, position, 'open', vwap, buy_price, amount, pl, 'None', local_index)
                
        if idx[-2] == i :
            # 마지막에 청산
            if amount > 0 :
                pl = getPl(dfmkt.loc[dti_post]['vwap'], buy_price, amount, 1) if position == 'long' else getPl(dfmkt.loc[dti_post]['vwap'], buy_price, amount, -1)
                local_index = dfmkt.loc[dti_post]['index']
                pre_position = position
                position = 'None'
                pre_status = status
                writeSummary(df_result, dti_post, time, pre_status, status, pre_position, position,'close', vwap, buy_price, amount, pl, 'last', local_index)
                amount = 0
                
        i+=1
    # dfmkt.dropna(inplace=True)
    dfmkt.fillna(method='backfill', inplace=True)
    
    if not os.path.exists('sto_test.xlsx'):
        with pd.ExcelWriter('sto_test.xlsx', mode = 'w', engine = 'openpyxl') as writer :
            df_result.to_excel(writer, sheet_name=str(date))
    else:
        with pd.ExcelWriter('sto_test.xlsx', mode = 'a', engine = 'openpyxl') as writer :
            df_result.to_excel(writer, sheet_name=str(date))
    writer.save()
    
    if plot=='Y' :
        fig = plt.figure(figsize=(8,8))
        ax1 = fig.add_subplot(2,1,1)
        for result_i in df_result.index:
            marker = ''
            if df_result.loc[result_i]['pl'] == 0 and df_result.loc[result_i]['post_position'] == 'short' :
                marker = 'v'
            elif df_result.loc[result_i]['pl'] == 0 and df_result.loc[result_i]['post_position'] == 'long':
                marker = '^'
            color = "tab:red" if marker == "^" else "b"
            x = result_i
            y = df_result.loc[result_i]['vwap']
            ax1.scatter(x, y, color=color, marker=marker, s=50)
        
        ax2 = fig.add_subplot(2,1,2)
        ax1.plot(idx, dfmkt['vwap'])
        ax2.plot(idx, dfmkt['fast_K'], color = 'green', linewidth=1.5)
        ax2.plot(idx, dfmkt['slow_K'], color = 'purple', linewidth=1)
        ax2.axhline(y= below_margin, color='r', linewidth = 1)
        ax2.axhline(y= above_margin, color='r', linewidth = 1)
        
        font = {'family': 'verdana',
        'color':  'darkblue',
        'weight': 'bold',
        'size': 10,
        }
        plot_name = str(dfmkt.iloc[0]['date']) + '   ' + str(dfmkt.iloc[-1]['vwap']) + '   pl:  ' + str(round(df_result['pl'].sum(),3))
        ax2.set_xlabel(plot_name, fontdict=font)
        plt.show()
    

    return df_result


N = 500
m = 200
t = 20
# day = dt.date(2021,5,31)
# dfmkt = util.setDfData(day, day, 'lktbf50vol')
# r = stochastic(dfmkt, day, N, m, t, plot='Y')


"""복수 일자 """
total = 0.00
df_summary = pd.DataFrame(columns=['day_pl_sum', 'day_signal_cnt'])
writer = pd.ExcelWriter("summary_sto_test.xlsx",engine="xlsxwriter")

ld = list(util.getDailyOHLC().index)[:]
ld = [d for d in ld if d.year==2021]

for i, day in tqdm(enumerate(ld)) :    
    dfmkt = util.setDfData(day, day, 'lktbf50vol')
    r = stochastic(dfmkt, day, N, m, t,plot='Y')
    
    daily_pl = round(r['pl'].sum(),3)
    trade_cnt = len(r.index)
    df_summary.loc[day, 'day_pl_sum'] = daily_pl
    df_summary.loc[day, 'day_signal_cnt'] = trade_cnt
    
    # calDailyPlRangeLoi(r, day)
    print("-------------------------------------------------------------\n"
    f'Day   | {day}    pl= {daily_pl}, {trade_cnt}')
    total += daily_pl
    print(round(total,3), "   ",round(total/(i+1),3))
    print("-------------------------------------------------------------------------------------\n")
df_summary.to_excel(writer)
writer.save()
    
