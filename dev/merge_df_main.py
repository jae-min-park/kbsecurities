import utils.util as util
import tradeLoi as tl
import pandas as pd
from matplotlib import pyplot as plt
import datetime as dt


def showGraph(loi, data, plot_name="QP") :
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1,1,1)
    x=[]
    time = tick_df['time']
    for i in time:
        x.append(str(i)[7:])
    y = tick_df['close']
    
    """
    x축(시간) 값들을 잘 보이도록 개수 및 각도 조정
    """
    ax.plot(x,y)
    plt.xticks(ticks=x, rotation=30)
    plt.locator_params(axis='x', nbins=len(x)/500)
    
    """
    loi 값들을 수평선으로 그음
    """
    for i in range(len(loi)) :
        plt.axhline(y=loi[i], linewidth=1)

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
    
def merge(loi, items) :
    
    """
    0.03이내 들어오는 loi 끼리는 정리
    """
    rm = []
    for i in range(len(loi)-1):
        for j in range(i+1,len(loi)) :
            if abs(round(loi[i]['val']-loi[j]['val'],2)) <=0.03:
               rm.append(i) 
    
    for i in range(len(rm))[::-1]:
        del loi[rm[i]]
    
    """
    loi option만을 저장, value만을 저장하는 리스트를 따로 만듬
    """
    opt_loi=[]
    val_loi=[]
    for i in range(len(loi)):
        opt_loi.append(loi[i]['opt'])
        val_loi.append(loi[i]['val'])
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
    
    return val_loi,resultDf


"""
날자 설정 및 플로팅용 틱데이터 차트를 불러옴
"""
date = dt.date(2019,4,4)
# for i in range(100):
#     date = util.date_offset(date, 1)
tick_df = util.setDfData(str(date), str(date), '`lktbftick`')

"""
5가지의 loi 기준으로 dataframe을 가져오고 이후 병합할 예정임
"""
ret = tl.tradeLoi(date)
ret2 = tl.tradeLoi(date, loi_option='yday_open')
ret3 = tl.tradeLoi(date, loi_option='yday_hi')
ret4 = tl.tradeLoi(date, loi_option='yday_lo')
ret5 = tl.tradeLoi(date, loi_option='yday_close')
# ret5 = tl.tradeLoi(date, loi_option='intraday_hi')
# ret5 = tl.tradeLoi(date, loi_option='multiday_hi')
# ret5 = tl.tradeLoi(date, loi_option='intraday_lo')
# ret5 = tl.tradeLoi(date, loi_option='multiday_lo')
# ret5 = tl.tradeEWMAC(date)

"""
앞에서 가져온 df에서 loi값이 있는 것만 꺼내고, 이게 유효하지 않은 범위인지는 merge에서 판단하도록 미룸
"""
loi = []
if not ret['df'].empty :
    loi.append({"opt":ret['loi_option'],"val":ret['df'].iloc[0]['loi']})
if not ret2['df'].empty :
    loi.append({"opt":ret2['loi_option'],"val":ret2['df'].iloc[0]['loi']})
if not ret3['df'].empty :
    loi.append({"opt":ret3['loi_option'],"val":ret3['df'].iloc[0]['loi']})
if not ret4['df'].empty :    
    loi.append({"opt":ret4['loi_option'],"val":ret4['df'].iloc[0]['loi']})
if not ret5['df'].empty :    
    loi.append({"opt":ret5['loi_option'],"val":ret5['df'].iloc[0]['loi']})


"""
병합작업 및 플로팅 call
"""
loi, result = merge(loi, [ret,ret2,ret3, ret4, ret5]) 
plot_name = str(result.index[0].date()) + str(loi) +str( list(result.columns[2:]))
# showGraph(loi, result, str(i)+') '+plot_name)
showGraph(loi, result, plot_name)
