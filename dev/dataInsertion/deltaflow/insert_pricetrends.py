import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pymysql
import re
from tqdm import tqdm

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


""" 설정 다중일 DB데이터 삽입용"""
def insertInfoFutures(df, table):
    idx = df.index
    for i in tqdm(range(len(idx))) :
        _1 = str(idx[i][0])[:10] # 삽입일
        _2 = str(idx[i][1]) # 코드
        _3 = str(df.iloc[i][0]) # 종목명
        _4 = str(df.iloc[i][1]) #bpv
        sql = "insert into "+table+" values ('"+_1 +"','"+_2+ "','"+_3+"',"+_4+');'
        print(sql)
        cursor.execute(sql)
    test_db.commit()
    

""" 설정 다중일 DB데이터 삽입용"""
def insertSettings(df, table):
    idx = df.index
    for i in tqdm(range(len(idx))) :
        _1 = str(idx[i][0])[:10] # 삽입일
        _2 = str(idx[i][1]) # 종목코드
        _3 = str(df.iloc[i][0]) # 한글종목명
        _4 = str(df.iloc[i][1])[:10] # 만기일
        _5 = str(df.iloc[i][2]) # 엘타
        _6 = str(df.iloc[i][3]) # 연물분류
        _7 = str(df.iloc[i][4]) # 듀레이션
        sql = "insert into "+table+" values ('"+_1 +"','"+_2+ "','"+_3+"','"+_4+"',"+_5+",'"+_6+"',"+_7+');'
        cursor.execute(sql)
    test_db.commit()

"""3선 10선 선택일 DB 삽입용"""
def insertKtbf(df, table, start_date, end_date):
    bools = []
    idx = df.index
    
    for i in idx:
        if i >= pd.Timestamp(start_date) and i <= pd.Timestamp(end_date):
            bools.append(True)
        else:
            bools.append(False)
    df = df[bools]
    print(df)
    for i in tqdm(range(len(df.index))) :
        _1 = str(df.index[i])[:10] # 일자
        _2 = str(df.iloc[i,0]) # 외국인합순매수수량
        _3 = str(df.iloc[i,1]) # 개인순매수수량
        _4 = str(df.iloc[i,2]) # 증권/선물순매수수량
        _5 = str(df.iloc[i,3]) # 투신순매수수량
        _6 = str(df.iloc[i,4]) # 사모펀드순매수수량
        _7 = str(df.iloc[i,5]) # 은행순매수수량
        _8 = str(df.iloc[i,6]) # 보험순매수수량
        _9 = str(df.iloc[i,7]) # 종신금순매수수량
        _10 = str(df.iloc[i,8]) # 연기금순매수수량
        _11 = str(df.iloc[i,9]) # 기타순매수수량
        _12 = str(df.iloc[i,10]) # 국가/지방순매수수량
        _13 = str(df.iloc[i,11]) #보험기금
        _14 = str(df.iloc[i,12]) # 은행
        _15 = str(df.iloc[i,13]) # 투신
        _16 = str(df.iloc[i,14]) # 외국인
        _17 = str(df.iloc[i,15]) # 증권
        _18 = str(df.iloc[i,16]) # 기타
        sql = "insert into "+table+" values ('"+_1 +"',"+_2+ ","+_3+","+_4+","+_5+","+_6+","+_7+","+_8+","+_9+","+_10+","+_11+","+_12+","+_13+","+_14+","+_15+","+_16+","+_17+","+_18 + ');'
        cursor.execute(sql)
    test_db.commit()


