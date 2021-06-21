import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import utils.util as util
import datetime
import os
from tqdm import tqdm


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


def getLoiFromPast(date, loi_option, table):
    """
    loi_option이 오늘 이전인 경우, loi 설정
    """
    #loi_option에 따라 loi 설정
    if loi_option == 'yday_close':
        loi = util.getYdayOHLC(date, table)['close']
    elif loi_option == 'yday_hi':
        loi = util.getYdayOHLC(date, table)['high']
    elif loi_option == 'yday_lo':
        loi = util.getYdayOHLC(date, table)['low']
    elif loi_option == 'yday_open':
        loi = util.getYdayOHLC(date, table)['open']
    elif loi_option == '2day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 2, table)['high']
    elif loi_option == '2day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 2, table)['low']
    elif loi_option == '3day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 3, table)['high']
    elif loi_option == '3day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 3, table)['low']
    elif loi_option == '5day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 5, table)['high']
    elif loi_option == '5day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 5, table)['low']
    elif loi_option == '10day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 10, table)['high']
    elif loi_option == '10day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 10, table)['low']
    elif loi_option == '20day_hi':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 20, table)['high']
    elif loi_option == '20day_lo':
        yday = util.date_offset(date, -1)
        loi = util.getNdayOHLC(yday, 20, table)['low']
    else:
        raise ValueError("Wrong LOI option!!")
        
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
    plt.plot(df.index, df['close'])
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



def tradeLoi(date, loi_option='open', vol_option='lktbf50vol', plot="N", execution="adjusted", margin=1.0):
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
    # #MySQL문법에 맞게 따옴표 처리
    # vol_option = "`" + vol_option + "`"
    
    #테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, vol_option)
    
    #loi_option에 따라 loi 설정, loi_option이 과거일 경우 함수호출
    if loi_option == 'open':
        loi = dfmkt.iloc[0]['close']
    else:
        table = ''
        if vol_option in ['lktbf50vol', 'lktbf100vol', 'lktbf200vol'] :
            table = 'lktbf_day'
        elif vol_option in ['ktbf100vol', 'ktbf200vol', 'lktbf300vol'] :
            table = 'ktbf_day'
        elif vol_option in ['usdkrw100vol', 'usdkrw200vol', 'usdkrw300vol'] :
            table = 'usdkrw_day'
        else :
            print("error table")
        loi = getLoiFromPast(date, loi_option, table)
    
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
    signal_before_at = dfmkt.at[dti[0], 'time']
    
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
            signal_now_at = dfmkt.at[dti_now, 'time']
            
            #이전시그널과 반대방향 또는 이전시그널발생후 30분이 지났을 때
            if (signal_before != signal_now) or (signal_now_at > signal_before_at + pd.Timedelta('30m')) :
                    
                df_result.at[dti_now, 'direction'] = signal_now
                signal_before = signal_now
                signal_before_at = signal_now_at
                
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


def lineDrawer(color,x1,y1,x2,y2) :
    plt.scatter(x1,y1,color=color)
    plt.scatter(x2,y2,color=color)
    x = np.array([x1, x2])
    y = np.array([y1, y2])
    plt.plot(x,y, color=color,linewidth=4)

def writeSummary(df_result, dti_now, time, pre_position, post_position, vwap, avg_price, amount, pl, local_index, nearest_loi_name, nearest_loi_val) :
    df_result.loc[dti_now,'time'] = time
    df_result.loc[dti_now,'pre_position'] = pre_position
    df_result.loc[dti_now,'post_position'] = post_position
    df_result.loc[dti_now,'vwap'] = vwap
    df_result.loc[dti_now,'avg_price'] = avg_price
    df_result.loc[dti_now,'left_amount'] = amount
    df_result.loc[dti_now,'pl'] = pl
    df_result.loc[dti_now,'local_index'] = local_index
    df_result.loc[dti_now,'nearest_loi_name'] = nearest_loi_name
    df_result.loc[dti_now,'nearest_loi_val'] = nearest_loi_val
    # df_result.loc[dti_now,'ptlc'] = ptlc
    
    return df_result

def getPl(vwap, buy_price, amt, direction=1) :
    return round(amt*(vwap - buy_price)*direction,3)

