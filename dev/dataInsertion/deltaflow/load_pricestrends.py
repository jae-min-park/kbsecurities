import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pymysql
from tqdm import tqdm
from datetime import datetime

font_path = "C:\Windows\Fonts\\batang.ttc"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)


test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='deltaflow',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)


"""데이터 가져오기"""
def setDfData(date_start, date_end, table, skip_datetime_col="N") :
    sql = "SELECT * FROM "+ table +" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + " ';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    df = pd.DataFrame(result)
    return df


""" 조회화면 값 입력하는 반복하여 호출되는 유틸성 함수 """
def getResultTable(df, set_df, treasury_result_df, start_date, end_date, asset) :
    tmp = set_df[set_df['연물분류']==asset]
    joined = pd.merge(treasury_result_df, tmp, left_on='종목코드', right_on='종목코드')
    bools =[]
    for i in joined.index:
        if joined.iloc[i]['date'] >=start_date and joined.iloc[i]['date']<=end_date:
            bools.append(True)
        else:
            bools.append(False)
    tmp_joined = joined[bools]
    if tmp_joined.empty :
        return df
    df.loc[asset,'외국인'] = round(np.sum(tmp_joined['외국인 순매수 거래량'] * tmp_joined['델타'])/10**12,2)
    df.loc[asset,'투신'] = round(np.sum(tmp_joined['자산운용(공모) 순매수 거래량'] * tmp_joined['델타'])/10**12,2)
    df.loc[asset,'보험기금'] = round(np.sum(tmp_joined['보험기금 순매수 거래량'] * tmp_joined['델타'])/10**12,2)
    df.loc[asset,'은행'] = round(np.sum(tmp_joined['은행 순매수 거래량'] * tmp_joined['델타'])/10**12,2)
    df.loc[asset,'증권'] = round(np.sum(tmp_joined['증권순매수(원)'] * tmp_joined['델타'])/10**12,2)
    df.loc[asset,'상장'] = round(np.sum(tmp_joined['낙찰금액'] * tmp_joined['델타'])/10**12,2)
    # df.loc[asset,'상장'] = round(np.sum(tmp_joined['상장잔액증감(원)'] * tmp_joined['델타'])/10**12,2)
    return df

