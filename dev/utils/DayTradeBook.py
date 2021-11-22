# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 19:08:16 2021

@author: infomax
"""


import pandas as pd
import numpy as np
import datetime
import os
from tqdm import tqdm
import sys
sys.path.append('D:\\dev\\kbsecurities\\dev\\utils')
import util

class DayTradeBook:
    
    """
    한 전략에 대해 해당일의 매매에 대한 기록을 담는 class
        - 상품에 대한 기본 정보도 같이 담는다
        - PLOTTING 기능도 탑재?
    
    2021.11.12
    """
    
    def __init__(self, date, db_table):
        
        if db_table[:3] == 'lkt':
            self.product = 'lktbf'
            self.tick_value = 0.01
            self.krw_commission_per_contract = 250 # 원래 248.95원/계약
            self.krw_value_1pt = 10**6
        elif db_table[:3] == 'ktb':
            self.product = 'ktbf'
            self.tick_value = 0.01
            self.krw_commission_per_contract = 250 # 원래 225.5원/계약
            self.krw_value_1pt = 10**6
        elif db_table[:3] == 'usd':
            self.product = 'usdkrw'
            self.tick_value = 0.1
            self.krw_commission_per_contract = 60 # 원래 57.9원/계약
            self.krw_value_1pt = 10**4
        else:
            raise NameError('Unexpected product')
            
        self.tick_conversion = 1 / self.tick_value
                
        self.date = date
        self.yday = util.date_offset(date, -1)
        
        self.yday_close = util.getDdayOHLC(self.yday, table=self.product + '_day')['close']
        self.yday_lo = util.getDdayOHLC(self.yday, table=self.product + '_day')['low']
        self.yday_hi = util.getDdayOHLC(self.yday, table=self.product + '_day')['high']
        
        self.siga_time = util.getMktTime(date)['start']
        
        self.book = pd.DataFrame(
            columns=['signal_time',
                     'signal_price',
                     'trade_time',
                     'trade_price',
                     'trade_qty',
                     'trade_type',
                     'remark',
                     'pos_id',
                     ])
        
        
        
    def logTrade(self, trade_time, trade_price, trade_qty, trade_type, 
                 signal_time=None, signal_price=None, remark=None):
        if signal_time == None: signal_time = trade_time
        if signal_price == None: signal_price = trade_price
        
        if trade_type == 'ini':
            if self.book.empty:
                pos_id = 1
            else:
                pos_id = self.book['pos_id'].iloc[-1] + 1
        else:
            pos_id = self.book['pos_id'].iloc[-1]
            
        row =[signal_time, signal_price, 
              trade_time, trade_price, trade_qty, 
              trade_type, remark, pos_id]
        self.book.loc[len(self.book)] = row
        print(trade_time, trade_price, trade_qty, trade_type, remark)
        pass
    
    def exitOpenPosition(self, trade_time, mid_price, remark, signal_price=None):
        open_position_qty = self.getOpenPositionQty()
        
        if open_position_qty == 0:
            raise ValueError("No Open Position")
        else:
            if open_position_qty > 0:
                self.logTrade(trade_time = trade_time, 
                              trade_price = mid_price - 0.5*self.tick_value, 
                              trade_qty = -open_position_qty,
                              trade_type='ext',
                              remark = remark,
                              signal_price=signal_price)
            else:
                self.logTrade(trade_time = trade_time, 
                              trade_price = mid_price + 0.5*self.tick_value, 
                              trade_qty = -open_position_qty, 
                              trade_type='ext',
                              remark = remark,
                              signal_price=signal_price)
        pass
    
    def addDatetimeColumn(self):
        if not self.book.empty:
            self.book['datetime'] = self.book['trade_time'].apply(lambda x: x + pd.Timestamp(self.date))
        pass
        
    def getOpenPositionQty(self):
        return self.book['trade_qty'].sum()
    
    def _getOpenPositionStartIndex(self):
        if self.book.empty:
            raise ValueError("No Trade yet")
        else:
            if not 'ext' in self.book.trade_type.values: # ext trade 한번도 없었음
                return 0
            elif self.book.trade_type.values[-1] == 'ext':
                raise ValueError("No Open Position")
            else:
                last_exit_index = self.book[self.book['trade_type'] == 'ext'].index[-1]
            return last_exit_index+1
    
    def _getOpenPositionTradeQtyArray(self):
        i_open = self._getOpenPositionStartIndex()
        return np.array(self.book[i_open:]['trade_qty'])
    
    def _getOpenPositionTradePriceArray(self):
        i_open = self._getOpenPositionStartIndex()
        return np.array(self.book[i_open:]['trade_price'])
    
    def getLastTradePrice(self):
        if self.book.empty:
            raise ValueError("No trade yet")
        else:
            return self.book['trade_price'].iloc[-1]
        
    def getLastTradeQty(self):
        if self.book.empty:
            raise ValueError("No trade yet")
        else:
            return self.book['trade_qty'].iloc[-1]
    
    def isMovedEnoughFromLastTrade(self, price, min_price_move_required):
        # mean reversion 관점에서 최근거래대비 가격 개선 여부를 체크 
        if self.book.empty: # 거래가 없는 경우
            return True
        elif self.getOpenPositionQty() == 0: # 거래는 있었는데 Open은 없는 경우
            return True
        else: # open position이 있는 경우
            # 마지막이 숏인 경우 더 강해져야 add
            if  self.getLastTradeQty() < 0:
                if price - self.getLastTradePrice() > min_price_move_required:
                    return True
            # 마지막이 롱인 경우 더 밀려야 add
            elif self.getLastTradeQty() > 0:
                if price - self.getLastTradePrice() < -min_price_move_required:
                    return True
            else: 
                return False
    
    def getLastClosedPositionInfo(self):
        if not 'ext' in self.book.trade_type.values: # ext trade 한번도 없었음
            raise ValueError("No Closed position yet")
        else:
            last_exit_index = self.book[self.book['trade_type'] == 'ext'].index[-1]
            last_pos_id = self.book.loc[last_exit_index]['pos_id']
            last_pos_book = self.book[self.book['pos_id'] == last_pos_id]
            
            last_pos_direction = 'short' if last_pos_book.iloc[0]['trade_qty'] < 0 else 'long'
            last_pos_remark = last_pos_book.iloc[-1]['remark']
            
            return last_pos_direction, last_pos_remark
            
        
    
    def getOpenPnl(self, price, unit='krw'):
        """
        returns open position pnl in unit ('krw' or 'tick')
        """
        if self.getOpenPositionQty() == 0:
            raise ValueError("No Open Position")
        else:
            qty_arr = self._getOpenPositionTradeQtyArray()
            price_arr = self._getOpenPositionTradePriceArray()
            sumproduct = sum(qty_arr * (price - price_arr))
            commission = sum(abs(qty_arr)) * self.krw_commission_per_contract
            
            if unit == 'krw':
                return round(self.krw_value_1pt * sumproduct - commission, 0)
            
            elif unit == 'tick': # without commission
                return round(self.tick_conversion * sumproduct / sum(qty_arr), 2)
            
    def getCumPl(self, price=None, unit='krw'):
        """
        returns cumulative pnl in unit ('krw' or 'tick')
        """
        if self.book.empty:
            return 0
        else:
            if price == None:
                price = self.book['trade_price'].iloc[-1]
            qty_arr = np.array(self.book.trade_qty)
            price_arr = np.array(self.book.trade_price)
            sumproduct = sum(qty_arr * (price - price_arr))
            commission = sum(abs(qty_arr)) * self.krw_commission_per_contract
            
            if unit == 'krw':
                return round(self.krw_value_1pt * sumproduct - commission, 0)
            
            elif unit == 'tick': # without commission
                return round(self.tick_conversion * sumproduct / sum(qty_arr), 2)

    def __repr__(self):
        return self.book.__repr__()


# date = datetime.date(2021, 1, 14)
# b = DayTradeBook(date, 'lktbf_10sec')

# tl = []
# for i in range(8):
#     tl.append(datetime.time(9, i+1))

# prl = []
# for i in range(8):
#     prl.append(101.01 + i/100)

# ql = [20, -20, 20, 20, -40, -20, 20, 20]

# tyl = ['ini', 'ext', 'ini', 'add', 'ext', 'ini', 'ext', 'ini']

# for i in range(8):
#     b.logTrade(tl[i], prl[i], ql[i], tyl[i])

# print(b)
# print(b.getCumPl(101.10))


# b2 = DayTradeBook(date, 'lktbf_10sec')
# b2.logTrade(tl[0], prl[0], ql[0], 'ini')
# b2.logTrade(tl[0], prl[0], ql[0], 'add')

# print(b2.getOpenPnl(101.10))

# df = b.book
# df2 = b2.book
# df0 = DayTradeBook(date, 'lktbf_10sec').book
# dfext = df.drop(index=7)

        
    
    
    
    
    
        
        
        
            