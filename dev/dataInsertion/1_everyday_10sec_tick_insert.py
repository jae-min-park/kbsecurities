import pandas as pd
from tqdm import tqdm
import pymysql

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

"""
엑셀 10초 데이터를 DB에 삽입해 주는 함수
"""
def insert10secData(cursor, df_excel, table):
    df = df_excel[1]
    print(df)
    
    for i in tqdm(range(len(df.index))) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])[0:10]
        time = str(df.iloc[i,2])
        o = str(df.iloc[i,3])
        h = str(df.iloc[i,4])
        l = str(df.iloc[i,5])
        c = str(df.iloc[i,6])
        vol = str(df.iloc[i,7])
        
        sql = "insert into "+table+" (code, date, time, open, high, low, close, volume) values ('" + code+ "','" + date + "','" + time + "','" + o + "','"+ h + "','"+ l + "','"+ c + "','"+ vol +"'" + ');'
        cursor.execute(sql)
    test_db.commit()


"""
엑셀 틱 데이터를 DB에 삽입해 주는 함수
"""
def insertTickData(cursor, df_excel, table):

    df = df_excel[2]
    print(df)
    
    for i in tqdm(range(len(df.index))) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])[0:10]
        time = str(df.iloc[i,2])
        close = str(df.iloc[i,3])
        vol = str(df.iloc[i,4])
        
        sql = "insert into " +table +" (code, date, time, close, volume) values ('" + code+ "','" + date + "','" + time + "','" + close + "','"+ vol +"'" + ');'
        cursor.execute(sql)
    test_db.commit()


    

"""국10년선물 10초봉"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\lktb_data.xlsx', sheet_name=[1])
insert10secData(cursor, df_excel, 'lktbf_10sec')

"""국10년선물 틱데이터"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\lktb_data.xlsx', sheet_name=[2])
insertTickData(cursor, df_excel, 'lktbftick')

"""국3년선물 10초봉"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선3년\ktb_data.xlsx', sheet_name=[1])
insert10secData(cursor, df_excel, 'ktbf_10sec')

"""국3년선물 틱데이터"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선3년\ktb_data.xlsx', sheet_name=[2])
insertTickData(cursor, df_excel, 'ktbftick')

"""달러원선물 10초봉"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\달러원선물\krwusd_data.xlsx', sheet_name=[1])
insert10secData(cursor, df_excel, 'usdkrw_10sec')

"""달러원선물 틱데이터"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\달러원선물\krwusd_data.xlsx', sheet_name=[2])
insertTickData(cursor, df_excel, 'usdkrwtick')
