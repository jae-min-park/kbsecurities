# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 19:31:35 2019

@author: infomax
"""

import os
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import ddt_util as du
from scipy import stats
import matplotlib.pyplot as plt
import datetime
from tqdm import tqdm
import math
import statistics


def list_ticks(df=DataFrame, d=pd.Timestamp, ref_prc=0.0, prc_col_name='종가',
               round_num=2, multiplier=100):
    """
    mkt_data와 날짜, 참조가격을 받아서 가격리스트리턴
    """

#    lp = list()
#    for p in df[d:d][prc_col_name]:
#        lp.append(multiplier*round(p-ref_prc, round_num))
    length_of_a_day = du.standard_length_of_day(df)
    
    if length_of_a_day > 1: 
        lp = np.array(df.loc[d][prc_col_name])
        lp = (lp - ref_prc)*multiplier
        ticks = list(lp)
        
    elif length_of_a_day == 1: #일간data yield일때 적용
        multiplier = 1000
        lp = df.loc[d][prc_col_name]
        lp = (lp - ref_prc)*multiplier
        ticks = []
        ticks.append(lp)
        
    return ticks

def list_consec_days(ld, df, ref_day, ref_price, prev_num=-2, next_num=+2, prc_col_name='종가', sectype='yield'):
    """연속된 날들의 분봉 tick list 연결"""

    prev_days = du.date_neighbor(ld, ref_day, prev_num)
    next_days = du.date_neighbor(ld, ref_day, next_num)
    
    prev_ticks = list(); next_ticks = list(); ref_ticks = list()
    
    for d in prev_days:
        if sectype == 'yield':
            prev_ticks = prev_ticks + list_ticks(df, d, ref_price)
        elif sectype == 'px':
            prev_ticks = prev_ticks + list_ticks_pct(df, d, ref_price)
        else: 
            print("wrong securities type")
            
    for d in next_days:
        if sectype == 'yield':
            next_ticks = next_ticks + list_ticks(df, d, ref_price)
        elif sectype =='px':
            next_ticks = next_ticks + list_ticks_pct(df, d, ref_price)
    
    ref_ticks = list_ticks(df, ref_day, ref_price)
    
    return prev_ticks + ref_ticks + next_ticks

def list_ticks_pct(df=DataFrame, 
                   d=pd.Timestamp, 
                   ref_prc=0.0, 
                   prc_col_name='종가'):
    """
    mkt_data와 날짜, 참조가격을 받아서 가격리스트리턴
    %변화를 표시. 1%변화를 1big으로 표현한다
    """

    daylen = du.standard_length_of_day(df)
    
    if daylen > 1: 
        lp = np.array(df.loc[d][prc_col_name]) #raw price list
        lp = ((lp - ref_prc) / ref_prc) * 10000 #pct list ex)0.1%=10
        ticks = list(lp)
        
    elif daylen == 1: #일간data 적용
        p = df.loc[d][prc_col_name] # raw price
        p = ((p - ref_prc) / ref_prc) * 10000 #pct ex)0.1%=10
        ticks = []
        ticks.append(lp)
        
    return ticks


def auction_dates(list_maturity=[3,5,10,20,30,50]):
    """입찰일, 만기 dictionary 리턴"""
    df_auct = pd.read_excel(os.getcwd()+'\입찰정보.xlsx')
    auct_dates = dict()
    for mty in list_maturity:
        sl = set(list(df_auct.loc[df_auct['만기']==mty, '입찰일']))
        for d in sl:
            auct_dates[d] = mty
    return auct_dates

   
def plot_multly(df_mkt, ld_plot, plot_name="cmpr plot", prev_num=-3, next_num=0, shift=0, sectype='yield', offset = 0, filename='default.jpg'):
    """
    intraday mkt_data와 날짜리스트를 받아서
    날짜들에 해당하는 consec_days plotting
    """
    ld_total = du.get_date_list(df_mkt)
    for d in ld_plot:
        if d not in ld_total:
            ld_plot.remove(d)
            print(str(d)," removed from list")
        
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1,1,1)
    
    if shift != 0:
        ld_all = du.get_date_list(df_mkt)
        ld_plot = du.date_offset_list(ld_all, ld_plot, shift)
    
    # Set plot name as xlabel
    font = {'family': 'verdana',
            'color':  'darkblue',
            'weight': 'bold',
            'size': 18,
            }
    
    fcast_result = fcast_multly(df_mkt, ld_plot, next_num)
    median_end_prc = fcast_result['mean']
    stdev = fcast_result['std']
    odds_of_up = int(fcast_result['odds_up']*100)
    
    #plot name 정의
    plot_name = plot_name + "\n" + " | mean=" + str(median_end_prc)
    plot_name = plot_name + " | std=" + str(stdev)
    plot_name = plot_name + " | odds_up=" + str(odds_of_up) + "%"
        
    ax.set_xlabel(filename, fontdict=font)

    #charting을 위한 기초정보들 정의    
    length_of_a_day = du.standard_length_of_day(df_mkt)

    minor_grid_interval = 3

    numdays = abs(prev_num) + next_num + 1
    
    if numdays * length_of_a_day > 50:
        dotsize = 1.5
    else : dotsize = 3    
    
    #주요 x축 포지션 및 5일 vertical line 위치 
    x_ref = length_of_a_day * abs(prev_num) - 1 
    x_start = 0
    x_end = length_of_a_day * numdays
    x_vline_inc = 5 * length_of_a_day
    vline1 = list(range(x_ref, x_end, x_vline_inc))
    vline2 = list(range(x_ref, x_start, -x_vline_inc))
    vline = list(set(vline1 + vline2))
    
    
    #개별라인 플로팅
    i = 0
    y_absmax = 0
    
    for day in ld_plot:
        if i == 0:
            lw = 4
        else:
            lw = 3 - 0.2 * min(10, i-1)
        
        ref_prc = du.juniljongga(ld_total, df_mkt, day)
        
        tl = np.array(list_consec_days(ld_total, df_mkt, day, ref_prc, prev_num, next_num, sectype))
        
        if length_of_a_day == 1: #daily data의 경우 zscore표시
            ZS_WINDOW_LIST = [5, 20, 60]
            zslabel_daily = str()
            for window in ZS_WINDOW_LIST:
                zs = round(du.zscore_find_daily(ld_total, df_mkt, day, window), 2)
                zslabel_daily = zslabel_daily + ' | ' + str(window)+'d=' + str(zs)
            legend_label = str(i)+') '+day.strftime('%Y-%m-%d')+', '+day.day_name()[0:3]+', '+ zslabel_daily
            
        else:
            legend_label = str(i)+') '+day.strftime('%Y-%m-%d')+', '+day.day_name()[0:3]    

        ax.plot(tl, marker='o', markersize=dotsize, label = legend_label, linewidth=lw)

        y_absmax = max(y_absmax, max(abs(min(tl)), abs(max(tl))))
        
        i = i + 1
    
    """GRID 정의"""
    #x축 major
    x_major_ticks = list(range(length_of_a_day-1, x_end, length_of_a_day))
    
    #x축 minor
    x_minor_ticks = []
    for nthday in range(numdays):
        grid_start = nthday * length_of_a_day
        x_minor_ticks = x_minor_ticks + list(range(grid_start-1, grid_start + length_of_a_day, minor_grid_interval))
    
    base = 20
    y_abxmax_adj = int(base * math.ceil(y_absmax/base))
    y_major_ticks = np.arange(-y_abxmax_adj, y_abxmax_adj, 20)
    y_minor_ticks = np.arange(-y_abxmax_adj, y_abxmax_adj, 10)
    
    
    ax.set_xticks(x_major_ticks)
    ax.set_xticks(x_minor_ticks, minor=True)
    ax.set_yticks(y_major_ticks)
    ax.set_yticks(y_minor_ticks, minor=True)
    
    ax.grid(which='major', color='grey', linewidth=0.6,linestyle='-')
    ax.grid(which='minor', color='grey', linewidth=0.4,linestyle=':')
    ax.yaxis.set_ticks_position('right')
    
 
    # 날짜 입력
    # num_x_major = len(x_major_ticks)
    # mid = int(num_x_major/2)
    
    # for i, item in enumerate(x_major_ticks):
    #     i - mid 
    #     if i >0 and i < num_x_major :
    #         ax.text(text_x, df['vwap'].max(), str(i-mid), 
    #                 ha="center", color="c")
    
    # 기준숫자 플로팅 상단에 입
    num_x_major = len(x_major_ticks)

    text_str = prev_num + offset
    # text_str = i - mid + offset
    ax.text(x_major_ticks[0]/2, np.max(y_major_ticks), text_str, ha="center", fontsize=15)
    for pre, post in zip(x_major_ticks, x_major_ticks[1:]) :
        text_str += 1
        # text_str = i - mid + offset
        ax.text((pre+post)/2, np.max(y_major_ticks), text_str, ha="center", fontsize=15)
    
    """legend location, ncol"""
    ax.legend(loc='upper left', ncol=2, bbox_to_anchor=(0,-0.1))
    
    #vline
    for vline_val in vline:
        plt.axvline(x = vline_val, color='black', linewidth=0.7, linestyle='--')
        
    plt.axhline(color='black', linewidth=0.7, linestyle='--')
 
    plt.savefig('D:\\dev\\case_data\\'+filename+'.jpg', bbox_inches='tight')
    # plt.savefig('D:\\dev\\data\\default2.jpeg')
    plt.show()
    
    
    
    """End of plot_mltly function"""
    
    
def datelist_from_dfptn(ld_all, dfptn, numplots=11, weekday_filter=None):
    """
    'simil_rank'열을 가진 ptn df에서 similarity 상위 날짜 리스트를 리턴
    weekday_filter = "Y"인 경우 today와 동일한 weekday만 필터링해서 리턴
    
    2020.09.02
    5일 이내의 자기복제 케이스 삭제 로직 추가
    """
    if weekday_filter == "Y":
        weekday_today = dfptn.index[-1].weekday()
        dfptn = dfptn.loc[dfptn.index.weekday == weekday_today]
    
    ld = list(dfptn['simil_rank'].sort_values()[:2*numplots].index)
    
    today = ld[0]
    for day in ld[1:]:
        distance = du.days_between_dates(day, today, ld_all)
        if distance < 5: ld.remove(day)
        
    ld = ld[:numplots]
    
    return ld

def dfptn_simplifier(dfptn, ld):
    """
    dfptn에서 plot dates만 남기고 핵심 정보만 추출, 출
    """
    for i in dfptn.index:
        if i not in ld:
            dfptn = dfptn.drop(index=i)
        
    dfptn_sim = dfptn.loc[:, ['corr_wavg','zscore','simil_rank']] #불필요열제거    
    
    dfptn_sim = dfptn_sim.sort_values('simil_rank')
    
    return dfptn_sim
    
    

""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""
"""과거 5일까지 path 확장"""
""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""
def get_df_ptn_dakamatsu(df, today=pd.Timestamp, zscore_co_rate=0.15, std_co_rate=0.5, 
                         corwdict_input=None):
    """
    분봉을 받아서 3일 전일종가대비변동 패턴 df 리턴
    """
    print("1/3 Preparing pattern analysis...")
       
    ld = du.get_date_list(df)
    standard_len = du.standard_length_of_day(df)
    print("  Standard datanum of a day: ", standard_len)

    #전일종가 dict
    junil = du.get_junil_jongga_dict(df)
    sjunil = Series(junil)
    df_ptn = pd.DataFrame(
            columns=['d1',
                     'ucinco', #path of past 5 days 
                     'ucuatro', #path of past 4 days
                     'ugg', #path of past 3 days
                     'ug', #path of past 2 days
                     'd0', #path 
                     'dn']
            )
    
# =============================================================================
#     Building daily consecutive patterns for ref data
# =============================================================================
    print("2/3 Building patterns...")
    for d0, d1, d2, d3, d4, d5 in tqdm(zip(ld[5:], ld[4:], ld[3:], ld[2:], ld[1:], ld)):
        
        ref = round(junil[d0],2)
        ptn_d0 = list(); ptn_d1 = list(); ptn_d2 = list(); ptn_d3 = list()
        ptn_d4 = list(); ptn_d5 = list()
        ptn_dn = list()
        #2016/8/1이전(2016/7/29까지)는 종가시간 15:15로 캔들갯수 차이 발생
        #ptn list 길이 보정해주는 로직 필요!!! -> 60분봉 사용해서 해결...
        for prc in df[d0:d0]['종가']:
            ptn_d0.append(100*round(prc-ref,2))
        for prc in df[d1:d1]['종가']:
            ptn_d1.append(100*round(prc-ref,2))
        for prc in df[d2:d2]['종가']:
            ptn_d2.append(100*round(prc-ref,2))
        for prc in df[d3:d3]['종가']:
            ptn_d3.append(100*round(prc-ref,2))
        for prc in df[d4:d4]['종가']:
            ptn_d4.append(100*round(prc-ref,2))
        for prc in df[d5:d5]['종가']:
            ptn_d5.append(100*round(prc-ref,2))
        if d0 != today: 
            dn = ld[ld.index(d0)+1] #d0다음날
            for prc in df[dn:dn]['종가']:
                ptn_dn.append(100*round(prc-ref,2))
        
#        df_ptn.at[d0, 'd0'] = ptn_d0 #d0는 오늘이므로 length check 안함
#        df_ptn.at[d0, 'dn'] = ptn_dn
        df_ptn.at[d0, 'd1'] = ptn_d1
#        df_ptn.at[d0, 'd2'] = ptn_d2
#        df_ptn.at[d0, 'd3'] = ptn_d3
#        df_ptn.at[d0, 'd4'] = ptn_d4
#        df_ptn.at[d0, 'd5'] = ptn_d5
            
        df_ptn.at[d0, 'ug'] = ptn_d2 + ptn_d1
        df_ptn.at[d0, 'ugg'] = ptn_d3 + ptn_d2 + ptn_d1
        df_ptn.at[d0, 'ucuatro'] = ptn_d4 + ptn_d3 + ptn_d2 + ptn_d1
        df_ptn.at[d0, 'ucinco'] = ptn_d5 + ptn_d4 + ptn_d3 + ptn_d2 + ptn_d1


# =============================================================================
#     Building daily ref data for simil_rank 
# =============================================================================
    print("3/3 Finallizing and ranking...")

    """today의 ucinco std를 구해서 추후 loop에서 비교 """
    stdev_ucinco_today = np.std(df_ptn.loc[today, 'ucinco'])    

    """today의 zs를 미리 구해서 추후 loop에서 비교"""
    zwindow = 20
    print("\n","zs window:", zwindow)

    si_today = max(zwindow, sjunil.index.get_loc(today)) 
    #junil indexing out of range방지. 즉, 최초일+zwindow보다는 큰 날짜를 indexing
    
    zl_today = sjunil[si_today-zwindow+1:si_today+1] 
    #slicing은 해당loc의 앞에서 끊으므로 +1이 필요. 
    #datetimeindex of Series preferred considering readability
    
    zscore_junil_today = stats.zscore(zl_today)[-1]
    
    """아래에서 ugg ug dq(=uje=yuday)의 각 corr의 weight를 정함"""
    if corwdict_input == None:
        corwdict = {'corw_ucinco':0.7, 
                    'corw_ucuatro':0,
                    'corw_ugg':0.1,
                    'corw_ug':0.1,
                    'corw_d1':0.1}
    else: corwdict = corwdict_input
    
    list_corr_weight = list(corwdict.values())
    
    print("corr weight ucinco :", corwdict['corw_ucinco'])
    print("corr weight ucuatro :", corwdict['corw_ucuatro'])    
    print("corr weight ugg :", corwdict['corw_ugg'])
    print("corr weight ug :", corwdict['corw_ug'])
    print("corr weight yday :", corwdict['corw_d1'])
    
    for dti in tqdm(df_ptn.index):
        #corr data 쌓기. pearsonr은 (coeff, p-value)튜플을 리턴하므로 [0]으로 coeff만 취함
        corr_ucinco = stats.pearsonr(df_ptn.loc[today,'ucinco'], df_ptn.loc[dti,'ucinco'])[0]
        corr_ucuatro = stats.pearsonr(df_ptn.loc[today,'ucuatro'], df_ptn.loc[dti,'ucuatro'])[0]
        corr_ugg = stats.pearsonr(df_ptn.loc[today,'ugg'], df_ptn.loc[dti,'ugg'])[0]
        corr_ug = stats.pearsonr(df_ptn.loc[today,'ug'], df_ptn.loc[dti,'ug'])[0]
        corr_d1 = stats.pearsonr(df_ptn.loc[today,'d1'], df_ptn.loc[dti,'d1'])[0]
        list_corr = [corr_ucinco, corr_ucuatro, corr_ugg, corr_ug, corr_d1]
        
        corr_wavg = sum([a*b for a,b in zip(list_corr_weight, list_corr)])
        
        #stdev data 쌓기
        stdev_ucinco = np.std(df_ptn.loc[dti, 'ucinco'])
        stdev_ucinco_diff = abs(stdev_ucinco_today - stdev_ucinco)
        
        #Z-score data 쌓기
        si = max(zwindow, sjunil.index.get_loc(dti)) #junil indexing out of range방지
        zl = sjunil[si-zwindow+1:si+1]
        zscore_junil = stats.zscore(zl)[-1].item()
        zscore_junil_diff = abs(zscore_junil_today - zscore_junil)
        
        #sum of distance data 쌓기
        sumsq_ucinco = sum_of_subtract_square(df_ptn.loc[today,'ucinco'], df_ptn.loc[dti,'ucinco'])
        sumsq_ucuatro = sum_of_subtract_square(df_ptn.loc[today,'ucuatro'], df_ptn.loc[dti,'ucuatro'])
        sumsq_ugg = sum_of_subtract_square(df_ptn.loc[today,'ugg'], df_ptn.loc[dti,'ugg'])
        sumsq_ug = sum_of_subtract_square(df_ptn.loc[today,'ug'], df_ptn.loc[dti,'ug'])
        sumsq_d1 = sum_of_subtract_square(df_ptn.loc[today,'d1'], df_ptn.loc[dti,'d1'])
        list_sumsq = [sumsq_ucinco, sumsq_ucuatro, sumsq_ugg, sumsq_ug, sumsq_d1]
        
        sumsq_wavg = sum([a*b for a,b in zip(list_corr_weight, list_sumsq)])
        
#        df_ptn.at[dti, 'corr_ugg'] = corr_ugg
#        df_ptn.at[dti, 'corr_ug'] = corr_ug 
#        df_ptn.at[dti, 'corr_d1'] = corr_d1
        df_ptn.at[dti, 'corr_wavg'] = corr_wavg
        df_ptn.at[dti, 'stdev_ucinco_diff'] = stdev_ucinco_diff
#        df_ptn.at[dti, 'mean_ugg_diff'] = mean_ugg_diff
        df_ptn.at[dti, 'zscore'] = zscore_junil
        df_ptn.at[dti, 'zscore_diff'] = zscore_junil_diff
        df_ptn.at[dti, 'sumsq_wavg'] = sumsq_wavg
  
    """end of for loop"""
    
    print("ranking...")
#        df_ptn.loc[d, 'start_diff'] = abs(df_ptn.loc[today, 'ugg'][0]-df_ptn.loc[d, 'ugg'][0])
#        df_ptn.loc[d, 'hi_diff'] = abs(max(df_ptn.loc[today, 'ugg'])-max(df_ptn.loc[d, 'ugg']))
#        df_ptn.loc[d, 'lo_diff'] = abs(min(df_ptn.loc[today, 'ugg'])-min(df_ptn.loc[d, 'ugg']))
#        stdev captures all but corr!!!
        
# =============================================================================
#     Find final simil_rank based on base ranks
# =============================================================================
    df_ptn['zscore_rank'] = df_ptn['zscore_diff'].rank(ascending=True) 
    zscore_cutoff = max(df_ptn['zscore_rank'])*zscore_co_rate # 1.0일 경우 cutoff없음
    df_ptn = df_ptn.loc[df_ptn['zscore_rank'] < zscore_cutoff, :]

    df_ptn['std_rank'] = df_ptn['stdev_ucinco_diff'].rank(ascending=True) #남은것중 랭킹
    std_cutoff = max(df_ptn['std_rank'])*std_co_rate # 1.0일 경우 cutoff 없음
    df_ptn = df_ptn.loc[df_ptn['std_rank'] < std_cutoff, :]
    
#    df_ptn['mean_rank'] = df_ptn['mean_ugg_diff'].rank(ascending=True) 
#    mean_cutoff = len(df_ptn)*1 # 1.0일 경우 cutoff없음
#    df_ptn = df_ptn.loc[df_ptn['mean_rank'] < mean_cutoff, :]
    
#    df_ptn['simil_rank'] = df_ptn['corr_wavg'].rank(ascending=False) #corr avg기준 랭킹
    df_ptn['simil_rank'] = df_ptn['sumsq_wavg'].rank(ascending=True) #corr avg기준 랭킹

    print("analysis completed")
    
    return df_ptn
    """End of dfptn function"""


def mktdata_timeunit(dfmkt=DataFrame):
    """
    returns minutes timedelta of intraday mkt data
    """
    datetimeA = datetime.datetime.combine(datetime.date.today(), dfmkt['시간'][0])
    datetimeB = datetime.datetime.combine(datetime.date.today(), dfmkt['시간'][1])
    datetimeDifference = datetimeB - datetimeA
    datetimeDifferenceInMinutes = datetimeDifference.total_seconds() / 60
    return datetimeDifferenceInMinutes

        
def mktdata_tilnow(dfmkt=DataFrame, country = 'KR', giventime=None):
    """ 
    Split intraday market data until current time
    ex) datetime.time(11, 35) or 11:35am
    This function eliminates mkt data after 11:35am+timeunit for all days 
    """
    if giventime == None:
        nowdatetime = datetime.datetime.now()
    elif type(giventime) == datetime.datetime:
        nowdatetime = giventime
    else :
        print("Wrong type of given time")
    
    print("Market time : ", nowdatetime)
    
    if country == 'US':
        nowdatetime = nowdatetime + datetime.timedelta(hours = -8)
    print("Converted market time : ", nowdatetime)
    
    timeunit = mktdata_timeunit(dfmkt)
    nowdatetime_plus_timeunit = nowdatetime + datetime.timedelta(minutes = timeunit)
    cutofftime = nowdatetime_plus_timeunit.time()
    print("Cutoff time : ", cutofftime, "\n")
    
    dfmkt_tilnow = dfmkt.loc[ dfmkt['시간'] < cutofftime, : ]
    
    return dfmkt_tilnow



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""Dynamic PR"""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def prdyna(df, today=pd.Timestamp, zscore_co_rate=0.15, std_co_rate=0.5,
           corwdict_input=None, country='KR', gvntime=None):
    """
    과거 N일 + 당일 현재까지 진행경로를 Pattern Matching.
    dakamatsu version과는 다르게 당일 현재시간까지를 과거data에도 적용.
    
    Parameters
    -----------
    df : market data
    ...
    country : country of market --> different now relative to country
    gvntime : use only when specfied time needed
    
    """
    print("Let's see what history shows!\n")
       
    standard_len = du.standard_length_of_day(df)
    print("Standard datanum of a day: ", standard_len)
    
    #전일종가 Dict, Series
    junil = du.get_junil_jongga_dict(df)
    sjunil = Series(junil)

    df_ptn = pd.DataFrame(
            columns=['d1', #path of y'day + today til now
                     'ucinco', #path of past 5 days + today til now 
                     'ucuatro', #path of past 4 days + today til now
                     'ugg', #path of past 3 days + today til now
                     'ug', #path of past 2 days + today til now
                     'd0', #path of today til now
                     ] 
            )
    