""" 국고 다중일 DB데이터 삽입용"""
def insertTreasury(df, table, start_date, end_date):
    bools = []
    idx = df.index
    for i in idx:
        if i[1] >= pd.Timestamp(start_date) and i[1] <= pd.Timestamp(end_date):
            bools.append(True)
        else:
            bools.append(False)
    df = df[bools]
    print(df)
    idx = df.index
    for i in tqdm(range(len(idx))) :
        _1 = str(idx[i][0]) # 종목코드
        _2 = str(idx[i][1])[:10] # 일자
        _3 = str(df.iloc[i,0]) # 외국인 순매수 거래량
        _4 = str(df.iloc[i,1]) # 은행 순매수 거래량
        _5 = str(df.iloc[i,2]) # 보험기금 순매수 거래량
        _6 = str(df.iloc[i,3]) # 자산운용(공모) 순매수 거래량
        _7 = str(df.iloc[i,4]) # 자산운용(사모) 순매수 거래량
        _8 = str(df.iloc[i,5]) # 종금 순매수 거래량
        _9 = str(df.iloc[i,6]) # 정부 순매수 거래량
        _10 = str(df.iloc[i,7]) # 기타법인 순매수 거래량
        _11 = str(df.iloc[i,8]) # 개인 순매수 거래량
        _12 = str(df.iloc[i,12]) # 낙찰금액
        _13 = str(df.iloc[i,11]) # 증권순매수(원)
        sql = "insert into "+table+" values ('"+_1 +"','"+_2+ "',"+_3+","+_4+","+_5+","+_6+","+_7+","+_8+","+_9+","+_10+","+_11+","+_12+","+_13+ ');'
        cursor.execute(sql)
    test_db.commit()


"""국선정보 data"""
future_df = pd.read_excel('sugup_ver1.2.xlsx', sheet_name='설정')
# future_df = future_df[['Unnamed: 19', 'Unnamed: 20', 'Unnamed: 22']]
future_df = future_df[['코드', '종목명', 'bpv']]
future_df = future_df.iloc[0:2][:]
future_df['조회일'] = str(datetime.today())[:10]
future_df.index = [future_df['조회일'], future_df['코드']]
future_df.drop(['조회일','코드'], axis=1, inplace=True)


"""국고채 델티, 듀레이션 설정 data"""
set_df = pd.read_excel('sugup_ver1.2.xlsx', sheet_name='설정')
set_df = set_df[['종목코드','한글종목명','만기일','델타','연물분류','듀레이션']]
set_df.dropna(inplace=True)
set_df['조회일'] = str(datetime.today())[:10]
set_df.index = [set_df['조회일'], set_df['종목코드']]
set_df.drop(['조회일','종목코드'], axis=1, inplace=True)


"""국고 data 만들기"""
# 화면번호 4516 엑셀
bid_amount_df  = pd.read_excel('bid_amount.xlsx',header = 2)
bid_amount_df = bid_amount_df[bid_amount_df['구분'] =='경쟁']
bid_amount_df = bid_amount_df[['입찰일','표준코드','낙찰금액']]
bid_amount_df.rename(columns={'입찰일':'일자', '표준코드':'종목코드'}, inplace=True)
bid_amount_df.set_index(['일자','종목코드'],inplace=True)
bid_amount_df['낙찰금액'] = bid_amount_df['낙찰금액']*1000000
# 원래 엑셀
treasury_df = pd.read_excel('sugup_ver1.2.xlsx', sheet_name='국고')
treasury_df = treasury_df.drop(['Unnamed: 0'],axis=1)
treasury_result_df = pd.DataFrame()

for i in range(int((treasury_df.shape[0]+1)/17)):
    df = treasury_df.loc[0+17*i:15+17*i]
    title = df.iloc[0][0]
    df = treasury_df.iloc[3+17*i:16+17*i].T
    df = df.dropna(subset=[3+17*i])
    df['종목코드'] = title
    df.loc['Unnamed: 1', '종목코드'] = '종목코드'
    df.columns = df.iloc[0][:]
    df.index = [df['종목코드'],df['일자']]
    df.drop(['일자', '종목코드'], axis=1, inplace=True)
    df.drop(['종목코드'], axis=0, inplace=True)
    df.fillna(0, inplace=True)
    treasury_result_df = pd.concat([treasury_result_df,df])