def rangeTradeMultiLoi(date, vol_option='lktbf50vol', plot="N", execution="vwap",
                  loi_redundancy_margin=10, pt_margin=5, lc_margin=15, entry_margin=5, scale_entry=10):
    """
    Parameters
    ----------
    date : datetime.date
        테스트하고자 하는 날짜
    loi_option : str
        'open', 'yday_close', 'yday_hi', 'yday_lo', 'yday_open'
        '2day_hi', '2day_lo', '3day_hi', '3day_lo',......
        
    vol_option : str
        몇개짜리 볼륨봉을 쓸 것인지 = DB의 table명과 동일하게
    Returns
    -------
    {'df': df_result,
     'dfmkt': 시장data
     }
        df_result
            trade_time : pd.Timestamp
            direction : +1 or -1
            price : 매매가 일어난 가격
        loi_option
    """
    
    #테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, vol_option)
    
    
    """사전정의된 loi_option에 따라 여러개의 loi를 사전 설정"""
    loi_list = ['open',
                'yday_close', 'yday_hi', 'yday_lo', 'yday_open', 
                '2day_hi', '2day_lo',
                '3day_hi', '3day_lo', 
                '5day_hi', '5day_lo',
                '10day_hi', '10day_lo',
                '20day_hi', '20day_lo',]
    
    df_loi = pd.DataFrame(index=loi_list, columns=['name','value', 'open_distance', 'abs_distance', 'margin'])
    df_loi.index.name = 'loi_name'
    df_loi['name']=df_loi.index

    for loi_option in loi_list:
        if loi_option == 'open':
            df_loi.at[loi_option, 'value'] = dfmkt.iloc[0]['close']
        else:
            table = ''
            if vol_option in ['lktbf50vol', 'lktbf100vol', 'lktbf200vol'] :
                table = 'lktbf_day'
            elif vol_option in ['ktbf100vol', 'ktbf200vol', 'lktbf300vol'] :
                table = 'ktbf_day'
            elif vol_option in ['usdkrw100vol', 'usdkrw200vol', 'usdkrw300vol'] :
                table = 'usdkrw_day'
            else :
                print("error table")
            df_loi.at[loi_option, 'value'] = getLoiFromPast(date, loi_option, table)
    
    # df_loi.sort_values(by='value', ascending=False, inplace=True)
    
    #중복 또는 근접으로 지워질 loi 옵션들
    rm_opt = []
    for i,opt in enumerate(df_loi.index):
        for j,opt2 in enumerate(df_loi.index): 
            if i < j and abs(df_loi.at[opt, 'value'] - df_loi.at[opt2,'value']) < loi_redundancy_margin/100 :
                rm_opt.append(opt2 if opt2 != 'open' else opt)
                # rm_opt.append(opt2 if opt2 != 'open' else opt)
    
    
    
    rm_opt = list(set(rm_opt))            
    
    rm_loi = pd.DataFrame(columns=['value'])
    for opt in rm_opt :
        rm_loi.loc[opt,'value'] = df_loi.at[opt,'value']
    
    df_loi.drop(rm_opt, inplace=True)
    
    
    #loi별 margin 설정, 시가에서 멀수록 margin을 넉넉히 설정하여 스쳐도 시그널 나오도록 한다
    #최소 마진은 entry_margin으로 param설정
    df_loi['margin'] = [max(entry_margin, 100*x) for x in 0.15*df_loi['open_distance'].abs()]
    
    
    #결과를 담는 df 정의
    dti = dfmkt.index
    # df_result = pd.DataFrame(index = dti, 
    #                          columns=['loi_name',
    #                                   'loi_value',
    #                                   'signal_time', 
    #                                   'direction', 
    #                                   'signal_vwap', 
    #                                   'trade_time', 
    #                                   'price',
    #                                   'local_index'])
    
    # #range 안 또는 밖의 상태를 저장
    # range_status_prev = "out_of_range"
    
    # #현재의 signal 상태를 저장
    # signal_before = 0 
    # signal_before_at = dfmkt.at[dti[0], 'time']
    
    
        
    pre_loi = ''
    nearest_loi = ''
    position = 'None'
    position_taken = False
    scale_traded = False
    margin = 0.0
    buy_price = 0.0
    amount = 0
    
    points=[]
    point = []
    
    cols = ['time','pre_position','post_position', 'vwap', 'avg_price', 'left_amount', 'pl', 'local_index', 'nearest_loi_name', 'nearest_loi_val']
    df_result = pd.DataFrame(columns=cols)
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        
        #현재 loop에서 사용될 시장가격
        vwap = dfmkt.loc[dti_now, 'vwap']
        df_loi['open_distance'] = df_loi['value'] - vwap
        df_loi['abs_distance'] = abs(df_loi['open_distance'])
        df_loi = df_loi.sort_values('abs_distance')
        
        if position_taken :
            nearest_loi = df_loi.iloc[0]
            margin = df_loi.iloc[0]['margin']
        else:
            if df_loi.iloc[0]['name'] != 'open':
                pre_loi = df_loi.loc['open']
                nearest_loi = df_loi.iloc[0]
            else :
                pre_loi = df_loi.iloc[1]
                nearest_loi = df_loi.iloc[1]
            margin = df_loi.iloc[1]['margin']
       
        # 마지막 시간때 청산
        if dti_now == dti[-1]:
            pl = getPl(vwap, buy_price,amount)
            if position != 'None':
                if position == 'long':
                    writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], position, 'None', vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                    point.extend([dti_now, vwap])
                    param = ['red']
                    param.extend(point)
                    points.append(param)
                    point = []
                else :
                    writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], position, 'None', vwap, buy_price, amount, -pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                    point.extend([dti_now, vwap])
                    param = ['blue']
                    param.extend(point)
                    points.append(param)
                    point = []
        elif position == 'None':
            # 처음 시작할때 가장 가까운 loi가 open이면 이를 우회하기 위해 두번째 가까운 loi를 nearest와 pre loi로 둔다
            open_val = df_loi[df_loi['name']=='open']['value'][0]

            if not position_taken and pre_loi['value'] == nearest_loi['value'] and open_val < nearest_loi['value'] and round(abs(vwap - nearest_loi['value']),3) < margin/100 :
                position = 'long'
                position_taken = True
                
                buy_price = vwap
                amount += 1
                # pl = getPl(vwap, buy_price,amount)
                pl = 0 
                point = [dti_now, vwap]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'None', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
            elif not position_taken and pre_loi['value'] == nearest_loi['value'] and open_val > nearest_loi['value'] and round(abs(vwap - nearest_loi['value']),3) < margin/100:
                position = 'short'
                position_taken = True
                
                buy_price = vwap
                amount += 1
                # pl = getPl(vwap, buy_price,amount,-1)
                pl = 0 
                point = [dti_now, vwap]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'None', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                
            # 거래 후에도 nearest loi가 바뀌지 않는다면 preloi와 nearest loi가 같게 된다. 이때 새로운 포지션 진입을 위한 코드    
            elif position_taken and pre_loi['value'] == nearest_loi['value'] and vwap > nearest_loi['value'] and round(abs(vwap - nearest_loi['value']),3) < margin/100:
                position = 'long'
                position_taken = True
                
                buy_price = vwap
                amount += 1
                # pl = getPl(vwap, buy_price,amount)
                pl = 0 
                point = [dti_now, vwap]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'None', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
            elif position_taken and pre_loi['value'] == nearest_loi['value'] and vwap < nearest_loi['value'] and round(abs(vwap - nearest_loi['value']),3) < margin/100:
                position = 'short'
                position_taken = True
                
                buy_price = vwap
                amount += 1
                # pl = getPl(vwap, buy_price,amount,-1)
                pl = 0 
                point = [dti_now, vwap]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'None', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                
        # long 포지션으로 매수 : 포지션이 없는데, 이전 loi보다 근처 loi가 밑에 있고, 근처 loi와 현재가의 차가 마진이내일때 pl이 계산되고 loi가 갱신된다.            
            elif pre_loi['value'] > nearest_loi['value'] and round(abs(vwap - nearest_loi['value']),3) < margin/100:
                pre_loi = nearest_loi
                position = 'long'
                position_taken = True
                
                buy_price = vwap
                amount += 1
                # pl = getPl(vwap, buy_price,amount)
                pl = 0 
                point = [dti_now, vwap]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'None', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                
        # short 포지션으로 매수 : 포지션이 없는데, 이전 loi보다 근처 loi가 위에 있고, 근처 loi와 현재가의 차가 마진이내일때 pl이 계산되고 loi가 갱신된다.
            elif pre_loi['value'] < nearest_loi['value'] and round(abs(vwap - nearest_loi['value']),3) < margin/100:
                pre_loi = nearest_loi
                position = 'short'
                position_taken = True
                
                buy_price = vwap
                amount += 1
                # pl = getPl(vwap, buy_price,amount,-1)
                pl = 0 
                point = [dti_now, vwap]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'None', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                
        # long 포지션에서 익절 : long 인데, 이전 loi보다 근처 loi가 위에 있고, pl이 pt_margin 이상일때 pl이 계산되고 loi가 갱신된다.
        elif position == 'long':
            if pre_loi['value'] <= nearest_loi['value'] and getPl(vwap,buy_price,amount) > pt_margin/100:
                pre_loi = nearest_loi
                position = 'None'
                
                scale_traded = False
                pl = getPl(vwap,buy_price,amount)
                amount = 0
                point.extend([dti_now, vwap])
                param = ['red']
                param.extend(point)
                points.append(param)
                point = []
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'long', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
        # long 포지션에서 물타기 : long인데, 이전 loi보다 근처 loi가 밑에 있고, pl이 -lc_margin/200 보다 작을때 1회 물타기를 한다.
            elif not scale_traded and pre_loi['value'] >= nearest_loi['value'] and getPl(vwap,buy_price,amount) < -scale_entry/100:
            # elif not scale_traded and pre_loi['value'] >= nearest_loi['value'] and round(nearest_loi['value']-vwap,3) > lc_margin/200:
                scale_traded = True
                buy_price = (buy_price + vwap)/2
                amount += 1
                # pl = getPl(vwap, buy_price,amount)
                pl = 0
                point.extend([dti_now, buy_price])
                param = ['red']
                param.extend(point)
                points.append(param)
                point = [dti_now,buy_price]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'long', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
        # long 포지션에서 손절 : long인데, 물탄 이후 이전 loi보다 근처 loi가 밑에 있고, pl이 -lc_margin 보다 작을때 손절한다.
            elif scale_traded and pre_loi['value'] >= nearest_loi['value'] and getPl(vwap,buy_price,amount) < -lc_margin/100:
                pre_loi = nearest_loi
                position = 'None'
                scale_traded = False
                pl = getPl(vwap, buy_price,amount)
                amount = 0
                point.extend([dti_now, vwap])
                param = ['red']
                param.extend(point)
                points.append(param)
                point = []
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'long', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                
        # short 포지션에서 익절 : short 인데, 이전 loi보다 근처 loi가 아래에 있고, pl이 pt_margin 이상일때 pl이 계산되고 loi가 갱신된다.
        elif position == 'short':
            if pre_loi['value'] >= nearest_loi['value'] and getPl(vwap,buy_price,amount,-1) > pt_margin/100:
                pre_loi = nearest_loi
                position = 'None'
                
                scale_traded = False
                pl = getPl(vwap,buy_price,amount,-1)
                amount = 0
                point.extend([dti_now, vwap])
                param = ['blue']
                param.extend(point)
                points.append(param)
                point = []
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'short', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
        # short 포지션에서 물타기 : short인데, 이전 loi보다 근처 loi가 위에 있고, pl이 -lc_margin/200 보다 작을때 1회 물타기를 한다.
            elif not scale_traded and pre_loi['value'] <= nearest_loi['value'] and getPl(vwap,buy_price,amount,-1) < -scale_entry/100:
            # elif not scale_traded and pre_loi['value'] >= nearest_loi['value'] and round(nearest_loi['value']-vwap,3) > lc_margin/200:
                scale_traded = True
                buy_price = (buy_price + vwap)/2
                amount += 1
                # pl = getPl(vwap, buy_price,amount,-1)
                pl = 0
                point.extend([dti_now, buy_price])
                param = ['blue']
                param.extend(point)
                points.append(param)
                point = [dti_now,buy_price]
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'short', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
        # short 포지션에서 손절 : short인데, 물탄 이후 이전 loi보다 근처 loi가 위에 있고, pl이 -lc_margin/100 보다 작을때 손절한다.
            elif scale_traded and pre_loi['value'] <= nearest_loi['value'] and getPl(vwap,buy_price,amount,-1) < -lc_margin/100:
                pre_loi = nearest_loi
                position = 'None'
                scale_traded = False
                pl = getPl(vwap, buy_price,amount,-1)
                amount = 0
                point.extend([dti_now, vwap])
                param = ['blue']
                param.extend(point)
                points.append(param)
                point = []
                
                writeSummary(df_result, dti_now, dfmkt.loc[dti_now,'time'], 'short', position, vwap, buy_price, amount, pl, dti_now, nearest_loi['name'], nearest_loi['value'])
                
                
                
    #     #dti_pre에서 signal 발생한 경우 dti_now에서 time, price 설정
    #     #df_result의 dti_pre행을 indexing
    #     if df_result.loc[dti_pre]['price'] == 'TBD':
    #         df_result.at[dti_pre, 'trade_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
            
    #         if execution =="adjusted":
    #             ent_price = upp(vwap) if df_result.iloc[-1]['direction'] == 1 else flr(vwap)
    #         elif execution == "vwap":
    #             ent_price = vwap
    #         else:
    #             raise NameError('Wrong execution option')
    #         df_result.at[dti_pre, 'price'] = ent_price
        
    #     #현재가(=vwap) 기준 LOI 거리순으로 정렬한 Series
    #     s_loi_dist = (df_loi['value']- vwap).abs().sort_values()
    #     current_loi_name = s_loi_dist.index[0]
        
    #     loi = df_loi.at[current_loi_name, 'value']
    #     margin = df_loi.at[current_loi_name, 'margin']
        
    #     range_status = rangeTest(vwap, loi, margin)
        
    #     #LOI 레인지 밖에서 안으로 들어온 경우 
    #     if range_status_prev == "out_of_range" and range_status == "within_range":
    #         range_status_prev = range_status
            
    #     elif range_status_prev == "out_of_range" and range_status == "out_of_range":
    #         pass
        
    #     elif range_status_prev == "within_range" and range_status == "within_range":
    #         pass
        
    #     #LOI 레인지 안에서 밖으로 나가는 경우 --> signal 발생
    #     elif range_status_prev == "within_range" and range_status == "out_of_range":
    #         range_status_prev = range_status
            
    #         #1은 LOI 레인지 상향돌파, vice versa
    #         signal_now = 1 if vwap > loi else -1
    #         signal_now_at = dfmkt.at[dti_now, 'time']
            
    #         #이전시그널과 반대방향 또는 이전시그널발생후 30분이 지났을 때
    #         if (signal_before != signal_now) or (signal_now_at > signal_before_at + pd.Timedelta('30m')) :
                    
    #             df_result.at[dti_now, 'loi_name'] = current_loi_name
    #             df_result.at[dti_now, 'loi_value'] = loi
    #             df_result.at[dti_now, 'direction'] = signal_now
    #             signal_before = signal_now
    #             signal_before_at = signal_now_at
                
    #             df_result.at[dti_now, 'loi'] = loi
    #             #timedelta --> datetime.time형식으로 변환
    #             df_result.at[dti_now, 'signal_time'] = pd.to_datetime(str(date) + ' ' + str(dfmkt.loc[dti_now,'time'])[7:])
                
    #             df_result.at[dti_now, 'signal_vwap'] = vwap
    #             df_result.at[dti_now, 'price'] = 'TBD'
    #             df_result.at[dti_now, 'local_index'] = dti_now
        
    # """vwap index기준 test loop종료"""
    
    df_result.dropna(inplace=True)
    
    if not os.path.exists('rangeTradeMultiLoi.xlsx'):
        with pd.ExcelWriter('rangeTradeMultiLoi.xlsx', mode = 'w', engine = 'openpyxl') as writer :
            df_result.to_excel(writer, sheet_name=str(date))
    else:
        with pd.ExcelWriter('rangeTradeMultiLoi.xlsx', mode = 'a', engine = 'openpyxl') as writer :
            df_result.to_excel(writer, sheet_name=str(date))
    # workbook = writer.book()
    # worksheet = workbook.add_worksheet(date)
    # writer sheets[date] = worksheet
    
    writer.save()

    """결과1차정리, PLOT을 위함"""
    result = {'df' : df_result, 
              'df_loi': df_loi, 
              'dfmkt': dfmkt,
              'rm_loi':rm_loi,
              'point':points
              }
    
    # """"결과PLOT"""    
    if plot == "Y":
        plotRangeTradeMultiLoi(result)

    """"결과정리"""    
    result['df'].index = result['df'].time
    result['df'].index.name = 'index'
    result['df_rmloi'] =rm_loi
        
    # result['df'].drop(columns='trade_time', inplace=True)
    
    return result