# =============================================================================
#     Building daily consecutive patterns for ref data
# =============================================================================
        
    ld = du.get_date_list(df)
    print("\nAnalysis of ", len(ld), " days")
    
    dftilnow = mktdata_tilnow(df, country, gvntime)
    
    for d0, d1, d2, d3, d4, d5 in tqdm(zip(ld[5:], ld[4:],
                                           ld[3:], ld[2:], 
                                           ld[1:], ld), desc="Accumulating data"):
        #d0 = pattern중 당일
        ref = round(junil[d0],2)
        ptn_d0 = list(); ptn_d1 = list(); ptn_d2 = list(); ptn_d3 = list()
        ptn_d4 = list(); ptn_d5 = list()
        ptn_dn = list()

        #tilnow를 아래의 d0에 넣었음
        for prc in dftilnow[d0:d0]['종가']:
            ptn_d0.append(100*round(prc-ref,2))
            
        for prc in df[d1:d1]['종가']:
            ptn_d1.append(100*round(prc-ref,2))
        for prc in df[d2:d2]['종가']:
            ptn_d2.append(100*round(prc-ref,2))
        for prc in df[d3:d3]['종가']:
            ptn_d3.append(100*round(prc-ref,2))
        for prc in df[d4:d4]['종가']:
            ptn_d4.append(100*round(prc-ref,2))
        for prc in df[d5:d5]['종가']:
            ptn_d5.append(100*round(prc-ref,2))
        if d0 != today: 
            dn = ld[ld.index(d0)+1] #d0다음날
            for prc in df[dn:dn]['종가']:
                ptn_dn.append(100*round(prc-ref,2))
        
        df_ptn.at[d0, 'd0'] = ptn_d0
        df_ptn.at[d0, 'd1'] = ptn_d1 + ptn_d0
        df_ptn.at[d0, 'ug'] = ptn_d2 + ptn_d1 + ptn_d0
        df_ptn.at[d0, 'ugg'] = ptn_d3 + ptn_d2 + ptn_d1 + ptn_d0
        df_ptn.at[d0, 'ucuatro'] = ptn_d4 + ptn_d3 + ptn_d2 + ptn_d1 + ptn_d0
        df_ptn.at[d0, 'ucinco'] = ptn_d5 + ptn_d4 + ptn_d3 + ptn_d2 + ptn_d1 + ptn_d0

