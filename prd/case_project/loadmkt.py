
"""
Created on Thu Sep 26 19:35:25 2019

Read & refresh Excel mkt data
Collected in one file to avoid messy configurations
"""

import os
import ddt_util as du
import pandas as pd
import datetime

FILE_KR = os.getcwd()+'\Kintra.xlsx'
FILE_KR_RT = os.getcwd()+'\MKT_KR_RT.xlsx'
FILE_US = os.getcwd()+"\\Uintra.xlsx"
FILE_HANMI = os.getcwd()+"\\MKT_HANMI.xlsx"
FILE_KR_CSV = os.getcwd()+'\MKT_KR.csv'
FILE_DAILY = os.getcwd()+'\daily.xlsx'
RT_FILENAME = os.getcwd()+'\RT.xlsx'


def read_ktb10y():
    """load KTBF 10Y mkt data"""
    USECOL = "B, C, E"
    df = du.read_excel_ust(FILE_KR, "KTBF", 1, USECOL)
    return df

def read_ktb3y():
    """load KTBF 3Y mkt data"""
    USECOL = "B, C, D"
    df = du.read_excel_ust(FILE_KR, "KTBF", 1, USECOL)
    return df

def read_ktbsp():
    """load KTB 3s10s mkt data """
    USECOL = "B, C, G"
    df = du.read_excel_ust(FILE_KR, "KTBF", 1, USECOL)
    return df

def read_usdkrw():
    """load USDKRW mkt data"""
    USECOL = "B, C, E"
    df = du.read_excel_ust(FILE_KR, "USDKRW", 1, USECOL)
    return df

def read_k200():
    """load K200 mkt data"""
    USECOL = "B, C, D"
    df = du.read_excel_ust(FILE_KR, "K200", 1, USECOL)
    return df

def read_ust10y():
    """load UST 10Y mkt data"""
    USECOL = "M, O, Q"
    df = du.read_excel_ust(FILE_US, "DB_UST", 1, USECOL)
    return df


def read_ust2y():
    """load UST 2Y mkt data"""
    USECOL = "M, O, P"
    df = du.read_excel_ust(FILE_US, "DB_UST", 1, USECOL)
    return df

def read_ust2s10s():
    """load UST 2s10s mkt data"""
    USECOL = "M, O, R"
    df = du.read_excel_ust(FILE_US, "DB_UST", 1, USECOL)
    return df

def read_ust5s30s():
    """load UST 5s30s mkt data"""
    USECOL = "M, O, S"
    df = du.read_excel_ust(FILE_US, "DB_UST", 1, USECOL)
    return df

def read_hanmi():
    """load HANMI mkt data"""
    USECOL = "B, C, K"
    df = du.read_excel_ust(FILE_HANMI, "HANMI", 1, USECOL)
    return df

def read_ktb10ycsv():
    """load KTBF 10Y mkt data in csv form"""
#    USECOL = [1, 2, 4]
    df = pd.read_csv(FILE_KR, header=1)
    return df

def read_daily():
    """
    Load daily bond market data using given COLUMN NAME
    
    update 2020.10.26 : spreads calcuation to be done in python not in excel
    Hence, applied "usecols=A:Z" to read outright data only.
    """
    
    USECOLS = "A : AE"
        
    df = pd.read_excel(FILE_DAILY, sheet_name='금리커브', header=2, index_col=0, usecols=USECOLS)

    df['일자'] = df.index
    df.index.names = ['Date']
    df = df.sort_index()
    
    """인포맥스 data 오류로 이종통화 0 생기는 경우 있음
    --> 바로위 행으로 대체
    """
    for fx in ['USDJPY', 'AUDUSD', 'EURUSD']:
        df[fx].replace(0, method='pad', inplace=True)
        #method 'pad'가 위에서 가져오는거 'bfill'은 아래 행에서
    if is_updatable():
        df = update_rt_daily(df)
    
    df = build_sp_daily(df)
    
    df = df.dropna()
# =============================================================================
#     holidays = du.read_casedates("HOLI_KR", mkt="KR")
#     for d in df_daily_all.index:
#         if d in holidays:
#             df_daily_all = df_daily_all.drop(index=d)
# =============================================================================
    
    return df

def update_rt_daily(df):
        
    #오늘이 영업일 & 오늘 RT file 변경 있을때에만 update수행
    today = datetime.date.today()

    
    if is_updatable():    
        #RT yield import
        df_ktb_rt = pd.read_excel(RT_FILENAME, sheet_name="KTBRT", header=5, index_col="ID")
        rt_sec = ['MSB1','MSB2','KTB3','KTB5','KTB10','KTB20','KTB30',
                  'FUT3','FUT10','FUT3PX','FUT10PX',
                  'IRS2','IRS3','IRS5', 'IRS10',
                  'US10','US2','US5','US30',
                  'DE5','DE10','DE30',
                  'USDKRW','USDJPY', 'EURUSD', 'AUDUSD']
        rt_dict = {}
        for sec in rt_sec:
            rt_dict[sec] = df_ktb_rt.loc[sec, 'LAST']
        
        #replace old data with RT yields
        tobe_replaced = df[today:].index
        for sec in rt_sec:
            df.loc[tobe_replaced, sec] = rt_dict[sec]
        
        #sp 컬럼도 update
        df = build_sp_daily(df)
    
    return df
    
    

