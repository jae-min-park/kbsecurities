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

# df_sample = pd.read_excel('reshape_real_1d.xlsx')


def setDfData(date_start, date_end) :
    sql = "SELECT * FROM `lktb30vol` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

df_sample = setDfData('2017-09-19','2018-09-20')

"""
li는 setDfData의 param으로 준 날자들의 집합을 오름차순으로 정렬해 놓은 값이다.
"""
li = sorted(list(set(df_sample['date'])))

"""
소스코드의 경로에 result.xlsx 파일로 결과가 정리되고 날자별로 시트가 나온다.
"""
writer = pd.ExcelWriter('result.xlsx', engine='xlsxwriter')


"""
dt는 각 날자이고, df_today는 날자를 만족시키는 dataframe이다.
"""
for dt in li :
    df_today = df_sample[df_sample['date'] == dt]
    df_today = df_today[df_today['time']<=df_today.iloc[0]['time']+pd.Timedelta("00:15:00")]
    dti = df_today.index
    
    for dti_pre, dti_mid, dti_post in zip(dti, dti[1:], dti[2:]):
        
        opn = df_today.loc[dti_post,'open']
        close = df_today.loc[dti_post,'price']
        high = df_today.loc[dti_post,'high']
        low = df_today.loc[dti_post,'low']
        
    # 매수조건
        # if df_today.loc[i-1, 'rbPattern'] == True:
        #     df_today.loc[i, 'buy'] = df_today.loc[i, 'price']
        
        # REBOUND 이기 위한 조건
        # if df_today.at[i-1,'gvsPattern'] == True and close <= opn  :
        #     df_today.at[i,'rbPattern'] = True
        #     df_today.at[i,'rbPattern2'] = 'Y'
        
        # GRAVE STONE 이면 패턴 체크
        if round(abs(close - opn),2) <= 0.01 and round(min(opn,close)-low,2) <= 0.01 and round(high-max(opn,close),2) >= 0.04:
            df_today.at[dti_post, 'gvsPattern'] = True
            df_today.at[dti_post,'v'] = df_today.at[dti_post,'price'] - df_today.at[dti_mid, 'price']
            df_today.at[dti_mid,'v'] = df_today.at[dti_mid,'price'] - df_today.at[dti_pre, 'price']
            df_today.at[dti_post,'a'] = df_today.at[dti_post,'v'] - df_today.at[dti_mid,'v']
    print(df_today)
    df_today.to_excel(writer, sheet_name=str(dt))
writer.save()



