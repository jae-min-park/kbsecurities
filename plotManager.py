# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:34:22 2021

@author: infomax
"""
import numpy as np
import matplotlib.pyplot as plt

"""
ticks를 10 곱하면 초단위가 나온다.
"""
ticks = 120


def getTicksAfterward(dfmkt, dt, num_ticks_afterward):
    """
    dfmkt : 전체 시장 data
    dt : datetimeindex중 특정시점 ex) '2021-04-06 09:06:10'
    num_ticks_afterward : dt이후 출력할 틱 개수, 60이면 10초*60 = 10분
    o.b.시 자동 조정 및 ticks_arr끝에 0 채워넣기
    """
    df_day = dfmkt[dfmkt.date == dt.date()]
    dti_day = df_day.index
    
    end_index_number = min(len(dti_day)-1, dti_day.get_loc(dt) + num_ticks_afterward)
    ticks_end_at = dti_day[end_index_number-1]
    
    reference_price = df_day.loc[dt]['close']
        
    ticks_arr = -reference_price + np.array(df_day.loc[dt : ticks_end_at]['close'])
    
    return ticks_arr

def getTicksBeforehand(dfmkt, dt, num_ticks_beforehand):
    """
    dfmkt : 전체 시장 data
    dt : datetimeindex중 특정시점 ex) '2021-04-06 09:06:10'
    num_ticks_beforehand : dt이전출력할 틱 개수, o.b시 자동 조정
    o.b.시 자동 조정 및 ticks_arr이전에 0 채워넣기
    """
    
    df_day = dfmkt[dfmkt.date == dt.date()]
    dti_day = df_day.index
    
    start_index_number = max(0, dti_day.get_loc(dt) - num_ticks_beforehand)
    ticks_start_at = dti_day[start_index_number+1]
    
    reference_price = df_day.loc[dt]['close']
        
    ticks_arr = -reference_price + np.array(df_day.loc[ticks_start_at:dt]['close'])
    
    if start_index_number == 0:
        start_value = df_day.iloc[0]['open'] - reference_price #그날의 시가
        ticks_arr = np.append([start_value]*(num_ticks_beforehand - len(ticks_arr)), ticks_arr)
    
    print(dt)
    return ticks_arr

# """
# plot 에서 사용되는데, ticks에 따른 close 값 리스트를 받아오는 함수
# """
# def getTicksAfter(dfmkt, dt, num_ticks):
#     df_day = dfmkt[dfmkt.date == dt.date()]
#     dti_day = df_day.index
#     ticks_end_at = dti_day[dti_day.get_loc(dt) + num_ticks]
    
#     reference_price = df_day.loc[dt]['close']
        
#     ticks = -reference_price + np.array(df_day.loc[dt : ticks_end_at]['close'])
    
#     return ticks

"""
df 와 전략이 발생하는 날자리스트를 입력받아 plotting 해주는 함수
"""
def plot(dfmkt, plot_list) :
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    for dt in plot_list:
        label = str(dt)
        # ax.plot(getTicksBeforehand(dfmkt, dt, 60), label = label)
        plt.plot(getTicksAfterward(dfmkt, dt, ticks), label = label)
        plt.pause(3.0)
    
    ax.legend(loc='upper left', ncol=2, bbox_to_anchor=(0,-0.1))
    
    plt.show()



