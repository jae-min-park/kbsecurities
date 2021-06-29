import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
# import utils.util as util
import datetime
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util

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


def tradeEma(dates, vol_option='ktbf300vol', plot="N", execution="adjusted",
             fast_coeff=0.03, slow_coeff=0.001, margin=0.5):
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
    
    _min = dates[0]
    _max = dates[0]
    for date in dates :
        if _min > date :
            _min = date
        if _max < date :
            _max = date
    
    dfmkt = util.setDfData(_min, _max, vol_option)
    dti = dfmkt.index
    
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
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'vwap']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'vwap']
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        vwap = dfmkt.loc[dti_now,'vwap']
        
        #dti_pre에서 signal 발생한 경우 dti_now에서 time, price 설정
        #df_result의 dti_pre행을 indexing
        if df_result.loc[dti_pre]['price'] == 'TBD':
            df_result.at[dti_pre, 'trade_time'] = pd.to_datetime(str(dfmkt.loc[dti_now,'date']) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
            # df_result.at[dti_pre, 'trade_time'] = dti_now
            
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
        
        #slow ema 형성시까지(=slow ema가 적정수량이 생길때까지 signal 발생 보류
        if (dfmkt.ema_slow.count() > 0.2*(1/slow_coeff)):
            
            if (prev_status == "above" or prev_status == "below") and tested_status == "attached":
                prev_status = tested_status
            
            elif prev_status == tested_status:
                pass
            
            #below -> above or above -> below or attahced -> above/below
            else: 
                # print(prev_status, tested_status)
                prev_status = tested_status
                
                signal_now = 1 if tested_status == "above" else -1
                
                #!!!이 경우에만 시그널 발생
                if signal_before != signal_now: 
                    # print("signal detected : ", signal_now)
                    df_result.at[dti_now, 'direction'] = signal_now
                    signal_before = signal_now
                    
                    #timedelta --> datetime.time형식으로 변환
                    df_result.at[dti_now, 'signal_time'] = dti_now
                    # df_result.at[dti_now, 'signal_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
                        
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
    df_result = tradeEma_result['df']
    df_result.index = df_result.local_index
    dfmkt = tradeEma_result['dfmkt']

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    date_changes=[]
    date = dfmkt.iloc[0]['date']
    for i in dfmkt.index:
        if dfmkt.iloc[i]['date'] != date :
            date = dfmkt.iloc[i]['date']
            date_changes.append(i)
        
    for d in date_changes:
        ax.axvline(d, c="c")
    
    # 날짜별 그룹 만들기
    dfmkt["tgroup"] = np.nan
    tg = 1
    date = dfmkt.iloc[0]['date']
    for i in dfmkt.index:
        if dfmkt.iloc[i]['date'] != date :
    # for i in range(dfmkt.shape[0]):
    #     if dfmkt["dt"].iloc[i] > 1000:
            date = dfmkt.iloc[i]['date']
            tg += 1
        dfmkt["tgroup"].iloc[i] = tg
        
    # 날짜 입력
    for i in range(tg):
        df_tg = dfmkt.loc[dfmkt["tgroup"] == i+1]
        text_x = np.mean(df_tg.index)
        ax.text(text_x, dfmkt['vwap'].max(), df_tg["date"].iloc[0], 
                ha="center", color="c")    
    
    
    for result_i in df_result.index:
        marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
        color = "tab:red" if marker == "^" else "b"
        x = result_i
        y = df_result.loc[result_i]['price']
        ax.scatter(x, y, color=color, marker=marker, s=300)
    plt.plot(dfmkt.index, dfmkt['close'])
    plt.plot(dfmkt.index, dfmkt['ema_fast'])
    plt.plot(dfmkt.index, dfmkt['ema_slow'])
    
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
                                 str(dfmkt['date'][0])+" ~ "+str(dfmkt['date'].iloc[-1]))
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass
    
