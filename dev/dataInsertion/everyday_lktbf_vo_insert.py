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
def insertExcelData(cursor, df, table):
    for i in range(len(df.index)) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])
        time = str(df.iloc[i,2])[7:]
        vwap =str(df.iloc[i,3])
        price = str(df.iloc[i,4])
        opn =str(df.iloc[i,5])
        high =str(df.iloc[i,6])
        low =str(df.iloc[i,7])        
        sql = "insert into "+table+" (code, date, time, vwap, price, open, high, low) values ('"  + code + "','" + date + "','" + time + "','" + vwap + "','"+ price +"','"+ opn +"','"+ high +"','"+ low +"'" + ');'
        cursor.execute(sql)
        

def setDfData(date_start, date_end, table) :
    sql = "SELECT * FROM "+ table + " where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

def reshapeVolandCommit(df_sample, li, table, unit_volume):
    for dt in li :
        df_today = df_sample[df_sample['date'] == dt]
        i = 0
        df_reshaped = pd.DataFrame(columns=['code', 'date', 'time', 'vwap', 'price', 'open','high','low'])
        
        # unit_volume = 200
        num_row = int(len(df_today) / unit_volume)
        
        
        opn = 0
        high = 0
        low = 100000
        
        for i in tqdm(range(num_row)):
            df_reshaped.at[i, 'code'] = df_today.iloc[i*unit_volume]['code']
            df_reshaped.at[i, 'date'] = dt
            df_reshaped.at[i, 'time'] = df_today.iloc[(i+1)*unit_volume - 1]['time']
            df_reshaped.at[i, 'vwap'] = round(df_today.iloc[i*unit_volume:(i+1)*unit_volume]['price'].mean(), 4)
            df_reshaped.at[i, 'price'] = round(df_today.iloc[(i+1)*unit_volume-1]['price'], 2)
            
            if i == 0 :
                opn = df_reshaped.at[0, 'price']
            if high < df_reshaped.at[i, 'price'] :
                high = df_reshaped.at[i, 'price']
            if low > df_reshaped.at[i, 'price'] :
                low = df_reshaped.at[i, 'price']
            
            df_reshaped.at[i,'open'] = opn
            df_reshaped.at[i,'high'] = high
            df_reshaped.at[i,'low'] = low
        print(df_reshaped)
        insertExcelData(cursor,df_reshaped,table)
        test_db.commit()

start_date ='2021-04-28'
end_date ='2021-06-03'

""" 국선 10년 10vol"""
df_sample = setDfData(start_date, end_date, 'lktb1vol')
li = sorted(list(set(df_sample['date'])))
reshapeVolandCommit(df_sample,li,'lktb10vol',10)

""" 국선 10년 30vol"""
df_sample = setDfData(start_date, end_date, 'lktb1vol')
li = sorted(list(set(df_sample['date'])))
reshapeVolandCommit(df_sample,li,'lktb30vol',30)

""" 국선 10년 50vol"""
df_sample = setDfData(start_date, end_date, 'lktb1vol')
li = sorted(list(set(df_sample['date'])))
reshapeVolandCommit(df_sample,li,'lktb50vol',50)

""" 국선 10년 100vol"""
df_sample = setDfData(start_date, end_date, 'lktb1vol')
li = sorted(list(set(df_sample['date'])))
reshapeVolandCommit(df_sample,li,'lktb100vol',100)

""" 국선 10년 200vol"""
df_sample = setDfData(start_date, end_date, 'lktb1vol')
li = sorted(list(set(df_sample['date'])))
reshapeVolandCommit(df_sample,li,'lktb200vol',200)