# =============================================================================
#     Building daily ref data for simil_rank 
# =============================================================================

    """today의 ucinco std를 구해서 추후 loop에서 비교 """
    stdev_ucinco_today = np.std(df_ptn.loc[today, 'ucinco'])    

    """today의 zs를 미리 구해서 추후 loop에서 비교"""
    zwindow = 20
    print("\nzs window:", zwindow)

    si_today = max(zwindow, sjunil.index.get_loc(today)) 
    #junil indexing out of range방지. 즉, 최초일+zwindow보다는 큰 날짜를 indexing
    
    zl_today = sjunil[si_today-zwindow+1:si_today+1] 
    #slicing은 해당loc의 앞에서 끊으므로 +1이 필요. 
    #datetimeindex of Series preferred considering readability
    
    zscore_junil_today = stats.zscore(zl_today)[-1]
    
    """아래에서 ugg ug dq(=uje=yday)의 각 corr의 weight를 정함"""
    if corwdict_input == None:
        corwdict = {'corw_ucinco':0, 
                    'corw_ucuatro':0,
                    'corw_ugg':0,
                    'corw_ug':0.5,
                    'corw_d1':0.2,
                    'corw_d0':0.3}
    else: corwdict = corwdict_input
    
    list_corr_weight = list(corwdict.values())
    
    print("weight ucinco :", corwdict['corw_ucinco'])
    print("weight ucuatro :", corwdict['corw_ucuatro'])    
    print("weight ugg :", corwdict['corw_ugg'])
    print("weight ug :", corwdict['corw_ug'])
    print("weight yday :", corwdict['corw_d1'])
    print("weight tday til now :", corwdict['corw_d0'], "\n")
    
