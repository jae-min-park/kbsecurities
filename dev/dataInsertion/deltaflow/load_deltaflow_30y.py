import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pymysql
from tqdm import tqdm
from datetime import datetime

pd.options.mode.chained_assignment = None

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

def getAuctValues(first_day ='2021-01-01', y5_day='2020-12-07') :
    dates_file = 'D:\\dev\\kbsecurities\\prd\\case_project\\dates.xlsx'
    
    auct30 = pd.read_excel(dates_file, sheet_name='AUCT30', header=1)
    auct30 = auct30[['30년최근','요일']]
    bools=[]
    for day in auct30['30년최근'] :
        if day >= pd.Timestamp(first_day):
            bools.append(True)
        else:
            bools.append(False)
    auct30 = auct30[bools]
    auct30 = auct30[::-1]
    auct30 = auct30.reset_index(drop=True)
    
    auct3 = pd.read_excel(dates_file, sheet_name='AUCT3', header=1)
    auct3 = auct3[['3년최근','요일']]
    bools=[]
    for day in auct3['3년최근'] :
        if day >= pd.Timestamp(first_day):
            bools.append(True)
        else:
            bools.append(False)
    auct3 = auct3[bools]
    auct3 = auct3[::-1]
    auct3 = auct3.reset_index(drop=True)
    
    auct10 = pd.read_excel(dates_file, sheet_name='AUCT10', header=1)
    auct10 = auct10[['10년최근','요일']]
    bools=[]
    for day in auct10['10년최근'] :
        if day >= pd.Timestamp(first_day):
            bools.append(True)
        else:
            bools.append(False)
    auct10 = auct10[bools]
    auct10 = auct10[::-1]
    auct10 = auct10.reset_index(drop=True)
    
    auct5 = pd.read_excel(dates_file, sheet_name='AUCT5', header=1)
    auct5 = auct5[['5년최근','요일']]
    bools=[]
    for day in auct5['5년최근'] :
        if day >= pd.Timestamp(y5_day):
            bools.append(True)
        else:
            bools.append(False)
    auct5 = auct5[bools]
    auct5 = auct5[::-1]
    auct5 = auct5.reset_index(drop=True)
    
    auct_none = pd.read_excel(dates_file, sheet_name='AUCTNONE', header=1)
    auct_none = auct_none[['입찰없는막주월요일','요일']]
    bools=[]
    for day in auct_none['입찰없는막주월요일'] :
        if day >= pd.Timestamp(first_day):
            bools.append(True)
        else:
            bools.append(False)
    auct_none = auct_none[bools]
    auct_none = auct_none[::-1]
    auct_none = auct_none.reset_index(drop=True)
    
    holi = pd.read_excel(dates_file, sheet_name='HOLI_KR', header=1)
    holi = holi[['DATES','DAY_NAME','NAME']]
    bools=[]
    for day in holi['DATES'] :
        if day >= pd.Timestamp(first_day):
            bools.append(True)
        else:
            bools.append(False)
    holi = holi[bools]
    holi = holi[::-1]
    
    bools=[]
    for name in holi['DAY_NAME'] :
        if name == 'Mon':
            bools.append(True)
        else:
            bools.append(False)
    mon_holi = holi[bools]
    mon_holi = mon_holi.reset_index(drop=True)
    
    # bools = [not i for i in bools]
    bools=[]
    for name in holi['DAY_NAME'] :
        if name == 'Mon' or name =='Sat' or name=='Sun':
            bools.append(False)
        else:
            bools.append(True)
    holi = holi[bools]
    holi = holi.reset_index(drop=True)
    
    return auct30, auct3, auct10, auct5, auct_none, holi, mon_holi