def plotRangeTradeMultiLoi(tradeLoi_result):
    """임시 플로팅 함수로 사용"""
    df_result = tradeLoi_result['df']
    df_result.index = df_result.local_index
    # loi_option = tradeLoi_result['loi_option']
    df = tradeLoi_result['dfmkt']
    # loi = tradeLoi_result['loi']
    loi = tradeLoi_result['df_loi']['value']
    rmloi = tradeLoi_result['rm_loi']['value']
    margin = tradeLoi_result['df_loi']['margin']
    points = tradeLoi_result['point']
    

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)

    for point in points :
        x1 = point[1]
        y1 = point[2]
        x2 = point[3]
        y2 = point[4]
        ax.scatter(x1,y1,color=point[0])
        ax.scatter(x2,y2,color=point[0])
        x = np.array([x1, x2])
        y = np.array([y1, y2])
        plt.plot(x,y, color=point[0],linewidth=1)

    # for result_i in df_result.index:
    #     marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
    #     color = "tab:red" if marker == "^" else "b"
    #     x = result_i
    #     y = df_result.loc[result_i]['price']
    #     ax.scatter(x, y, color=color, marker=marker, s=200)
    
    """
    loi 값들을 수평선으로 그음(loi[0] : opt, loi[1] : val)
    """

    for i in range(len(loi)):
        plt.axhline(y=loi[i], linewidth=1, color="blue")
        plt.text(df_result.index[-1] if not df_result.empty else 0, loi[i], str(loi[i])+" / "+str(loi.index[i] + " / "+str(round(margin[i],2))), color="blue")
        
    for i in range(len(rmloi)):
        plt.axhline(y=rmloi[i], linewidth=1, color="gray")
        plt.text(0, rmloi[i], str(rmloi[i])+" / "+str(rmloi.index[i]), color="gray")
    # for i in range(len(loi[1])) :
    #     plt.axhline(y=loi[1][i], linewidth=1, color="blue")
    #     plt.text("right", loi[1][i], loi[0][i] + " " +str(loi[1][i]), color="blue")
    
    
    plt.plot(df.index, df['close'])
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 18,
            }
    # plot_name = '{0}: {1}, Margin: {2}'
    # plot_name = '{0}: {1}'
    # plot_name = plot_name.format(loi, tradeLoi_result['margin'])
    plot_name = str(df.iloc[0]['date']) + '   ' + str(df.iloc[-1]['close'])
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass

# """ tradeMultiLoi의 결과를 param으로 넣어주면 pl table을 계산한다 """
# def calDailyPlRangeLoi(result, day):
#     df=result['df']
#     close = result['dfmkt'].iloc[-1]['close']
#     dti = df.index
#     df_pl = pd.DataFrame(index=dti, columns=['pl'])
#     for i,dt in enumerate(dti) :
#         df_pl.loc[dt,'pl'] = df.iloc[i]['pl']
#     pl_of_the_day = round(df_pl.pl.sum(),3)
#     num_trade = len(dti)
#     print("---------------------------------------------------------------\n"
#         f'Day   | {day}    pl= {pl_of_the_day}, {num_trade}')
    

def tradeMultiLoi(date, vol_option='lktbf50vol', plot="N", execution="vwap",
                  loi_redundancy_margin=10):
    """
    Parameters
    ----------
    date : datetime.date
        테스트하고자 하는 날짜
    loi_option : str
        'open', 'yday_close', 'yday_hi', 'yday_lo', 'yday_open'
        '2day_hi', '2day_lo', '3day_hi', '3day_lo',......
        
    vol_option : str
        몇개짜리 볼륨봉을 쓸 것인지 = DB의 table명과 동일하게
    Returns
    -------
    {'df': df_result,
     'dfmkt': 시장data
     }
        df_result
            trade_time : pd.Timestamp
            direction : +1 or -1
            price : 매매가 일어난 가격
        loi_option
    """
    
    #테스트를 위한 해당일의 시장 data load
    dfmkt = util.setDfData(date, date, vol_option)
    
    
    """사전정의된 loi_option에 따라 여러개의 loi를 사전 설정"""
    loi_list = ['open',
                'yday_close', 'yday_hi', 'yday_lo', 'yday_open', 
                '2day_hi', '2day_lo',
                '3day_hi', '3day_lo', 
                '5day_hi', '5day_lo',
                '10day_hi', '10day_lo',
                '20day_hi', '20day_lo',]
    
    df_loi = pd.DataFrame(index=loi_list, columns=['value', 'open_distance','margin'])
    df_loi.index.name = 'loi_name'

    for loi_option in loi_list:
        if loi_option == 'open':
            df_loi.at[loi_option, 'value'] = dfmkt.iloc[0]['close']
        else:
            table = ''
            if vol_option in ['lktbf50vol', 'lktbf100vol', 'lktbf200vol'] :
                table = 'lktbf_day'
            elif vol_option in ['ktbf100vol', 'ktbf200vol', 'lktbf300vol'] :
                table = 'ktbf_day'
            elif vol_option in ['usdkrw100vol', 'usdkrw200vol', 'usdkrw300vol'] :
                table = 'usdkrw_day'
            else :
                print("error table")            
            df_loi.at[loi_option, 'value'] = getLoiFromPast(date, loi_option, table)
    
    # df_loi.sort_values(by='value', ascending=False, inplace=True)
    
    #중복 또는 근접으로 지워질 loi 옵션들
    rm_opt = []
    for i,opt in enumerate(df_loi.index):
        for j,opt2 in enumerate(df_loi.index): 
            if i < j and abs(df_loi.at[opt, 'value'] - df_loi.at[opt2,'value']) < loi_redundancy_margin/100 :
                rm_opt.append(opt2 if opt2 != 'open' else opt)
                # rm_opt.append(opt2 if opt2 != 'open' else opt)
    
    
    
    rm_opt = list(set(rm_opt))            
    
    rm_loi = pd.DataFrame(columns=['value'])
    for opt in rm_opt :
        rm_loi.loc[opt,'value'] = df_loi.at[opt,'value']
    
    df_loi.drop(rm_opt, inplace=True)
    
    df_loi['open_distance'] = df_loi['value'] - df_loi.at['open', 'value']
    
    #loi별 margin 설정, 시가에서 멀수록 margin을 넉넉히 설정하여 스쳐도 시그널 나오도록 한다
    #최소 마진은 1.5틱으로 설정
    df_loi['margin'] = [max(1.5, 100*x) for x in 0.15*df_loi['open_distance'].abs()]
    
    
    #결과를 담는 df 정의
    dti = dfmkt.index
    df_result = pd.DataFrame(index = dti, 
                             columns=['loi_name',
                                      'loi_value',
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
    signal_before_at = dfmkt.at[dti[0], 'time']
    
    
    """vwap index기준 test loop시작"""
    for dti_pre, dti_now in zip(dti, dti[1:]):
        
        #현재 loop에서 사용될 시장가격
        vwap = dfmkt.loc[dti_now, 'vwap']
        
        
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
        
        #현재가(=vwap) 기준 LOI 거리순으로 정렬한 Series
        s_loi_dist = (df_loi['value']- vwap).abs().sort_values()
        current_loi_name = s_loi_dist.index[0]
        
        loi = df_loi.at[current_loi_name, 'value']
        margin = df_loi.at[current_loi_name, 'margin']
        
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
            signal_now_at = dfmkt.at[dti_now, 'time']
            
            #이전시그널과 반대방향 또는 이전시그널발생후 30분이 지났을 때
            if (signal_before != signal_now) or (signal_now_at > signal_before_at + pd.Timedelta('30m')) :
                    
                df_result.at[dti_now, 'loi_name'] = current_loi_name
                df_result.at[dti_now, 'loi_value'] = loi
                df_result.at[dti_now, 'direction'] = signal_now
                signal_before = signal_now
                signal_before_at = signal_now_at
                
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
              'df_loi': df_loi, 
              'dfmkt': dfmkt,
              'rm_loi':rm_loi
              }
    
    """"결과PLOT"""    
    if plot == "Y":
        plotMultiLoi(result)

    """"결과정리"""    
    result['df'].index = result['df'].trade_time
    result['df'].index.name = 'index'
    result['df_rmloi'] =rm_loi
        
    # result['df'].drop(columns='trade_time', inplace=True)
    
    return result


def calPlMultiLoi(result_MultiLoi):
    """단순 종가기준 PL만 산출"""
    df_trade = result_MultiLoi['df']

    close_price = result_MultiLoi['dfmkt'].iloc[-1]['price']
    
    df_trade['amt'] = 2
    df_trade.at[df_trade.index[0], 'amt'] = 1
    df_trade['pl'] = 100 * df_trade.direction * df_trade.amt * (close_price - df_trade.price)
    #!!! stop-out loss 
    
    
    date = str(df_trade.index[0].date())
    day_pl_sum = round(df_trade['pl'].sum(), 1)
    day_signal_count = df_trade['pl'].count()
    print(date, day_pl_sum, day_signal_count)
    
    return date, day_pl_sum, day_signal_count

""" tradeMultiLoi의 결과를 param으로 넣어주면 pl table을 계산한다 """
def calDailyPlLoi(result):
    df=result['df']
    close = result['dfmkt'].iloc[-1]['close']
    dti = df.index
    df_pl = pd.DataFrame(index=dti, columns=['loi_name','direction','close', 'price','amt','pl'])
    for i,dt in enumerate(dti) :
        amt = 1
        if i != 0:
            amt = 0 if df.iloc[i]['direction'] == df.iloc[i-1]['direction'] else 2
        direction = df.iloc[i]['direction']
        price = df.iloc[i]['price']
        pl = (close - price)*direction*amt*100
        df_pl.loc[dt,'loi_name'] = df.iloc[i]['loi_name']
        df_pl.loc[dt,'direction'] = direction
        df_pl.loc[dt,'close'] = close
        df_pl.loc[dt,'price'] = price
        df_pl.loc[dt,'amt'] = amt
        df_pl.loc[dt,'pl'] = pl
    day = str(dti[0])[:11]
    pl_of_the_day = round(df_pl.pl.sum(),3)
    num_trade = len(dti)
    print(f'Day   | {day}    pl= {pl_of_the_day}, {num_trade}'
      "\n---------------------------------------------------------------")
    
    return df_pl, pl_of_the_day, num_trade
        
    
def plotMultiLoi(tradeLoi_result):
    """임시 플로팅 함수로 사용"""
    df_result = tradeLoi_result['df']
    df_result.index = df_result.local_index
    # loi_option = tradeLoi_result['loi_option']
    df = tradeLoi_result['dfmkt']
    # loi = tradeLoi_result['loi']
    loi = tradeLoi_result['df_loi']['value']
    rmloi = tradeLoi_result['rm_loi']['value']
    margin = tradeLoi_result['df_loi']['margin']
    
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
    for result_i in df_result.index:
        marker = "^" if df_result.loc[result_i]['direction'] == 1 else "v"
        color = "tab:red" if marker == "^" else "b"
        x = result_i
        y = df_result.loc[result_i]['price']
        ax.scatter(x, y, color=color, marker=marker, s=200)
    
    """
    loi 값들을 수평선으로 그음(loi[0] : opt, loi[1] : val)
    """

    for i in range(len(loi)):
        plt.axhline(y=loi[i], linewidth=1, color="blue")
        plt.text(df_result.index[-1], loi[i], str(loi[i])+" / "+str(loi.index[i] + " / "+str(round(margin[i],2))), color="blue")
        
    for i in range(len(rmloi)):
        plt.axhline(y=rmloi[i], linewidth=1, color="gray")
        plt.text(0, rmloi[i], str(rmloi[i])+" / "+str(rmloi.index[i]), color="gray")
    # for i in range(len(loi[1])) :
    #     plt.axhline(y=loi[1][i], linewidth=1, color="blue")
    #     plt.text("right", loi[1][i], loi[0][i] + " " +str(loi[1][i]), color="blue")
    
    
    plt.plot(df.index, df['close'])
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 18,
            }
    # plot_name = '{0}: {1}, Margin: {2}'
    # plot_name = '{0}: {1}'
    # plot_name = plot_name.format(loi, tradeLoi_result['margin'])
    plot_name = str(df.iloc[0]['date']) + '   ' + str(df.iloc[-1]['close'])
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()
    pass
          
