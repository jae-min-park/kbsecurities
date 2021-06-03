import utils.util as util
import datetime
import pandas as pd
import numpy as np

date = datetime.date(2021,6,3)
vol_option='usdkrwtick'

dftick = util.setDfData(date, date, vol_option)
dfbinned = pd.DataFrame(columns=['date','time','vwap','price','open','high','low'])

vol_bin = 100

vol_list = []
prc_list = []

i_resampled = 0

for i in dftick.index:
    vol = dftick.at[i, 'vol']
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
            dfbinned.at[i_resampled, 'time'] = dftick.at[i, 'time']
            dfbinned.at[i_resampled, 'price'] = dftick.at[i, 'close']
            dfbinned.at[i_resampled, 'open'] = dftick.iloc[0]['close']
            dfbinned.at[i_resampled, 'high'] = dfbinned.price.max()
            dfbinned.at[i_resampled, 'low'] = dfbinned.price.min()
            i_resampled += 1
        
        vol_list = [leftover] #[0]이어도 무관
        prc_list = [prc]
    
    else:
        pass
    