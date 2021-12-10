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

def insertSecData(cursor, df, table):
    for i in df.index :
        code = str(df.loc[i]['code'])
        date = str(df.loc[i]['date'])
        time = str(df.loc[i]['time'])[7:]
        o = str(df.loc[i]['open'])
        h = str(df.loc[i]['high'])
        l = str(df.loc[i]['low'])
        c = str(df.loc[i]['close'])
        vol = str(df.loc[i]['volume'])
        sql = "insert into " + table + " (code, date, time, open, high, low, close, volume) values ('" +code + "','" + date + "','" + time + "','" + o + "','" + h + "','" + l +"','" + c +"','" + vol +"'" + ');'
        cursor.execute(sql)
    print(df)
    test_db.commit()


def getlOneSecTable(day, tick_table) :
    df = setDfData(day, day, tick_table)
    
    pre_time = df.loc[0,'time']
    post_time = pre_time + pd.Timedelta(seconds=1)
    
    t_pre_time = df.loc[0,'time']
    t_post_time = pre_time + pd.Timedelta(seconds=1)
    
    
    rslt = pd.DataFrame(columns=['code','date','time','open','high','low','close','volume'])
    j = 0
    tmp = pd.DataFrame(columns=['code','date','time','close','volume'])
    bak = pd.DataFrame(columns=['code','date','time','close','volume'])
    
    last_time = df.loc[df.index[-1],'time']
    
    
    for i in df.index : 
        t = df.loc[i,'time']
        tmp.loc[i] = df.loc[i]
        if t == post_time :
            if not tmp.empty :
                
                bak.loc[i] = tmp.iloc[-1]
                tmp.drop(index = tmp.index[-1], inplace=True)
                
                rslt.loc[j,'code'] = tmp.iloc[0]['code']
                rslt.loc[j,'date'] = tmp.iloc[0]['date']
                rslt.loc[j,'time'] = post_time
                rslt.loc[j,'open'] = tmp.iloc[0]['close']
                rslt.loc[j,'high'] = max(tmp['close'])
                rslt.loc[j,'low'] = min(tmp['close'])
                rslt.loc[j,'close'] = tmp.iloc[-1]['close']
                rslt.loc[j,'volume'] = sum(tmp['volume'])
                j+=1        
                tmp = pd.DataFrame(columns=['code','date','time','close','volume'])
                tmp = bak.copy()
                bak = pd.DataFrame(columns=['code','date','time','close','volume'])
                
                pre_time = df.loc[i,'time']
                post_time = pre_time + pd.Timedelta(seconds = 1)
                        
        elif t > post_time :
    
            if not tmp.empty :
                
                bak.loc[i] = tmp.iloc[-1]
                tmp.drop(index = tmp.index[-1], inplace=True)
                
                rslt.loc[j,'code'] = tmp.iloc[0]['code']
                rslt.loc[j,'date'] = tmp.iloc[0]['date']
                rslt.loc[j,'time'] = post_time
                rslt.loc[j,'open'] = tmp.iloc[0]['close']
                rslt.loc[j,'high'] = max(tmp['close'])
                rslt.loc[j,'low'] = min(tmp['close'])
                rslt.loc[j,'close'] = tmp.iloc[-1]['close']
                rslt.loc[j,'volume'] = sum(tmp['volume'])
                j+=1        
                tmp = pd.DataFrame(columns=['code','date','time','close','volume'])
                tmp = bak.copy()
                bak = pd.DataFrame(columns=['code','date','time','close','volume'])
                
                t_pre_time = pre_time
                t_post_time = post_time
                
                pre_time = df.loc[i,'time']
                post_time = pre_time + pd.Timedelta(seconds = 1)
                
            
            while t > t_post_time :
                
                if last_time == t_post_time+pd.Timedelta(seconds = 1) :
                    rslt.loc[j,'code'] = df.loc[i,'code']
                    rslt.loc[j,'date'] = df.loc[i,'date']
                    rslt.loc[j,'time'] = t_post_time+pd.Timedelta(seconds = 1)
                    rslt.loc[j,'open'] = df.loc[i, 'close']
                    rslt.loc[j,'high'] = df.loc[i, 'close']
                    rslt.loc[j,'low'] = df.loc[i, 'close']
                    rslt.loc[j,'close'] = df.loc[i, 'close']
                    rslt.loc[j,'volume'] = df.loc[i, 'volume']
                    break;
                else :
                    rslt.loc[j,'code'] = rslt.loc[j-1,'code']
                    rslt.loc[j,'date'] = rslt.loc[j-1,'date']
                    rslt.loc[j,'time'] = t_post_time+pd.Timedelta(seconds = 1)
                    rslt.loc[j,'open'] = rslt.loc[j-1,'close']
                    rslt.loc[j,'high'] = rslt.loc[j-1,'close']
                    rslt.loc[j,'low'] = rslt.loc[j-1,'close']
                    rslt.loc[j,'close'] = rslt.loc[j-1,'close']
                    rslt.loc[j,'volume'] = 0
                    j+=1
                    
                    t_pre_time = t_post_time
                    t_post_time = t_pre_time + pd.Timedelta(seconds = 1)                   
    return rslt


start_date = str(datetime.datetime.today())[:10]
end_date = str(datetime.datetime.today())[:10]
validate_dates = sorted(list(setDfData(start_date, end_date, 'lktbf_day')['date']),reverse=True)
# validate_dates = list(setDfData('2021-11-17', '2021-11-17', 'lktbf_day')['date'])
tick_table = 'lktbftick'

for day in tqdm(validate_dates) :
    rslt = getlOneSecTable(day, tick_table)
    insertSecData(cursor, rslt, 'lktbf_1sec')        