def showGraph(loi, rm_loi, result, plot_name="QP") :
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
            'size': 10,
            }
    
    ax.set_xlabel(plot_name, fontdict=font)
    plt.show()

# #%%trade multi Loi 백테스트
# # date = datetime.date(2018,2,7)
# ld = list(util.getDailyOHLC().index)[20:]
# ld = [d for d in ld if d.year==2021 and d.month ==6]
# # ld = [d for d in ld if d.year<=2021 and d.year >=2017]
# # r = rangeTradeMultiLoi(date, plot="Y")
# total = 0.00
# df_summary = pd.DataFrame(columns=['day_pl_sum', 'day_signal_cnt'])
# writer = pd.ExcelWriter("summary_range_multiloi.xlsx",engine="xlsxwriter")

# for i, day in tqdm(enumerate(ld)) :
#     r = rangeTradeMultiLoi(day , plot="Y")
#     daily_pl = r['df']['pl'].sum()
#     trade_cnt = len(r['df'].index)
#     df_summary.loc[day, 'day_pl_sum'] = daily_pl
#     df_summary.loc[day, 'day_signal_cnt'] = trade_cnt
    
#     # x, pl, cnt = calDailyPlLoi(r)
#     # df_summary.loc[day,'day_pl_sum'] = pl
#     # df_summary.loc[day,'day_signal_cnt'] = cnt
#     # total += pl
#     # print(total, "   ",total/(i+1))
# # df_summary.to_excel(writer)
# writer.save()

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
    
    

