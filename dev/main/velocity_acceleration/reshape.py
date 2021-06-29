import pandas as pd

df_sample = pd.read_excel('reshape_real_1d.xlsx')
print(df_sample)
print(len(df_sample.index))

from tqdm import tqdm

df_all = pd.DataFrame(columns=['time', 'price'])

i = 0
total_row = len(df_sample.index)

for row in tqdm(range(1, total_row-1)):
#     print('row=', row)
#     if row == 0:
#         df_all.at['day_open', 'price'] = df_sample.iloc[row]['close']
#     elif row == len(df_sample.index) - 1:
#         df_all.at['day_close', 'price'] = df_sample.iloc[-1]['close']
#     else:
    t = df_sample.iloc[row]['time']
    p = df_sample.iloc[row]['close']
    for v in range(df_sample.iloc[row]['vol']):
        i += 1
#             print(i)
        df_all.at[i, 'time'] = t
        df_all.at[i, 'price'] = p

#2분 50초 걸림

df_reshaped = pd.DataFrame(columns=['time', 'vwap', 'price'])

unit_volume = 30
# num_row = (len(df_all) - (len(df_all) % unit_volume)) / unit_volume
num_row = int(len(df_all) / unit_volume)

for i in tqdm(range(num_row)):
    df_reshaped.at[i, 'time'] = df_all.iloc[(i+1)*unit_volume - 1]['time']
    df_reshaped.at[i, 'vwap'] = round(df_all.iloc[i*unit_volume:(i+1)*unit_volume]['price'].mean(), 4)
    df_reshaped.at[i, 'price'] = round(df_all.iloc[(i+1)*unit_volume-1]['price'], 2)
#     print(i)

dti = df_reshaped.index
for dti_pre, dti_post in zip(dti, dti[1:]) :
    df_reshaped.at[dti_post, 'v1'] = df_reshaped.at[dti_post, 'price'] - df_reshaped.at[dti_pre, 'price']

for dti_pre, dti_post in zip(dti, dti[2:]) :
    df_reshaped.at[dti_post, 'v2'] = df_reshaped.at[dti_post, 'price'] - df_reshaped.at[dti_pre, 'price']

for dti_pre, dti_post in zip(dti, dti[3:]) :
    df_reshaped.at[dti_post, 'v3'] = df_reshaped.at[dti_post, 'price'] - df_reshaped.at[dti_pre, 'price']


# for dti_1, dti_2 in zip(dti[1:], dti[2:]) :
#     df_reshaped.at[dti_2,'a1'] = df_reshaped.at[dti_2,'v1'] - df_reshaped.at[dti_1,'v1']
    
for dti_1, dti_2, dti_3, dti_4 in zip(dti[1:], dti[2:], dti[3:], dti[4:]) :
    df_reshaped.at[dti_2,'a1'] = round(df_reshaped.at[dti_2,'v1'] - df_reshaped.at[dti_1,'v1'],2)
    df_reshaped.at[dti_3,'a2'] = round(df_reshaped.at[dti_3,'v2'] - df_reshaped.at[dti_2,'v2'],2)
    df_reshaped.at[dti_4,'a3'] = round(df_reshaped.at[dti_4,'v3'] - df_reshaped.at[dti_3,'v3'],2)
    

buy_cost = sell_cost = 0
temp = 0
longPosition = False
for i in dti[4:] :
    if df_reshaped.at[i, 'v1'] <= 0 and df_reshaped.at[i, 'a1'] > 0 and df_reshaped.at[i, 'v2'] < 0 and df_reshaped.at[i, 'a2'] > 0 and df_reshaped.at[i, 'v3'] < 0 and df_reshaped.at[i, 'a3'] > 0:
        if i < dti[-1] :
            df_reshaped.at[i+1,'buy'] = True
            longPosition = True
            buy_cost = tenmp = df_reshaped.at[i+1,'buy_cost'] = df_reshaped.at[i+1,'price']
        elif longPosition :
            df_reshaped.at[i,'sell'] = True
            longPosition = False
            sell_cost = df_reshaped.at[i,'sell_cost'] = df_reshaped.at[i,'price']
            df_reshaped.at[i,'profit'] = round(sell_cost-buy_cost,2)
    else:
        if longPosition :
            if i < dti[-1] :
                if temp <= df_reshaped.at[i+1,'price']:
                    temp = df_reshaped.at[i+1,'price']
                else:
                    df_reshaped.at[i+1,'sell'] = True
                    longPosition=False
                    sell_cost = df_reshaped.at[i+1,'sell_cost'] = df_reshaped.at[i+1, 'price']
                    df_reshaped.at[i+1,'profit'] = round(sell_cost-buy_cost,2)
            else:
                df_reshaped.at[i,'sell'] = True
                longPosition = False
                sell_cost = df_reshaped.at[i,'sell_cost'] = df_reshaped.at[i,'price']
                df_reshaped.at[i,'profit'] = round(sell_cost-buy_cost,2)

df_reshaped.to_excel("df_reshaped.xlsx")