def build_sp_daily(df):
    """build spread table"""
    df['1*3'] = df['KTB3'] - df['MSB1']
    df['2*3'] = df['KTB3'] - df['MSB2']
    df['2*3F'] = df['FUT3'] - df['MSB2']
    df['2*5'] = df['KTB5'] - df['MSB2']
    df['2*10'] = df['KTB10'] - df['MSB2']
    df['2*10F'] = df['FUT10'] - df['MSB2']
    df['3*5'] = df['KTB5'] - df['KTB3']
    df['3F*5'] = df['KTB5'] - df['FUT3']
    df['3*10'] = df['KTB10'] - df['KTB3']
    df['3*30'] = df['KTB30'] - df['KTB3']
    df['3F*30'] = df['KTB30'] - df['FUT3']
    df['5*10'] = df['KTB10'] - df['KTB5']
    df['5*10F'] = df['FUT10'] - df['KTB5']
    df['5*20'] = df['KTB20'] - df['KTB5']
    df['5*30'] = df['KTB30'] - df['KTB5']
    df['10*20'] = df['KTB20'] - df['KTB10']
    df['10*30'] = df['KTB30'] - df['KTB10']
    df['20*30'] = df['KTB30'] - df['KTB20']
    df['10F*30'] = df['KTB30'] - df['FUT10']
    df['2*5*10'] = 2*df['KTB5'] - df['MSB2'] - df['KTB10']
    df['3*5*10'] = 2*df['KTB5'] - df['KTB3'] - df['KTB10']
    df['3F*5*10'] = 2*df['KTB5'] - df['FUT3'] - df['KTB10']
    df['3*5*10F'] = 2*df['KTB5'] - df['KTB3'] - df['FUT10']
    df['3F*10F*30'] = 2*df['FUT10'] - df['FUT3'] - df['KTB30']
    df['5*10F*30'] = 2*df['FUT10'] - df['KTB5'] - df['KTB30']
    df['3*10*30'] = 2*df['KTB10'] - df['KTB3'] - df['KTB30']
    df['5*10*30'] = 2*df['KTB10'] - df['KTB5'] - df['KTB30']
    df['10*20*30'] = 2*df['KTB20'] - df['KTB10'] - df['KTB30']
    df['3F*10F'] = df['FUT10'] - df['FUT3']
    df['BS2'] = df['IRS2'] - df['MSB2']
    df['BS3'] = df['IRS3'] - df['KTB3']
    df['F3S3'] = df['IRS3'] - df['FUT3']
    df['F3S5'] = df['IRS5'] - df['FUT3']
    df['F10S5'] = df['IRS5'] - df['FUT10']
    df['BS5'] = df['IRS5'] - df['KTB5']
    df['BS10'] = df['IRS10'] - df['KTB10']
    df['US10-KR10'] = df['US10'] - df['KTB10']
    df['US10-KR30'] = df['US10'] - df['KTB30']
    df['US2*10'] = df['US10'] - df['US2']
    df['US5*10'] = df['US10'] - df['US5']
    df['US5*30'] = df['US30'] - df['US5']
    df['US10*30'] = df['US30'] - df['US10']
    df['US2*5*10'] = 2*df['US5'] - df['US2'] - df['US10']
    df['US5*10*30'] = 2*df['US10'] - df['US5'] - df['US30']
    df['JPYKRW'] = df['USDKRW'] / df['USDJPY']
    df['EURJPY'] = df['EURUSD'] * df['USDJPY']
    df['JPYEUR'] = 1/df['EURJPY'] * 100
    df['US10PX'] = 100-10*df['US10']
    
    return df

    
def get_dfint_daily(df_daily_all, sec):
    """
    Select timeseries of interest from df_daily_all
    parameter
    df_daily_all : Whole Dataframe from Excel file (infomax)
    COL_NAME : Name of Column contaning timeseries data of interest
    """
       
    dfint = df_daily_all[['일자', sec]]
    dfint = dfint.rename(columns= {sec:'종가'})    
    return dfint
    
def remove_holidays_daily(ld, country="KR" ):
    """
    list of dates를 받아서 휴일리스트에 있는 날들을 제거
    where, 휴일리스트는 CASE_dates_KR.xlsx의 HOLI_KR
    미국 휴일리스트는 CASE_dates_KR.xlsx의 HOLI_US
    mkt="KR"은 CASE_dates_KR.xlsx 파일을 사용하기 위함으로
    추후 한 파일로 통합
    """
    if country == "US":
        holidays = du.read_casedates("HOLI_US", mkt="KR")
    elif country == "KR":
        holidays = du.read_casedates("HOLI_KR", mkt="KR")
    else:
        print ("Wrong country code")
        
    
    return [d for d in ld if d not in holidays] 

