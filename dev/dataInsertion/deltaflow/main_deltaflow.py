import load_deltaflow_30y as ldf30y
import load_deltaflow_3y as ldf3y
import load_deltaflow_10y as ldf10y
import load_deltaflow_5y as ldf5y
import pandas as pd
pd.options.mode.chained_assignment = None


# # 30년입찰주
# calendar = ldf30y.showDeltaflow(month=7,first_day ='2021-01-01', y5_day='2020-12-07')

# # 3년입찰주
# calendar = ldf3y.showDeltaflow(month=7,first_day ='2021-01-01', y5_day='2020-12-07')

# 10년입찰주
calendar = ldf10y.showDeltaflow(month=7,first_day ='2021-01-01', y5_day='2020-12-07')

# 5년입찰주 및 입찰공백주
# calendar = ldf5y.showDeltaflow(month=7,first_day ='2021-01-01', y5_day='2020-12-07')
