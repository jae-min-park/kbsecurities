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
    # df1 = df[1]
    # df2 = df[2]
    # df = df1.append(df2)
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

    
"""국10년선물 10초봉"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\국10_10초봉.xlsx', sheet_name=[1])
insertData(cursor, df_excel, 'lktbf_10sec')

"""국3년선물 10초봉"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선3년\국3_10초봉.xlsx', sheet_name=[1])
insertData(cursor, df_excel, 'ktbf_10sec')


"""달러원선물 10초봉"""
df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\달러원선물\달러원_10초봉.xlsx', sheet_name=[1])
insertData(cursor, df_excel, 'usdkrw_10sec')

