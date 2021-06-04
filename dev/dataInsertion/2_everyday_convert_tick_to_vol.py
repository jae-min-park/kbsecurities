import datetime
import pandas as pd
import numpy as np
import pymysql
from tqdm import tqdm

test_db = pymysql.connect(user='admin',
                          passwd='se21121',
                          # host = '211.232.156.57',
                          host='127.0.0.1',
                          db='testschema',
                          charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

def setDfData(date_start, date_end, table) :
    sql = "SELECT * FROM "+ table+" where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    cursor.execute(sql)
    result = cursor.fetchall()
    return pd.DataFrame(result)

def insertExcelData(cursor, df, table):

    for i in range(len(df.index)) :
        date = str(df.iloc[i,0])
        time = str(df.iloc[i,1])[7:]
        vwap = str(df.iloc[i,2])
        close = str(df.iloc[i,3])
        sql = "insert into "+table+" (date, time, ,vwap, close) values ('"  + date + "','" + time + "','"+ vwap + "','" + close +"'" + ');'
        cursor.execute(sql)
    test_db.commit()

def parseVolandCommit(dftick, vol_bin, table):
    
    dfbinned = pd.DataFrame(columns=['date','time','vwap','price','open','high','low'])
    
    vol_list = []
    prc_list = []
    
    i_resampled = 0
    
    for i in tqdm(dftick.index):
        vol = dftick.at[i, 'volume']
        prc = dftick.at[i, 'close']
            
        vol_list.append(vol)
        prc_list.append(prc)
        
        cumsum_vol = sum(vol_list)
        
        if cumsum_vol >= vol_bin:
            bins_made = int(cumsum_vol / vol_bin)
            leftover = cumsum_vol % vol_bin
            vol_list[-1] = vol_list[-1] - leftover
            vwap = sum(np.array(prc_list) * np.array(vol_list)) / (bins_made * vol_bin)
            
            for n in range(bins_made):
                dfbinned.at[i_resampled, 'vwap'] = vwap
                dfbinned.at[i_resampled, 'date'] = dftick.at[i, 'date']
                dfbinned.at[i_resampled, 'time'] = str(dftick.at[i, 'time'])[7:]
                dfbinned.at[i_resampled, 'price'] = dftick.at[i, 'close']
                i_resampled += 1
            
            vol_list = [leftover] #[0]이어도 무관
            prc_list = [prc]
        
        else:
            pass
    print(dfbinned)
    insertExcelData(cursor,dfbinned, table)



# start_date = str(datetime.datetime.today())[:10]
# end_date = str(datetime.datetime.today())[:10]

start_date = datetime.date(1999,1,1)
end_date = datetime.date(2021,6,4)

""" 10년국채 선물 50vol"""
vol_option='lktbftick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 50, 'lktbf50vol')

""" 10년국채 선물 100vol"""
vol_option='lktbftick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 100, 'lktbf100vol')

""" 10년국채 선물 200vol"""
vol_option='lktbftick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 200, 'lktbf200vol')

start_date = datetime.date(2017,9,19)

""" 3년국채 선물 100vol"""
vol_option='ktbftick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 100, 'ktbf100vol')

""" 3년국채 선물 200vol"""
vol_option='ktbftick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 200, 'ktbf200vol')

""" 3년국채 선물 300vol"""
vol_option='ktbftick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 300, 'ktbf300vol')


start_date = datetime.date(2018,3,31)

""" 달러원 선물 100vol"""
vol_option='usdkrwtick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 100, 'usdkrw100vol')

""" 달러원 선물 200vol"""
vol_option='usdkrwtick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 200, 'usdkrw200vol')

""" 달러원 선물 300vol"""
vol_option='usdkrwtick'
dftick = setDfData(start_date, end_date, vol_option)
parseVolandCommit(dftick, 300, 'usdkrw300vol')