def makeCalendar(first_day ='2021-01-01', y5_day='2020-12-07') :
    auct30, auct3, auct10, auct5, auct_none, holi, mon_holi = getAuctValues(first_day, y5_day)
    cols = ['3Y','3Y+1','3Y+2','3Y+3','3Y+4',
            '10Y','10Y+1','10Y+2','10Y+3','10Y+4',
            '5Y','5Y+1','5Y+2','5Y+3','5Y+4',
            'N','N+1','N+2','N+3','N+4',
            '30Y','30Y+1','30Y+2','30Y+3','30Y+4',
            ]
    idx = list(range(1,13))
    calendar = pd.DataFrame(columns=cols, index=idx)
    calendar.fillna(0, inplace=True)
    holidays = np.array(holi['DATES'])
    # mon_holidays = np.array(mon_holi['DATES'])
    
    """변형코드"""
    i = 1
    for day in auct5['5년최근'] :
        is_mon_holi = ''
        if auct5.loc[i-1,'요일'] == 'Mon':
            calendar.loc[i+1,'5Y'] = day
        else :
            calendar.loc[i+1,'5Y'] = day
            if auct5.loc[i-1,'요일'] == 'Tue':
                is_mon_holi='Tue'
                calendar.loc[i+1,'5Y+4'] = 0
            elif auct5.loc[i-1,'요일'] == 'Wed':
                is_mon_holi='Wed'
                calendar.loc[i+1,'5Y+3'] = 0
                calendar.loc[i+1,'5Y+4'] = 0
            elif auct5.loc[i-1,'요일'] == 'Thu':
                is_mon_holi='Thu'
                calendar.loc[i+1,'5Y+2'] = 0
                calendar.loc[i+1,'5Y+3'] = 0
                calendar.loc[i+1,'5Y+4'] = 0
            elif auct5.loc[i-1,'요일'] == 'Fri':
                is_mon_holi='Fri'
                calendar.loc[i+1,'5Y+1'] = 0
                calendar.loc[i+1,'5Y+2'] = 0
                calendar.loc[i+1,'5Y+3'] = 0
                calendar.loc[i+1,'5Y+4'] = 0
        if is_mon_holi != 'Fri' and (day + pd.Timedelta(days=1)) not in holidays :
            calendar.loc[i+1,'5Y+1'] = day + pd.Timedelta(days=1)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and (day + pd.Timedelta(days=2)) not in holidays :
            calendar.loc[i+1,'5Y+2'] = day + pd.Timedelta(days=2)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and (day + pd.Timedelta(days=3)) not in holidays :
            calendar.loc[i+1,'5Y+3'] = day + pd.Timedelta(days=3)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and is_mon_holi != 'Tue' and (day + pd.Timedelta(days=4)) not in holidays :
            calendar.loc[i+1,'5Y+4'] = day + pd.Timedelta(days=4)
        i+=1
    
    """정상코드"""
    # i = 1
    # for day in auct5['5년최근'] :
    #     is_mon_holi = ''
    #     if auct5.loc[i-1,'요일'] == 'Mon':
    #         calendar.loc[i,'5Y'] = day
    #     else :
    #         calendar.loc[i,'5Y'] = day
    #         if auct5.loc[i-1,'요일'] == 'Tue':
    #             is_mon_holi='Tue'
    #             calendar.loc[i,'5Y+4'] = 0
    #         elif auct5.loc[i-1,'요일'] == 'Wed':
    #             is_mon_holi='Wed'
    #             calendar.loc[i,'5Y+3'] = 0
    #             calendar.loc[i,'5Y+4'] = 0
    #         elif auct5.loc[i-1,'요일'] == 'Thu':
    #             is_mon_holi='Thu'
    #             calendar.loc[i,'5Y+2'] = 0
    #             calendar.loc[i,'5Y+3'] = 0
    #             calendar.loc[i,'5Y+4'] = 0
    #         elif auct5.loc[i-1,'요일'] == 'Fri':
    #             is_mon_holi='Fri'
    #             calendar.loc[i,'5Y+1'] = 0
    #             calendar.loc[i,'5Y+2'] = 0
    #             calendar.loc[i,'5Y+3'] = 0
    #             calendar.loc[i,'5Y+4'] = 0
    #     if is_mon_holi != 'Fri' and (day + pd.Timedelta(days=1)) not in holidays :
    #         calendar.loc[i,'5Y+1'] = day + pd.Timedelta(days=1)
    #     if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and (day + pd.Timedelta(days=2)) not in holidays :
    #         calendar.loc[i,'5Y+2'] = day + pd.Timedelta(days=2)
    #     if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and (day + pd.Timedelta(days=3)) not in holidays :
    #         calendar.loc[i,'5Y+3'] = day + pd.Timedelta(days=3)
    #     if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and is_mon_holi != 'Tue' and (day + pd.Timedelta(days=4)) not in holidays :
    #         calendar.loc[i,'5Y+4'] = day + pd.Timedelta(days=4)
    #     i+=1
    
    i = 1
    for day in auct30['30년최근'] :
        is_mon_holi = ''
        if auct30.loc[i-1,'요일'] == 'Mon':
            calendar.loc[i,'30Y'] = [day]
        else :
            calendar.loc[i,'30Y'] = day
            if auct30.loc[i-1,'요일'] == 'Tue':
                is_mon_holi='Tue'
                calendar.loc[i,'30Y+4'] = 0
            elif auct30.loc[i-1,'요일'] == 'Wed':
                is_mon_holi='Wed'
                calendar.loc[i,'30Y+3'] = 0
                calendar.loc[i,'30Y+4'] = 0
            elif auct30.loc[i-1,'요일'] == 'Thu':
                is_mon_holi='Thu'
                calendar.loc[i,'30Y+2'] = 0
                calendar.loc[i,'30Y+3'] = 0
                calendar.loc[i,'30Y+4'] = 0
            elif auct30.loc[i-1,'요일'] == 'Fri':
                is_mon_holi='Fri'
                calendar.loc[i,'30Y+1'] = 0
                calendar.loc[i,'30Y+2'] = 0
                calendar.loc[i,'30Y+3'] = 0
                calendar.loc[i,'30Y+4'] = 0
        if is_mon_holi != 'Fri' and (day + pd.Timedelta(days=1)) not in holidays :
            calendar.loc[i,'30Y+1'] = day + pd.Timedelta(days=1)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and (day + pd.Timedelta(days=2)) not in holidays :
            calendar.loc[i,'30Y+2'] = day + pd.Timedelta(days=2)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and (day + pd.Timedelta(days=3)) not in holidays :
            calendar.loc[i,'30Y+3'] = day + pd.Timedelta(days=3)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and is_mon_holi != 'Tue' and (day + pd.Timedelta(days=4)) not in holidays :
            calendar.loc[i,'30Y+4'] = day + pd.Timedelta(days=4)
        i+=1
    
    i = 1
    for day in auct3['3년최근'] :
        is_mon_holi = ''
        if auct3.loc[i-1,'요일'] == 'Mon':
            calendar.loc[i,'3Y'] = [day]
        else :
            calendar.loc[i,'3Y'] = day
            if auct3.loc[i-1,'요일'] == 'Tue':
                is_mon_holi='Tue'
                calendar.loc[i,'3Y+4'] = 0
            elif auct3.loc[i-1,'요일'] == 'Wed':
                is_mon_holi='Wed'
                calendar.loc[i,'3Y+3'] = 0
                calendar.loc[i,'3Y+4'] = 0
            elif auct3.loc[i-1,'요일'] == 'Thu':
                is_mon_holi='Thu'
                calendar.loc[i,'3Y+2'] = 0
                calendar.loc[i,'3Y+3'] = 0
                calendar.loc[i,'3Y+4'] = 0
            elif auct3.loc[i-1,'요일'] == 'Fri':
                is_mon_holi='Fri'
                calendar.loc[i,'3Y+1'] = 0
                calendar.loc[i,'3Y+2'] = 0
                calendar.loc[i,'3Y+3'] = 0
                calendar.loc[i,'3Y+4'] = 0
        if is_mon_holi != 'Fri' and (day + pd.Timedelta(days=1)) not in holidays :
            calendar.loc[i,'3Y+1'] = day + pd.Timedelta(days=1)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and (day + pd.Timedelta(days=2)) not in holidays :
            calendar.loc[i,'3Y+2'] = day + pd.Timedelta(days=2)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and (day + pd.Timedelta(days=3)) not in holidays :
            calendar.loc[i,'3Y+3'] = day + pd.Timedelta(days=3)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and is_mon_holi != 'Tue' and (day + pd.Timedelta(days=4)) not in holidays :
            calendar.loc[i,'3Y+4'] = day + pd.Timedelta(days=4)
        i+=1
    
    i = 1
    for day in auct10['10년최근'] :
        is_mon_holi = ''
        if auct10.loc[i-1,'요일'] == 'Mon':
            calendar.loc[i,'10Y'] = [day]
        else :
            calendar.loc[i,'10Y'] = day
            if auct10.loc[i-1,'요일'] == 'Tue':
                is_mon_holi='Tue'
                calendar.loc[i,'10Y+4'] = 0
            elif auct10.loc[i-1,'요일'] == 'Wed':
                is_mon_holi='Wed'
                calendar.loc[i,'10Y+3'] = 0
                calendar.loc[i,'10Y+4'] = 0
            elif auct10.loc[i-1,'요일'] == 'Thu':
                is_mon_holi='Thu'
                calendar.loc[i,'10Y+2'] = 0
                calendar.loc[i,'10Y+3'] = 0
                calendar.loc[i,'10Y+4'] = 0
            elif auct10.loc[i-1,'요일'] == 'Fri':
                is_mon_holi='Fri'
                calendar.loc[i,'10Y+1'] = 0
                calendar.loc[i,'10Y+2'] = 0
                calendar.loc[i,'10Y+3'] = 0
                calendar.loc[i,'10Y+4'] = 0
        if is_mon_holi != 'Fri' and (day + pd.Timedelta(days=1)) not in holidays :
            calendar.loc[i,'10Y+1'] = day + pd.Timedelta(days=1)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and (day + pd.Timedelta(days=2)) not in holidays :
            calendar.loc[i,'10Y+2'] = day + pd.Timedelta(days=2)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and (day + pd.Timedelta(days=3)) not in holidays :
            calendar.loc[i,'10Y+3'] = day + pd.Timedelta(days=3)
        if is_mon_holi != 'Fri' and is_mon_holi != 'Thu' and is_mon_holi != 'Wed' and is_mon_holi != 'Tue' and (day + pd.Timedelta(days=4)) not in holidays :
            calendar.loc[i,'10Y+4'] = day + pd.Timedelta(days=4)
        i+=1
    
    
    i = 1
    for day in auct_none['입찰없는막주월요일'] :
        if auct_none.loc[i-1,'요일'] == 'Mon':
            for j in range(1,12):
                if type(calendar.loc[j, '30Y']) != int and type(calendar.loc[j, '5Y']) != int  :
                    if calendar.loc[j, '5Y'] <= day and day <= calendar.loc[j, '30Y'] :
                        calendar.loc[j,'N'] = day
                        calendar.loc[j,'N+1'] = day+ pd.Timedelta(days=1)
                        calendar.loc[j,'N+2'] = day+ pd.Timedelta(days=2)
                        calendar.loc[j,'N+3'] = day+ pd.Timedelta(days=3)
                        calendar.loc[j,'N+4'] = day+ pd.Timedelta(days=4)
            if type(calendar.loc[j, '5Y']) != int:
                if calendar.loc[12, '5Y'] <= day :
                    calendar.loc[12,'N'] = day
                    calendar.loc[12,'N+1'] = day+ pd.Timedelta(days=1)
                    calendar.loc[12,'N+2'] = day+ pd.Timedelta(days=2)
                    calendar.loc[12,'N+3'] = day+ pd.Timedelta(days=3)
                    calendar.loc[12,'N+4'] = day+ pd.Timedelta(days=4)
        i+=1
    
    for i in range(2,13) :
        calendar.loc[i-1,'5Y':'30Y+4']= calendar.loc[i,'5Y':'30Y+4']
    return calendar, holi

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
    df.loc[asset,'외국인'] = round(np.sum(tmp_joined['외국인 순매수 거래량'] * tmp_joined['델타'])/10**12,3)
    df.loc[asset,'투신'] = round(np.sum(tmp_joined['자산운용(공모) 순매수 거래량'] * tmp_joined['델타'])/10**12,3)
    df.loc[asset,'보험기금'] = round(np.sum(tmp_joined['보험기금 순매수 거래량'] * tmp_joined['델타'])/10**12,3)
    df.loc[asset,'은행'] = round(np.sum(tmp_joined['은행 순매수 거래량'] * tmp_joined['델타'])/10**12,3)
    df.loc[asset,'증권'] = round(np.sum(tmp_joined['증권순매수(원)'] * tmp_joined['델타'])/10**12,3)
    df.loc[asset,'상장'] = round(np.sum(tmp_joined['낙찰금액'] * tmp_joined['델타'])/10**12,3)
    # df.loc[asset,'상장'] = round(np.sum(tmp_joined['상장잔액증감(원)'] * tmp_joined['델타'])/10**12,2)
    return df

