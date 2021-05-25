

import pandas as pd
import pymysql

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)


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
