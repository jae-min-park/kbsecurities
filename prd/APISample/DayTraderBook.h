#pragma once
#include "afxwin.h"
#define MAX_TRADE_NUM 1000

struct TradeBook {
	CString signal_time[MAX_TRADE_NUM];
	float signal_price[MAX_TRADE_NUM];
	CString trade_time[MAX_TRADE_NUM];
	float trade_price[MAX_TRADE_NUM];
	int trade_qty[MAX_TRADE_NUM];
	CString trade_type[MAX_TRADE_NUM];
	CString remark[MAX_TRADE_NUM];
	int pos_id[MAX_TRADE_NUM];

	int trade_num;
};

class DayTraderBook {

public :
	CString product;
	float tick_value;
	int krw_commission_per_contract;
	int krw_value_1pt;

	float tick_conversion;
	struct TradeBook book;

	float max_gain;
	float max_gain_price;
	float draw_down;

	DayTraderBook();
	DayTraderBook(CString jongmok);
	
	void logTrade(CString trade_time, float trade_price, int trade_qty, CString trade_type, CString signal_time, float signal_price, CString remark);

	void exitOpenPosition(CString trade_time, float mid_price, CString remark, float signal_price);

	int getOpenPositionQty();
	int _getOpenPositionStartIndex();
	//bool isMovedEnoughFromLastTrade(float price, float min_price_move_required);

	int getCurQty();

	float getOpenPnl(float price, CString unit);
	float getCumPl(float price, CString unit);

};