def ohlc_ktbf(sec="10y"):
    """
    Load KTBF 10Y daily OHLC data
    Parameters:
        sec : "10y" or "3y" 
    Returns: Dataframe of OHLC KTB futures    
    """
    if sec == "10y": usecol = "A:E"
    elif sec == "3y": usecol = "J:O"
    df = pd.read_excel(RT_FILENAME, 
                       sheet_name="KTBF_OHLC", 
                       header=2, usecols=usecol, index_col=0)
    
    df = df.rename(columns={"시가":"open", \
                            "고가":"high",
                            "저가":"low",
                            "현재가":"close"})
    df.index.name = 'date'
    df = df.sort_index()
    
    diff_days = [1,2,3,4,5, -1,-2,-3,-4,-5]
    
    for n in diff_days:
        if n >= 0:
            col_name = 'close_'+str(n)+'d_chg'
            df[col_name] = 100*df.close.diff(periods=n)
        if n < 0:
            col_name = 'close_next_'+str(-n)+'d_chg'
            df[col_name] = -100*df.close.diff(periods=n)
    
    
    
    return df

def update_futures_rt(df, fut_name='10y'):
    """update 3선, 10선, SP rt data"""
    if is_updatable():
        USECOL = {'3y' : 'B, C, D',
                  '10y' : 'B, C, E',
                  'sp' : 'B, C, G'}
        dfrt = du.read_excel_ust(RT_FILENAME, "KTBF", 1, USECOL[fut_name])
        lastpx = dfrt['종가'][-1]
        
        today = pd.Timestamp(datetime.date.today())
        tomrw = today + pd.Timedelta(days=1)
      
        df.loc[today, '종가'] = dfrt.loc[today, '종가']
        df.loc[tomrw:, '종가'] = lastpx
        
    return df

def update_ust_rt(df, name='10y'):
    """update UST rt data"""
    if is_updatable():
        USECOL = {'2y' : 'M,O,P',
                  '10y' : 'M,O,Q',
                  '2s10s' : 'M,O,R',
                  '5s30s' : 'M,O,S'              
                  }
        dfrt = du.read_excel_ust(RT_FILENAME, "DB_UST", 1, USECOL[name])
        lastpx = dfrt['종가'][-1]
        
        today = pd.Timestamp(datetime.date.today())
        tomrw = today + pd.Timedelta(days=1)
      
        df.loc[today, '종가'] = dfrt['종가']
        df.loc[tomrw:, '종가'] = lastpx
        
    return df

def is_updatable():
    # if 오늘==영업일 & RT파일수정일 == 오늘 --> True
    
    #오늘이 영업일인가?
    today = datetime.date.today()
    is_weekday = today.weekday() < 5 #if toay is weekday (휴일로직은 daily에 쓰지 않는다)
    
    #RT파일이 오늘 수정됨?
    time_updated = os.path.getmtime(RT_FILENAME)
    date_updated = datetime.datetime.fromtimestamp(time_updated).date()
    is_RT_updated = today == date_updated
    
    return is_weekday & is_RT_updated

def read_lfjk():
    """
    load LF(10년선물) JK(JPYKRW) mkt data
    returns (dflf, dfjk) with 종가 columns in each dataframe
    """
    LFJK_FILENAME = os.getcwd()+'\LFJK.xlsx'
    USECOL = "B, C, G, H"
    df = pd.read_excel(LFJK_FILENAME, sheet_name="lfjk_main", header=1, usecols=USECOL)
    df = df.dropna()
    df = df.sort_values(['일자', '시간'], ascending=[True, True])
    df.loc[:,'datetime'] = pd.to_datetime(df.일자.astype(str) + ' ' + df.시간.astype(str))
    df.index = df['datetime']
    df.index.name = 'datetime'
    df = df.drop('datetime', axis=1)
    
    dfjk = df.drop('LKTBF', axis=1)
    pxcolname = 'JPYKRW' #마지막 컬럼이 종가열임
    dfjk = dfjk.rename(columns = {pxcolname:'종가'})
    
    dflf = df.drop('JPYKRW', axis=1)
    pxcolname = 'LKTBF' #마지막 컬럼이 종가열임
    dflf = dflf.rename(columns = {pxcolname:'종가'})
    
    return (dflf, dfjk, df)

def read_hanmi10():
    """
    load hanmi10 mkt data
    returns dfhanmi10
    """
    FILENAME = os.getcwd()+'\hanmi10.xlsx'
    USECOL = "A, J"
    df = pd.read_excel(FILENAME, sheet_name="hanmi_main", header=1, usecols=USECOL)
    df = df.dropna()
    df = df.sort_values('datetime', ascending=True)
    # df.loc[:,'datetime'] = pd.to_datetime(df.일자.astype(str) + ' ' + df.시간.astype(str))
    df.index = df['datetime']
    df = df.drop('datetime', axis=1)
    
    # df = df.rename(columns = {pxcolname:'종가'})
    
    return df