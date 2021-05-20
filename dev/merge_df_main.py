import utils.util as util
import tradeLoi as tl
import pandas as pd
from matplotlib import pyplot as plt
import datetime as dt


def showGraph(loi, rm_loi, result, dfmkt, plot_name="QP") :
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1,1,1)
    x=[]
    time = tick_df['time']
    for i in time:
        x.append(str(i)[7:])
    y = tick_df['close']
    

    """
    각 거래별로 누적을 시킨 후 이득 15틱 이상이 발생하는 시점 알아보기
    """
    num_trade = 0
    status = 'None'
    trade_price = []
    trade_status = []
    dfmkt['pl_sum'] = 0.000
    dfmkt['long_sum'] = 0
    dfmkt['short_sum'] = 0
    for i in dfmkt.index:
        sum_ = 0 
        for idx in result.index:
            if idx == dfmkt.at[i, 'dt']:
                vwap = dfmkt[dfmkt['dt']==idx].iloc[-1]['vwap']
                if status!='long' and result.loc[idx, 'direction'] > 0 :
                    status = 'long'
                    trade_price.append(result.loc[idx, 'price'])
                    trade_status.append(status)
                    pl= (vwap - trade_price[num_trade])*100
                    dfmkt.at[i, num_trade] = pl
                    # dfmkt.loc[i, num_trade] = {'ent':result.loc[idx, 'price'], 
                    #                            'pl':result.loc[idx, 'price'] - dfmkt[dfmkt['dt']==idx].iloc[-1]['vwap'],
                    #                            'status':'long'}
                    num_trade+=1
                    # for j in range(num_trade):
                    #     dfmkt.loc[i, j] = trade_price[j] - dfmkt[dfmkt['dt']==idx].iloc[-1]['vwap']
                elif status!='short' and result.loc[idx, 'direction'] < 0 :
                    status = 'short'
                    trade_price.append(result.loc[idx, 'price'])
                    trade_status.append(status)
                    pl = (trade_price[num_trade] - vwap)*100
                    dfmkt.at[i, num_trade] = pl
                    num_trade+=1        
                elif status == 'long' or status =='short':
                    for j in range(num_trade):
                        pl = (vwap - trade_price[j])*100
                        if trade_status[j]=='long':
                            dfmkt.loc[i, j] = pl
                        elif trade_status[j]=='short':
                            dfmkt.loc[i, j] = -pl
            else:
                for j in range(num_trade):
                    pl = (dfmkt.at[i,'vwap'] - trade_price[j])*100
                    if trade_status[j]=='long':
                        dfmkt.loc[i, j] = pl
                    elif trade_status[j]=='short':
                        dfmkt.loc[i, j] = -pl
        for j in range(num_trade) :
            sum_ += round(dfmkt.at[i,j],3)
        dfmkt.at[i, 'pl_sum'] = sum_
        for status in trade_status:
            if status =='long':
                dfmkt.at[i, 'long_sum'] += 1
            elif status =='short':
                dfmkt.at[i, 'short_sum'] += 1
                
    
    """
    x축(시간) 값들을 잘 보이도록 개수 및 각도 조정
    """
    ax.plot(x,y)
    plt.xticks(ticks=x, rotation=30)
    plt.locator_params(axis='x', nbins=len(x)/500)
    
    """
    loi 값들을 수평선으로 그음(loi[0] : opt, loi[1] : val)
    """
    for i in range(len(rm_loi[1])) :
        plt.axhline(y=rm_loi[1][i], linewidth=1,color="grey")
        plt.text(0, rm_loi[1][i], rm_loi[0][i], color="gray")

    for i in range(len(loi[1])) :
        plt.axhline(y=loi[1][i], linewidth=1, color="blue")
        plt.text("right", loi[1][i], loi[0][i] + " " +str(loi[1][i]), color="blue")
   

    """
    마커를 플로팅함
    """
    for i in result.index:
        marker = "^" if result.loc[i]['direction'] == 1 else "v"
        color = "tab:red" if marker == "^" else "b"
        x = str(i)[11:]
        y = result.loc[i]['price']
        ax.scatter(x, y, color=color, marker=marker, s=100) #s=마커사이즈
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 18,
            }
    
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    return dfmkt, trade_price, trade_status
    