#    for dti in df_ptn.index:
#        if len(df_ptn.loc[today,'ucinco']) != len(df_ptn.loc[dti,'ucinco']):
#            print("ucinco", today, len(df_ptn.loc[today,'ucinco']),dti, len(df_ptn.loc[dti,'ucinco']))
#            
#    for dti in df_ptn.index:
#        if len(df_ptn.loc[today,'ugg']) != len(df_ptn.loc[dti,'ugg']):
#            print("ugg", today, len(df_ptn.loc[today,'ugg']),dti, len(df_ptn.loc[dti,'ugg']))
#            

    for dti in tqdm(df_ptn.index, desc = "Analyzing data", mininterval=0.2):
        #corr data 쌓기. pearsonr은 (coeff, p-value)튜플을 리턴하므로 [0]으로 coeff만 취함
        corr_ucinco = stats.pearsonr(df_ptn.loc[today,'ucinco'], df_ptn.loc[dti,'ucinco'])[0]
        corr_ucuatro = stats.pearsonr(df_ptn.loc[today,'ucuatro'], df_ptn.loc[dti,'ucuatro'])[0]
        corr_ugg = stats.pearsonr(df_ptn.loc[today,'ugg'], df_ptn.loc[dti,'ugg'])[0]
        corr_ug = stats.pearsonr(df_ptn.loc[today,'ug'], df_ptn.loc[dti,'ug'])[0]
        corr_d1 = stats.pearsonr(df_ptn.loc[today,'d1'], df_ptn.loc[dti,'d1'])[0]
        corr_d0 = stats.pearsonr(df_ptn.loc[today,'d0'], df_ptn.loc[dti,'d0'])[0]

        list_corr = [corr_ucinco, corr_ucuatro, corr_ugg, corr_ug, corr_d1, corr_d0]
        
        corr_wavg = sum([a*b for a,b in zip(list_corr_weight, list_corr)])
        
        #stdev data 쌓기
        stdev_ucinco = np.std(df_ptn.loc[dti, 'ucinco'])
        stdev_ucinco_diff = abs(stdev_ucinco_today - stdev_ucinco)
        
        #Z-score data 쌓기
        si = max(zwindow, sjunil.index.get_loc(dti)) #junil indexing out of range방지
        zl = sjunil[si-zwindow+1:si+1]
        zscore_junil = stats.zscore(zl)[-1].item()
        zscore_junil_diff = abs(zscore_junil_today - zscore_junil)
        
        #sum of distance data 쌓기
        sumsq_ucinco = sum_of_subtract_square(df_ptn.loc[today,'ucinco'], 
                                                 df_ptn.loc[dti,'ucinco'])
        sumsq_ucuatro = sum_of_subtract_square(df_ptn.loc[today,'ucuatro'], 
                                                  df_ptn.loc[dti,'ucuatro'])
        sumsq_ugg = sum_of_subtract_square(df_ptn.loc[today,'ugg'], 
                                              df_ptn.loc[dti,'ugg'])
        sumsq_ug = sum_of_subtract_square(df_ptn.loc[today,'ug'], 
                                             df_ptn.loc[dti,'ug'])
        sumsq_d1 = sum_of_subtract_square(df_ptn.loc[today,'d1'], 
                                             df_ptn.loc[dti,'d1'])
        sumsq_d0 = sum_of_subtract_square(df_ptn.loc[today,'d0'], 
                                             df_ptn.loc[dti,'d0'])
        sumsq_d0_adj = sumsq_d0 * standard_len / len(df_ptn.loc[today,'d0'])
        
        list_sumsq = [
                sumsq_ucinco, 
                sumsq_ucuatro, 
                sumsq_ugg, 
                sumsq_ug, 
                sumsq_d1,
                sumsq_d0_adj
                ]
        
        sumsq_wavg = sum([a*b for a,b in zip(list_corr_weight, list_sumsq)])
        
        df_ptn.at[dti, 'corr_wavg'] = corr_wavg
        df_ptn.at[dti, 'stdev_ucinco_diff'] = stdev_ucinco_diff
        df_ptn.at[dti, 'zscore'] = zscore_junil
        df_ptn.at[dti, 'zscore_diff'] = zscore_junil_diff
        df_ptn.at[dti, 'sumsq_wavg'] = sumsq_wavg        
        
    """end of for loop"""
    
    print("ranking...")
        
