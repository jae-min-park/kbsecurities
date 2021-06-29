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


def tradeEma(dates, sp1_option='ktbf_10sec', sp2_option='lktbf_10sec', plot="N", execution="adjusted",
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
    dfmkt = pd.DataFrame(columns=['vwap'])
    last_index = 0
    
    special_days=[] # 수능일, 국선 만기 5일간
    for date in dates :
        if date in special_days :
            continue;
        df_sp1 = util.setDfData(date,date,sp1_option)
        df_sp2 = util.setDfData(date,date,sp2_option)
    
        df_sp1['prc_vol_product'] = df_sp1.close * df_sp1.volume
        df_sp1['datetime'] = pd.to_datetime(df_sp1.date.astype(str) + ' ' + df_sp1.time.astype(str).apply(lambda x: x[7:]))
        df_sp1['local_index']=df_sp1.index+last_index
        df_sp1.set_index('datetime', inplace=True)
        df_sp1_resampled = df_sp1.resample('min', 
                                            label='right', 
                                            origin='start_day',
                                            closed='right').agg(
                                                {'volume': 'sum', 'prc_vol_product': 'sum', 'local_index':'min'})
        df_sp2['prc_vol_product'] = df_sp2.close * df_sp2.volume
        df_sp2['datetime'] = pd.to_datetime(df_sp2.date.astype(str) + ' ' + df_sp2.time.astype(str).apply(lambda x: x[7:]))
        df_sp2['local_index']=df_sp2.index+last_index
        df_sp2.set_index('datetime', inplace=True)
        df_sp2_resampled = df_sp2.resample('min', 
                                            label='right', 
                                            origin='start_day',
                                            closed='right').agg(
                                                {'volume': 'sum', 'prc_vol_product': 'sum', 'local_index':'min'})

 
        for i in df_sp1_resampled.index:
            # if not str(i)[:10] in special_days :
            if str(i)[-8:] > '15:45:00' or str(i)[-8:] < '09:00:00':
                df_sp1_resampled = df_sp1_resampled.drop(index = i)
                df_sp2_resampled = df_sp2_resampled.drop(index = i)

            
        df_sp1_resampled['vwap'] = df_sp1_resampled['prc_vol_product']/df_sp1_resampled['volume']
        # df_sp1_resampled['vwap'] = df_sp1_resampled['vwap'].fillna(method='bfill')
        df_sp1_resampled['vwap'] = df_sp1_resampled['vwap'].fillna(method='ffill')
        df_sp2_resampled['vwap'] = df_sp2_resampled['prc_vol_product']/df_sp2_resampled['volume']
        # df_sp2_resampled['vwap'] = df_sp2_resampled['vwap'].fillna(method='bfill')
        df_sp2_resampled['vwap'] = df_sp2_resampled['vwap'].fillna(method='ffill')
    
        tmp = pd.DataFrame(columns=['vwap','local_index'])
        tmp['vwap'] = df_sp2_resampled['vwap'] - 3.3*df_sp1_resampled['vwap'] + 300
        tmp['local_index'] = df_sp2_resampled['local_index']
        last_index=df_sp2_resampled['local_index'][-1]+6
        dfmkt = pd.concat([dfmkt,tmp])
                                            
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
            # df_result.at[dti_pre, 'trade_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
            df_result.at[dti_pre, 'trade_time'] = dti_now
            
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
                    df_result.at[dti_now, 'local_index'] = dfmkt.at[dti_now, 'local_index']
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
    df_result = tradeEma_result['df'].copy()
    df_result.index = df_result.local_index
    df = tradeEma_result['dfmkt'].copy()

    # for i in df.index:
        # tmp = i.second + i.minute*60 + i.hour*3600 + i.day*3600*24 + i.month*3600*24*31 - 2764800
        # idx.append(tmp)
        # idx.append(str(i)[5:16])
        # index.append(str(i)[5:13])
    # idx = sorted(list(set(idx)))
    # index = sorted(list(set(index)))
    # idx = np.array(idx)
    # idx = df.index
        # 날짜 변경 지점 찾기

    df['index'] = df.index
    
    # df.set_index('local_index',inplace=True)
    # df.index = df.index.astype(int)
    df.reset_index(inplace=True)
    df["dt"] = df["index"] - df["index"].shift(1) # 데이터간 시간차
    df["dt"] = df["dt"].apply(lambda x: x.total_seconds())  # 초단위 환산
    df["dt"].fillna(0, inplace=True)              # 첫 데이터 빈칸 채우기
    
    # 날짜별 그룹 만들기
    df["tgroup"] = np.nan
    tg = 1
    for i in range(df.shape[0]):
        if df["dt"].iloc[i] > 1000:
            tg += 1
        df["tgroup"].iloc[i] = tg

    df["tgroup"] = df["tgroup"].astype("int")
    
    # 날짜, 시간 데이터 쪼개기
    df["date"] = df["index"].apply(lambda x: x.strftime("%y-%m-%d"))
    df["time"] = df["index"].apply(lambda x: x.strftime("%H:%M"))
    
    # 시각화
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df['vwap'])
    xticks = [int(x) for x in ax.get_xticks() if (x >= 0 and x < ax.get_xbound()[1])]
    del xticks[-1]
    xticklabels = df['time'].loc[xticks]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    # 날짜분리선
    date_changes = df.loc[df["dt"] > 1000].index
    for d in date_changes:
        ax.axvline(d, c="c")

    # 날짜 입력
    for i in range(tg):
        df_tg = df.loc[df["tgroup"] == i+1]
        text_x = np.mean(df_tg.index)
        ax.text(text_x, df['vwap'].max(), df_tg["date"].iloc[0], 
                ha="center", color="c")

    # fig = plt.figure(figsize=(8,8))
    # ax = fig.add_subplot(1,1,1)
    for result_i in df_result.index:
        marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
        color = "tab:red" if marker == "^" else "b"
        # x = str(result_i)[5:16]
        x = df_result.loc[result_i]['local_index']/6
        y = df_result.loc[result_i]['price']
        ax.scatter(x, y, color=color, marker=marker, s=400)
    # plt.plot(df['local_index'], df['vwap'])
    plt.plot(df['local_index']/6, df['ema_fast'])
    plt.plot(df['local_index']/6, df['ema_slow'])
    
    # plt.xticks(rotation=45)
    # plt.locator_params(axis='x', nbins=len(idx)/6000)
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 12,
            }
    plot_name = '{3}, F.c: {0}, S.c: {1}, m.g: {2}'
    plot_name = plot_name.format(tradeEma_result['config'][0],
                                 tradeEma_result['config'][1],
                                 tradeEma_result['config'][2],
                                 str(df['date'][0])+" ~ "+str(df['date'].iloc[-1]))
                                 
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