"""현재 사용하지는 않는 함수"""
def showPricesTrend(last_df, start_date, end_date, opt = '은증') :
    # treasury_result_df = setDfData(start_date, end_date,'treasury_vol')[::-1]
    # set_df = setDfData('2021-07-26', '2021-07-26','setting_delta').drop('date',axis=1)
    # future_df = setDfData('2021-07-26', '2021-07-26','futures_bpv')[::-1]
    df3f = setDfData(start_date, end_date,'ktbf3y_vol')[::-1]
    # df10f = setDfData(start_date, end_date,'ktbf10y_vol')[::-1]
    
    df3f.set_index('date', inplace=True)
    # df10f.set_index('date', inplace=True)
    
    datelist = list(df3f.index)
    
    move_date = start_date
    while move_date <= end_date :
        if move_date not in datelist :
            move_date += pd.Timedelta(days=1)
            continue
        """ // set_df : 설정 // future_df : 선물 bpv // treasury_result_df : 국고 // df3f, df10f : 선물 """
        set_df = setDfData(str(datetime.today())[:10], str(datetime.today())[:10],'setting_delta').drop('date',axis=1)
        future_df = setDfData(str(datetime.today())[:10], str(datetime.today())[:10],'futures_bpv')
        treasury_result_df = setDfData(start_date, move_date,'treasury_vol')
        df3f = setDfData(start_date, move_date,'ktbf3y_vol')[::-1]
        df10f = setDfData(start_date, move_date,'ktbf10y_vol')[::-1]
        df3f.set_index('date', inplace=True)
        df10f.set_index('date', inplace=True)
        
        cols = ['외국인','투신','보험기금','은행','증권','상장']
        idx = ['2Y','3Y','3선','5Y','7Y','10Y','10선','물가','15Y','20Y','20원금','30Y','30원금','50Y','50원금','합계']
        df = pd.DataFrame(columns=cols,index=idx)
        df.fillna(0,inplace=True)
        
        
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'2Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'3Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'5Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'7Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'10Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'15Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'20Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'30Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'50Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'물가')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'20원금')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'30원금')
        df = getResultTable(df,set_df, treasury_result_df, start_date, end_date,'50원금')
        
        df.loc['3선','외국인'] = round(sum(df3f.loc[move_date:start_date, '외국인'] * future_df.iloc[0]['bpv']/10000),2)
        df.loc['3선','투신'] = round(sum(df3f.loc[move_date:start_date, '투신'] * future_df.iloc[0]['bpv']/10000),2)
        df.loc['3선','보험기금'] = round(sum(df3f.loc[move_date:start_date, '보험기금'] * future_df.iloc[0]['bpv']/10000),2)
        df.loc['3선','은행'] = round(sum(df3f.loc[move_date:start_date, '은행'] * future_df.iloc[0]['bpv']/10000),2)
        df.loc['3선','증권'] = round(sum(df3f.loc[move_date:start_date, '증권'] * future_df.iloc[0]['bpv']/10000),2)
        # df.loc['3선','상장'] = sum(df3f.loc[end_ date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
        df.loc['10선','외국인'] = round(sum(df10f.loc[move_date:start_date, '외국인'] * future_df.iloc[1]['bpv']/10000),2)
        df.loc['10선','투신'] = round(sum(df10f.loc[move_date:start_date, '투신'] * future_df.iloc[1]['bpv']/10000),2)
        df.loc['10선','보험기금'] = round(sum(df10f.loc[move_date:start_date, '보험기금'] * future_df.iloc[1]['bpv']/10000),2)
        df.loc['10선','은행'] = round(sum(df10f.loc[move_date:start_date, '은행'] * future_df.iloc[1]['bpv']/10000),2)
        df.loc['10선','증권'] = round(sum(df10f.loc[move_date:start_date, '증권'] * future_df.iloc[1]['bpv']/10000),2)
        # df.loc['3선','상장'] = sum(df3f.loc[end_date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
        
        df.loc['합계','외국인'] = sum(df.loc[:'50원금','외국인'])
        df.loc['합계','투신'] = sum(df.loc[:'50원금','투신'])
        df.loc['합계','보험기금'] = sum(df.loc[:'50원금','보험기금'])
        df.loc['합계','은행'] = sum(df.loc[:'50원금','은행'])
        df.loc['합계','증권'] = sum(df.loc[:'50원금','증권'])
        df.loc['합계','상장'] = sum(df.loc[:'50원금','상장'])
        
        
        """요약본 테이블"""
        cols = ['외인','투신','은증']
        idx = ['2년이하','3년','5년','7년','10년','15년~20년','30년이상']
        summary_df = pd.DataFrame(columns=cols,index=idx)
        summary_df.fillna(0,inplace=True)
        
        summary_df.loc['2년이하', '외인'] = df.loc['2Y','외국인']
        summary_df.loc['3년', '외인'] = df.loc['3Y','외국인']+df.loc['3선','외국인']
        summary_df.loc['5년', '외인'] = df.loc['5Y','외국인']
        summary_df.loc['7년', '외인'] = df.loc['7Y','외국인']
        summary_df.loc['10년', '외인'] = df.loc['10Y','외국인']+df.loc['10선','외국인']
        summary_df.loc['15년~20년', '외인'] = df.loc['15Y','외국인']+df.loc['20Y','외국인']+df.loc['20원금','외국인']
        summary_df.loc['30년이상', '외인'] = df.loc['30Y','외국인']+df.loc['50Y','외국인']+df.loc['30원금','외국인']+df.loc['50원금','외국인']
        
        summary_df.loc['2년이하', '투신'] = df.loc['2Y','보험기금']
        summary_df.loc['3년', '투신'] = df.loc['3Y','보험기금']+df.loc['3선','보험기금']
        summary_df.loc['5년', '투신'] = df.loc['5Y','보험기금']
        summary_df.loc['7년', '투신'] = df.loc['7Y','보험기금']
        summary_df.loc['10년', '투신'] = df.loc['10Y','보험기금']+df.loc['10선','보험기금']
        summary_df.loc['15년~20년', '투신'] = df.loc['15Y','보험기금']+df.loc['20Y','보험기금']+df.loc['20원금','보험기금']
        summary_df.loc['30년이상', '투신'] = df.loc['30Y','보험기금']+df.loc['50Y','보험기금']+df.loc['30원금','보험기금']+df.loc['50원금','보험기금']
        
        summary_df.loc['2년이하', '은증'] = df.loc['2Y','은행']+df.loc['2Y','증권']
        summary_df.loc['3년', '은증'] = df.loc['3Y','은행']+df.loc['3선','은행'] + df.loc['3Y','증권']+df.loc['3선','증권']
        summary_df.loc['5년', '은증'] = df.loc['5Y','은행'] + df.loc['5Y','증권']
        summary_df.loc['7년', '은증'] = df.loc['7Y','은행'] + df.loc['7Y','증권']
        summary_df.loc['10년', '은증'] = df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']
        summary_df.loc['15년~20년', '은증'] = df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']
        summary_df.loc['30년이상', '은증'] = df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']
    
        # summary_df.loc['2년이하', '은증'] = df.loc['2Y','은행']+df.loc['2Y','증권']
        # summary_df.loc['3년', '은증'] = df.loc['3Y','은행']+df.loc['3선','은행'] + df.loc['3Y','증권']+df.loc['3선','증권']
        # summary_df.loc['5년', '은증'] = df.loc['5Y','은행'] + df.loc['5Y','증권']
        # summary_df.loc['7년', '은증'] = df.loc['7Y','은행'] + df.loc['7Y','증권']
        # summary_df.loc['10년', '은증'] = df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']
        # summary_df.loc['15년~20년', '은증'] = df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']
        # summary_df.loc['30년이상', '은증'] = df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']
    
        if opt == '은증' :
            last_df.loc[move_date,'3선'] = df.loc['3선','은행'] + df.loc['3선','증권']
            last_df.loc[move_date,'3년'] = summary_df.loc['3년', '은증'] - last_df.loc[move_date,'3선']
            # last_df.loc[move_date,'3년'] = summary_df.loc['3년', '은증']
            last_df.loc[move_date,'5년'] = summary_df.loc['5년', '은증']
            last_df.loc[move_date,'7년'] = summary_df.loc['7년', '은증']
            last_df.loc[move_date,'10선'] = df.loc['10선','은행'] + df.loc['10선','증권']
            last_df.loc[move_date,'10년'] = summary_df.loc['10년', '은증'] - last_df.loc[move_date,'10선']
            # last_df.loc[move_date,'10년'] = summary_df.loc['10년', '은증']
            last_df.loc[move_date,'15년~20년'] = summary_df.loc['15년~20년', '은증']
            last_df.loc[move_date,'30년이상'] = summary_df.loc['30년이상', '은증']
        elif opt == '외국인':
            last_df.loc[move_date,'3선'] = df.loc['3선','외국인'] + df.loc['3선','외국인']
            last_df.loc[move_date,'3년'] = summary_df.loc['3년', '외인'] - last_df.loc[move_date,'3선']
            last_df.loc[move_date,'5년'] = summary_df.loc['5년', '외인']
            last_df.loc[move_date,'7년'] = summary_df.loc['7년', '외인']
            last_df.loc[move_date,'10선'] = df.loc['10선','외국인'] + df.loc['10선','외국인']
            last_df.loc[move_date,'10년'] = summary_df.loc['10년', '외인'] - last_df.loc[move_date,'10선']
            last_df.loc[move_date,'10년'] = summary_df.loc['10년', '외인']
            last_df.loc[move_date,'15년~20년'] = summary_df.loc['15년~20년', '외인']
            last_df.loc[move_date,'30년이상'] = summary_df.loc['30년이상', '외인']
            
        move_date += pd.Timedelta(days=1)
    
    tmp = last_df.iloc[0].copy()
    for i in last_df.index:
        last_df.loc[i] -= tmp
    # last_df = last_df.cumsum()
    ax = last_df.plot()
    ax.set_title(opt)
    ax.set_ylabel('억원')
    ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1,-0.5))
    # ax.legend(loc='best')


