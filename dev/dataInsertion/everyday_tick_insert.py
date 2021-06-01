import pandas as pd
from tqdm import tqdm
import pymysql

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                          # host = '211.232.156.57',
                          host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

"""
엑셀 데이터를 DB에 삽입해 주는 함
"""
def insertKtbData(cursor):
    df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선3년\ktbtickdata수집.xlsx', sheet_name=[1])
    # df1 = df[1]
    # df2 = df[2]
    # df = df1.append(df2)
    df = df_excel[1]
    print(df)
    
    for i in range(len(df.index)) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])[0:10]
        time = str(df.iloc[i,2])
        # _open = str(df_excel.iloc[i,3])
        # _hi = str(df_excel.iloc[i,4])
        # _lo = str(df_excel.iloc[i,5])
        _close = str(df.iloc[i,3])
        vol = str(df.iloc[i,4])
        
        sql = "insert into `ktbftick` (code, date, time, close, vol) values ('" + code+ "','" + date + "','" + time + "','" + _close + "','"+ vol +"'" + ');'
        cursor.execute(sql)

def insertLktbData(cursor):
    df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\lktbtickdata수집.xlsx', sheet_name=[1])
    # df1 = df[1]
    # df2 = df[2]
    # df = df1.append(df2)
    df = df_excel[1]
    print(df)
    
    for i in range(len(df.index)) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])[0:10]
        time = str(df.iloc[i,2])
        # _open = str(df_excel.iloc[i,3])
        # _hi = str(df_excel.iloc[i,4])
        # _lo = str(df_excel.iloc[i,5])
        _close = str(df.iloc[i,3])
        vol = str(df.iloc[i,4])
        
        sql = "insert into `lktbftick` (code, date, time, close, vol) values ('" + code+ "','" + date + "','" + time + "','" + _close + "','"+ vol +"'" + ');'
        cursor.execute(sql)

def insertUsdKrwData(cursor):
    df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\원달러선물\달러원선물rawdata수집.xlsx', sheet_name=[1])
    # df1 = df[1]
    # df2 = df[2]
    # df = df1.append(df2)
    df = df_excel[1]
    print(df)
    
    for i in range(len(df.index)) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])[0:10]
        time = str(df.iloc[i,2])
        # _open = str(df_excel.iloc[i,3])
        # _hi = str(df_excel.iloc[i,4])
        # _lo = str(df_excel.iloc[i,5])
        _close = str(df.iloc[i,3])
        vol = str(df.iloc[i,4])
        
        sql = "insert into `usdkrwtick` (code, date, time, close, vol) values ('" + code+ "','" + date + "','" + time + "','" + _close + "','"+ vol +"'" + ');'
        cursor.execute(sql)
    

insertLktbData(cursor)
test_db.commit()    
insertKtbData(cursor)
test_db.commit()
insertUsdKrwData(cursor)
test_db.commit()

