

import pandas as pd
import pymysql

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)


df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\인포맥스_10초봉.xlsx', sheet_name=[1])
# print(df)
# df1 = df[1]
# df2 = df[2]
# df = df1.append(df2)
df_excel = df_excel[1]

for i in range(len(df_excel.index)) :
    code = str(df_excel.iloc[i,0])
    date = str(df_excel.iloc[i,1])[0:10]
    time = str(df_excel.iloc[i,2])
    _open = str(df_excel.iloc[i,3])
    _hi = str(df_excel.iloc[i,4])
    _lo = str(df_excel.iloc[i,5])
    _close = str(df_excel.iloc[i,6])
    vol = str(df_excel.iloc[i,7])
    print(code, date, time, _open, _hi, _lo, _close, vol)



def insertExcelData(cursor):
    df_excel = pd.read_excel('D:\dev\kbsecurities\dev\dataInsertion\국선10년\인포맥스_10초봉.xlsx', sheet_name=[1])
    # print(df)
    # df1 = df[1]
    # df2 = df[2]
    # df = df1.append(df2)
    df_excel = df_excel[1]
    
    for i in range(len(df_excel.index)) :
        code = str(df_excel.iloc[i,0])
        date = str(df_excel.iloc[i,1])[0:10]
        time = str(df_excel.iloc[i,2])
        _open = str(df_excel.iloc[i,3])
        _hi = str(df_excel.iloc[i,4])
        _lo = str(df_excel.iloc[i,5])
        _close = str(df_excel.iloc[i,6])
        vol = str(df_excel.iloc[i,7])
        print(code, date, time, _open, _hi, _lo, _close, vol)
        # sql = "insert into `lktbf10sec` (code, date, time, open, hi, lo, close, vol) values ('" + code+ "','" + date + "','" + time + "','" + _open + "','" + _hi + "','" + _lo + "','" + _close + "','"+ vol +"'" + ');'
        # cursor.execute(sql)

insertExcelData(cursor)


def setDfData(date_start, date_end) :
    sql = "SELECT * FROM `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

df = setDfData('2000-04-26','2099-04-27')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))

dfr = df.resample('min', label='right', closed='right').agg({'date': 'last',
                                                             'time': 'last',
                                                             'open': 'first',
                                                             'hi': 'max',
                                                             'lo': 'min',
                                                             'close': 'last',
                                                             'vol': 'sum'})
dfr= dfr.dropna()


"""
엑셀 데이터를 DB에 삽입해 주는 함
"""
def insertExcelData(cursor, df):

    for i in df.index :
        date = str(df.loc[i]['date'])
        _open = str(df.loc[i]['open'])
        hi = str(df.loc[i]['hi'])
        lo = str(df.loc[i]['lo'])
        close = str(df.loc[i]['close'])
        time = str(df.loc[i]['time'])[7:]
        datetime = str(i)
        vol = str(df.loc[i]['vol'])
        sql = "insert into `lktb1min` ( datetime, date, time, open, hi, lo, close, vol) values ('"  + datetime + "','"+ date + "','" + time + "','" + _open + "','" + hi + "','" + lo +"','" + close +"','" + vol +"'" + ');'
        cursor.execute(sql)
        
insertExcelData(cursor, dfr)

test_db.commit()