"""실제 사용중인 함수"""
def showPricesPerTenor (last_df, y30_list, target_dt, diff) :
    """30년입찰 최근제외 올해 일자들"""
    for date in y30_list :
        start_date = date - pd.Timedelta(days=31)
        end_date = date + pd.Timedelta(days=diff)
        df3f_1 = setDfData(start_date, date,'ktbf3y_vol').iloc[-13:]
        df3f_1.set_index('date', inplace=True)
        dti1 = list(df3f_1.index)
        
        df3f_2 = setDfData(date+pd.Timedelta(days=1), end_date,'ktbf3y_vol')
        df3f_2.set_index('date', inplace=True)
        dti2 = list(df3f_2.index)
        
        workdays = dti1+dti2
        num = len(workdays)
        move_date = workdays[0]
        end_date = workdays[-1]
        i = 0 
        while i < num :
            if move_date not in workdays :
                move_date += pd.Timedelta(days=1)
                continue
            """ // set_df : 설정 // future_df : 선물 bpv // treasury_result_df : 국고 // df3f, df10f : 선물 """
            set_df = setDfData(str(datetime.now())[:10], str(datetime.now())[:10],'setting_delta').drop('date',axis=1)
            future_df = setDfData(str(datetime.now())[:10], str(datetime.now())[:10],'futures_bpv')
            treasury_result_df = setDfData(start_date, move_date,'treasury_vol')
            df3f = setDfData(start_date, move_date,'ktbf3y_vol')[::-1]
            df10f = setDfData(start_date, move_date,'ktbf10y_vol')[::-1]
            df3f.set_index('date', inplace=True)
            df10f.set_index('date', inplace=True)
            
            cols = ['외국인','투신','보험기금','은행','증권','상장']
            idx = ['2Y','3Y','3선','5Y','7Y','10Y','10선','물가','15Y','20Y','20원금','30Y','30원금','50Y','50원금','합계']
            df = pd.DataFrame(columns=cols,index=idx)
            df.fillna(0,inplace=True)
            
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'2Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'3Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'5Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'7Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'10Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'15Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'20Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'30Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'50Y')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'물가')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'20원금')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'30원금')
            df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'50원금')
            
            # df.loc['3선','외국인'] = round(sum(df3f.loc[move_date:start_date, '외국인'] * future_df.iloc[0]['bpv']/10000),2)
            # df.loc['3선','투신'] = round(sum(df3f.loc[move_date:start_date, '투신'] * future_df.iloc[0]['bpv']/10000),2)
            # df.loc['3선','보험기금'] = round(sum(df3f.loc[move_date:start_date, '보험기금'] * future_df.iloc[0]['bpv']/10000),2)
            df.loc['3선','은행'] = round(sum(df3f.loc[move_date:start_date, '은행'] * future_df.iloc[0]['bpv']/10000),2)
            df.loc['3선','증권'] = round(sum(df3f.loc[move_date:start_date, '증권'] * future_df.iloc[0]['bpv']/10000),2)
            # df.loc['3선','상장'] = sum(df3f.loc[end_ date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
            # df.loc['10선','외국인'] = round(sum(df10f.loc[move_date:start_date, '외국인'] * future_df.iloc[1]['bpv']/10000),2)
            # df.loc['10선','투신'] = round(sum(df10f.loc[move_date:start_date, '투신'] * future_df.iloc[1]['bpv']/10000),2)
            # df.loc['10선','보험기금'] = round(sum(df10f.loc[move_date:start_date, '보험기금'] * future_df.iloc[1]['bpv']/10000),2)
            df.loc['10선','은행'] = round(sum(df10f.loc[move_date:start_date, '은행'] * future_df.iloc[1]['bpv']/10000),2)
            df.loc['10선','증권'] = round(sum(df10f.loc[move_date:start_date, '증권'] * future_df.iloc[1]['bpv']/10000),2)
            # df.loc['3선','상장'] = sum(df3f.loc[end_date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
            
            # df.loc['합계','외국인'] = sum(df.loc[:'50원금','외국인'])
            # df.loc['합계','투신'] = sum(df.loc[:'50원금','투신'])
            # df.loc['합계','보험기금'] = sum(df.loc[:'50원금','보험기금'])
            df.loc['합계','은행'] = sum(df.loc[:'50원금','은행'])
            df.loc['합계','증권'] = sum(df.loc[:'50원금','증권'])
            # df.loc['합계','상장'] = sum(df.loc[:'50원금','상장'])
            
            
            """요약본 테이블"""
            # cols = ['외인','투신','은증']
            cols = ['은증']
            idx = ['2년이하','3년','5년','7년','10년','15년~20년','30년이상']
            summary_df = pd.DataFrame(columns=cols,index=idx)
            summary_df.fillna(0,inplace=True)
            
            # summary_df.loc['2년이하', '외인'] = df.loc['2Y','외국인']
            # summary_df.loc['3년', '외인'] = df.loc['3Y','외국인']+df.loc['3선','외국인']
            # summary_df.loc['5년', '외인'] = df.loc['5Y','외국인']
            # summary_df.loc['7년', '외인'] = df.loc['7Y','외국인']
            # summary_df.loc['10년', '외인'] = df.loc['10Y','외국인']+df.loc['10선','외국인']
            # summary_df.loc['15년~20년', '외인'] = df.loc['15Y','외국인']+df.loc['20Y','외국인']+df.loc['20원금','외국인']
            # summary_df.loc['30년이상', '외인'] = df.loc['30Y','외국인']+df.loc['50Y','외국인']+df.loc['30원금','외국인']+df.loc['50원금','외국인']
            
            # summary_df.loc['2년이하', '투신'] = df.loc['2Y','보험기금']
            # summary_df.loc['3년', '투신'] = df.loc['3Y','보험기금']+df.loc['3선','보험기금']
            # summary_df.loc['5년', '투신'] = df.loc['5Y','보험기금']
            # summary_df.loc['7년', '투신'] = df.loc['7Y','보험기금']
            # summary_df.loc['10년', '투신'] = df.loc['10Y','보험기금']+df.loc['10선','보험기금']
            # summary_df.loc['15년~20년', '투신'] = df.loc['15Y','보험기금']+df.loc['20Y','보험기금']+df.loc['20원금','보험기금']
            # summary_df.loc['30년이상', '투신'] = df.loc['30Y','보험기금']+df.loc['50Y','보험기금']+df.loc['30원금','보험기금']+df.loc['50원금','보험기금']
            
            summary_df.loc['2년이하', '은증'] = df.loc['2Y','은행']+df.loc['2Y','증권']
            summary_df.loc['3년', '은증'] = df.loc['3Y','은행']+df.loc['3선','은행'] + df.loc['3Y','증권']+df.loc['3선','증권']
            summary_df.loc['5년', '은증'] = df.loc['5Y','은행'] + df.loc['5Y','증권']
            summary_df.loc['7년', '은증'] = df.loc['7Y','은행'] + df.loc['7Y','증권']
            summary_df.loc['10년', '은증'] = df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']
            summary_df.loc['15년~20년', '은증'] = df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']
            summary_df.loc['30년이상', '은증'] = df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']
        
            # summary_df.loc['2년이하', '은증'] = df.loc['2Y','은행']+df.loc['2Y','증권']
            # summary_df.loc['3년', '은증'] = df.loc['3Y','은행']+df.loc['3선','은행'] + df.loc['3Y','증권']+df.loc['3선','증권']
            # summary_df.loc['5년', '은증'] = df.loc['5Y','은행'] + df.loc['5Y','증권']
            # summary_df.loc['7년', '은증'] = df.loc['7Y','은행'] + df.loc['7Y','증권']
            # summary_df.loc['10년', '은증'] = df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']
            # summary_df.loc['15년~20년', '은증'] = df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']
            # summary_df.loc['30년이상', '은증'] = df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']
        
            # if opt == '은증' :
            last_df.loc[i,'3선_avg'] += (df.loc['3선','은행'] + df.loc['3선','증권'])
            last_df.loc[i,'3년_avg'] += (df.loc['3Y','은행'] + df.loc['3Y','증권'])
            # last_df.loc[i,'3년_avg'] += (summary_df.loc['3년', '은증'] - last_df.loc[i,'3선_avg'])
            # last_df.loc[move_date,'3년'] = summary_df.loc['3년', '은증']
            last_df.loc[i,'5년_avg'] += summary_df.loc['5년', '은증']
            last_df.loc[i,'7년_avg'] += summary_df.loc['7년', '은증']
            last_df.loc[i,'10선_avg'] += (df.loc['10선','은행'] + df.loc['10선','증권'])
            last_df.loc[i,'10년_avg'] += (df.loc['10Y','은행'] + df.loc['10Y','증권'])
            # last_df.loc[i,'10년_avg'] += (summary_df.loc['10년', '은증'] - last_df.loc[i,'10선_avg'])
            # last_df.loc[move_date,'10년'] = summary_df.loc['10년', '은증']
            last_df.loc[i,'15년~20년_avg'] += summary_df.loc['15년~20년', '은증']
            last_df.loc[i,'30년이상_avg'] += summary_df.loc['30년이상', '은증']
            
            last_df.loc[i,'10년미만_avg'] += (summary_df.loc['2년이하', '은증']+
                                           summary_df.loc['3년', '은증']+
                                           summary_df.loc['5년', '은증']+
                                           summary_df.loc['7년', '은증']
                                           )
            last_df.loc[i,'10년이상_avg'] += (summary_df.loc['10년', '은증']+
                                           summary_df.loc['15년~20년', '은증']+
                                           summary_df.loc['30년이상', '은증']
                                           )
            last_df.loc[i,'total_avg'] += (summary_df.loc['2년이하', '은증']+
                                           summary_df.loc['3년', '은증']+
                                           summary_df.loc['5년', '은증']+
                                           summary_df.loc['7년', '은증']+
                                           summary_df.loc['10년', '은증']+
                                           summary_df.loc['15년~20년', '은증']+
                                           summary_df.loc['30년이상', '은증']
                                           )
            # elif opt == '외국인':
            #     last_df.loc[move_date,'3선'] = df.loc['3선','외국인'] + df.loc['3선','외국인']
            #     last_df.loc[move_date,'3년'] = summary_df.loc['3년', '외인'] - last_df.loc[move_date,'3선']
            #     last_df.loc[move_date,'5년'] = summary_df.loc['5년', '외인']
            #     last_df.loc[move_date,'7년'] = summary_df.loc['7년', '외인']
            #     last_df.loc[move_date,'10선'] = df.loc['10선','외국인'] + df.loc['10선','외국인']
            #     last_df.loc[move_date,'10년'] = summary_df.loc['10년', '외인'] - last_df.loc[move_date,'10선']
            #     last_df.loc[move_date,'10년'] = summary_df.loc['10년', '외인']
            #     last_df.loc[move_date,'15년~20년'] = summary_df.loc['15년~20년', '외인']
            #     last_df.loc[move_date,'30년이상'] = summary_df.loc['30년이상', '외인']
                
            move_date += pd.Timedelta(days=1)
            i+=1
        
    """최근기준"""
    start_date = target_dt - pd.Timedelta(days=31)
    end_date = target_dt + pd.Timedelta(days=diff)
    df3f_1 = setDfData(start_date, target_dt,'ktbf3y_vol').iloc[-13:]
    df3f_1.set_index('date', inplace=True)
    dti1 = list(df3f_1.index)
    df3f_2 = setDfData(target_dt+pd.Timedelta(days=1), end_date,'ktbf3y_vol')
    df3f_2.set_index('date', inplace=True)
    dti2 = list(df3f_2.index)
    
    workdays = dti1+dti2
    move_date = workdays[0]
    end_date = workdays[-1]
    
    i = 0 
    while i < len(workdays) :
        if move_date not in workdays :
            move_date += pd.Timedelta(days=1)
            continue
        """ // set_df : 설정 // future_df : 선물 bpv // treasury_result_df : 국고 // df3f, df10f : 선물 """
        set_df = setDfData(str(datetime.now())[:10], str(datetime.now())[:10],'setting_delta').drop('date',axis=1)
        future_df = setDfData(str(datetime.now())[:10], str(datetime.now())[:10],'futures_bpv')
        treasury_result_df = setDfData(start_date, move_date,'treasury_vol')
        df3f = setDfData(start_date, move_date,'ktbf3y_vol')[::-1]
        df10f = setDfData(start_date, move_date,'ktbf10y_vol')[::-1]
        df3f.set_index('date', inplace=True)
        df10f.set_index('date', inplace=True)
        
        cols = ['외국인','투신','보험기금','은행','증권','상장']
        idx = ['2Y','3Y','3선','5Y','7Y','10Y','10선','물가','15Y','20Y','20원금','30Y','30원금','50Y','50원금','합계']
        df = pd.DataFrame(columns=cols,index=idx)
        df.fillna(0,inplace=True)
        
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'2Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'3Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'5Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'7Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'10Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'15Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'20Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'30Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'50Y')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'물가')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'20원금')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'30원금')
        df = getResultTable(df,set_df, treasury_result_df, start_date, move_date,'50원금')
        
        # df.loc['3선','외국인'] = round(sum(df3f.loc[move_date:start_date, '외국인'] * future_df.iloc[0]['bpv']/10000),2)
        # df.loc['3선','투신'] = round(sum(df3f.loc[move_date:start_date, '투신'] * future_df.iloc[0]['bpv']/10000),2)
        # df.loc['3선','보험기금'] = round(sum(df3f.loc[move_date:start_date, '보험기금'] * future_df.iloc[0]['bpv']/10000),2)
        df.loc['3선','은행'] = round(sum(df3f.loc[move_date:start_date, '은행'] * future_df.iloc[0]['bpv']/10000),2)
        df.loc['3선','증권'] = round(sum(df3f.loc[move_date:start_date, '증권'] * future_df.iloc[0]['bpv']/10000),2)
        # df.loc['3선','상장'] = sum(df3f.loc[end_ date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
        # df.loc['10선','외국인'] = round(sum(df10f.loc[move_date:start_date, '외국인'] * future_df.iloc[1]['bpv']/10000),2)
        # df.loc['10선','투신'] = round(sum(df10f.loc[move_date:start_date, '투신'] * future_df.iloc[1]['bpv']/10000),2)
        # df.loc['10선','보험기금'] = round(sum(df10f.loc[move_date:start_date, '보험기금'] * future_df.iloc[1]['bpv']/10000),2)
        df.loc['10선','은행'] = round(sum(df10f.loc[move_date:start_date, '은행'] * future_df.iloc[1]['bpv']/10000),2)
        df.loc['10선','증권'] = round(sum(df10f.loc[move_date:start_date, '증권'] * future_df.iloc[1]['bpv']/10000),2)
        # df.loc['3선','상장'] = sum(df3f.loc[end_date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
        
        # df.loc['합계','외국인'] = sum(df.loc[:'50원금','외국인'])
        # df.loc['합계','투신'] = sum(df.loc[:'50원금','투신'])
        # df.loc['합계','보험기금'] = sum(df.loc[:'50원금','보험기금'])
        df.loc['합계','은행'] = sum(df.loc[:'50원금','은행'])
        df.loc['합계','증권'] = sum(df.loc[:'50원금','증권'])
        # df.loc['합계','상장'] = sum(df.loc[:'50원금','상장'])
        
        
        """요약본 테이블"""
        # cols = ['외인','투신','은증']
        cols = ['은증']
        idx = ['2년이하','3년','5년','7년','10년','15년~20년','30년이상']
        summary_df = pd.DataFrame(columns=cols,index=idx)
        summary_df.fillna(0,inplace=True)
        
        # summary_df.loc['2년이하', '외인'] = df.loc['2Y','외국인']
        # summary_df.loc['3년', '외인'] = df.loc['3Y','외국인']+df.loc['3선','외국인']
        # summary_df.loc['5년', '외인'] = df.loc['5Y','외국인']
        # summary_df.loc['7년', '외인'] = df.loc['7Y','외국인']
        # summary_df.loc['10년', '외인'] = df.loc['10Y','외국인']+df.loc['10선','외국인']
        # summary_df.loc['15년~20년', '외인'] = df.loc['15Y','외국인']+df.loc['20Y','외국인']+df.loc['20원금','외국인']
        # summary_df.loc['30년이상', '외인'] = df.loc['30Y','외국인']+df.loc['50Y','외국인']+df.loc['30원금','외국인']+df.loc['50원금','외국인']
        
        # summary_df.loc['2년이하', '투신'] = df.loc['2Y','보험기금']
        # summary_df.loc['3년', '투신'] = df.loc['3Y','보험기금']+df.loc['3선','보험기금']
        # summary_df.loc['5년', '투신'] = df.loc['5Y','보험기금']
        # summary_df.loc['7년', '투신'] = df.loc['7Y','보험기금']
        # summary_df.loc['10년', '투신'] = df.loc['10Y','보험기금']+df.loc['10선','보험기금']
        # summary_df.loc['15년~20년', '투신'] = df.loc['15Y','보험기금']+df.loc['20Y','보험기금']+df.loc['20원금','보험기금']
        # summary_df.loc['30년이상', '투신'] = df.loc['30Y','보험기금']+df.loc['50Y','보험기금']+df.loc['30원금','보험기금']+df.loc['50원금','보험기금']
        
        summary_df.loc['2년이하', '은증'] = df.loc['2Y','은행']+df.loc['2Y','증권']
        summary_df.loc['3년', '은증'] = df.loc['3Y','은행'] + df.loc['3선','은행'] + df.loc['3Y','증권']+df.loc['3선','증권']
        summary_df.loc['5년', '은증'] = df.loc['5Y','은행'] + df.loc['5Y','증권']
        summary_df.loc['7년', '은증'] = df.loc['7Y','은행'] + df.loc['7Y','증권']
        summary_df.loc['10년', '은증'] = df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']
        summary_df.loc['15년~20년', '은증'] = df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']
        summary_df.loc['30년이상', '은증'] = df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']
    
        # summary_df.loc['2년이하', '은증'] = df.loc['2Y','은행']+df.loc['2Y','증권']
        # summary_df.loc['3년', '은증'] = df.loc['3Y','은행']+df.loc['3선','은행'] + df.loc['3Y','증권']+df.loc['3선','증권']
        # summary_df.loc['5년', '은증'] = df.loc['5Y','은행'] + df.loc['5Y','증권']
        # summary_df.loc['7년', '은증'] = df.loc['7Y','은행'] + df.loc['7Y','증권']
        # summary_df.loc['10년', '은증'] = df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']
        # summary_df.loc['15년~20년', '은증'] = df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']
        # summary_df.loc['30년이상', '은증'] = df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']
    
        # if opt == '은증' :
        last_df.loc[i,'3선'] += (df.loc['3선','은행'] + df.loc['3선','증권'])
        last_df.loc[i,'3년'] += (summary_df.loc['3년', '은증'] - last_df.loc[i,'3선'])
        # last_df.loc[move_date,'3년'] = summary_df.loc['3년', '은증']
        last_df.loc[i,'5년'] += summary_df.loc['5년', '은증']
        last_df.loc[i,'7년'] += summary_df.loc['7년', '은증']
        last_df.loc[i,'10선'] += (df.loc['10선','은행'] + df.loc['10선','증권'])
        last_df.loc[i,'10년'] += (summary_df.loc['10년', '은증'] - last_df.loc[i,'10선'])
        # last_df.loc[move_date,'10년'] = summary_df.loc['10년', '은증']
        last_df.loc[i,'15년~20년'] += summary_df.loc['15년~20년', '은증']
        last_df.loc[i,'30년이상'] += summary_df.loc['30년이상', '은증']

        last_df.loc[i,'10년미만'] += (summary_df.loc['2년이하', '은증']+
                               summary_df.loc['3년', '은증']+
                               summary_df.loc['5년', '은증']+
                               summary_df.loc['7년', '은증']
                               )
        last_df.loc[i,'10년이상'] += (summary_df.loc['10년', '은증']+
                               summary_df.loc['15년~20년', '은증']+
                               summary_df.loc['30년이상', '은증']
                               )
        last_df.loc[i,'total'] += (summary_df.loc['2년이하', '은증']+
                               summary_df.loc['3년', '은증']+
                               summary_df.loc['5년', '은증']+
                               summary_df.loc['7년', '은증']+
                               summary_df.loc['10년', '은증']+
                               summary_df.loc['15년~20년', '은증']+
                               summary_df.loc['30년이상', '은증']
                               )
        # elif opt == '외국인':
        #     last_df.loc[move_date,'3선'] = df.loc['3선','외국인'] + df.loc['3선','외국인']
        #     last_df.loc[move_date,'3년'] = summary_df.loc['3년', '외인'] - last_df.loc[move_date,'3선']
        #     last_df.loc[move_date,'5년'] = summary_df.loc['5년', '외인']
        #     last_df.loc[move_date,'7년'] = summary_df.loc['7년', '외인']
        #     last_df.loc[move_date,'10선'] = df.loc['10선','외국인'] + df.loc['10선','외국인']
        #     last_df.loc[move_date,'10년'] = summary_df.loc['10년', '외인'] - last_df.loc[move_date,'10선']
        #     last_df.loc[move_date,'10년'] = summary_df.loc['10년', '외인']
        #     last_df.loc[move_date,'15년~20년'] = summary_df.loc['15년~20년', '외인']
        #     last_df.loc[move_date,'30년이상'] = summary_df.loc['30년이상', '외인']
        move_date += pd.Timedelta(days=1)
        i+=1
    
    last_df = last_df.iloc[:i]
    last_df['3선_avg'] /= len(y30_list)
    last_df['3년_avg'] /= len(y30_list)
    last_df['5년_avg'] /= len(y30_list)
    last_df['7년_avg'] /= len(y30_list)
    last_df['10선_avg'] /= len(y30_list)
    last_df['10년_avg'] /= len(y30_list)
    last_df['15년~20년_avg'] /= len(y30_list)
    last_df['30년이상_avg'] /= len(y30_list)

    last_df['10년미만_avg'] /= len(y30_list)
    last_df['10년이상_avg'] /= len(y30_list)    
    last_df['total_avg'] /= len(y30_list)
    
    
    tmp = last_df.iloc[0].copy()
    for i in last_df.index:
        last_df.loc[i] -= tmp

    df1 = last_df[['3선', '3선_avg']]
    df2 = last_df[['3년','3년_avg']]
    df3 = last_df[['5년','5년_avg']]
    df4 = last_df[['7년','7년_avg']]
    df5 = last_df[['10선','10선_avg']]
    df6 = last_df[['10년','10년_avg']]
    df7 = last_df[['15년~20년','15년~20년_avg']]
    df8 = last_df[['30년이상','30년이상_avg']]
    df9 = last_df[['10년미만','10년미만_avg']]
    df10 = last_df[['10년이상','10년이상_avg']]
    df11 = last_df[['total','total_avg']]
    dfs = [df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11]

    label_dates =[]
    for t in workdays:
        label_dates.append(str(t)[5:10])
    for df in dfs :
        ax = df.plot()
        plt.xticks(np.arange(0,num), label_dates, rotation=45)
        ax.set_title(df.columns[0])
        ax.set_ylabel('억원')
        ax.set_xlabel('영업일기준')
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1,-0.5))
#%%