# =============================================================================
#     Find final simil_rank based on base ranks
# =============================================================================
    df_ptn['zscore_rank'] = df_ptn['zscore_diff'].rank(ascending=True) 
    zscore_cutoff = max(df_ptn['zscore_rank'])*zscore_co_rate # 1.0일 경우 cutoff없음
    df_ptn = df_ptn.loc[df_ptn['zscore_rank'] < zscore_cutoff, :]

    df_ptn['std_rank'] = df_ptn['stdev_ucinco_diff'].rank(ascending=True) #남은것중 랭킹
    std_cutoff = max(df_ptn['std_rank'])*std_co_rate # 1.0일 경우 cutoff 없음
    df_ptn = df_ptn.loc[df_ptn['std_rank'] < std_cutoff, :]
    
#    df_ptn['mean_rank'] = df_ptn['mean_ugg_diff'].rank(ascending=True) 
#    mean_cutoff = len(df_ptn)*1 # 1.0일 경우 cutoff없음
#    df_ptn = df_ptn.loc[df_ptn['mean_rank'] < mean_cutoff, :]
    
#    df_ptn['simil_rank'] = df_ptn['corr_wavg'].rank(ascending=False) #corr avg기준 랭킹
    df_ptn['simil_rank'] = df_ptn['sumsq_wavg'].rank(ascending=True) #corr avg기준 랭킹

    print("analysis completed")
    
    return df_ptn
    """End of dfptn function"""

