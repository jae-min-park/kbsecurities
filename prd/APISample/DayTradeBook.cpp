#include "stdafx.h"
#include "DayTraderBook.h"
using namespace std;

DayTraderBook::DayTraderBook() {

	CString jongmok = "LKTBF";
	if (jongmok == "KTBF" || jongmok == "LKTBF") {
		product = jongmok;
		tick_value=0.01;
		krw_commission_per_contract = 250;
		krw_value_1pt = 1000000;
	} else if (jongmok == "USD") {
		product = jongmok;
		tick_value = 0.1;
		krw_commission_per_contract = 60;
		krw_value_1pt = 10000;
	} else {
		throw ERROR("Unexpected product");
	}
	tick_conversion = 1 / tick_value;
	book.trade_num = 0;
}

DayTraderBook::DayTraderBook(CString jongmok) {
	if (jongmok == "KTBF" || jongmok == "LKTBF") {
		product = jongmok;
		tick_value=0.01;
		krw_commission_per_contract = 250;
		krw_value_1pt = 1000000;
	} else if (jongmok == "USD") {
		product = jongmok;
		tick_value = 0.1;
		krw_commission_per_contract = 60;
		krw_value_1pt = 10000;
	} else {
		throw ERROR("Unexpected product");
	}
	tick_conversion = 1 / tick_value;
	book.trade_num = 0;
}

void DayTraderBook::logTrade(CString trade_time, float trade_price, int trade_qty, CString trade_type, CString signal_time, float signal_price, CString remark) {

	if (signal_time == "") {signal_time = trade_time;}
	if (signal_price == 0) {signal_price = trade_price;}

	int pos_id=1;
	if (trade_type == "ini") {
		if (book.trade_num == 0) {
			pos_id = 1;
		} else {
			pos_id = book.pos_id[book.trade_num] +1;
		}
	} else {
		pos_id = book.pos_id[book.trade_num];
	}

	book.signal_time[book.trade_num] = signal_time;
	book.signal_price[book.trade_num] = signal_price;
	book.trade_qty[book.trade_num] = trade_qty;
	book.trade_type[book.trade_num] = trade_type;
	book.trade_time[book.trade_num] = trade_time;
	book.trade_price[book.trade_num] = trade_price;
	book.remark[book.trade_num] = remark;
	book.pos_id[book.trade_num] = pos_id;
	
	book.trade_num++;
}

void DayTraderBook::exitOpenPosition(CString trade_time, float mid_price, CString remark, float signal_price) {
	int open_position_qty = getOpenPositionQty();
	if (open_position_qty == 0) {
		throw ERROR("No open position");
	} else {
		if (open_position_qty >0 ) {
			logTrade(trade_time, mid_price-0.5*tick_value, -open_position_qty, "ext", "", 0,remark);
		} else {
			logTrade(trade_time, mid_price+0.5*tick_value, -open_position_qty, "ext", "", 0, remark);
		}
	}
}

int DayTraderBook::getOpenPositionQty() {
	int sumQty = 0;
	for (int i = 0; i < book.trade_num; i++) {
		sumQty += book.trade_qty[i];
	}
	return sumQty;
}

int DayTraderBook::_getOpenPositionStartIndex() {
	if (book.trade_num == 0) {
		throw ERROR("No trade yet"); // no open position
	} else { 
		int idx = 0;
		for (int i = book.trade_num-1; i >0 ;i--) {
			if (book.trade_type[i] =="ext") {
				idx = i;
				break;
			}
		}

		if (idx == 0) { // non exist
			return 0;
		} else if (idx == book.trade_num-1) {
			throw ERROR("No open position");  //no open position
		} else {
			return idx+1; // openposition 이 있고 정상적인 경우
		}

		return -1;
	}
}

//bool DayTraderBook::isMovedEnoughFromLastTrade(float price, float min_price_move_required) {
//	if (book.trade_num == 0) {
//		return true;
//	} else {
//		float abs = (price - book.trade_price[book.trade_num-1] > 0) ? price - book.trade_price[book.trade_num-1] : - price + book.trade_price[book.trade_num-1];
//		if (abs > min_price_move_required) {
//			return true;
//		} else {
//			return false;
//		}
//	}
//}
int DayTraderBook::getCurQty() {
	if(book.trade_num==0) {
		return 0;
	}
	int qty = 0;
	for(int i =0; i< book.trade_num; i++) {
		qty += book.trade_qty[i];
	}
	return qty;
}

float DayTraderBook::getOpenPnl(float price, CString unit) {
	if (getOpenPositionQty() == 0 ) { 
		throw ERROR("No open position"); // no open position
	} else {
		float sum_product = 0;
		float commission = 0;
		for (int i = _getOpenPositionStartIndex(); i< book.trade_num; i++ ) {
			sum_product += book.trade_qty[i] * book.trade_price[i];
			commission += krw_commission_per_contract * ((book.trade_qty[i] >0)? book.trade_qty[i] : -book.trade_qty[i]);
		}

		if (unit =="krw") {
			return int(krw_value_1pt * sum_product-commission);
		} else if (unit =="tick") { // without commission
			int tmp = tick_conversion * sum_product / (float)getOpenPositionQty() * 100;
			return (float)tmp / 100;
		}
	}
}

float DayTraderBook::getCumPl(float price, CString unit) {
	if (book.trade_num == 0) {
		return 0;
	} else {
		float sum_product = 0;
		float commission = 0;
		for (int i = 0; i< book.trade_num; i++ ) {
			sum_product += book.trade_qty[i] * (price - book.trade_price[i]);
			commission += krw_commission_per_contract * ((book.trade_qty[i] >0)? book.trade_qty[i] : -book.trade_qty[i]);
		}
		if (unit == "krw") {
			return int(krw_value_1pt * sum_product - commission);
		} else if (unit =="tick") {
			int tmp = tick_conversion * sum_product / (float)getOpenPositionQty() * 100;
			return (float)tmp / 100;
		}
	}
}