treasury_result_df = pd.merge(treasury_result_df, bid_amount_df, how='left', left_index=True, right_index=True)
treasury_result_df = treasury_result_df.fillna(0)
treasury_result_df['증권순매수(원)'] = treasury_result_df['낙찰금액'] - (treasury_result_df['외국인 순매수 거래량'] + treasury_result_df['은행 순매수 거래량'] + treasury_result_df['보험기금 순매수 거래량'] + treasury_result_df['자산운용(공모) 순매수 거래량'] + treasury_result_df['종금 순매수 거래량'] + treasury_result_df['기타법인 순매수 거래량'] + treasury_result_df['개인 순매수 거래량'])


""" test용 : treasury_result_df에서 21년 7월 22일만 걸른후 insert 준비"""
start_date = ''
end_date = ''
bools = []
idx = treasury_result_df.index
for i in idx:
    if i[1] >= pd.Timestamp(start_date) and i[1] <= pd.Timestamp(end_date):
        bools.append(True)
    else:
        bools.append(False)
tmp = treasury_result_df[bools]


"""선물 data"""
p=re.compile('Unnamed: [\d]+')
df3f = pd.read_excel('sugup_ver1.2.xlsx', sheet_name='선물', header =3)
for col in df3f.columns :
    if p.findall(str(col)):
        df3f = df3f.drop(columns=[col])
df3f = (df3f.loc[0:10]).T
df3f=df3f.fillna(0)
df3f.columns = df3f.iloc[0][:]
df3f.drop(['일자'], axis=0, inplace=True)
df3f.index.name = '일자'
df3f['보험기금'] = df3f['보험순매수수량'] + df3f['연기금순매수수량']
df3f['은행'] = df3f['은행순매수수량']
df3f['투신'] = df3f['투신순매수수량']
df3f['외국인'] = df3f['외국인합순매수수량']
df3f['증권'] = df3f['증권/선물순매수수량']
df3f['기타'] = -(df3f['보험기금']+df3f['은행']+df3f['투신']+df3f['외국인']+df3f['증권'])


# """ 3선 누적합 플로팅 출력(진행중) """
# start_date = pd.Timestamp('2021-06-12')
# end_date = pd.Timestamp('2021-07-22')
# print(df3f.loc[end_date])
# df3f_plot = df3f.loc[end_date:start_date,['보험기금','은행','투신','외국인','증권','기타']]

# df3f_plot = df3f_plot[::-1]
# tmp = df3f_plot.iloc[0].copy()
# for i in df3f_plot.index:
#     df3f_plot.loc[i] -= tmp
# df3f_plot = df3f_plot.cumsum()
# df3f_plot = df3f_plot*future_df.iloc[0]['bpv']/10000
# df3f_plot.plot()

df10f = pd.read_excel('sugup_ver1.2.xlsx', sheet_name='선물', header =29)
for col in df10f.columns :
    if p.findall(str(col)):
        df10f = df10f.drop(columns=[col])
df10f = (df10f.loc[0:10]).T
df10f=df10f.fillna(0)
df10f.columns = df10f.iloc[0][:]
df10f.drop(['일자'], axis=0, inplace=True)
df10f.index.name = '일자'
df10f['보험기금'] = df10f['보험순매수수량'] + df10f['연기금순매수수량']
df10f['은행'] = df10f['은행순매수수량']
df10f['투신'] = df10f['투신순매수수량']
df10f['외국인'] = df10f['외국인합순매수수량']
df10f['증권'] = df10f['증권/선물순매수수량']
df10f['기타'] = -(df10f['보험기금']+df10f['은행']+df10f['투신']+df10f['외국인']+df10f['증권'])

# """ 10선 누적합 플로팅 출력(진행중) """
# df10f_plot = df10f.loc[end_date:start_date,['보험기금','은행','투신','외국인','증권','기타']]
# df10f_plot = df10f_plot[::-1]
# tmp = df10f_plot.iloc[0].copy()
# for i in df10f_plot.index:
#     df10f_plot.loc[i] -= tmp
# df10f_plot = df10f_plot.cumsum()
# df10f_plot = df10f_plot*future_df.iloc[1]['bpv']/10000
# df10f_plot.plot()