def calPlEma(result_ema):
    """단순 종가기준 PL만 산출"""
    df_trade = result_ema['df']

    close_price = result_ema['dfmkt'].iloc[-1]['vwap']
    
    df_trade['amt'] = 2
    df_trade.at[df_trade.index[0], 'amt'] = 1
    df_trade['pl'] = 100 * df_trade.direction * df_trade.amt * (close_price - df_trade.price)- (df_trade.amt*0.03+df_trade.amt*0.03*3.3)
    #!!! stop-out loss 
    
    
    date = str(df_trade.index[0].date())
    day_pl_sum = round(df_trade['pl'].sum(), 1)
    day_signal_count = df_trade['pl'].count()
    print(date, day_pl_sum, day_signal_count)
    df_summary.loc[date,'day_pl_sum'] = day_pl_sum
    df_summary.loc[date,'day_signal_count'] = day_signal_count
    df_summary.to_excel(writer, sheet_name=date[:4])
    
    return date, day_pl_sum, day_signal_count

writer = pd.ExcelWriter("usdkrw_ema_result.xlsx",engine="xlsxwriter")
df_summary = pd.DataFrame(columns=['day_pl_sum', 'day_signal_count'])


def calPlEmaTimely(r, timebin="5min", losscut="N", asset='lktbf'):
    """시간흐름에 따른 PL 계산
    Parameters
        r : tradeEma 리턴값
            {'df' : df_result, 
             'dfmkt': dfmkt,
             'config': (fast_coeff, slow_coeff, margin)}
    Returns
        timelyPL : 시간대별 PL을 기록한 dataframe
    
    """
    
    #signal table 정리, 첫 signal 이후의 trade는 두배이므로 amt = 2
    sig = r['df']
    sig['amt'] = 2 
    sig.at[sig.index[0], 'amt'] = 1
    
    #오늘 날짜 정의
    # date = r['dfmkt']['date'][0]
    start_date = r['dfmkt']['date'].min()
    end_date = r['dfmkt']['date'].max()
        
    #시간대별 PL을 알아보기 위한 기초 시장 DATA
    if asset == 'lktbf':
        asset_time_table = 'lktbf_min'
        asset_multiplier = 100 #한 틱을 PL 1.0으로 표시하기 위함
        lc = -0.15 #15틱 손절
    elif asset == 'ktbf':
        asset_time_table = 'ktbf_min'
        asset_multiplier = 100 #한 틱을 PL 1.0으로 표시하기 위함
        lc = -0.05 #5틱 손절
    elif asset == 'usdkrw':
        asset_time_table = 'usdkrw_min'
        asset_multiplier = 10 #한 틱을 PL 1.0으로 표시하기 위함
        lc = -3.0 #3원 손절
        
    df1min = util.setDfData(start_date, end_date, asset_time_table, datetime_col="Y")
    
    #시간대별 PL을 정리하기 위한 dataframe
    df = df1min.resample(timebin, label='right', closed='right').agg({'close': 'last'})
    
    pl0930 = pl1000 = pl1030 = pl1100 = pl1130 = pl1200 = pl1300 = pl1400 = 99999
    
    # for t in sig.index:
    for t in df.index:
        #ts: til now signal table
        
        # ts = sig[:t]
        ts = sig[sig.index<t]
        prc = df.at[t, 'close']
        
        pl = sum(asset_multiplier * ts.direction.values * ts.amt.values * (prc - ts.price.values))
        num_trade = ts.amt.sum()
        df.at[t, 'pl'] = pl - num_trade * 0.03
        
        num_trade = ts.amt.sum()
        df.at[t, 'num_trade'] = num_trade
        
        if t.time() == datetime.time(9,30):
            pl0930 = pl
        elif t.time() ==datetime.time(10,00):
            pl1000 = pl
        # elif t.time() ==datetime.time(10,30):
        #     pl1030 = pl
        elif t.time() ==datetime.time(11,00):
            pl1100 = pl
        # elif t.time() ==datetime.time(11,30):
        #     pl1130 = pl
        elif t.time() ==datetime.time(12,00):
            pl1200 = pl
        elif t.time() ==datetime.time(13,00):
            pl1300 = pl
        elif t.time() ==datetime.time(14,00):
            pl1400 = pl
        
        #손절조건검토
        # 시간 조건 같이 검토
        if losscut == "Y" and pl < lc*asset_multiplier and (pl1000 > pl1100 > pl1300) and t.time() < datetime.time(13,5) :
            break
        #시간 조건 제외
        # if losscut == "Y" and pl < -15 and (pl1000 > pl1100 > pl1130):
        #     break
        #손익 조건만 검토
        # if losscut == "Y" and pl < -15:
        #     break
    
    df.dropna(inplace=True)
        
    return df


