import pandas as pd
import matplotlib.pyplot as plt
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 15:18:14 2021

@author: infomax
"""

data = []

f = open('udp.txt', 'rt', encoding='UTF8')

col = ['DATA구분', '현재가격','체결수량','시각', '직전가격', '최종매도매수구분코드', 
       '매수1단계우선호가가격','매수1단계우선호가잔량','매수2단계우선호가가격','매수2단계우선호가잔량',
       '매도1단계우선호가가격','매도1단계우선호가잔량','매도2단계우선호가가격','매도2단계우선호가잔량',
       '매수1단계우선호가건수','매수2단계우선호가건수','매도1단계우선호가건수','매도2단계우선호가건수'
       ]
df = pd.DataFrame(columns = col)

line_num = 0
line = f.readline()
while line:
    goo_boon = line[:2]
    line_num += 1
    # if line_num == 644 : 
    #     print(line)
    if goo_boon == 'A3':
        df.loc[line_num, 'DATA구분'] = goo_boon
        df.loc[line_num, '현재가격'] = float(line[23:31])/100
        df.loc[line_num, '체결수량'] = int(line[31:37])

        time = line[39:47]
        hour = int(time[:2])
        minute = int(time[2:4])
        sec = float(time[4:6]+'.'+time[6:])

        df.loc[line_num, '시각'] = pd.Timedelta(hours= hour, minutes = minute, seconds=sec)
        df.loc[line_num, '직전가격'] = float(line[91:99])/100
        df.loc[line_num, '최종매도매수구분코드'] = line[135:136]
        
        # tmp = {
        #     'DATA구분' : goo_boon,
        #     '현재가격' : float(line[23:31])/100,
        #     '체결수량' : int(line[31:37]),
        #     '체결시각' : line[39:47],
        #     '직전가격' : float(line[91:99])/100,
        #     '최종매도매수구분코드' : line[135:136]
        #     }
        # data.append(tmp)
    elif goo_boon == 'B6':
        df.loc[line_num, 'DATA구분'] = goo_boon
        df.loc[line_num, '매수1단계우선호가가격'] = float(line[32:40])/100
        df.loc[line_num, '매수1단계우선호가잔량'] = int(line[40:46])
        df.loc[line_num, '매수2단계우선호가가격'] = float(line[47:55])/100
        df.loc[line_num, '매수2단계우선호가잔량'] = int(line[55:61])
        
        df.loc[line_num, '매도1단계우선호가가격'] = float(line[114:122])/100
        df.loc[line_num, '매도1단계우선호가잔량'] = int(line[122:128])
        df.loc[line_num, '매도2단계우선호가가격'] = float(line[129:137])/100
        df.loc[line_num, '매도2단계우선호가잔량'] = int(line[137:143])
        
        df.loc[line_num, '매수1단계우선호가건수'] = int(line[193:197])
        df.loc[line_num, '매수2단계우선호가건수'] = int(line[197:201])
        df.loc[line_num, '매도1단계우선호가건수'] = int(line[218:222])
        df.loc[line_num, '매도2단계우선호가건수'] = int(line[222:226])

        time = line[238:246]        
        hour = int(time[:2])
        minute = int(time[2:4])
        sec = float(time[4:6]+'.'+time[6:])
        
        df.loc[line_num, '시각'] = pd.Timedelta(hours= hour, minutes = minute, seconds=sec)
        
        # tmp = {
        #     'DATA구분' : goo_boon,
        #     '매수1단계우선호가가격' : float(line[32:40])/100,
        #     '매수1단계우선호가잔량' : int(line[40:46]),
        #     '매수2단계우선호가가격' : float(line[47:55])/100,
        #     '매수2단계우선호가잔량' : int(line[55:61]),

        #     '매도1단계우선호가가격' : float(line[114:122])/100,
        #     '매도1단계우선호가잔량' : int(line[122:128]),
        #     '매도2단계우선호가가격' : float(line[129:137])/100,
        #     '매도2단계우선호가잔량' : int(line[137:143]),

        #     '매수1단계우선호가건수' : int(line[193:197]),
        #     '매수2단계우선호가건수' : int(line[197:201]),
        #     '매도1단계우선호가건수' : int(line[218:222]),
        #     '매도2단계우선호가건수' : int(line[222:226]),
        #     '호가접수시간' : line[238:246]
        #     }
        # data.append(tmp)
    elif goo_boon == 'G7':
        df.loc[line_num, 'DATA구분'] = goo_boon
        df.loc[line_num, '현재가격'] = float(line[23:31])/100
        df.loc[line_num, '체결수량'] = int(line[31:37])
        
        time = line[39:47]
        hour = int(time[:2])
        minute = int(time[2:4])
        sec = float(time[4:6]+'.'+time[6:])
        df.loc[line_num, '시각'] = pd.Timedelta(hours= hour, minutes = minute, seconds=sec)
        
        df.loc[line_num, '직전가격'] = float(line[91:99])/100
        df.loc[line_num, '최종매도매수구분코드'] = line[135:136]
        
        df.loc[line_num, '매수1단계우선호가가격'] = float(line[144:152])/100
        df.loc[line_num, '매수1단계우선호가잔량'] = int(line[152:158])
        df.loc[line_num, '매수2단계우선호가가격'] = float(line[159:167])/100
        df.loc[line_num, '매수2단계우선호가잔량'] = int(line[167:173])
        
        df.loc[line_num, '매도1단계우선호가가격'] = float(line[226:234])/100
        df.loc[line_num, '매도1단계우선호가잔량'] = int(line[234:240])
        df.loc[line_num, '매도2단계우선호가가격'] = float(line[241:249])/100
        df.loc[line_num, '매도2단계우선호가잔량'] = int(line[249:255])
        
        df.loc[line_num, '매수1단계우선호가건수'] = int(line[305:309])
        df.loc[line_num, '매수2단계우선호가건수'] = int(line[309:313])
        df.loc[line_num, '매도1단계우선호가건수'] = int(line[330:334])
        df.loc[line_num, '매도2단계우선호가건수'] = int(line[334:338])
        # tmp = {
        #     'DATA구분' : goo_boon,
        #     '현재가격' : float(line[23:31])/100,
        #     '체결수량' : int(line[31:37]),
        #     '체결시각' : line[39:47],
        #     '직전가격' : float(line[91:99])/100,
        #     '최종매도매수구분코드' : line[135:136],

        #     '매수1단계우선호가가격' : float(line[144:152])/100,
        #     '매수1단계우선호가잔량' : int(line[152:158]),
        #     '매수2단계우선호가가격' : float(line[159:167])/100,
        #     '매수2단계우선호가잔량' : int(line[167:173]),
            
        #     '매도1단계우선호가가격' : float(line[226:234])/100,
        #     '매도1단계우선호가잔량' : int(line[234:240]),
        #     '매도2단계우선호가가격' : float(line[241:249])/100,
        #     '매도2단계우선호가잔량' : int(line[249:255]),

        #     '매수1단계우선호가건수' : int(line[305:309]),
        #     '매수2단계우선호가건수' : int(line[309:313]),
        #     '매도1단계우선호가건수' : int(line[330:334]),
        #     '매도2단계우선호가건수' : int(line[334:338]),     
        #     }
        # data.append(tmp)
    else :
        line_num-=1
        pass
    line = f.readline()

df.fillna(0.0)

f.close()

