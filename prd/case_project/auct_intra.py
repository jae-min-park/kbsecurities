# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 07:55:22 2020

@author: infomax
"""

import pandas as pd
import sys
sys.path.append('c:/pywork/DDT_lib')
sys.path.append('d:/pywork/DDT_lib')
sys.path.append('d:/pywork/DDT(4)PR')
import ddt_util as du
import pr_util as pu
import loadmkt

""""""""""""""""""""""""""""""""""""""""""""""""
"""AUCTION"""
""""""""""""""""""""""""""""""""""""""""""""""""
df10 = loadmkt.read_ktb10y()
df3 = loadmkt.read_ktb3y()

dfktbsp = loadmkt.read_ktbsp()
# dfhanmi = loadmkt.read_hanmi()

ld_all = du.get_date_list(df10)

#%%
from datetime import datetime
timenote = datetime.now().strftime("%Y/%m/%d, %H:%M")

CASE = ['AUCT3', 'AUCT5','AUCT10','AUCT30','BOKMPC']
ASSET =['KTBF3Y','KTBF10Y','SP']
NUMPLOT = [6,7,8]
OFFSET = [-3,-2,-1,0,1,2,3]
PREV_NUM = [-4,-3,-2]
NEXT_NUM = [2,3,4]

df10 = loadmkt.update_futures_rt(df10, fut_name='10y')
df3 = loadmkt.update_futures_rt(df3, fut_name='3y')
dfktbsp = loadmkt.update_futures_rt(dfktbsp, fut_name='sp')


# """short test"""
# case='AUCT5'
# asset='KTBF10Y'
# numplot = 5
# offset = 0
# prev_num = -5
# next_num = 5


# filename = f'{case}_{asset}_{numplot}series_{offset}off_{prev_num}prev_{next_num}next'
# # OFFSET = 1
# # NUMPLOT = 6

# # dates = du.read_casedates(CASE, "KR", nth_in_year=[1] )[:7] #매년 첫 입찰
# dates = du.read_casedates(case, "KR", )[:numplot] #최근 입찰


# dates = du.date_offset_list(ld_all, dates, offset)
# # dates += [pd.Timestamp(2021,4,19)]
# dates = du.remove_yyyymm(dates, [202002, 202003, 202004,]) #코로나 변동월 제거
# # dates = du.select_months(dates, [1,2,3,4])
# # dates = dates[:7] + du.select_months(dates, [1])[1:]
# # dates = du.select_years(dates, [2015, 2016, 2017, 2019, 2020])

# # dates = dates[:5]

# # pu.plot_multly(df10, dates, CASE+" LKTB "+timenote, PREV_NUM, NEXT_NUM, shift=0)
# if asset == 'KTBF3Y':
#     pu.plot_multly(df3, dates, case+' '+asset+' '+timenote, prev_num, next_num, filename=filename)
# elif asset == 'KTBF10Y':
#     pu.plot_multly(df10, dates, case+' '+asset+' '+timenote, prev_num, next_num, filename=filename)
# # pu.plot_multly(dfktbsp, dates, CASE+" SP "+timenote, PREV_NUM, NEXT_NUM)
# # pu.plot_multly(dfhanmi, dates, CASE+" HANMI "+timenote, PREV_NUM, NEXT_NUM)

""" 이미지를 요청시 생성"""
def setPlot(df, case, asset, offset=0, startplot=0, endplot=6, prev_num=3, next_num=-2) :
    dates = du.read_casedates(case, "KR", )[startplot:endplot] #최근 입찰
    ld_all = du.get_date_list(df)
    dates = du.date_offset_list(ld_all, dates, offset)
    # dates += [pd.Timestamp(2021,4,19)]
    dates = du.remove_yyyymm(dates, [202002, 202003, 202004,]) #코로나 변동월 제거
    filename = f'{case}_{asset}_{startplot}start_{endplot}end_{offset}off_{prev_num}prev_{next_num}next'
    pu.plot_multly(df, dates, case+' '+asset+' '+timenote, prev_num, next_num, offset=offset, filename=filename)


"""이미지 미리 생성해놓기"""
# for case in CASE :
#     for asset in ASSET :
#         for numplot in NUMPLOT :
#             for offset in OFFSET :
#                 for prev_num in PREV_NUM :
#                     for next_num in NEXT_NUM:
#                         filename = f'{case}_{asset}_{numplot}series_{offset}off_{prev_num}prev_{next_num}next'
#                         # OFFSET = 1
#                         # NUMPLOT = 6
                        
#                         # dates = du.read_casedates(CASE, "KR", nth_in_year=[1] )[:7] #매년 첫 입찰
#                         dates = du.read_casedates(case, "KR", )[:numplot] #최근 입찰
                        
                        
#                         dates = du.date_offset_list(ld_all, dates, offset)
#                         # dates += [pd.Timestamp(2021,4,19)]
#                         dates = du.remove_yyyymm(dates, [202002, 202003, 202004,]) #코로나 변동월 제거
#                         # dates = du.select_months(dates, [1,2,3,4])
#                         # dates = dates[:7] + du.select_months(dates, [1])[1:]
#                         # dates = du.select_years(dates, [2015, 2016, 2017, 2019, 2020])
                        
#                         # dates = dates[:5]
                        
#                         # pu.plot_multly(df10, dates, CASE+" LKTB "+timenote, PREV_NUM, NEXT_NUM, shift=0)
#                         if asset == 'KTBF3Y':
#                             pu.plot_multly(df3, dates, case+' '+asset+' '+timenote, prev_num, next_num, offset=offset, filename=filename)
#                         elif asset == 'KTBF10Y':
#                             pu.plot_multly(df10, dates, case+' '+asset+' '+timenote, prev_num, next_num, offset=offset, filename=filename)
#                         elif asset == 'SP':
#                             pu.plot_multly(dfktbsp, dates, case+' '+asset+' '+timenote, prev_num, next_num, offset=offset, filename=filename)
#                         # pu.plot_multly(dfktbsp, dates, CASE+" SP "+timenote, PREV_NUM, NEXT_NUM)
#                         # pu.plot_multly(dfhanmi, dates, CASE+" HANMI "+timenote, PREV_NUM, NEXT_NUM)