def main():
    
    print("Running main function\n")
    pd.set_option('mode.chained_assignment',  None)
    
    # tables = ['ktbf300vol', 'lktbf200vol']
    tables = ['ktbf300vol','lktb200vol']
    numdate = [4,5]
    # num = 10

        #일봉기준 전체 date list
    ld = list(util.getDailyOHLC(market_table_name='ktbf_day').index)
    # ld = [d for d in ld if d.year==2020 ]
    # ld = ['2020-04-20','2020-04-21','2020-04-22']
    ld = [d for d in ld if d.year >= 2017]
    # ld = [datetime.date(2021, 6, 21)]
    
    special_days=util.getMaturityDays() # 수능일, 국선 만기 5일간 등 제외해야 할 날들 
    
    for table in tables :
        for num in numdate :
            #일간 PL을 기록하는 dataframe
            dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])
            writer = pd.ExcelWriter(f"summary_{table}_{num}_ema.xlsx",engine="xlsxwriter")
            
            n_days_plot = num

            # frequency
            n = 3
            # before=ld[0]
            for i, days in enumerate(zip(ld,ld[n_days_plot-1:])):
                dates=[]
                d = days[0]
                
                # 일주일 후 다시 돌리게 하기 위한 로직
                # print(d, before)
                # if before == d or before+pd.Timedelta(days=7) == d or (before+pd.Timedelta(days=7) not in ld and before+pd.Timedelta(days=14) == d) or (before+pd.Timedelta(days=7) not in ld and before+pd.Timedelta(days=14) not in ld and before+pd.Timedelta(days=21) == d):
                    # before = d
                # else :
                #     continue
            
                # n(window수/2) 일 후에 다시 돌리게 하기 위한 로직
                if i % n == 0 :
                    pass
                else :
                    continue
                
                while d<=days[-1] :
                    if d in ld :
                        dates.append(d)
                    d = d+pd.Timedelta(days=1)
                
                # 제외해야 할 날들이 dates 에 있으면 안한다.
                countinueable = True
                for date in dates :
                    if date in special_days:
                        countinueable = False    
                        
                if not countinueable:
                    continue;
        
                result_ema = tradeEma(dates, table, plot="Y", execution="vwap", 
                                      fast_coeff=0.1,
                                      slow_coeff=0.02,
                                      margin = 0)
                
                timelyPl = calPlEmaTimely(result_ema, timebin="1min", losscut="N", asset = 'ktbf')
                
                dfpl.at[i, 'date'] = str(days[0]) +'~'+str(days[-1])
                
                pl_of_the_day = round(timelyPl.pl[-1], 2)
                dfpl.at[i, 'pl'] = pl_of_the_day
                
                num_trade = timelyPl.num_trade[-1]
                dfpl.at[i, 'num_trade'] = num_trade
                
                trade_ended_at = str(timelyPl.index[-1])[-8:]
                
                #당일의 결과
                #print(day, "    ", pl_of_the_day, str(timelyPl.index[-1])[-8:])
                print(f'Day   | {days}    \npl= {pl_of_the_day}, trade end= {trade_ended_at},  num trade= {num_trade}')
                
                #누적결과
                cumsum = round(dfpl.pl.sum(), 1)
                mean = round(dfpl.pl.mean(), 2)
                std = round(dfpl.pl.std(), 3)
                sr = round(mean / std, 3)
                num_trade_avg = round(dfpl.num_trade.mean(), 1)
                print(f'Cumul | cumsum: {cumsum}  mean:{mean}  SR: {sr}  trades/day: {num_trade_avg}',
                      "\n---------------------------------------------------------------")
            
            # dfpl.set_index(pd.to_datetime(dfpl.date), inplace=True)
            
            dfpl.to_excel(writer)
            writer.save()
    return dfpl

if __name__ == "__main__":
    dfpl = main()



