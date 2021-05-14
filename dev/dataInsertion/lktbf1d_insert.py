

import pandas as pd
import pymysql

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

# df_sample = pd.read_excel('reshape_real_1d.xlsx')


def setDfData(date_start, date_end) :
    sql = "SELECT * FROM `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

df = setDfData('2000-10-01','2099-04-30')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))

dfr = df.resample('D', closed='right').agg({'open': 'first',
                                                           'hi': 'max',
                                                           'lo': 'min',
                                                           'close': 'last'})
dfr= dfr.dropna()


"""
엑셀 데이터를 DB에 삽입해 주는 함
"""
def insertExcelData(cursor, df):

    for i in range(len(df.index)) :
        date = str(df.index[i])[:10]
        _open = str(df.iloc[i,0])
        hi = str(df.iloc[i,1])
        lo = str(df.iloc[i,2])
        close = str(df.iloc[i,3])
        sql = "insert into `lktb1day` ( date, open, hi, lo, close) values ('"  + date + "','" + _open + "','" + hi + "','" + lo +"','" + close +"'" + ');'
        cursor.execute(sql)
        
insertExcelData(cursor, dfr)

# test_db.commit()