def tradeEma(date, vol_option='lktbf50vol', plot="N", execution="adjusted",
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
    dfmkt.at[dti[0], 'ema_fast'] = dfmkt.at[dti[0], 'close']
    dfmkt.at[dti[0], 'ema_slow'] = dfmkt.at[dti[0], 'close']
    
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
        
        #slow ema 형성시까지(=slow ema가 적정수량이 생길때까지 signal 발생 보류
        if (dfmkt.ema_slow.count() > 1 / slow_coeff):
            
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
    dfmkt = tradeEma_result['dfmkt']

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    
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



def calPlEma_wlossCut(result_ema):
    """daytrader를 가정하고 PL에 따른 손절 실행"""
    pass

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
    date = r['dfmkt']['date'][0]
    
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
        
    df1min = util.setDfData(date, date, asset_time_table, datetime_col="Y")
    
    #시간대별 PL을 정리하기 위한 dataframe
    df = df1min.resample(timebin, label='right', closed='right').agg({'close': 'last'})
    
    pl0930 = pl1000 = pl1030 = pl1100 = pl1130 = pl1200 = pl1300 = pl1400 = 99999
    
    for t in df.index:
        #ts: til now signal table
        ts = sig[:t]
        prc = df.at[t, 'close']
        
        pl = sum(asset_multiplier * ts.direction.values * ts.amt.values * (prc - ts.price.values))
        df.at[t, 'pl'] = pl
        
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

def emaBT(ld, vol_option, execution, fast_coeff=0.3, slow_coeff=0.05, margin = 1.5):
    dfpl = pd.DataFrame(columns=['date', 'pl', 'num_signal'])
    for i, day in enumerate(ld):
        result_ema = tradeEma(day, vol_option=vol_option, plot="N", execution=execution, 
                              fast_coeff=fast_coeff, slow_coeff=slow_coeff, margin = margin)
        dfpl.at[i, 'date'], dfpl.at[i, 'pl'], dfpl.at[i, 'num_signal'] = calPlEma(result_ema)
        print(round(dfpl.pl.sum(), 1), round(dfpl.pl.mean(), 2), round(dfpl.pl.std(),2))
    
    dfpl.set_index(pd.to_datetime(dfpl.date), inplace=True)
    # dfpl.resample('Y').sum()
    
    return dfpl
