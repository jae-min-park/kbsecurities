# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 16:33:33 2021

@author: infomax
"""
import math
import pandas as pd
from tqdm import tqdm

grvStn_max_body = 0.02
grvStn_min_utail = 0.05
grvStn_max_ltail = 0.02
rebound_min_body = 0.03
decline_max_body = -0.04
# class CandleSnapShot :
#     def __init__(self, dt, body, u_tail, l_tail) :
#         self.dt = dt
#         self.body = round(body,2)
#         self.u_tail = round(u_tail,2)
#         self.l_tail = round(l_tail,2)
        
#     def isGraveStonePattern(self) :
#         if abs(self.body) <= 0.01 and self.u_tail >= 0.03 and self.l_tail <= 0.01 :
#             return True
#         else : 
#             return False
        
#     def isReboundPattern(self, df) :
#         for i in df.index:
#             t_diff = self.dt - i
#             if t_diff <= pd.Timedelta('00:00:00'):
#                 return False
            
#             if t_diff <= pd.Timedelta('00:00:30') and t_diff >= pd.Timedelta('00:00:10') :
#                 j = pd.Timedelta('00:00:00')
#                 while t_diff > pd.Timedelta('00:00:00') :
#                     t_diff = t_diff - pd.Timedelta('00:00:10')
#                     if df.loc[i+j, 'gravePattern'] :
#                         if self.body >= 0.04 :
#                             return True
#                         else:
#                             j += pd.Timedelta('00:00:10')
#                     else:
#                         break;

class DataFrameManager:
    def __init__(self, cursor) :
        self.cursor = cursor
        

    # """
    # 캔들성 데이터인, 그레이브스톤패턴, 리바운드패턴을 dataFrame에 세팅해준다
    # """
    # def setDfDayCandleData(self, date_start, date_end) :
    #     self.setDfDailyData(date_start, date_end)
        
    #     self.setGraveStoneAndReboundValue()
        
    #     # for i in tqdm(self.df.index) :
    #     #     if self.df.loc[i, 'CandleSnapShot'].isGraveStonePattern() :
    #     #     # if self.isGraveStonePattern(self.df.loc[i,'body'], self.df.loc[i,'u_tail'], self.df.loc[i,'l_tail']) :
    #     #         self.df.loc[i, 'gravePattern'] = True
    #     #     else :
    #     #         self.df.loc[i, 'gravePattern'] = False

    #     # for i in tqdm(self.df.index) :
    #     #     if self.df.loc[i, 'CandleSnapShot'].isReboundPattern(self.df) :
    #     #     # if self.isReboundPattern(self.df.loc[i,'body'], self.df.loc[i,'u_tail'], self.df.loc[i,'l_tail']) :
    #     #         self.df.loc[i, 'reboundPattern'] = True
    #     #     else :
    #     #         self.df.loc[i, 'reboundPattern'] = False

    """
    date_start부터 date_end까지 데이터를 받는 sql을 수행
    """
    def setDfData(self, date_start, date_end) :
        sql = "select * from `lktbf` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
        self.getSQLData(sql)
        self.df.index = pd.to_datetime(self.df.date.astype(str) + ' ' + self.df.time.astype(str).apply(lambda x: x[7:]))
        
    """
    하루어치 ohlc 및 candle 데이타 값 df에 세팅함
    """
    def getCandleValueDf(self, paramDf):
        _max = 0
        _min = 1000

        for i in paramDf.index :
            paramDf.loc[i, 'o_day'] = paramDf.loc[paramDf.index[0], 'open']
            if _max < paramDf.loc[i, 'hi'] :
                _max = paramDf.loc[i, 'hi_day'] = paramDf.loc[i, 'hi']
            else :
                paramDf.loc[i, 'hi_day'] = _max
            if _min > paramDf.loc[i, 'lo'] :
                _min = paramDf.loc[i, 'lo_day'] = paramDf.loc[i, 'lo']
            else :
                paramDf.loc[i, 'lo_day'] = _min

            paramDf.loc[i, 'body'] = paramDf.loc[i, 'close'] - paramDf.loc[i, 'o_day']
            paramDf.loc[i, 'u_tail'] = paramDf.loc[i, 'hi_day'] - max(paramDf.loc[i, 'o_day'], paramDf.loc[i, 'close'])
            paramDf.loc[i, 'l_tail'] = min(paramDf.loc[i, 'o_day'], paramDf.loc[i, 'close']) - paramDf.loc[i, 'lo_day']

            # body = paramDf.loc[i, 'body'] 
            # u_tail = paramDf.loc[i, 'u_tail']
            # l_tail = paramDf.loc[i, 'l_tail'] 
            # paramDf.loc[i,'CandleSnapShot'] = CandleSnapShot(i,body,u_tail,l_tail)            
        
        return paramDf
    
    # """
    # date_start부터 date_end까지 데이터를 받아서 dataframe에 o,h,l,c,body,u_tail,l_tail 값을 설정한다.
    # """
    # def setDfDailyData(self, date_start, date_end) :
    #     sql = "select * from `lktbf` where date >= '"+ str(date_start)[:10] + "' and date <= '" + str(date_end)[:10] + "';"
    #     self.getDfData(sql)
        
    #     self.df.index = pd.to_datetime(self.df.date.astype(str) + ' ' + self.df.time.astype(str).apply(lambda x: x[7:]))
        
    #     _max = 0
    #     _min = 1000

    #     for i in self.df.index :
    #         self.df.loc[i, 'o_day'] = self.df.loc[self.df.index[0], 'open']
    #         if _max < self.df.loc[i, 'hi'] :
    #             _max = self.df.loc[i, 'hi_day'] = self.df.loc[i, 'hi']
    #         else :
    #             self.df.loc[i, 'hi_day'] = _max
    #         if _min > self.df.loc[i, 'lo'] :
    #             _min = self.df.loc[i, 'lo_day'] = self.df.loc[i, 'lo']
    #         else :
    #             self.df.loc[i, 'lo_day'] = _min
            
    #         # temp = {'body' : self.df.loc[i, 'close'] - self.df.loc[i, 'o_day'],
    #         #         'u_tail' : self.df.loc[i, 'hi_day'] - max(self.df.loc[i, 'o_day'], self.df.loc[i, 'close']),
    #         #         'l_tail' : min(self.df.loc[i, 'o_day'], self.df.loc[i, 'close']) - self.df.loc[i, 'lo_day']
    #         #         }
            
    #         self.df.loc[i, 'body'] = self.df.loc[i, 'close'] - self.df.loc[i, 'o_day']
    #         self.df.loc[i, 'u_tail'] = self.df.loc[i, 'hi_day'] - max(self.df.loc[i, 'o_day'], self.df.loc[i, 'close'])
    #         self.df.loc[i, 'l_tail'] = min(self.df.loc[i, 'o_day'], self.df.loc[i, 'close']) - self.df.loc[i, 'lo_day']

    #         body = self.df.loc[i, 'close'] - self.df.loc[i, 'o_day']
    #         u_tail = self.df.loc[i, 'hi_day'] - max(self.df.loc[i, 'o_day'], self.df.loc[i, 'close'])
    #         l_tail = min(self.df.loc[i, 'o_day'], self.df.loc[i, 'close']) - self.df.loc[i, 'lo_day']            
    #         self.df.loc[i,'CandleSnapShot'] = CandleSnapShot(i,body,u_tail,l_tail)            
    

    """
    하루어치 그레이브스톤 이후 리바운드 패턴까지 dataFrame에 세팅함
    """
    def getGraveStoneAndReboundValueDf(self, paramDf, pre_close):
        # dti = paramDf.index
        dti = paramDf[paramDf['time'] <= pd.Timedelta("10:00:10")].index
        if paramDf.loc[dti[0],'open'] - pre_close < 0 :
            paramDf['gravePattern'] = False
            paramDf['reboundPattern'] = False
            paramDf['declinePattern'] = False
            return paramDf
        
        for dti_pre, dti_post in zip(dti, dti[1:]) :
            if round(abs(paramDf.loc[dti_pre,'body']),2) <= grvStn_max_body and round(paramDf.loc[dti_pre, 'u_tail'],2) >= grvStn_min_utail and round(paramDf.loc[dti_pre, 'l_tail'],2) <= grvStn_max_ltail :
                paramDf.loc[dti_pre, 'gravePattern'] = True
                if paramDf.loc[dti_post, 'body'] >= rebound_min_body :
                    paramDf.loc[dti_post, "reboundPattern"] = True
                elif paramDf.loc[dti_post, 'body'] <= decline_max_body : 
                    paramDf.loc[dti_post, "declinePattern"] = True
                else:
                    paramDf.loc[dti_post, "reboundPattern"] = False
                    paramDf.loc[dti_post, "declinePattern"] = False
            else :
                paramDf.loc[dti_pre, 'gravePattern'] = False
                paramDf.loc[dti_post, 'reboundPattern'] = False
                paramDf.loc[dti_post, "declinePattern"] = False
        paramDf['gravePattern'] = paramDf['gravePattern'].fillna(False)
        paramDf['reboundPattern'] = paramDf['reboundPattern'].fillna(False)
        paramDf['declinePattern'] = paramDf['declinePattern'].fillna(False)
        return paramDf
 
    # def setGraveStoneAndReboundValue2(self):
    #     for i in tqdm(self.df.index) :
    #         if abs(self.df.loc[i,'body']) <= 0.01 and self.df.loc[i, 'u_tail'] >= 0.03 and self.df.loc[i, 'l_tail'] <= 0.01 :
    #             self.df.loc[i, 'gravePattern'] = True
    #             diff = pd.Timedelta('00:00:00')
    #             tempDf = self.df
    #             stillGrave = True
    #             while diff <= pd.Timedelta('00:00:30') and stillGrave :
    #                 diff += pd.Timedelta('00:00:10')
    #                 if i+diff <= self.df.index[-1]:
    #                     if self.df.loc[i+diff, 'body'] >= 0.04:
    #                         self.df.loc[i+diff, "reboundPattern"] = True
    #                     else :
    #                         self.df.loc[i+diff, "reboundPattern"] = False
                    
    #                 tempDf = tempDf.shift(-1)
    #                 if abs(tempDf.loc[i, 'body'] < 0.01) and tempDf.loc[i, 'u_tail'] >= 0.03 and tempDf.loc[i, 'l_tail'] <=0.01 : 
    #                     stillGrave = True
    #                 else :
    #                     stillGrave = False
                    
    # def setGraveStoneAndReboundValue3(self):
    #     for i in tqdm(self.df.index) :
    #         if abs(self.df.loc[i,'body']) <= 0.01 and self.df.loc[i, 'u_tail'] >= 0.03 and self.df.loc[i, 'l_tail'] <= 0.01 :
    #             self.df.loc[i, 'gravePattern'] = True
    #             t_diff = pd.Timedelta('00:00:10')
    #             stillGrave = True
    #             while t_diff <= pd.Timedelta('00:00:30') and stillGrave :
    #                 if i+t_diff > self.df.index[-1] :
    #                     break
    #                 if self.df.loc[i+t_diff, 'body'] >= 0.04 :
    #                     self.df.loc[i+t_diff, "reboundPattern"] = True
    #                 elif math.isnan(self.df[i+t_diff, 'gravePattern']) and abs(self.df.loc[i+t_diff,'body']) <= 0.01 and self.df.loc[i+t_diff, 'u_tail'] >= 0.03 and self.df.loc[i+t_diff, 'l_tail'] <= 0.01 :
    #                     pass
    #                 else :
    #                     stillGrave = False
    #                 t_diff += pd.Timedelta('00:00:10')

    # """
    # 그레이브스톤 패턴확인. 비석을 꽂은듯한 모양으로 upper_tail 이 길고 body 가 작은 모양이다.
    # """
    # def isGraveStonePattern(self, body, u_tail, l_tail) :
    #     if abs(body) <= 0.01 and u_tail > 0.03 and l_tail <= 0.01 :
    #         return True
    #     else : 
    #         return False
        
    # """
    # 리바운드 패턴확인. graveStonePattern 이 전제되엇을때 body의 길이가 어느정도 있으면 rebound했다고 본다.
    # """
    # def isReboundPattern(self, body, u_tail, l_tail) :
    #     if self.df['gravePattern'][0] and body >= 0.02 :
    #         return True
    #     else :
    #         return False

    """
    전달받은 sql을 수행하여 dataframe에 세팅해주는 유틸 함수
    """
    def getSQLData(self,sql) :
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.df = pd.DataFrame(result)
        

    """
    엑셀 데이터를 DB에 삽입해 주는 함
    """
    def insertExcelData(self, cursor):
        df_excel = pd.read_excel('D:/dev/data/Kintra_10sec.xlsx', sheet_name=[2])
        # print(df)
        # df1 = df[1]
        # df2 = df[2]
        # df = df1.append(df2)
        df_excel = df_excel[2]
        
        for i in range(len(df_excel.index)) :
            code = str(df_excel.iloc[i,0])
            date = str(df_excel.iloc[i,1])[0:10]
            time = str(df_excel.iloc[i,2])
            _open = str(df_excel.iloc[i,3])
            _hi = str(df_excel.iloc[i,4])
            _lo = str(df_excel.iloc[i,5])
            _close = str(df_excel.iloc[i,6])
            vol = str(df_excel.iloc[i,7]) 
            sql = "insert into `lktbf` (code, date, time, open, hi, lo, close, vol) values ('" + code+ "','" + date + "','" + time + "','" + _open + "','" + _hi + "','" + _lo + "','" + _close + "','"+ vol +"'" + ');'
            cursor.execute(sql)
            
        