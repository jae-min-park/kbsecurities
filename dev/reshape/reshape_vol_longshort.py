import pandas as pd
from tqdm import tqdm
import pymysql
from matplotlib import pyplot as plt

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                          # host = '211.232.156.57',
                          host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

# df_sample = pd.read_excel('reshape_real_1d.xlsx')


def setDfData(date_start, date_end) :
    sql = "SELECT * FROM `lktb50vol` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    # sql = "select * from `lktbf10sec` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

df_sample = setDfData('2017-10-11','2017-10-11')

"""
li는 setDfData의 param으로 준 날자들의 집합을 오름차순으로 정렬해 놓은 값이다.
"""
li = sorted(list(set(df_sample['date'])))

"""
소스코드의 경로에 result.xlsx 파일로 결과가 정리되고 날자별로 시트가 나온다.
"""
writer = pd.ExcelWriter('precise.xlsx', engine='xlsxwriter')


"""
엑셀에 요약본 작성하려고 만드는 dataframe
"""
tag_list = "long_sum", "long_len", "long_avg", "short_sum", "short_len", "short_avg", "total", "long_win", "long_lose", "short_win","short_lose"
df_tag = pd.DataFrame(columns=tag_list)


preday_close = 0
"""
dt는 각 날자이고, df_today는 날자를 만족시키는 dataframe이다.
"""
pt = 0.10
lc = -0.10

