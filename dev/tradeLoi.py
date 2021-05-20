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
        

def rangeTest(vwap, loi):
    """
    vwap과 loi 거리 비교하여 loi range 내외를 판단
    """
    if 100*abs(vwap - loi) <= 1.2:
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
    plot_name = str(loi_option) + ': '+ str(loi)
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass


def tradeLoi(date, loi_option='open', vol_option='lktb50vol'):
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
     'loi_option': loi_option}
        df_result
            trade_time : pd.Timestamp
            direction : +1 or -1
            price : 매매가 일어난 가격
        loi_option
    """
    #MySQL문법에 맞게 따옴표 처리
    vol_option = "`" + vol_option + "`"
    
    #테스트를 위한 해당일의 시장 data load
    df = util.setDfData(date, date, vol_option)
    
    #loi_option에 따라 loi 설정, loi_option이 과거일 경우 함수호출
    if loi_option == 'open':
        loi = df.iloc[0]['open']
    else:
        loi = getLoiFromPast(date, loi_option)
    
    dti = df.index
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
        vwap = df.loc[dti_now,'vwap']
        
        #dti_pre에서 signal 발생한 경우 dti_now에서 time, price 설정
        #df_result의 dti_pre행을 indexing
        if df_result.loc[dti_pre]['price'] == 'TBD':
            df_result.at[dti_pre, 'trade_time'] = pd.to_datetime(str(date) + ' ' + str(df.loc[dti_now,'time'])[7:])
            ent_price = upp(vwap) if df_result.iloc[-1]['direction'] == 1 else flr(vwap)
            df_result.at[dti_pre, 'price'] = ent_price
        
        range_status = rangeTest(vwap, loi)
        
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
                df_result.at[dti_now, 'signal_time'] = pd.to_datetime(str(date) + ' ' + str(df.loc[dti_now,'time'])[7:])
                
            df_result.at[dti_now, 'signal_vwap'] = vwap
            df_result.at[dti_now, 'price'] = 'TBD'
            df_result.at[dti_now, 'local_index'] = dti_now
        
    """vwap index기준 test loop종료"""
    
    df_result.dropna(inplace=True)
    

    """결과1차정리, PLOT을 위함"""
    result = {'df' : df_result, 
              'loi_option': loi_option, 
              'loi': loi,
              'dfmkt': df
              }
    
    """"결과PLOT"""    
    plotSingleLoi(result)

    """"결과정리"""    
    result['df'].index = result['df'].trade_time
    result['df'].index.name = 'index'
        
    # result['df'].drop(columns='trade_time', inplace=True)
    
    return result


            
date = datetime.date(2021,4,1)

# df = tradeLoi(date, loi_option='yday_hi')['df']
# print(df)        
# df = tradeLoi(date, loi_option='yday_lo')['df']
# print(df)        
# df = tradeLoi(date, loi_option='yday_close')['df']
# print(df)        
df = tradeLoi(date, loi_option='open')['df']
# print(df)        
# df = tradeLoi(date, loi_option='2day_hi')['df']
# print(df)        
# df = tradeLoi(date, loi_option='2day_lo')['df']
# print(df)        
# df = tradeLoi(date, loi_option='3day_lo')['df']
# print(df)        
# df = tradeLoi(date, loi_option='3day_hi')['df']
# print(df)        

  

# """
# 엑셀에 요약본 작성하려고 만드는 dataframe
# """
# tag_list = "long_sum", "long_len", "long_avg", "short_sum", "short_len", "short_avg", "total", "long_win", "long_lose", "short_win","short_lose"
# df_tag = pd.DataFrame(columns=tag_list)

# """
# li는 setDfData의 param으로 준 날자들의 집합을 오름차순으로 정렬해 놓은 값이다.
# """
# li = sorted(list(set(df_sample['date'])))

# """
# 소스코드의 경로에 result.xlsx 파일로 결과가 정리되고 날자별로 시트가 나온다.
# """
# writer = pd.ExcelWriter('precise.xlsx', engine='xlsxwriter')

# strategy(df_sample, 'preday_close')
# strategy(df_sample, 'preday_max')
# strategy(df_sample, 'open')
    
# writer.save()