def sum_of_subtract_square(lx=list, ly=list):
    """return sum of square of subtracted two lists"""
    if len(lx) != len(ly):
        print("Different length of lists")
    
    arr = np.subtract(lx, ly)
#    return np.sum(arr**2) #급히 튄 가격 잡을때 활용
    return np.sqrt(np.sum(arr**2)) #일반적 경우에 활용

def simil_event_filtered(ld_all, dfptn, eventdate, NUMPLOTS=11):
    """
    Return list of dates of simil from dfptn given list of dates.
    List of dates can be dates of events (e.g. BOKMPC, FOMC, NFP) or any.
    
    Parameters
    -----------
    dfptn : df of prdyna or pr_dakamatsu
    eventdates : list of dates of interest   
    """
    ld_ptn = datelist_from_dfptn(ld_all, dfptn, 1000)
    set_eventdate = set(eventdate)
    simil_event_date = [x for x in ld_ptn if x in set_eventdate]
    simil_event_date = simil_event_date[:NUMPLOTS+1]
        
    return simil_event_date
    

def get_candle(ld_all, 
             dfmkt=DataFrame, 
             day=pd.Timestamp, 
             candle_start_offset = 0,
             net_chg_adj = "Y"
             ):
    """
    Return OHLC dictionary of a given date
    
    parameters
    -----------
    dfmkt : Dataframe of market data with '일자' and '시간' columns
    day : pd.Timestamp date OHLC dictionary needed
    candle_start_offset : e.g. -2 meaning D-2, D-1, D-0 in one candle
    net_chg_adj : "Y" converts absolute values into 1-day net change values
    
    """
    day_past = du.date_offset(ld_all, day, candle_start_offset)
    
    if candle_start_offset > 0:
        raise Exception('잘못된 candle offset')
    else: dfday = dfmkt[day_past:day]
    
    open_prc = round(dfday.iloc[0]['종가'], 2)
    close_prc = round(dfday.iloc[-1]['종가'], 2)
    high_prc = round(max(dfday['종가']), 2)
    low_prc = round(min(dfday['종가']), 2)
    
    candle = {
            'open': open_prc,
            'high': high_prc,
            'low': low_prc,
            'close': close_prc,
            'top_tail': round(high_prc - max(open_prc, close_prc), 2),
            'bottom_tail': round(min(open_prc, close_prc) - low_prc, 2),
            'body': round(close_prc - open_prc, 2),
            'net_chg': 0,
            'start_day' : day_past,
            'end_day' : day
            }
    
    if net_chg_adj == "Y":
        #candle시작일의 전일종가대비 가격변화로 변경
        ref_prc = du.juniljongga(ld_all, dfmkt, day_past)
        for key, value in candle.items():
            if key in ['open', 'high', 'low', 'close']:
                candle[key] = round(value - ref_prc, 2)
        candle['net_chg'] = round(close_prc - ref_prc, 2)
            
    return candle


