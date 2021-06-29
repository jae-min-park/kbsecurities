import datetime
import pandas as pd
from tqdm import tqdm
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util
from tradeLoi import *



#%%trade multi Loi 백테스트



# day = datetime.date(2021,2,8)

"""10선 rangeTradeMultiLoi 호출"""
# r = rangeTradeMultiLoi(day, vol_option='lktbf50vol', plot="Y", execution="vwap",
#                   loi_redundancy_margin=10, pt_margin=5, lc_margin=15, entry_margin=5, scale_entry=10)

"""3선 rangeTradeMultiLoi 호출"""
# r = rangeTradeMultiLoi(day, vol_option='ktbf100vol', plot="Y", execution="vwap",
#                   loi_redundancy_margin=10/3, pt_margin=5/3, lc_margin=15/3, entry_margin=5/3, scale_entry=10/3)


"""달러원 rangeTradeMultiLoi 호출"""
# r = rangeTradeMultiLoi(day, vol_option='usdkrw100vol', plot="Y", execution="vwap",
#                   loi_redundancy_margin=10*10, pt_margin=5*10, lc_margin=15*10, entry_margin=5*10, scale_entry=10*10)


"""복수 일자 """
ld = list(util.getDailyOHLC().index)[20:]
ld = [d for d in ld if d.year>=2017 and d.year<=2021]

total = 0.00
df_summary = pd.DataFrame(columns=['day_pl_sum', 'day_signal_cnt'])
writer = pd.ExcelWriter("summary_range_multiloi.xlsx",engine="xlsxwriter")

for i, day in tqdm(enumerate(ld)) :
    r = rangeTradeMultiLoi(day, vol_option='usdkrw100vol', plot="Y", execution="vwap",
                  loi_redundancy_margin=10*10, pt_margin=5*10, lc_margin=15*10, entry_margin=5*10, scale_entry=10*10)
    
    daily_pl = r['df']['pl'].sum()
    trade_cnt = len(r['df'].index)
    df_summary.loc[day, 'day_pl_sum'] = daily_pl
    df_summary.loc[day, 'day_signal_cnt'] = trade_cnt
    
    # calDailyPlRangeLoi(r, day)
    print("-------------------------------------------------------------\n"
    f'Day   | {day}    pl= {daily_pl}, {trade_cnt}')
    total += daily_pl
    print(total, "   ",total/(i+1))
    print("-------------------------------------------------------------------------------------\n")
df_summary.to_excel(writer)
writer.save()