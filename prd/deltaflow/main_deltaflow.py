import load_deltaflow_30y as ldf30y
import load_deltaflow_3y as ldf3y
import load_deltaflow_10y as ldf10y
import load_deltaflow_5y as ldf5y
import pandas as pd
from datetime import datetime
pd.options.mode.chained_assignment = None


# # 30년입찰주
# calendar,last_df = ldf30y.showDeltaflow(date = str(datetime.now())[:10], month=8,first_day ='2021-01-01', y5_day='2020-12-07')
# calendar,last_df = ldf30y.showDeltaflow(date = '2021-08-30', month=8,first_day ='2021-01-01', y5_day='2020-12-07')

# # 3년입찰주
# calendar,last_df = ldf3y.showDeltaflow(date = str(datetime.now())[:10], month=8,first_day ='2021-01-01', y5_day='2020-12-07')

# 10년입찰주
calendar, last_df = ldf10y.showDeltaflow(date = str(datetime.now())[:10], month=8,first_day ='2021-01-01', y5_day='2020-12-07')
# calendar, last_df = ldf10y.showDeltaflow(date = '2021-08-20', month=7, first_day ='2021-01-01', y5_day='2020-12-07')

# 5년입찰주 및 입찰공백주
# calendar, last_df = ldf5y.showDeltaflow(date = str(datetime.now())[:10], month=8,first_day ='2021-01-01', y5_day='2020-12-07')
# calendar, last_df = ldf5y.showDeltaflow(date = '2021-08-24', month=8,first_day ='2021-01-01', y5_day='2020-12-07')