def fcast_multly(df_mkt, ld_plot, next_num, sectype='yield'):
    """
    각 날짜들의 forecast horizon에 따른 end price를 구하고
    end price list의 결과값 summary를 return
    ------------------------------------------------
    Parameters
        df_mkt : market data
        ld_plot : dates of similarity
        next_num : forecast horizon
    Returns: result dictionary
    """

    ld_total = du.get_date_list(df_mkt)
    endprc_list = []
    total_prc_list = []
    # sharpe_list = []
    
    for day in ld_plot:
        ref_prc = du.juniljongga(ld_total, df_mkt, day)
        tl = np.array(list_consec_days(ld_total, df_mkt, day, ref_prc, 0, next_num, sectype))
        endprc = round(tl[-1], 2)
        endprc_list.append(endprc)
        
        total_prc_list += list(tl)
        
        # chg_arr = np.diff(tl)
        # sharpe = np.mean(chg_arr) / np.std(chg_arr)
        # sharpe_list.append(sharpe)
        # end of loop

    crnt_prc = 0 #과거자료 fcast할때 crnt prc 무시하기위해
    endprc_arr_adj = np.array(endprc_list) - crnt_prc
    
    mean_end_prc = round(statistics.mean(endprc_arr_adj), 1)
    #mean of end price
    stdev_end_prc = round(statistics.stdev(endprc_arr_adj),1)
    #std of end price
    ms_ratio = round(mean_end_prc/stdev_end_prc,2)
    #mean std ratio
    
    num_positive_value = sum(x > 0 for x in endprc_arr_adj)
    num_total_case = len(endprc_arr_adj)
    odds_of_up = round(num_positive_value / num_total_case, 2)
    #odds of positive value in !!!end!!! prices
    
    num_total_point = len(total_prc_list)
    positives = sum([x > 0 for x in total_prc_list])
    # num_major = max(positives, num_total_point - positives)
    bias_ratio = round(positives / num_total_point, 2)
    
    # sharpe_avg = round(np.mean(sharpe_list), 3)
    #average of sharpe raios from each series
    
    return {'mean': mean_end_prc, 
            'std': stdev_end_prc, 
            'm/s': ms_ratio,
            'odds_up': odds_of_up,
            'bias_ratio': bias_ratio,
            # 'sharpe_avg': sharpe_avg
            }

