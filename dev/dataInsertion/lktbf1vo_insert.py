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
def insertExcelData(cursor, df):

    for i in range(len(df.index)) :
        code = str(df.iloc[i,0])
        date = str(df.iloc[i,1])
        time = str(df.iloc[i,2])[7:]
        price = str(df.iloc[i,3])
        sql = "insert into `lktb1vol` (code, date, time, price) values ('"  + code + "','" + date + "','" + time + "','" + price +"'" + ');'
        cursor.execute(sql)
        

def setDfData(date_start, date_end) :
    sql = "SELECT * FROM `lktbftick` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

df_sample = setDfData('2017-09-21','2021-04-27')
print(df_sample)
print(len(df_sample.index))

li = sorted(list(set(df_sample['date'])))


for dt in li :
    df_all = pd.DataFrame(columns=['code', 'date', 'time', 'price'])
    df_today = df_sample[df_sample['date'] == dt]
    i = 0
    total_row = len(df_today.index)
    
    for row in tqdm(range(total_row)):
        code = df_today.iloc[row]['code']
        t = df_today.iloc[row]['time']
        p = df_today.iloc[row]['close']
        for v in range(df_today.iloc[row]['vol']):
            i += 1
    #             print(i)
            df_all.at[i,'code'] = code
            df_all.at[i,'date'] = dt
            df_all.at[i,'time'] = t
            df_all.at[i,'price'] = p

    insertExcelData(cursor,df_all)
    
test_db.commit()