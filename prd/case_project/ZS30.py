# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 10:07:28 2021

@author: infomax
"""


import sys
sys.path.append('c:/pywork/DDT_lib')
sys.path.append('d:/pywork/DDT_lib')
sys.path.append('d:/pywork/DDT(4)PR')
import loadmkt
from qpclass import CaseDaily


df_daily_all = loadmkt.read_daily()

#%%
df_daily_all = loadmkt.update_rt_daily(df_daily_all)

info = {'event' : 'AUCT30', 'secname' : '', 'prev_num' : -99,
        'numplot' : 7, 'offset' : 0, 'next_num' : 99}

strategy_list = [
    # ('KTB5', -5, 0),
    # ('KTB5', 1, 1),
    # ('KTB10', -5, 1),
    # ('KTB10', -2, 0),
    # ('KTB30', -3, 0),
    ('KTB30', 1, 5),
    ('KTB10', 1, 5),
    ('10*30', 1, 5),
    ('5*30', 1, 5),
    ('3F*10F*30', 1, 5),
    # ('3F*10F', -4, 1),
    # ('3F*30', -3, -2),
    # ('3F*30', -2, 1),
    # ('5*10', -2, 2),
    # ('5*10*30', -6, 1),
    # ('US10-KR10', -5, 0),
    ('US10-KR10', 2, 3)

    ]
    
begin_watch_before = 0

for s in strategy_list:
    info['secname'] = s[0]
    info['offset'] = s[1] - begin_watch_before
    info['prev_num'] = info['offset'] - 10
    info['next_num'] = s[2]
    case = CaseDaily(df_daily_all, info)
    # case.remove_yyyymm([ 202106])
    # case.select_nth_in_year([1])
    # case.select_years([2021])
    # case.sortby_zs_simil(0.3)
    case.plot()
    case.print_fcast()

    