"""조회화면 값 입력"""
# start_date = pd.Timestamp('2021-07-12')
# end_date = pd.Timestamp('2021-07-23')

cols = ['외국인','투신','보험기금','은행','증권','상장']
idx = ['2Y','3Y','3선','5Y','7Y','10Y','10선','물가','15Y','20Y','20원금','30Y','30원금','50Y','50원금','합계']
df = pd.DataFrame(columns=cols,index=idx)
df.fillna(0,inplace=True)

def getResultTable(df, asset) :
    tmp = set_df[set_df['연물분류']==asset]
    joined = pd.merge(treasury_result_df, tmp, left_index=True, right_index=True)
    bools =[]
    # print(joined.index)
    for i in joined.index:
        if i[1] >=start_date and i[1]<=end_date:
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
    df.loc[asset,'상장'] = round(np.sum(tmp_joined['상장잔액증감(원)'] * tmp_joined['델타'])/10**12,2)
    return df

df = getResultTable(df,'2Y')
df = getResultTable(df,'3Y')
df = getResultTable(df,'5Y')
df = getResultTable(df,'7Y')
df = getResultTable(df,'10Y')
df = getResultTable(df,'15Y')
df = getResultTable(df,'20Y')
df = getResultTable(df,'30Y')
df = getResultTable(df,'50Y')
df = getResultTable(df,'물가')
df = getResultTable(df,'20원금')
df = getResultTable(df,'30원금')
df = getResultTable(df,'50원금')

df.loc['3선','외국인'] = round(sum(df3f.loc[end_date:start_date, '외국인'] * future_df.iloc[0]['bpv']/10000),2)
df.loc['3선','투신'] = round(sum(df3f.loc[end_date:start_date, '투신'] * future_df.iloc[0]['bpv']/10000),2)
df.loc['3선','보험기금'] = round(sum(df3f.loc[end_date:start_date, '보험기금'] * future_df.iloc[0]['bpv']/10000),2)
df.loc['3선','은행'] = round(sum(df3f.loc[end_date:start_date, '은행'] * future_df.iloc[0]['bpv']/10000),2)
df.loc['3선','증권'] = round(sum(df3f.loc[end_date:start_date, '증권'] * future_df.iloc[0]['bpv']/10000),2)
# df.loc['3선','상장'] = sum(df3f.loc[end_date:start_date, '상장'] * future_df.iloc[0]['bpv']/10000)
df.loc['10선','외국인'] = round(sum(df10f.loc[end_date:start_date, '외국인'] * future_df.iloc[1]['bpv']/10000),2)
df.loc['10선','투신'] = round(sum(df10f.loc[end_date:start_date, '투신'] * future_df.iloc[1]['bpv']/10000),2)
df.loc['10선','보험기금'] = round(sum(df10f.loc[end_date:start_date, '보험기금'] * future_df.iloc[1]['bpv']/10000),2)
df.loc['10선','은행'] = round(sum(df10f.loc[end_date:start_date, '은행'] * future_df.iloc[1]['bpv']/10000),2)
df.loc['10선','증권'] = round(sum(df10f.loc[end_date:start_date, '증권'] * future_df.iloc[1]['bpv']/10000),2)
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

#%%


"""일별 선물정보 - bpv"""
insertInfoFutures(future_df, 'futures_bpv')

""" 일별 세팅 data DB에 추가 """
insertSettings(set_df, 'setting_delta')

"""일별 3선 10선 DB에 데이터 추가 """
start_date = '2021-08-04'
end_date = str(datetime.now()-pd.Timedelta(days=1))[:10]
insertKtbf(df10f, 'ktbf10y_vol', start_date, end_date)
insertKtbf(df3f, 'ktbf3y_vol', start_date, end_date)


start_date = str(datetime.now()-pd.Timedelta(days=1))[:10]
end_date = str(datetime.now())[:10]

"""일별 국고 data DB에 추가 """
insertTreasury(treasury_result_df, 'treasury_vol', '2018-01-01', end_date)

    