def calPlEmaTimely(r, timebin="5min", losscut="N"):
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
    
    #시간대별 PL을 알아보기 위한 기초 시장 DATA
    # if asset == 'lktbf':
    #     asset_time_table = 'lktbf_min'
    #     asset_multiplier = 100 #한 틱을 PL 1.0으로 표시하기 위함
    #     lc = -0.15 #15틱 손절
    # elif asset == 'ktbf':
    #     asset_time_table = 'ktbf_min'
    #     asset_multiplier = 100 #한 틱을 PL 1.0으로 표시하기 위함
    #     lc = -0.05 #5틱 손절
    # elif asset == 'usdkrw':
    #     asset_time_table = 'usdkrw_min'
    #     asset_multiplier = 10 #한 틱을 PL 1.0으로 표시하기 위함
    #     lc = -3.0 #3원 손절
        
    asset_multiplier = 100
    lc = -0.1
    # df1min = util.setDfData(date, date, asset_time_table, datetime_col="Y")
    
    #시간대별 PL을 정리하기 위한 dataframe
    df = r['dfmkt'].resample(timebin, label='right', closed='right').agg({'vwap': 'last'})
    
    pl0930 = pl1000 = pl1030 = pl1100 = pl1130 = pl1200 = pl1300 = pl1400 = 99999
    
    for t in df.index:
        #ts: til now signal table
        ts = sig[:str(t)]
        prc = df.at[t, 'vwap']
        
        pl = sum(asset_multiplier * ts.direction.values * ts.amt.values * (prc - ts.price.values))
                               
        # df.at[t, 'pl'] = pl
        num_trade = ts.amt.sum()
        df.at[t, 'num_trade'] = num_trade
        
        df.at[t, 'pl'] = pl - num_trade * 0.03 * ( 1 + 3.3 )
        
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
    
    #일봉기준 전체 date list
    ld = list(util.getDailyOHLC(market_table_name='ktbf_day').index)
    # ld = [d for d in ld if d.year==2020 ]
    # ld = ['2020-04-20','2020-04-21','2020-04-22']
    ld = [d for d in ld if d.year == 2021]
    # ld = [datetime.date(2021, 6, 21)]
    
    #일간 PL을 기록하는 dataframe
    dfpl = pd.DataFrame(columns=['date', 'pl', 'num_trade'])
    writer = pd.ExcelWriter("summary_spread_ema.xlsx",engine="xlsxwriter")
    
    n_days_plot = 3
    special_days=util.getMaturityDays() # 수능일, 국선 만기 5일간 등 제외해야 할 날들
    for i, days in enumerate(zip(ld,ld[n_days_plot-1:])):
        
        
        dates=[]
        d = days[0]
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

        result_ema = tradeEma(dates, 'ktbf_10sec', 'lktbf_10sec', plot="Y", execution="vwap", 
                              fast_coeff=0.1,
                              slow_coeff=0.01,
                              margin = 0)
        
        timelyPl = calPlEmaTimely(result_ema, timebin="1min", losscut="N")
        
        dfpl.at[i, 'date'] = str(days[0]) +'~'+str(days[-1])
        
        pl_of_the_day = round(timelyPl.pl[-1], 2)
        dfpl.at[i, 'pl'] = pl_of_the_day
        
        num_trade = timelyPl.num_trade[-1]
        dfpl.at[i, 'num_trade'] = num_trade
        
        trade_ended_at = str(timelyPl.index[-1])[-8:]
        
        #당일의 결과
        #print(day, "    ", pl_of_the_day, str(timelyPl.index[-1])[-8:])
        print(f'Day   | {days}    pl= {pl_of_the_day},  {trade_ended_at},   {num_trade}')
        
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



