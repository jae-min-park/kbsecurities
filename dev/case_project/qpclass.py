# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 13:42:29 2020

@author: infomax
"""

import pandas as pd
from pandas import DataFrame, Series
import ddt_util as du
from ddt_util import dt
import pr_util as pu
from scipy import stats
import matplotlib.pyplot as plt
import datetime
import loadmkt
import os
from pandas.tseries.offsets import BDay
import numpy as np


class CaseDaily:
    """
    All quant strategies are based on dates, which are considered 
    to have similarities. 
    As many 'dates' operations needed repeatedly, dates 'class' highly needed.
    2020.10.30
    """

        
    def __init__(self, df_daily_all=None, info=None):
        """
        df_daily_all과 info로 Case의 기초정보 설정
        
        Parameters:
            df_daily_all : 모든 daily data를 담고 있는 엑셀
            info = {
                'event' : 'AUCT30',
                'secname' : 'KTB10',
                'prev_num' : -6,
                'next_num' : 8,
                'numplot' : 12,
                'offset' : 0 }
        returns : None
        """
        
        self.CASEFILENAME = os.getcwd() + '\dates.xlsx'

        
        self.info = info
        self.df_daily_all = df_daily_all
        self.ld_all = du.get_date_list(self.df_daily_all)
        self.ld_all += pd.bdate_range(self.ld_all[-1]+BDay(1), periods=100).tolist()
        # +1bday ~ +100 bday to be added to original ld_all
        
        self.numplot = info['numplot']

        self.ld = []
        
        self.secname = info['secname']
        self.set_sec(self.secname)

        self.eventname = info['event']
        if self.eventname != "":
            self.set_event(self.eventname)
        
        self.set_horizon()
        
        

        
        
    def set_sec(self, new_secname=str):
        """
        종목 세팅. init에서 만든 종목 변경시에도 사용.
        
        Parameters:
            secname = 종목명
        returns : None
        """
        self.secname = new_secname
        self.secdata = loadmkt.get_dfint_daily(self.df_daily_all, self.secname)
    
    def set_event(self, new_eventname=str):
        """
        casedates DB인 엑셀에서 직접 날짜를 가져옴. 최초 이벤트 변경시에도 사용
        
        Parameters:
            new_eventname = 종목명
        Returns : None
        """
        self.eventname = new_eventname
        df = pd.read_excel(self.CASEFILENAME,
                           sheet_name=self.eventname, 
                           header=1, usecols="A").dropna()
        df.columns = ['dates']
        
        df = df.sort_values(by=['dates'], ascending=False)
        
        df['year'] = [d.year for d in df['dates']]
        
        df['month'] = [d.month for d in df['dates']]
        
        for yr in set(df['year']):
            series_nth_in_year = df[df['year']==yr]['dates'].rank(ascending=True)
            #temporary seires for nth
            for i in series_nth_in_year.index:
                df.loc[i, 'nth_in_year'] = series_nth_in_year[i]
        
        self.df_case_excel = df
        
        self.ld = sorted(list(self.df_case_excel['dates']), reverse=True)[:self.numplot]
        
    def select_nth_in_year(self, nth_list):
        """
        Leaves only nth events in years. Changes self.ld
        
        Parameters: 
            nth_list : nth events list e.g. [1,3,5] 
        Returns : None
        """
        nth_bool = self.df_case_excel['nth_in_year'].isin(nth_list)
        self.ld = sorted(list(self.df_case_excel[nth_bool]['dates']), reverse=True)
        self.set_horizon()
        #ld를 overwrite했으므로  set_horizon 다시 해줘야함
    
    def set_horizon(self):
        """
        관찰기간을 정의
        
        Parameters: None
        Returns : None
        """
        
        self.prev_num = self.info['prev_num']
        self.next_num = self.info['next_num']
        self.offset = self.info['offset']
        
#         last_eventdate = max(self.ld)
#         offset_abs = abs(du.days_between_dates(self.today, last_eventdate, self.ld_all))
#         if self.today >= last_eventdate:
#             self.offset = offset_abs
#         else: self.offset = -offset_abs
        
        self.next_num = self.next_num - self.offset
        self.prev_num = self.prev_num - self.offset
        
        self.ref_day = du.date_offset(self.ld_all, self.ld[0], self.offset)
        
        self.start_date = du.date_offset(self.ld_all, self.ref_day, self.prev_num)
        self.end_date = du.date_offset(self.ld_all, self.ref_day, self.next_num)
        self.shift_date(self.offset)
        
    def plot(self):
        """
        Plot ld
        
        Parameters: 
            numplot : newly given number of plots. Assigns initial if empty
            prev_num : newly given # of previous days. Assigns initial if empty
            next_num : newly given # of next days. Assigns initial if empty
        Returns : None
        """
        self.set_plot_note()
        pu.plot_multly(self.secdata, self.ld[:self.numplot], self.plot_note, self.prev_num, self.next_num)
    
    def set_plot_note(self, comment=None):
        """
        Set plot_note
        
        Parameters: 
            comment : additional comment to be added at the end of note
        Returns : None
        """
        self.plot_note = self.eventname + " : " + self.secname +  " yield : " 
        self.plot_note += self.start_date.strftime('%m/%d') + '~' + self.end_date.strftime('%m/%d')
        self.plot_note += " : @" + self.ref_day.strftime('%m/%d')
        if comment != None:
            self.plot_note += " : " + comment
    
    def shift_date(self, shift=0):
        self.ld = du.date_offset_list(self.ld_all, self.ld, shift)
        
    def from_dfptn(self, dfptn, numplot=99, weekday_filter=None):
        self.ld = pu.datelist_from_dfptn(self.ld_all, dfptn, numplot, weekday_filter=None)
        
    def __repr__(self):
        repr_info = {'event' : self.eventname,
                     'secname' : self.secname,
                     'numplot' : self.numplot,
                     'offset' : self.offset,
                     'dates' : self.ld[-1].strftime('%y/%m/%d')+"..."+self.ld[0].strftime('%y/%m/%d')
                     }
        return str(repr_info)
    

        
    def sortby_zs_simil(self, zscutoff=float):
#        self.numplot = max(3, int(self.numplot * zscutoff * 2))
        self.ld = du.sort_zs_similarity(self.secdata, self.ld, zscutoff)
        
    def print_fcast(self):
        print(pu.fcast_multly(self.secdata, self.ld, self.next_num))
        
    def remove_yyyymm(self, yyyymm_list=list):
        self.ld = du.remove_yyyymm(self.ld, yyyymm_list)
        
    def select_yyyymm(self, yyyymm_list=list):
        self.ld = du.select_yyyymm(self.ld, yyyymm_list)
        
    def select_months(self, months_list=list):
        self.ld = du.select_months(self.ld, months_list)
        
    def select_years(self, years_list=list):
        self.ld = du. select_years(self.ld, years_list)
        

    
class SecData:
    """
    Class of Securities data. Assumes !!!daily data!!! 2020.11.18 
    주요기능 :
        parity build등 market data 조작에 필요한 것들을 여기에 담자
        spread, butterfly build등도 loadmkt.read_daily가 아니라 여기서 수행
    
    Class [CaseDaily] will use [SecData] --> 수정작업필요 2020.11.18
    DateList라는 클래스를 만들어서 SecData와 함께 Case class를 구성하자
    
    2020.11.18
    """
    
    def __init__(self, df_daily_all=DataFrame, secname=str, sectype=None):
        """
        df_daily_all과 기초정보로 class 생성
        
        Parameters:
            df_daily_all : 일간데이터 master
            sectype : 
                "yield" : 이자율 data, 스프레드, 버터플라이 포함, 전일비가 bp임
                "px" : price data 전일비가 %인 것이 yield와 다름
        returns : None
        """
        
        self.df_daily_all = df_daily_all
        self.ld_all = du.get_date_list(self.df_daily_all)
        self.secname = secname
        
        if sectype == None:
            if secname in ['USDKRW','EURUSD','AUDUSD','FUT3PX','FUT10PX',
                       'JPYKRW', 'EURJPY', 'AUDJPY', 'US10PX', 'JPYEUR']:
                self.sectype = 'px'
            else: self.sectype = 'yield'
        
        self.df = self.get_dfsec(self.df_daily_all, self.secname, self.sectype)
        
        self.today = datetime.date.today()
        self.last_mktday = du.last_mktday(self.df)
        
    def get_dfsec(self, df_daily_all, secname, sectype):
        #self.df를 정의
        df = loadmkt.get_dfint_daily(df_daily_all, secname)
        
        #chg col 만들기
        if sectype == 'yield':
            df['bp_chg'] = df['종가'].diff(periods=1)*100
        elif sectype == 'px':
            df['pct_chg'] = df['종가'].pct_change(periods=1)*100
        else: print("Unexpected Sectype")
         
        
        return df

    def update_rt(self):
        #update mkt data 
        df_daily_updated = loadmkt.update_rt_daily(self.df_daily_all)
        self.df_daily_all = df_daily_updated
        self.df = self.get_dfsec(df_daily_updated, self.secname, self.sectype)
        print(self.secname, " market data(daily) updated\n")
        print(self.df[:self.today].tail(10))
    
    def var(self, window=1, confidence=0.95, test_years=1):
        """
        Calcuate VaR 
        
        Parameters:
            window : calculation window ex) 10-d Var -> varwindow=10
            confidence : confidence level ex) 95% -> 0.95
            test_years : n yrs of cacluation period
    
        Returns: Var value 
        2020.11.18
        """
        
        tday = datetime.datetime.today()
        test_since = tday - datetime.timedelta(days=test_years*365+window) 
        
        df_test = self.df[test_since:tday]
        
        if self.sectype == 'yield':
            chg = df_test['종가'].diff(periods=window)
        else:
            chg = df_test['종가'].pct_change(periods=window)
        
        chg_abs = chg.abs()*100 #0.01-> 1bp, 0.01 -> 1%
        rank = int(len(chg)*(1-confidence)) #top 1-confidence % 
        var = chg_abs.nlargest(rank)[-1]
                
        return round(var, 1), "bp" if self.sectype == 'yield' else 'pct', window, confidence, test_years
    
    def zscore(self, x, window=10):
        """
        Return zscore series of [x].
        shift(1) is used to comply with time-series analysis convention
        
        ref_page
        https://stackoverflow.com/questions/47164950/
        compute-rolling-z-score-in-pandas-dataframe
        https://turi.com/products/create/docs/generated/
        graphlab.toolkits.anomaly_detection.moving_zscore.create.html
        """
        r = x.rolling(window=window)
        m = r.mean().shift(1)
        s = r.std(ddof=0).shift(1)
        z = (x-m)/s
        return z
    
    def zs(self, window=20, ref_date=None):
        """
        Return zscore of daily market data
        Zscore of n days upto ref_date-1
        """
        if ref_date == None: 
            ref_date = du.date_offset(self.ld_all, self.last_mktday, 1)
        
        return du.zscore_find_daily(self.ld_all, self.df, ref_date, zswindow=window)
    
    def ma(self, window=20, ref_date=None):
        """
        Return moving average of daily market data
        MA of n days upto ref_date-1
        """
        if ref_date == None: 
            ref_date = du.date_offset(self.ld_all, self.last_mktday, 1)
        #일요일에 조회하는 경우 last_mktday=금요일, ref_date는 월요일로 만들기
        
        enddate = du.date_offset(self.ld_all, ref_date, -1)
        startdate = du.date_offset(self.ld_all, ref_date, -window)
        df_window = self.df[startdate:enddate]
        
        window_avg = np.mean(df_window['종가'])
        
        return round(window_avg, 2)
    
    def __repr__(self):
        #today-5일~ today까지만 프린트한다
        
        print_begins_on = du.date_offset(self.ld_all, self.today, -5)
        df_print = self.df[print_begins_on:self.today].drop(columns='일자')
        df_print['종가'] = round(df_print['종가'], 3)
                
        return df_print.__repr__()
    

class DateList:
    """
    SecData와 함께 Case class를 구성할 class
    """
    pass



class Test_Series_mean_reverse:
    """
    datetimeindex와 가격으로 이루어진 timeseries데이터(pandas.Series)를 받아서 backtest
    """
    
    def __init__(self, se, threshold, pt, lc):
        """
        se : pd.Series, timeseries data (index, price)
        threshold : threshold, initiate mean_reverse trade beyond this level
        pt : profit taking level, always +ve value
        lc : loss cut level, always -ve value
        """
        
        self.se = se
        self.threshold = threshold
        self.pt = pt
        self.lc = -abs(lc)
        #lc가 양수로 전달됐을 경우에 음수로 전환
        
        self.trade = {'start': se.index[0].date().strftime('%y-%m-%d'), 
                      'status':"none", #none, long, short, profit, losscut, timeup
                      'ent':0, #entry price
                      'ent_time': "",
                      'ext_time': "",
                      'pl':0} #pl of trade
        
        self.pl_hist = DataFrame(index=sorted(set(se.index.date)), 
                                 columns=['pl'])
        self.start_of_se = se.index[0]
        self.end_of_se = se.index[-1]

        self.start_time_of_se_days = se.index[0].time()
        self.end_time_of_se_days = se.index[-1].time()
        
    def entry_test(self, price, dti):
        """
        changes self.trade as to be open (long or short)
        !!!전략이 바뀌면 class에서 entry_test만 바뀌면 됨
        price : from timeseries data
        returns : none
        """
        if self.trade['status'] != "none": 
            raise Exception('Wrong test. Trade already open.')
        
        
        
        if self.threshold < price: 
            # short 진입조건 만족
            self.open_short(dti)
            
        elif price < -self.threshold: 
            # long 진입조건 만족
            self.open_long(dti)
    
    def open_short(self, dti):
        self.trade['status'] = 'short'
        self.trade['ent'] = self.threshold 
        #!!!백테스트 문제 있음. 갭 발생시 진입가 문제
        #
        self.trade['ent_time'] = dti
    
    def open_long(self, dti):
        self.trade['status'] = "long"
        self.trade['ent'] = -self.threshold
        #!!!백테스트 문제 있음. 갭 발생시 진입가 문제
        self.trade['ent_time'] = dti
        

        
    def exit_test(self, price, time):
        if self.trade['status'] == "none": 
            raise Exception('Wrong test. Trade not yet entered.')
        
        if self.trade['pl'] > self.pt:
            # 익절조건 만족
            self.trade['status'] += ' profit'
            self.trade['pl'] = self.pt
            # pl을 pt값으로 조정. 보수적 가정을 반영
            self.trade['ext_time'] = time
            
        elif self.trade['pl'] < self.lc:
            # 손절조건 만족 TT
            self.trade['status'] += ' losscut'
            # self.trade['pl'] = self.lc
            # pl을 lc값으로 맞추지 않는다. 보수적 가정을 반영
            self.trade['ext_time'] = time
            
        else: pass
        #익절도 손절도 아님. 다음시간으로 test로 넘긴다.


    def close_by_time(self, price, time):
        """시간청산할때 시장가로 청산 가정"""
        if self.trade['status'] == 'none': 
            pass
        
        elif self.trade["status"] == "long" or self.trade["status"] == "short":
            self.trade['pl'] = self.cal_pl(price)
            self.trade['status'] += ' timeup'
            self.trade['ext_time'] = time
            self.book_pl(time)
            
    
    def cal_pl(self, price):
        """
        Calculates P&L with current price.

        Returns : pl
        """
        if self.trade['status'] == "none": 
            raise Exception('Wrong call. Trade not yet entered.')
            
        elif self.trade['status'] == 'long':
            # self.trade['pl'] = price - self.trade['ent']
            pl = price - self.trade['ent']
            
        elif self.trade['status'] == 'short':
            # self.trade['pl'] = self.trade['ent'] - price
            pl = self.trade['ent'] - price
        
        return pl
    
    def book_pl(self, dti):
        """
        Keep daily P&L on self.pl_hist using current pl. i.e. self.trade['pl']
        """
        self.pl_hist.at[dti.date(), 'pl'] = self.trade['pl']
        
            
    def print_log(self, time):
        print(self.trade['start'], self.trade['status'], self.trade['pl'], time)
        
        
    def backtest(self):
        """
        perform backtest on a single timeseries data. Main function of class.

        Returns
        -------
        trade : dictionary
            Contains information of pl, end up result and etc.
        """
        
        for dti, price in self.se.items():
            # print(time, price)
            if dti == self.end_of_se:
                self.close_by_time(price, dti)
                self.print_log(dti)
                break
            #status가 profit, losscut이었으면 이미 break였으므로 위 test할 일이 없다.
            
            if self.trade["status"] == "none":
                self.entry_test(price, dti)
            
            elif self.trade["status"] == "long" or self.trade["status"] == "short":
                self.exit_test(price, dti)
                #entry후에 바로 exit test는 skip한다
            
            result = self.trade['status'].split()[-1]
            if result == 'profit' or result == 'losscut':
                self.print_log(dti)
                break
            
            # print(result)
            
        return self.trade
    
