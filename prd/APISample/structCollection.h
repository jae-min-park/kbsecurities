#include<string>
#include<iostream>
#pragma once

struct HogaSise {
	CString type;
	CString code;

	float price;
	int c_price;
	int volume;
	double pre_price;
	CString time;

	float buy_hoga1_price;
	float buy_hoga2_price;
	float sell_hoga1_price;
	float sell_hoga2_price;

	int buy_hoga1_balance;
	int buy_hoga2_balance;
	int sell_hoga1_balance;
	int sell_hoga2_balance;

	int buy_hoga1_count;
	int buy_hoga2_count;
	int sell_hoga1_count;
	int sell_hoga2_count;

	CString sell_or_buy;

};

struct candleSecond {
	CString type;
	CString code;

	int hour;
	int min;
	int sec;

	float price;
	int volume;
};

struct Trade {
	int direction;
	CString product;
	int product_multiplier;

	bool is_triggered;
	bool is_traded;
	float trade_price;
	CString trade_time;

	bool is_timely_close;

	bool is_losscut_triggered;
	bool is_losscut_traded;
	float losscut_price;
	//char losscut_time[7];

	bool is_pt_triggered;
	bool is_pt_traded;
	float pt_price;
	//char pt_time[7];

	float pl;

	float max_gain;
	float max_gain_price;
	//char max_gain_time[7];
	float draw_down;
};

struct OrderItem {
	CString orgordno;
	int intQty;
	float floatPrice;
	CString strGubun;
	CString strItemCode;
	CString jongmok;
};