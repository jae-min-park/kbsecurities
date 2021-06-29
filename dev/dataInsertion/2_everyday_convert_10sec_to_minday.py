import pandas as pd
import datetime
import pymysql
from tqdm import tqdm

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)


def setDfData(date_start, date_end, table) :
    sql = "SELECT * FROM "+ table +" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

def insertMinData(cursor, df, table):
    for i in tqdm(df.index) :
        date = str(df.loc[i]['date'])
        time = str(df.loc[i]['time'])[7:]
        o = str(df.loc[i]['open'])
        h = str(df.loc[i]['high'])
        l = str(df.loc[i]['low'])
        c = str(df.loc[i]['close'])
        vol = str(df.loc[i]['volume'])
        sql = "insert into " + table + " (date, time, open, high, low, close, volume) values ('"  + date + "','" + time + "','" + o + "','" + h + "','" + l +"','" + c +"','" + vol +"'" + ');'
        cursor.execute(sql)
    test_db.commit()

def insertDayData(cursor, df, table):
    for i in tqdm(range(len(df.index))) :
        date = str(df.index[i])[:10]
        o = str(df.iloc[i,0])
        h = str(df.iloc[i,1])
        l = str(df.iloc[i,2])
        c = str(df.iloc[i,3])
        vol = str(df.iloc[i,4])
        sql = "insert into "+ table +" ( date, open, high, low, close, volume) values ('"  + date + "','" + o + "','" + h + "','" + l +"','" + c +"','" + vol +"'" + ');'
        cursor.execute(sql)
    test_db.commit()



start_date = str(datetime.datetime.today())[:10]
end_date = str(datetime.datetime.today())[:10]
# start_date = '2000-10-01'
# end_date = '2021-06-03'


"""10년선물 1분봉 처리"""
df = setDfData(start_date, end_date, 'lktbf_10sec')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
dfr = df.resample('min', label='right', closed='right').agg({'date': 'last','time': 'last','open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
dfr= dfr.dropna()
print(dfr)
insertMinData(cursor,dfr,'lktbf_min')

"""3년선물 1분봉 처리"""
df = setDfData(start_date, end_date, 'ktbf_10sec')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
dfr = df.resample('min', label='right', closed='right').agg({'date': 'last','time': 'last','open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
dfr= dfr.dropna()
print(dfr)
insertMinData(cursor,dfr,'ktbf_min')

"""달러원선물 1분봉 처리"""
df = setDfData(start_date, end_date, 'usdkrw_10sec')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
dfr = df.resample('min', label='right', closed='right').agg({'date': 'last','time': 'last','open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
dfr= dfr.dropna()
print(dfr)
insertMinData(cursor,dfr,'usdkrw_min')


"""10년선물 1일봉 처리"""
df = setDfData(start_date, end_date, 'lktbf_10sec')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
dfr = df.resample('D', closed='right').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
dfr= dfr.dropna()
print(dfr)
insertDayData(cursor, dfr, 'lktbf_day')

"""3년선물 1일봉 처리"""
df = setDfData(start_date, end_date, 'ktbf_10sec')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
dfr = df.resample('D', closed='right').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
dfr= dfr.dropna()
print(dfr)
insertDayData(cursor, dfr, 'ktbf_day')

"""달러원선물 1일봉 처리"""
df = setDfData(start_date, end_date, 'usdkrw_10sec')
df.index = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
dfr = df.resample('D', closed='right').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
dfr= dfr.dropna()
print(dfr)
insertDayData(cursor, dfr,'usdkrw_day')



