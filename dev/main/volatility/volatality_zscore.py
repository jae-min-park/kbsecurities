import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pymysql
import re
from tqdm import tqdm

import warnings
# warnings.filterwarnings('error', category=UserWarning)
warnings.filterwarnings(action='ignore')

font_path = "C:\Windows\Fonts\\batang.ttc"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)


test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                           host = '211.232.156.57',
                          # host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

""" table이 param으로 주어지면 해당 table에서 날자 리스트를 오름차순으로 뽑아주는 함수 """
def getDateList(table, start_date = '2000-10-01', end_date='2099-04-30'):
    df = setDfData(start_date, end_date, table)
    li = sorted(list(set(df['date'])))
    return li

"""데이터 가져오기"""
def setDfData(date_start, date_end, table, skip_datetime_col="N") :
    sql = "SELECT * FROM "+ table +" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    df = pd.DataFrame(result)
    
    if skip_datetime_col == "Y":
        return df
    else:
        df['datetime'] = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
    #     df['datetime'] = pd.to_datetime(df.date.astype(str) + ' ' + df.time.astype(str).apply(lambda x: x[7:]))
        # df.set_index('datetime', inplace=True)
    return df


start_date = '2021-01-05'
end_date = '2021-09-10'

start_date = '2020-01-03'
end_date = '2020-12-02'

start_date = '2019-01-03'
end_date = '2019-11-13'

start_date = '2018-01-03'
end_date = '2018-11-14'

start_date = '2017-01-03'
end_date = '2017-11-15'

datelist = getDateList('ktbf_min',start_date,end_date)

df = pd.DataFrame(index=datelist, columns = ['volume','volatality','z-score'])

# df_min = setDfData(start_date,end_date,'ktbf_min')
# df_min = df_min[df_min['time'] <= pd.Timedelta('10:00:00')]

# for date in datelist :
#     tmp = df_min[df_min['date'] == date]
    
#     df.loc[date,'volume'] = round(sum(tmp['volume']),2)
#     df.loc[date,'volatality'] = round(max(tmp['high'])- min(tmp['low']),2)

df_days = setDfData(start_date,end_date,'lktbf_day' , skip_datetime_col='Y')
i=0
for date in datelist :
    tmp = df_days[df_days['date'] == date]
    
    df.loc[date,'volume'] = tmp['volume'][i]
    df.loc[date,'volatality'] = round(tmp['high'][i]- tmp['low'][i],2)
    i+=1

df.reset_index(inplace=True)
df.rename(columns={'index':'date'}, inplace=True)

rslt = pd.DataFrame(columns=['corrcoef'])
for N in range(2,99) :
    for i in range(N, len(df)+1) :
        sigma = np.std(df.loc[i-N:i]['volume'])
        u = np.mean(df.loc[i-N:i]['volume'])
        df.loc[i-1,'z-score'] = (df.iloc[i-1]['volume'] - u)/sigma
        # print(df.loc[i-1, 'date'], df.loc[i-1,'z-score'])
        
        # df.iloc[i,'sigma'] = np.std(df.iloc[i-N:i,'volume'])
    # vol = sum(df['volume'])
    X = df.volatality.values[N:]
    Y = df['z-score'].values[N:]
    
    plt.scatter(X,Y, alpha = 0.5)
    plt.title(f'{start_date[:4]}년도 {N}윈도우 상관관계 산점도')
    plt.xlabel('변동성')
    plt.ylabel('z-score')
    plt.show()
    
    rslt.loc[N, 'corrcoef'] = np.corrcoef(X.astype(float),Y.astype(float))[0,1]
    
                  
