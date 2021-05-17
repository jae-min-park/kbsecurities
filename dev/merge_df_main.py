import pandas as pd


date = [pd.to_datetime("2020-02-01 11:00:00"), pd.to_datetime("2020-02-01 11:00:01"), pd.to_datetime("2020-02-01 11:00:03")]
param = {
        'direction' : [1,-1,1],
        'price' : [128.12, 122.23, 125.5]
        }
df1 = pd.DataFrame(param, index=date)

date = [pd.to_datetime("2020-02-01 11:00:01"), pd.to_datetime("2020-02-01 11:00:03"), pd.to_datetime("2020-02-01 11:00:05")]
param = {
        'close' : [1,1,0],
        'price' : [128.34, 122.11, 125.2]
        }
df2 = pd.DataFrame(param, index=date)

date = [pd.to_datetime("2020-02-01 11:00:01"), pd.to_datetime("2020-02-01 11:00:03"), pd.to_datetime("2020-02-02 11:00:05")]
param = {
        'open' : [-1,1,0],
        'close' : [0,1,-1],
        'price' : [128.00, 122.11, 125.2]
        }
df3 = pd.DataFrame(param, index=date)


def getIndex(*items) :
    index = items[0]['df'].index
    for item in items :
        index = index.append(item.df.index)
    idx = sorted(list(set(index)))
    return idx

def merge(idx, *items) :
    cols=[]
    for item in items:
        cols = cols.append(item.loi_option)
    result = pd.DataFrame(index = idx, columns=cols)
    result = result.fillna(0)
    for i in idx : 
        for item in items:
            if item['loi_option'] == 'open':
                if i in item['df'].index:
                    result.loc[i,'open'] += item.loc[i,'open']
                    result.loc[i,'price'] = item.loc[i,'price']
            elif item['loi_option'] == 'close':
                if i in item['df'].index:
                    result.loc[i,'close'] += item.loc[i,'close']
                    result.loc[i,'price'] = item.loc[i,'price']
                            
    return result
                

idx = getIndex(df1,df2)

df = merge(idx, df1,df2)
print(df)
