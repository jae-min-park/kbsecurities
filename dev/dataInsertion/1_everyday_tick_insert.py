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
def insertData(cursor, df_excel, table):

    df = df_excel[1]
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


"""국10년선물 틱데이터"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\lktbtickdata수집.xlsx', sheet_name=[1])
insertData(cursor, df_excel, 'lktbftick')

"""국3년선물 틱데이터"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선3년\ktbtickdata수집.xlsx', sheet_name=[1])
insertData(cursor, df_excel, 'ktbftick')

"""달러원선물 틱데이터"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\달러원선물\달러원선물tickdata수집.xlsx', sheet_name=[1])
insertData(cursor, df_excel, 'usdkrwtick')
