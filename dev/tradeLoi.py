import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import utils.util as util
import datetime


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
        

def rangeTest(vwap, loi, margin):
    """
    vwap과 loi 거리 비교하여 loi range 내외를 판단
    """
    if 100*abs(vwap - loi) <= margin:
        where = "within_range"
    else:
        where = "out_of_range"
    return where
    
def getLoiFromPast(date, loi_option):
    """
    loi_option이 오늘 이전인 경우, loi 설정
    """
    #loi_option에 따라 loi 설정
    if loi_option == 'yday_close':
        loi = util.getYdayOHLC(date)['close']
    elif loi_option == 'yday_hi':
        loi = util.getYdayOHLC(date)['hi']
    elif loi_option == 'yday_lo':
        loi = util.getYdayOHLC(date)['lo']
    elif loi_option == 'yday_open':
        loi = util.getYdayOHLC(date)['open']
    elif loi_option == '2day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 2)['hi']
    elif loi_option == '2day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 2)['lo']
    elif loi_option == '3day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 3)['hi']
    elif loi_option == '3day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 3)['lo']
        
    else:
        print("Wrong LOI option!!")
        
    return loi


def plotSingleLoi(tradeLoi_result):
    """임시 플로팅 함수로 사용"""
    df_result = tradeLoi_result['df']
    df_result.index = df_result.local_index
    loi_option = tradeLoi_result['loi_option']
    df = tradeLoi_result['dfmkt']
    loi = tradeLoi_result['loi']

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    for result_i in df_result.index:
        marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
        color = "tab:red" if marker == "^" else "b"
        x = result_i
        y = df_result.loc[result_i]['price']
        ax.scatter(x, y, color=color, marker=marker, s=200)
    plt.plot(df.index, df['price'])
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 18,
            }
    plot_name = '{0}: {1}, Margin: {2}'
    plot_name = plot_name.format(loi_option, loi, tradeLoi_result['margin'])
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass



def tradeLoi(date, loi_option='open', vol_option='lktb50vol', plot="N", execution="adjusted", margin=1.0):
    """
    Parameters
    ----------
    date : datetime.date
        테스트하고자 하는 날짜
    loi_option : str
        'open', 'yday_close', 'yday_hi', 'yday_lo', 'yday_open'
        '2day_hi', '2day_lo', '3day_hi', '3day_lo',
        
    vol_option : str
        몇개짜리 볼륨봉을 쓸 것인지 = DB의 table명과 동일하게

    Returns
    -------
    {'df': df_result,
     'loi_option': loi_option
     'loi': loi
     'dfmkt': 시장data
     
     }
        df_result
            trade_time : pd.Timestamp
            direction : +1 or -1
            price : 매매가 일어난 가격
        loi_option
    """
    #MySQL문법에 맞게 따옴표 처리
    vol_option = "`" + vol_option + "`"
    
    #테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, vol_option)
    
    #loi_option에 따라 loi 설정, loi_option이 과거일 경우 함수호출
    if loi_option == 'open':
        loi = dfmkt.iloc[0]['open']
    else:
        loi = getLoiFromPast(date, loi_option)
    
    dti = dfmkt.index
    #결과를 담는 df 정의
    df_result = pd.DataFrame(index = dti, 
                             columns=['loi',
                                      'signal_time', 
                                      'direction', 
                                      'signal_vwap', 
                                      'trade_time', 
                                      'price',
                                      'local_index'])
    
    #range 안 또는 밖의 상태를 저장
    range_status_prev = "out_of_range"
    
    #현재의 signal 상태를 저장
    signal_before = 0 
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        vwap = dfmkt.loc[dti_now,'vwap']
        
        #dti_pre에서 signal 발생한 경우 dti_now에서 time, price 설정
        #df_result의 dti_pre행을 indexing
        if df_result.loc[dti_pre]['price'] == 'TBD':
            df_result.at[dti_pre, 'trade_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
            
            if execution =="adjusted":
                ent_price = upp(vwap) if df_result.iloc[-1]['direction'] == 1 else flr(vwap)
            elif execution == "vwap":
                ent_price = vwap
            else:
                raise NameError('Wrong execution option')
            df_result.at[dti_pre, 'price'] = ent_price
        
        range_status = rangeTest(vwap, loi, margin)
        
        #LOI 레인지 밖에서 안으로 들어온 경우 
        if range_status_prev == "out_of_range" and range_status == "within_range":
            range_status_prev = range_status
            
        elif range_status_prev == "out_of_range" and range_status == "out_of_range":
            pass
        
        elif range_status_prev == "within_range" and range_status == "within_range":
            pass
        
        #LOI 레인지 안에서 밖으로 나가는 경우 --> signal 발생
        elif range_status_prev == "within_range" and range_status == "out_of_range":
            range_status_prev = range_status
            
            #1은 LOI 레인지 상향돌파, vice versa
            signal_now = 1 if vwap > loi else -1
            
            if signal_before != signal_now :
                df_result.at[dti_now, 'direction'] = signal_now
                signal_before = signal_now
                
                df_result.at[dti_now, 'loi'] = loi
                #timedelta --> datetime.time형식으로 변환
                df_result.at[dti_now, 'signal_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
                
                df_result.at[dti_now, 'signal_vwap'] = vwap
                df_result.at[dti_now, 'price'] = 'TBD'
                df_result.at[dti_now, 'local_index'] = dti_now
        
    """vwap index기준 test loop종료"""
    
    df_result.dropna(inplace=True)
    

    """결과1차정리, PLOT을 위함"""
    result = {'df' : df_result, 
              'loi_option': loi_option, 
              'loi': loi,
              'dfmkt': dfmkt,
              'margin': margin
              }
    
    """"결과PLOT"""    
    if plot == "Y":
        plotSingleLoi(result)

    """"결과정리"""    
    result['df'].index = result['df'].trade_time
    result['df'].index.name = 'index'
        
    # result['df'].drop(columns='trade_time', inplace=True)
    
    return result



def crossTest(ema_fast, ema_slow, margin=0.5):
    """
    ema_fast와 ema_slow를 비교
    
    Returns
    -------
        "attached" / "above" / "below" 중에 하나를 리턴
    """
    if 100*abs(ema_fast - ema_slow) <= margin:
        cross_status = "attached"
    elif ema_fast > ema_slow:
        cross_status = "above"
    elif ema_fast < ema_slow:
        cross_status = "below"
    else:
        raise NameError("Unexpected!!!")
        
    return cross_status
    
    

def tradeEma(date, vol_option='lktb50vol', plot="N", execution="adjusted", fast_coeff=0.3, slow_coeff=0.1, margin=0.5):
    """
    tradeEma는 tradeLoi보다 느린 시그널을 잡는 것을 기본 전제로 한다.
    주 활용처가 LOI가 없는 곳에서 긴 시간 머무를 때이기 때문이다.
    
    Parameters
    ----------
    date : datetime.date
        테스트하고자 하는 날짜
        
    vol_option : str
        몇개짜리 볼륨봉을 쓸 것인지 = DB의 table명과 동일하게
        
    execution : 
        "adjusted" --> upp/flr 활용하여 보수적 진입가격
        "vwap" --> dti_next의 vwap 그대로 활용
    
    fast_coeff, slow_coeff : ema용 Coefficient

    Returns
    -------
    {'df': df_result,
     'loi': loi
     'dfmkt': 시장data}
    
        df_result
            trade_time : pd.Timestamp
            direction : +1 or -1
            price : 매매가 일어난 가격
    """
    #MySQL문법에 맞게 따옴표 처리
    vol_option = "`" + vol_option + "`"
    
    #테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, vol_option)
    
    #local index
    dti = dfmkt.index
    
    #결과를 담는 df 정의
    df_result = pd.DataFrame(index = dti, 
                             columns=['signal_time', 
                                      'direction', 
                                      'signal_vwap', 
                                      'trade_time', 
                                      'price',
                                      'local_index',
                                      'ema_fast',
                                      'ema_slow'
                                      ])
    
    #ema_fast와 ema_slo의 상대위치 정의
    #"above_then_attached" / "below_then_attached" / "below" / "above" 중에 하나
    #초기상태에 대한 정의 필요
    prev_status = "attached"
    
    #현재의 signal 상태를 저장
    signal_before = 0 
    
    #ema_fast, ema_slow 시작점 정의, ema는 dfmkt에 저장한다
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'open']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'open']
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        vwap = dfmkt.loc[dti_now,'vwap']
        
        #dti_pre에서 signal 발생한 경우 dti_now에서 time, price 설정
        #df_result의 dti_pre행을 indexing
        if df_result.loc[dti_pre]['price'] == 'TBD':
            df_result.at[dti_pre, 'trade_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
            
            if execution =="adjusted":
                ent_price = upp(vwap) if df_result.iloc[-1]['direction'] == 1 else flr(vwap)
            elif execution == "vwap":
                ent_price = vwap
            else:
                raise NameError('Wrong execution option')
                
            df_result.at[dti_pre, 'price'] = ent_price
        
        dfmkt.at[dti_now, 'ema_fast'] = fast_coeff * vwap + (1-fast_coeff) * dfmkt.at[dti_pre, 'ema_fast']
        dfmkt.at[dti_now, 'ema_slow'] = slow_coeff * vwap + (1-slow_coeff) * dfmkt.at[dti_pre, 'ema_slow']
        
        tested_status = crossTest(dfmkt.at[dti_now, 'ema_fast'], dfmkt.at[dti_now, 'ema_slow'], margin=margin)
        
        if (prev_status == "above" or prev_status == "below") and tested_status == "attached":
            prev_status = tested_status
        
        elif prev_status == tested_status:
            pass
        
        #below -> above or above -> below or attahced -> above/below
        else: 
            # print(prev_status, tested_status)
            prev_status = tested_status
            
            signal_now = 1 if tested_status == "above" else -1
            
            if signal_before != signal_now : #이 경우에만 시그널 발생
                print("signal detected : ", signal_now)
                df_result.at[dti_now, 'direction'] = signal_now
                signal_before = signal_now
                
                #timedelta --> datetime.time형식으로 변환
                df_result.at[dti_now, 'signal_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
                    
                df_result.at[dti_now, 'signal_vwap'] = vwap
                df_result.at[dti_now, 'price'] = 'TBD'
                df_result.at[dti_now, 'ema_fast'] = dfmkt.at[dti_now, 'ema_fast']
                df_result.at[dti_now, 'ema_slow'] = dfmkt.at[dti_now, 'ema_slow']
                df_result.at[dti_now, 'local_index'] = dti_now
    
    """index기준 test loop종료"""       
    
    df_result.dropna(inplace=True)
    
    """가동시간 설정 """
    start_time = '10:30:00'
    activate_after = pd.to_datetime(str(date) + ' ' +start_time )
    # df_result = df_result[activate_after:]
    
    
    """결과1차정리, PLOT을 위함"""
    result = {'df' : df_result, 
              'dfmkt': dfmkt,
              'config': (fast_coeff, slow_coeff, margin)}
        
    if plot == "Y":
        plotSingleMA(result)
        
    """"결과정리"""    
    result['df'].index = result['df'].trade_time
    result['df'].index.name = 'index'
    
    return result
  


def plotSingleMA(tradeEma_result):
    """임시 플로팅 함수로 사용"""
    df_result = tradeEma_result['df']
    df_result.index = df_result.local_index
    df = tradeEma_result['dfmkt']

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    for result_i in df_result.index:
        marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
        color = "tab:red" if marker == "^" else "b"
        x = result_i
        y = df_result.loc[result_i]['price']
        ax.scatter(x, y, color=color, marker=marker, s=300)
    plt.plot(df.index, df['price'])
    plt.plot(df.index, df['ema_fast'])
    plt.plot(df.index, df['ema_slow'])
    
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 12,
            }
    plot_name = 'Fast_coef: {0}, Slow_coef: {1}, margin: {2}'
    plot_name = plot_name.format(tradeEma_result['config'][0],
                                 tradeEma_result['config'][1],
                                 tradeEma_result['config'][2])
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass


#%% MAIN 실행 영역
date = datetime.date(2019,4,30)

df = tradeLoi(date, loi_option='yday_lo', vol_option='lktb30vol', plot="Y", execution="vwap", margin=0.7)['df']
df = tradeLoi(date, loi_option='2day_hi', vol_option='lktb30vol', plot="Y", execution="vwap", margin=0.7)['df']
df = tradeLoi(date, loi_option='open', vol_option='lktb50vol', plot="Y", execution="vwap", margin=1.0)['df']

result = tradeEma(date, vol_option='lktb200vol', plot="Y", execution="vwap", fast_coeff=0.3, slow_coeff=0.05, margin = 0.5)
