import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import utils.util as util
import datetime


""" 파는 가격을 보수적으로 잡을때 """
def flr(item):
    item = item * 100
    item = math.floor(item)
    return item / 100

""" 사는 가격을 보수적으로 잡을때 """
def upp(item) :
    item = item * 100
    item = math.ceil(item)
    return item / 100

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
    

def tradeEma(date, vol_option='lktb50vol', plot="N", execution="adjusted",
             fast_coeff=0.3, slow_coeff=0.1, margin=0.5):
    """
    tradeEma는 장중 한방향 트렌드가 지속될 때 많은 수익을 추구
    필연적으로 방향전환이 많은 날은 손실 발생 가능
    
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
    result = {'df' : df_result, 
              'dfmkt': dfmkt,
              'config': (fast_coeff, slow_coeff, margin)}
    
    """
    # #MySQL문법에 맞게 따옴표 처리
    # vol_option = "`" + vol_option + "`"
    
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
    #"attached" / "below" / "above" 중에 하나
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
                # print("signal detected : ", signal_now)
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
    
    """NA제거"""
    df_result.dropna(inplace=True)
    
    """가동시간 설정 """
    # start_time = '10:30:00'
    # activate_after = pd.to_datetime(str(date) + ' ' +start_time )
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
    plot_name = '{3}, Fast_coef: {0}, Slow_coef: {1}, margin: {2}'
    plot_name = plot_name.format(tradeEma_result['config'][0],
                                 tradeEma_result['config'][1],
                                 tradeEma_result['config'][2],
                                 str(tradeEma_result['dfmkt'].date[0]))
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass

def calPlEma(result_ema):
    """단순 종가기준 PL만 산출"""
    df_trade = result_ema['df']

    close_price = result_ema['dfmkt'].iloc[-1]['price']
    
    df_trade['amt'] = 2
    df_trade.at[df_trade.index[0], 'amt'] = 1
    df_trade['pl'] = 100 * df_trade.direction * df_trade.amt * (close_price - df_trade.price)
    #!!! stop-out loss 
    
    
    date = str(df_trade.index[0].date())
    day_pl_sum = round(df_trade['pl'].sum(), 1)
    day_signal_count = df_trade['pl'].count()
    print(date, day_pl_sum, day_signal_count)
    
    return date, day_pl_sum, day_signal_count


def main():
    
    print("Running main function")
    tradeEma
    #일봉기준 전체 date list
    # ld = list(util.getDailyOHLC().index)
    ld = [datetime.date(2018,3,27)]
    # ld = util.getDateList('usdkrw100vol')
    
    #일간 PL을 기록하는 dataframe
    dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])
    
    for i, day in enumerate(ld):
        result_ema = tradeEma(day, 'usdkrw100vol', plot="Y", execution="vwap", 
                              fast_coeff=0.3,
                              slow_coeff=0.05,
                              margin = 5.0)
        # result_ema = tradeEma(day, 'lktb50vol', plot="N", execution="vwap", 
        #                       fast_coeff=0.3,
        #                       slow_coeff=0.05,
        #                       margin = 1.0)
        
        # timelyPl = calPlEmaTimely(result_ema, timebin="1min", losscut="N")
        date, dailyPl, cnt = calPlEma(result_ema)
        
        dfpl.at[i, 'date'] = day
        dfpl.at[i, 'pl'] = dailyPl
        dfpl.at[i, 'num_trade'] = cnt
        
        # pl_of_the_day = round(timelyPl.pl[-1], 2)
        # dfpl.at[i, 'pl'] = pl_of_the_day
        
        
        
        # num_trade = timelyPl.num_trade[-1]
        # dfpl.at[i, 'num_trade'] = num_trade
        
        # trade_ended_at = str(timelyPl.index[-1])[-8:]
        
        #당일의 결과
        # print(day, "    ", pl_of_the_day, str(timelyPl.index[-1])[-8:])
        # print(f'{day}    pl={pl_of_the_day},  {trade_ended_at},   {num_trade}')
        
        #누적결과
        print(round(dfpl.pl.sum(), 1), 
              round(dfpl.pl.mean(), 2), 
              round(dfpl.pl.std(), 2),
              round(dfpl.num_trade.mean(), 1), "trades/day",
              "\n=====================================")
    
    dfpl.set_index(pd.to_datetime(dfpl.date), inplace=True)
    
    return dfpl

if __name__ == "__main__":
    dfpl = main()