def merge(loi, items) :
    
    """
    0.03이내 들어오는 loi 끼리는 정리, 정리된 loi와 삭제된 rmLoi로 나눔
    """
    rm = []
    for i in range(len(loi)-1):
        for j in range(i+1,len(loi)) :
            if abs(round(loi[i]['val']-loi[j]['val'],2)) <=0.03:
               rm.append(j) 
    rm = sorted(list(set(rm)))
    
    rm_loi =[]
    for i in reversed(range(len(rm))):
        rm_loi.append(loi.pop(rm[i]))
    
    for i in range(len(loi)-1):
        for j in range(i+1, len(loi)) :
            if loi[i]['val'] > loi[j]['val'] :
                tmp = loi[i]['val']
                loi[i]['val'] = loi[j]['val']
                loi[j]['val'] = tmp
                
                tmp = loi[i]['opt']
                loi[i]['opt']=loi[j]['opt']
                loi[j]['opt']=tmp
                
    """
    loi option만을 저장, value만을 저장하는 리스트를 따로 만듬 
    추가로 삭제된 loi에도 처리
    """
    opt_loi=[]
    val_loi=[]
    for i in range(len(loi)):
        opt_loi.append(loi[i]['opt'])
        val_loi.append(loi[i]['val'])
    
    opt_rm_loi=[]
    val_rm_loi=[]
    for i in range(len(rm_loi)):
        opt_rm_loi.append(rm_loi[i]['opt'])
        val_rm_loi.append(rm_loi[i]['val'])
    # result.drop(columns=loi[rm[i]]['opt'], inplace=True)

    """
    items 중에서 opt_loi 안에 있는 컬럼만 사용으로 대체
    삭제할 list index는 delItems에 넣고 역순으로 삭제
    """
    cols=['direction','price']
    delItems =[]
    for i, item in enumerate(items):
        if item['loi_option'] in opt_loi:
            cols.append(item['loi_option'])
        else :
            delItems.append(i)
    for i in delItems[::-1] :
        del items[i]
    
    """
    병합될 df 의 전체 index를 가져오고 정렬한다.
    """
    index = items[0]['df'].index
    for item in items :
        index = index.append(item['df'].index)
    idx = sorted(list(set(index)))
  
    """
    병합될 df의 골격을 만든다
    """
    resultDf = pd.DataFrame(index = idx, columns=cols)
    resultDf = resultDf.fillna(0)
    
    """
    병합될 df에 값들을 넣어준다
    """
    for i in idx : 
        for item in items:
            if i in item['df'].index:
                resultDf.loc[i,'direction'] += item['df'].loc[i,'direction']
                resultDf.loc[i,item['loi_option']] = item['df'].loc[i,'direction']
                resultDf.loc[i,'price'] = item['df'].loc[i,'price']
    
    loi = [opt_loi,val_loi]
    rm_loi = [opt_rm_loi, val_rm_loi]
    return loi,rm_loi,resultDf


"""
날자 설정 및 플로팅용 틱데이터 차트를 불러옴
"""
date = dt.date(2019,1,16)
# for i in range(100):
#     date = util.date_offset(date, 1)
tick_df = util.setDfData(str(date), str(date), '`lktbftick`')

"""
9가지의 loi 기준으로 dataframe을 가져오고 이후 병합할 예정임
"""
ret = tl.tradeLoi(date, loi_option='yday_close')
ret2 = tl.tradeLoi(date, loi_option='open')
ret3 = tl.tradeLoi(date, loi_option='yday_hi')
ret4 = tl.tradeLoi(date, loi_option='yday_lo')
ret5 = tl.tradeLoi(date, loi_option='yday_open')
ret6 = tl.tradeLoi(date, loi_option='2day_hi')
ret7 = tl.tradeLoi(date, loi_option='2day_lo')
ret8 = tl.tradeLoi(date, loi_option='3day_hi')
ret9 = tl.tradeLoi(date, loi_option='3day_lo')
# ret5 = tl.tradeLoi(date, loi_option='intraday_hi')
# ret5 = tl.tradeLoi(date, loi_option='multiday_hi')
# ret5 = tl.tradeLoi(date, loi_option='intraday_lo')
# ret5 = tl.tradeLoi(date, loi_option='multiday_lo')
# ret5 = tl.tradeEWMAC(date)

"""
앞에서 가져온 df에서 loi를 꺼내고 이게 유효하지 않은 범위인지는 merge에서 판단하도록 미룸
"""
loi = []
loi.append({"opt":ret['loi_option'],"val":ret['loi']})
loi.append({"opt":ret2['loi_option'],"val":ret2['loi']})
loi.append({"opt":ret3['loi_option'],"val":ret3['loi']})
loi.append({"opt":ret4['loi_option'],"val":ret4['loi']})
loi.append({"opt":ret5['loi_option'],"val":ret5['loi']})
loi.append({"opt":ret6['loi_option'],"val":ret6['loi']})
loi.append({"opt":ret7['loi_option'],"val":ret7['loi']})
loi.append({"opt":ret8['loi_option'],"val":ret8['loi']})
loi.append({"opt":ret9['loi_option'],"val":ret9['loi']})


"""
병합작업 및 플로팅 call
"""
loi, rm_loi, result = merge(loi, [ret,ret2,ret3, ret4, ret5, ret6, ret7, ret8, ret9]) 
plot_name = str(result.index[0].date()) + str(loi[1]) +str(loi[0])
# showGraph(loi, result, str(i)+') '+plot_name)

ret['dfmkt']['dt'] = pd.Timestamp(date) + ret['dfmkt']['time'] 

a,b,c = showGraph(loi, rm_loi, result, ret['dfmkt'], plot_name)