"""결과값 받는 df 초기화"""
last_df = pd.DataFrame()
for i in range(100):
    last_df.loc[i,'3선'] = 0
    last_df.loc[i,'3년'] = 0
    last_df.loc[i,'5년'] = 0
    last_df.loc[i,'7년'] = 0
    last_df.loc[i,'10선'] = 0
    last_df.loc[i,'10년'] = 0
    last_df.loc[i,'15년~20년'] = 0
    last_df.loc[i,'30년이상'] = 0
    last_df.loc[i,'10년미만'] = 0
    last_df.loc[i,'10년이상'] = 0
    last_df.loc[i,'total'] = 0
for i in range(100):
    last_df.loc[i,'3선_avg'] = 0
    last_df.loc[i,'3년_avg'] = 0
    last_df.loc[i,'5년_avg'] = 0
    last_df.loc[i,'7년_avg'] = 0
    last_df.loc[i,'10선_avg'] = 0
    last_df.loc[i,'10년_avg'] = 0
    last_df.loc[i,'15년~20년_avg'] = 0
    last_df.loc[i,'30년이상_avg'] = 0
    last_df.loc[i,'10년미만_avg'] = 0
    last_df.loc[i,'10년이상_avg'] = 0
    last_df.loc[i,'total_avg'] = 0



"""30년물 입찰일들"""
y30_list = [
            pd.Timestamp('2021-01-04'),
            pd.Timestamp('2021-02-01'),
            pd.Timestamp('2021-03-02'),
            pd.Timestamp('2021-04-05'),
            pd.Timestamp('2021-05-03'),
            pd.Timestamp('2021-05-31'),
            pd.Timestamp('2021-06-28')
            ]

"""2주일전~최근입찰일~어제 중 영업일만 포함"""
target_date = pd.Timestamp('2021-08-02')
yesterday = pd.Timestamp(str(datetime.now())[:10])-pd.Timedelta(days=1)
# yesterday = pd.Timestamp('2021-06-30')
diff = int(str(yesterday - target_date)[:2])

showPricesPerTenor(last_df, y30_list, target_date, diff)