def showDeltaflow(month=7) :
    calendar, holi = makeCalendar()
    last_df = pd.DataFrame()
    for i in range(21): # 0:5Y, 1:5Y+1, 2:5Y+2, 3:5Y+3, 4:5Y+4, 5:30Y, 6:30Y+1, 7:30Y+2, 8:30Y+3, 9:30Y+4, 10:3Y, 11:3Y+1, 12:3Y+2, 13:3Y+3, 14:3Y+4, 15:10Y, 16:10Y+1, 17:10Y+2, 18:10Y+3, 19:10Y+4
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
        last_df.loc[i,'물가'] = 0
        last_df.loc[i,'total'] = 0
    for i in range(21): # 0:5Y-3, 1:5Y, 2:5Y+1, 3:5Y+2, 4:5Y+3, 5:5Y+4, 6:30Y, 7:30Y+1, 8:30Y+2, 9:30Y+3, 10:30Y+4, 11:3Y, 12:3Y+1, 13:3Y+2, 14:3Y+3, 15:3Y+4, 16:10Y, 17:10Y+1, 18:10Y+2, 19:10Y+3, 20:10Y+4
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
        last_df.loc[i,'물가_avg'] = 0        
        last_df.loc[i,'total_avg'] = 0
    
    future_df = setDfData(str(datetime.now())[:10], str(datetime.now())[:10],'futures_bpv')
    set_df = setDfData(str(datetime.now())[:10], str(datetime.now())[:10],'setting_delta').drop('date',axis=1)
    
    """평균값구하기"""
    cnt=cnt5y=cnt5y_1=cnt5y_2=cnt5y_3=cnt5y_4=cnt30y=cnt30y_1=cnt30y_2=cnt30y_3=cnt30y_4=cnt3y=cnt3y_1=cnt3y_2=cnt3y_3=cnt3y_4=cnt10y=cnt10y_1=cnt10y_2=cnt10y_3=cnt10y_4=0
    
    for i in range(1, month):
        for j in range(21) :
            start_date = calendar.loc[i,'3Y']-pd.Timedelta(days=3)
            while start_date in np.array(holi['DATES']) or start_date.day_name() == 'Saturday' or start_date.day_name() == 'Sunday' :
                start_date = start_date - pd.Timedelta(days=1)
            move_date = ''
            if j == 0:
                move_date = start_date
                cnt+=1
            if j == 1:
                move_date = calendar.loc[i,'3Y']
                if move_date == 0:
                    continue
                else :
                    cnt3y+=1
            if j == 2:
                move_date = calendar.loc[i,'3Y+1']
                if move_date == 0:
                    continue
                else :
                    cnt3y_1+=1
            if j == 3:
                move_date = calendar.loc[i,'3Y+2']
                if move_date == 0:
                    continue
                else :
                    cnt3y_2+=1
            if j == 4:
                move_date = calendar.loc[i,'3Y+3']
                if move_date == 0:
                    continue
                else :
                    cnt3y_3+=1        
            if j == 5:
                move_date = calendar.loc[i,'3Y+4']
                if move_date == 0:
                    continue
                else :
                    cnt3y_4+=1
            if j == 6:
                move_date = calendar.loc[i,'10Y']
                if move_date == 0:
                    continue
                else :
                    cnt10y+=1        
            if j == 7:
                move_date = calendar.loc[i,'10Y+1']
                if move_date == 0:
                    continue
                else :
                    cnt10y_1+=1
            if j == 8:
                move_date = calendar.loc[i,'10Y+2']
                if move_date == 0:
                    continue
                else :
                    cnt10y_2+=1        
            if j == 9:
                move_date = calendar.loc[i,'10Y+3']
                if move_date == 0:
                    continue
                else :
                    cnt10y_3+=1        
            if j == 10:
                move_date = calendar.loc[i,'10Y+4']
                if move_date == 0:
                    continue
                else :
                    cnt10y_4+=1        
            if j == 11:
                move_date = calendar.loc[i,'5Y']
                if move_date == 0:
                    continue
                else :
                    cnt5y+=1        
            if j == 12:
                move_date = calendar.loc[i,'5Y+1']
                if move_date == 0:
                    continue
                else :
                    cnt5y_1+=1        
            if j == 13:
                move_date = calendar.loc[i,'5Y+2']
                if move_date == 0:
                    continue
                else :
                    cnt5y_2+=1                
            if j == 14:
                move_date = calendar.loc[i,'5Y+3']
                if move_date == 0:
                    continue
                else :
                    cnt5y_3+=1                
            if j == 15:
                move_date = calendar.loc[i,'5Y+4']
                if calendar.loc[i,'N+4'] != 0 :
                    move_date = calendar.loc[i,'N+4']            
                if move_date == 0:
                    continue
                else :
                    cnt5y_4+=1                
            if j == 16:
                move_date = calendar.loc[i,'30Y']
                if move_date == 0:
                    continue
                else :
                    cnt30y+=1                
            if j == 17:
                move_date = calendar.loc[i,'30Y+1']
                if move_date == 0:
                    continue
                else :
                    cnt30y_1+=1                
            if j == 18:
                move_date = calendar.loc[i,'30Y+2']
                if move_date == 0:
                    continue
                else :
                    cnt30y_2+=1                        
            if j == 19:
                move_date = calendar.loc[i,'30Y+3']
                if move_date == 0:
                    continue
                else :
                    cnt30y_3+=1                        
            if j == 20:
                move_date = calendar.loc[i,'30Y+4']
                if move_date == 0:
                    continue
                else :
                    cnt30y_4+=1       
    
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
            
            df.loc['3선','은행'] = sum(df3f.loc[move_date:start_date, '은행'] * future_df.iloc[0]['bpv']/10000)
            df.loc['3선','증권'] = sum(df3f.loc[move_date:start_date, '증권'] * future_df.iloc[0]['bpv']/10000)
            df.loc['10선','은행'] = sum(df10f.loc[move_date:start_date, '은행'] * future_df.iloc[1]['bpv']/10000)
            df.loc['10선','증권'] = sum(df10f.loc[move_date:start_date, '증권'] * future_df.iloc[1]['bpv']/10000)
            
            
            last_df.loc[j,'3선_avg'] += (df.loc['3선','은행'] + df.loc['3선','증권'])
            last_df.loc[j,'3년_avg'] += (df.loc['3Y','은행'] + df.loc['3Y','증권'])
            last_df.loc[j,'5년_avg'] += (df.loc['5Y','은행'] + df.loc['5Y','증권'])
            last_df.loc[j,'7년_avg'] += (df.loc['7Y','은행'] + df.loc['7Y','증권'])
            last_df.loc[j,'10선_avg'] += (df.loc['10선','은행'] + df.loc['10선','증권'])
            last_df.loc[j,'10년_avg'] += (df.loc['10Y','은행'] + df.loc['10Y','증권'])
            last_df.loc[j,'15년~20년_avg'] += (df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권'])
            last_df.loc[j,'30년이상_avg'] += (df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권'])
            
            last_df.loc[j,'10년미만_avg'] += (df.loc['2Y','은행']+df.loc['2Y','증권']+
                                            df.loc['3Y','은행']+df.loc['3Y','증권']+
                                            df.loc['3선','은행']+df.loc['3선','증권']+
                                            df.loc['5Y','은행']+df.loc['5Y','증권']+
                                            df.loc['7Y','은행']+df.loc['7Y','증권']
                                            )
            
            last_df.loc[j,'10년이상_avg'] += (df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']+
                                           df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']+
                                           df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']+
                                           df.loc['물가','은행']+df.loc['물가','증권']
                                           )
            last_df.loc[j,'물가_avg'] += (df.loc['물가','은행']+df.loc['물가','증권'])              
            last_df.loc[j,'total_avg'] += (df.loc['3선','은행'] + df.loc['3선','증권'] + df.loc['3Y','은행'] + df.loc['3Y','증권'] +
                                           df.loc['5Y','은행'] + df.loc['5Y','증권'] + df.loc['7Y','은행'] + df.loc['7Y','증권'] +
                                           df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권'] +
                                           df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권'] +
                                           df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']+
                                           df.loc['물가','은행']+df.loc['물가','증권']
                                           )
    
    last_df.loc[0,:] /= cnt
    last_df.loc[1,:] /= cnt3y
    last_df.loc[2,:] /= cnt3y_1
    last_df.loc[3,:] /= cnt3y_2
    last_df.loc[4,:] /= cnt3y_3
    last_df.loc[5,:] /= cnt3y_4
    last_df.loc[6,:] /= cnt10y
    last_df.loc[7,:] /= cnt10y_1
    last_df.loc[8,:] /= cnt10y_2
    last_df.loc[9,:] /= cnt10y_3
    last_df.loc[10,:] /= cnt10y_4
    last_df.loc[11,:] /= cnt5y
    last_df.loc[12,:] /= cnt5y_1
    last_df.loc[13,:] /= cnt5y_2
    last_df.loc[14,:] /= cnt5y_3
    last_df.loc[15,:] /= cnt5y_4
    last_df.loc[16,:] /= cnt30y
    last_df.loc[17,:] /= cnt30y_1
    last_df.loc[18,:] /= cnt30y_2
    last_df.loc[19,:] /= cnt30y_3
    last_df.loc[20,:] /= cnt30y_4
    
    """단일값구하기"""
    # i = month
    flag = False
    target_idx = 0
    target_date = start_date
    dates=[]
    for j in range(21) :    
        start_date = calendar.loc[month,'3Y']-pd.Timedelta(days=3)
        while start_date in np.array(holi['DATES']) or start_date.day_name() == 'Saturday' or start_date.day_name() == 'Sunday' :
            start_date = start_date - pd.Timedelta(days=1)
        move_date = ''
        if j == 0:
            move_date = start_date
            dates.append(str(move_date)[5:10])
        if j == 1:
            move_date = calendar.loc[month,'3Y']
            if move_date == 0 :
                calendar.loc[month,'3Y']=move_date = start_date
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 2:
            move_date = calendar.loc[month,'3Y+1']
            if move_date == 0:
                calendar.loc[month,'3Y+1']=move_date = calendar.loc[month,'3Y']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 3:
            move_date = calendar.loc[month,'3Y+2']
            if move_date == 0:
                calendar.loc[month,'3Y+2']=move_date = calendar.loc[month,'3Y+1']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 4:
            move_date = calendar.loc[month,'3Y+3']
            if move_date == 0:
                calendar.loc[month,'3Y+3']=move_date = calendar.loc[month,'3Y+2']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 5:
            move_date = calendar.loc[month,'3Y+4']
            if move_date == 0:
                calendar.loc[month,'3Y+4']=move_date = calendar.loc[month,'3Y+3']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 6:
            move_date = calendar.loc[month,'10Y']
            if move_date == 0:
                calendar.loc[month,'10Y']=move_date = calendar.loc[month,'3Y+4']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 7:
            move_date = calendar.loc[month,'10Y+1']
            if move_date == 0:
                calendar.loc[month,'10Y+1']=move_date = calendar.loc[month,'10Y']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 8:
            move_date = calendar.loc[month,'10Y+2']
            if move_date == 0:
                calendar.loc[month,'10Y+2']=move_date = calendar.loc[month,'10Y+1']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 9:
            move_date = calendar.loc[month,'10Y+3']
            if move_date == 0:
                calendar.loc[month,'10Y+3']=move_date = calendar.loc[month,'10Y+2']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 10:
            move_date = calendar.loc[month,'10Y+4']
            if move_date == 0:
                calendar.loc[month,'5Y+4']=move_date = calendar.loc[month,'10Y+3']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 11:
            move_date = calendar.loc[month,'5Y']
            if move_date == 0:
                calendar.loc[month,'5Y']=move_date = calendar.loc[month,'10Y+4']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 12:
            move_date = calendar.loc[month,'5Y+1']
            if move_date == 0:
                calendar.loc[month,'5Y+1']=move_date = calendar.loc[month,'5Y']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 13:
            move_date = calendar.loc[month,'5Y+2']
            if move_date == 0:
                calendar.loc[month,'5Y+2']=move_date = calendar.loc[month,'5Y+1']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 14:
            move_date = calendar.loc[month,'5Y+3']
            if move_date == 0:
                calendar.loc[month,'5Y+3']=move_date = calendar.loc[month,'5Y+2']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 15:
            move_date = calendar.loc[month,'5Y+4']
            if calendar.loc[month,'N+4'] != 0:
                move_date = calendar.loc[month,'N+4']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 16:
            move_date = calendar.loc[month,'30Y']
            if move_date == 0:
                calendar.loc[month,'30Y']=move_date = calendar.loc[month,'5Y+4']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 17:
            move_date = calendar.loc[month,'30Y+1']
            if move_date == 0:
                calendar.loc[month,'30Y+1']=move_date = calendar.loc[month,'30Y']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 18:
            move_date = calendar.loc[month,'30Y+2']
            if move_date == 0:
                calendar.loc[month,'30Y+2']=move_date = calendar.loc[month,'30Y+1']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 19:
            move_date = calendar.loc[month,'30Y+3']
            if move_date == 0 :
                calendar.loc[month,'30Y+3']=move_date = calendar.loc[month,'30Y+2']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
        if j == 20:
            move_date = calendar.loc[month,'30Y+4']
            if move_date == 0 :
                calendar.loc[month,'30Y+4']=move_date = calendar.loc[month,'30Y+3']
                dates.append('공백')
                # dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            elif pd.Timestamp(str(datetime.now())[:10]) <= move_date : 
            # elif pd.Timestamp('2021-08-23') <= move_date : 
                if flag != True:
                    flag = True
                    target_idx = j-1
                    target_date = start_date
                    dates.append(str(move_date)[5:10])
                else:
                    move_date = start_date                        
                    dates.append(str(move_date+pd.Timedelta(days=1))[5:10])
            else :
                dates.append(str(move_date)[5:10])
            
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
        
        df.loc['3선','은행'] = sum(df3f.loc[move_date:start_date, '은행'] * future_df.iloc[0]['bpv']/10000)
        df.loc['3선','증권'] = sum(df3f.loc[move_date:start_date, '증권'] * future_df.iloc[0]['bpv']/10000)
        df.loc['10선','은행'] = sum(df10f.loc[move_date:start_date, '은행'] * future_df.iloc[1]['bpv']/10000)
        df.loc['10선','증권'] = sum(df10f.loc[move_date:start_date, '증권'] * future_df.iloc[1]['bpv']/10000)
        
        
        last_df.loc[j,'3선'] = (df.loc['3선','은행'] + df.loc['3선','증권'])
        last_df.loc[j,'3년'] = (df.loc['3Y','은행'] + df.loc['3Y','증권'])
        last_df.loc[j,'5년'] = (df.loc['5Y','은행'] + df.loc['5Y','증권'])
        last_df.loc[j,'7년'] = (df.loc['7Y','은행'] + df.loc['7Y','증권'])
        last_df.loc[j,'10선'] = (df.loc['10선','은행'] + df.loc['10선','증권'])
        last_df.loc[j,'10년'] = (df.loc['10Y','은행'] + df.loc['10Y','증권'])
        last_df.loc[j,'15년~20년'] = (df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권'])
        last_df.loc[j,'30년이상'] = (df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권'])
        
        last_df.loc[j,'10년미만'] = (df.loc['2Y','은행']+df.loc['2Y','증권']+
                                        df.loc['3Y','은행']+df.loc['3Y','증권']+
                                        df.loc['3선','은행']+df.loc['3선','증권']+
                                        df.loc['5Y','은행']+df.loc['5Y','증권']+
                                        df.loc['7Y','은행']+df.loc['7Y','증권']
                                        )
        
        last_df.loc[j,'10년이상'] = (df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권']+
                                       df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권']+
                                       df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']+
                                       df.loc['물가','은행']+df.loc['물가','증권']
                                       )
        last_df.loc[j,'물가'] += (df.loc['물가','은행']+df.loc['물가','증권'])                                        
        last_df.loc[j,'total'] = (df.loc['3선','은행'] + df.loc['3선','증권'] + df.loc['3Y','은행'] + df.loc['3Y','증권'] +
                                       df.loc['5Y','은행'] + df.loc['5Y','증권'] + df.loc['7Y','은행'] + df.loc['7Y','증권'] +
                                       df.loc['10Y','은행']+df.loc['10선','은행'] + df.loc['10Y','증권']+df.loc['10선','증권'] +
                                       df.loc['15Y','은행']+df.loc['20Y','은행']+df.loc['20원금','은행'] + df.loc['15Y','증권']+df.loc['20Y','증권']+df.loc['20원금','증권'] +
                                       df.loc['30Y','은행']+df.loc['50Y','은행']+df.loc['30원금','은행']+df.loc['50원금','은행'] + df.loc['30Y','증권']+df.loc['50Y','증권']+df.loc['30원금','증권']+df.loc['50원금','증권']+
                                       df.loc['물가','은행']+df.loc['물가','증권']
                                       )
    
    
    tmp = last_df.iloc[0].copy()
    for i in last_df.index:
        last_df.loc[i] -= tmp
    
    df0 = last_df[['total','total_avg']]
    df1 = last_df[['3년','3년_avg']]
    df2 = last_df[['3선', '3선_avg']]
    df3 = last_df[['5년','5년_avg']]
    df4 = last_df[['7년','7년_avg']]
    df5 = last_df[['10년미만','10년미만_avg']]
    df6 = last_df[['10년이상','10년이상_avg']]
    df7 = last_df[['10년','10년_avg']]
    df8 = last_df[['10선','10선_avg']]
    df9 = last_df[['15년~20년','15년~20년_avg']]
    df10 = last_df[['30년이상','30년이상_avg']]
    df11 = last_df[['물가','물가_avg']]
    
    dfs = [df0, df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11]
    
    
    barplot_diff=[] # 델타괴리 barplot diff
    
    """테너별 plot"""
    for df in dfs :
        ax = df.plot()
        plt.xticks(np.arange(0,len(dates)), dates, rotation=45)
        
        first_diff = df.iloc[target_idx][0] - df.iloc[target_idx][1]
        second_diff = df.iloc[target_idx-1][0] - df.iloc[target_idx-1][1]         
        # print(first_diff, second_diff)
        # title = df.columns[0] + "(전일비괴리 :" + + ")"
        diff = round(first_diff-second_diff,1)
        barplot_diff.append(diff)
        title = f'{df.columns[0]} / 전일대비 괴리 변화 : {diff} 억원'
        plt.axvline(target_idx, color='black')
        plt.text(target_idx-1, 0, f'최근영업일\n{str(target_date)[5:10]}')
        ax.set_title(title)
        ax.set_ylabel('억원')
        ax.set_xlabel(f"\n {str(calendar.loc[month,'3Y'])[5:10]} : 3Y입찰 / {str(calendar.loc[month,'10Y'])[5:10]} : 10Y입찰 / {str(calendar.loc[month,'5Y'])[5:10]} : 5Y입찰 / {str(calendar.loc[month,'30Y'])[5:10]} : 30Y입찰")
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1,-0.5))   
        
    """델타괴리 bar plot 표시"""
    barplot_df = pd.DataFrame(columns= ['val'], index= ['3년','3선','5년','7년','10년','10선','15년~20년','30년이상','물가','10년미만','10년이상'])
    barplot_df.loc['3년','val'] = df1.iloc[target_idx][0] - df1.iloc[target_idx][1]
    barplot_df.loc['3선','val'] = df2.iloc[target_idx][0] - df2.iloc[target_idx][1]
    barplot_df.loc['5년','val'] = df3.iloc[target_idx][0] - df3.iloc[target_idx][1]
    barplot_df.loc['7년','val'] = df4.iloc[target_idx][0] - df4.iloc[target_idx][1]
    barplot_df.loc['10년','val'] = df7.iloc[target_idx][0] - df7.iloc[target_idx][1]
    barplot_df.loc['10선','val'] = df8.iloc[target_idx][0] - df8.iloc[target_idx][1]
    barplot_df.loc['15년~20년','val'] = df9.iloc[target_idx][0] - df9.iloc[target_idx][1]
    barplot_df.loc['30년이상','val'] = df10.iloc[target_idx][0] - df10.iloc[target_idx][1]
    barplot_df.loc['물가','val'] = df11.iloc[target_idx][0] - df11.iloc[target_idx][1]    
    barplot_df.loc['10년미만','val'] = df5.iloc[target_idx][0] - df5.iloc[target_idx][1]
    barplot_df.loc['10년이상','val'] = df6.iloc[target_idx][0] - df6.iloc[target_idx][1]
    
    barplot_diff[0],barplot_diff[1],barplot_diff[2],barplot_diff[3],barplot_diff[4],barplot_diff[5],barplot_diff[6],barplot_diff[7],barplot_diff[8],barplot_diff[9],barplot_diff[10] = barplot_diff[1],barplot_diff[2],barplot_diff[3],barplot_diff[4],barplot_diff[7],barplot_diff[8],barplot_diff[9],barplot_diff[10],barplot_diff[11],barplot_diff[5],barplot_diff[6]
    
    del barplot_diff[-1]
    ax = barplot_df.plot.bar(rot=0) 
    for i, v in enumerate(barplot_diff):
        plt.text(i-0.4, 0, '{0:+}'.format(v), fontsize = 12, color='black')
        
    plt.xticks(rotation=45)
    plt.axvline(8.5, color='grey')
    ax.set_ylabel('억원')
    ax.set_xlabel('테너')
    title = f'{str(target_date)[5:10]} YTD월평균 대비 은증델타 괴리 (숫자는 전일비)'
    # title = f' YTD월평균 대비 은증델타 괴리 (일간, 숫자는 전일비)'
    ax.set_title(title)
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    ax.get_legend().remove()
    
    return calendar
    
# showDeltaflow()