for dt in li :
    df_today = df_sample[df_sample['date'] == dt]
    # df_today = df_today[df_today['time']<=df_today.iloc[0]['time']+pd.Timedelta("00:15:00")]
    dti = df_today.index
    long = False
    long_win = 0
    long_lose = 0 
    long_price = 0
    long_index = 0
    long_profit = []
    short = False
    short_win = 0
    short_lose = 0 
    short_price = 0 
    short_index = 0
    short_profit=[]
    
    for dti_pre, dti_mid, dti_post in zip(dti, dti[1:], dti[2:]):
        opn = df_today.loc[dti_mid,'open']
        close = df_today.loc[dti_mid,'price']
        high = df_today.loc[dti_mid,'high']
        low = df_today.loc[dti_mid,'low']
        
    # 매수조건
        # if df_today.loc[i-1, 'rbPattern'] == True:
        #     df_today.loc[i, 'buy'] = df_today.loc[i, 'price']
        
        # REBOUND 이기 위한 조건
        # if df_today.at[i-1,'gvsPattern'] == True and close <= opn  :
        #     df_today.at[i,'rbPattern'] = True
        #     df_today.at[i,'rbPattern2'] = 'Y'

        v = df_today.at[dti_post,'v'] = df_today.at[dti_post,'price'] - df_today.at[dti_mid, 'price']
        df_today.at[dti_mid,'v'] = df_today.at[dti_mid,'price'] - df_today.at[dti_pre, 'price']
        v2 = df_today.at[dti_post,'v2'] = df_today.at[dti_post,'price'] - df_today.at[dti_pre, 'price']
        a = df_today.at[dti_post,'a'] = df_today.at[dti_post,'v'] - df_today.at[dti_mid,'v']
        
        # 롱진입, 숏진입 초입부
        if not long and round(abs(close - opn),2) <= 0.01 and a>0 and v > 0 and v2>0:
            long = True
            long_index=dti_post
            long_price = df_today.loc[dti_mid,'price']
        elif not short and round(abs(close - opn),2) <= 0.01 and a<0 and v < 0 and v2<0:
            short = True
            short_index = dti_post
            short_price = df_today.loc[dti_post,'price']
        # 롱 익절 및 롱 손절후 숏으로 전환
        if long and df_today.loc[dti_mid,'price'] > long_price + pt:
            win = pt
            # win = round(df_today.loc[dti_post,'price'] - long_price,2)
            # print(str(df_today.loc[dti_mid,'date'])+" win:"+str(win))
            plt.axvspan(long_index, dti_post, facecolor="red")
            long_win+=1
            long_profit.append(win)
            long=False
        elif long and df_today.loc[dti_mid,'price'] <= long_price +lc:
            plt.axvspan(long_index, dti_post, facecolor="blue")
            lose = lc
            # lose = round(df_today.loc[dti_post,'price']-long_price,2)
            print(str(df_today.loc[dti_post,'time'])+" lose:"+str(lose))
            long = False
            long_profit.append(lose)
            long_lose+=1
            
            # short = True
            # short_index = dti_post
            # short_price = df_today.loc[dti_post,'price']
        # 숏 익절 및 숏 손절후 롱으로 전환
        elif short and df_today.loc[dti_mid,'price'] <= short_price - pt:
            win = pt
            # win = round(short_price - df_today.loc[dti_post,'price'],2)
            # print(str(df_today.loc[dti_mid,'date'])+" win:"+str(win,2))
            plt.axvspan(short_index, dti_post, facecolor="yellow")
            short_profit.append(win)
            short_win+=1
            short=False
        elif short and df_today.loc[dti_mid,'price'] >= short_price -lc:
            plt.axvspan(short_index, dti_post, facecolor="grey")
            lose = lc
            # lose = round(short_price - df_today.loc[dti_post,'price'],2)
            print(str(df_today.loc[dti_post,'time'])+" lose:"+str(lose))
            short = False
            short_lose+=1
            short_profit.append(lose)
            
            # long = True
            # long_index = dti_post
            # long_price = df_today.loc[dti_post,'price']
        # 마지막 인덱스에서 처분    
        elif long and dti_post == dti[-1]:
            plt.axvspan(long_index, dti_post, facecolor="black")
            last = round(df_today.loc[dti_post,'price'] - long_price,2)
            # (str(df_today.loc[dti_post,'date'])+" last:"+str(last))
            if last > 0 :
                long_win = 0 
            else:
                long_lose = 0 
            long_profit.append(last)
            long = False
        elif short and dti_post == dti[-1]:
            plt.axvspan(short_index, dti_post, facecolor="black")
            last = round(short_price - df_today.loc[dti_post,'price'],2)
            # print(str(df_today.loc[dti_post,'date'])+" last:"+str(last))
            if last > 0 :
                short_win = 0 
            else:
                short_lose = 0 
            short_profit.append(last)
            short = False
        
        # near preday_close, today_open 인지 체크
        # if not short and round(abs(close - opn),2) <= 0.01 and a<0 and v < 0 and v2<0:
        #     # plt.axvspan(dti_mid, dti_post, facecolor="red")
        #     short = True
        #     short_index=dti_mid
        #     short_price = df_today.loc[dti_post,'price']
        # # if short and df_today.loc[dti_post,'a'] > 0.01 :
        # if short and df_today.loc[dti_mid,'price'] < short_price - 0.04:
        #     win = short_price - df_today.loc[dti_post,'price']
        #     print(str(df_today.loc[dti_mid,'date'])+" win:"+str(round(win,2)))
        #     plt.axvspan(short_index, dti_post, facecolor="gray")
        #     # plt.fill_between(dti[short_index:dti_post+1],df_today['price'][short_index:dti_post+1], alpha=0.5)
        #     short=False
        # elif short and v >0 and v2>0 and a>0:
        #     plt.axvspan(short_index, dti_mid, facecolor="red")
        #     lose = df_today.loc[dti_post,'price'] - short_price
        #     print(str(df_today.loc[dti_post,'date'])+" lose:"+str(round(lose,2)))
        #     short = False
        # elif short and df_today.loc[dti_mid,'price'] > short_price + 0.03:
        #     plt.axvspan(short_index, dti_mid, facecolor="red")
        #     lose = df_today.loc[dti_post,'price'] - short_price
        #     print(str(df_today.loc[dti_post,'date'])+" lose:"+str(round(lose,2)))
        #     short = False
        # elif short and dti_post == dti[-1]:
        #     plt.axvspan(short_index, dti_post, facecolor="red")
        #     lose = df_today.loc[dti_post,'price'] - short_price
        #     print(str(df_today.loc[dti_post,'date'])+" lose:"+str(round(lose,2)))
        #     short = False
        # if round(abs(close - opn), 2) <= 0.01 and a<0 and v < 0:
        #     df_today.at[dti_post,'todayOpn'] = opn
        #     plt.axvspan(dti_mid, dti_post, facecolor="blue")
            
        # GRAVE STONE 이면 패턴 체크
        if round(abs(close - opn),2) <= 0.01 and round(min(opn,close)-low,2) <= 0.01 and round(high-max(opn,close),2) >= 0.04:
            df_today.at[dti_post, 'gvsPattern'] = True
    preday_close = df_today.iloc[-1]['price']
    # print(df_today)
    
    print("long:"+str(long_profit)+ str(sum(long_profit))+ ", " + str(len(long_profit))+ " " + str(0))
    print("short:"+str(short_profit)+ str(sum(short_profit))+ ", " + str(len(short_profit))+ " " + str(0))

    df_tag.loc[dt] = [sum(long_profit), len(long_profit), 0, sum(short_profit), len(short_profit), 0, (sum(long_profit)+sum(short_profit)), long_win, long_lose, short_win, short_lose]
    df_tag.to_excel(writer)
    
    plt.plot(dti,df_today['price'])
    plt.show()
    # df_today.to_excel(writer, sheet_name=str(dt))
    
    
writer.save()