def comp_candle_way(ld_all, 
                    dfmkt, 
                    refday, 
                    compday,
                    candle_start_offset
                   ):
    """
    Return dictionary of distance of OHLC data
    parameters
    -----------
    dfmkt : Dataframe of market data with '일자' and '시간' columns
    refday : day of interest, usually current day
    compday : day of comparison, usually past day
    """
    candle_start_offset = -2

    candle_ref = get_candle(ld_all, dfmkt, refday, candle_start_offset)
    candle_comp = get_candle(ld_all, dfmkt, compday, candle_start_offset)

    distance = {}
    for component in ['top_tail', 'bottom_tail', 'body', 'net_chg']:
        distance[component] = (candle_ref[component] - candle_comp[component])**2
        
    return distance
    
def prcandle():
    
    pass


def build_df_tobefiltered(pos, df_daily_all, test_years = 5):

    from loadmkt import get_dfint_daily
    
    tday = datetime.datetime.now() + datetime.timedelta(days=10) 
    
    test_since = tday - datetime.timedelta(days=test_years*365) 
    
    diff_days = [1,2,3,4,5,7,10,15,20, -1,-2,-3,-4,-5]
        
    df = get_dfint_daily(df_daily_all, pos)
    df = df[test_since:tday]
    
    for n in diff_days:
        if n >= 0:
            col_name = str(n)+'d_chg'
            df[col_name] = 100*df.종가.diff(periods=n)
        if n < 0:
            col_name = 'next_'+str(-n)+'d_chg'
            df[col_name] = -100*df.종가.diff(periods=n)
    
    # df = df.dropna()
    
    return df

def simil_find_daily(dfint, today, numplot = 10):
    """
    Find simil days from dfint [build_df_tobefiltered]
    Compare 2d_chg, 5d_chg, 10d_chg, 20d_chg using equally weighted sqrt

    Parameters
    ----------
    dfint : DataFrame containg n-day changes
        
    Returns
    -------
    list of days 

    """
    
    df = pd.DataFrame(index = [day for day in dfint.index if day <= today],
                      columns=['changes', 'diff', 'simil_rank'])
    
    chg_comp_windows = [1,2,5,10,15,20]
    ref_changes = np.array([])
    
    for n in chg_comp_windows:
        ref_changes = np.append(ref_changes, dfint.loc[today][str(n)+'d_chg'])
        
    for day in tqdm(df.index):
        day_changes = np.array([])
        for n in chg_comp_windows:
            day_changes = np.append(day_changes, dfint.loc[day][str(n)+'d_chg'])
        df.loc[day]['diff'] = np.sum((np.subtract(ref_changes, day_changes))**2)
                
    df['simil_rank'] = df['diff'].rank(ascending=True)
    
    df_trimmed = df[df['simil_rank'] <= numplot]
    df_trimmed = df_trimmed.sort_values(by=['simil_rank'])
    
    return list(df_trimmed.index)
    

def sharpe_daily(dfmkt, refday, ent, ext, normalize_to=20):
    """
    ext - ent > 3
    """
    horizon = ext - ent
    
    if horizon < 5:
        return 0
    
    else: 
        ld_all = list(dfmkt.index)
        entday = du.date_offset(ld_all, refday, ent)
        extday = du.date_offset(ld_all, refday, ext)
        arr = np.array(dfmkt[entday:extday]['종가'].diff().dropna())
        sr = arr.mean() / arr.std()
        norm_coeff = normalize_to / len(arr)
        sr_norm = sr * norm_coeff / np.sqrt(norm_coeff)
        print(entday, extday, sr, sr_norm)
        print(arr, arr.sum())
        
        return sr_norm
