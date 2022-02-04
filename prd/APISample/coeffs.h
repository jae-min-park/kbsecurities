#pragma once
#include "structCollection.h"
#include<iostream>
#include<string.h>
#include<string>
#include"DayTraderBook.h"

static int test_int = 0;
/*edr stratagy*/
static CString ktbf_trading_time_start = "090000";		static CString lktbf_trading_time_start = "090000";			static CString usd_trading_time_start = "090000";
static bool ktbf_edr = false;							static bool lktbf_edr = false;								static bool usd_edr = false;
static float ktbf_diff_std = 0.0166;					static float lktbf_diff_std = 0.04;							static float usd_diff_std = 0.321194;
static float ktbf_edr_fast_coeff = 0.2;					static float lktbf_edr_fast_coeff = 0.2;					static float usd_edr_fast_coeff = 0.07;
static float ktbf_edr_slow_coeff = 0.03;				static float lktbf_edr_slow_coeff = 0.03;					static float usd_edr_slow_coeff = 0.01;
static float ktbf_edr_ema_fast =0;						static float lktbf_edr_ema_fast =0;							static float usd_edr_ema_fast =0;
static float ktbf_edr_ema_slow =0;						static float lktbf_edr_ema_slow =0;							static float usd_edr_ema_slow =0;
static int ktbf_edr_max_trade_qty =4;					static int lktbf_edr_max_trade_qty =4;						static int usd_edr_max_trade_qty =10;
static int ktbf_edr_max_qty = 25;						static int lktbf_edr_max_qty = 20;							static int usd_edr_max_qty = 100;
static float ktbf_edr_tick_cross_margin=0.1;			static float lktbf_edr_tick_cross_margin=0.5;				static float usd_edr_tick_cross_margin=0.5;
static bool ktbf_being_trade=false;						static bool lktbf_being_trade=false;						static bool usd_being_trade=false;
static float ktbf_last_prc;								static float lktbf_last_prc;								static float usd_last_prc;

static int ktbf_abs_max_short_qty = 25;				static int lktbf_abs_max_short_qty = 200;					static int usd_abs_max_short_qty = 10;
static int ktbf_edr_losscut = -30000000;				static int lktbf_edr_losscut = -30000000;					static int usd_edr_losscut = -30000000;

static float ktbf_krw_commission_per_contract = 250;	static float lktbf_krw_commission_per_contract = 250;		static float usd_krw_commission_per_contract = 60;
static float ktbf_tick_value = 0.01;					static float lktbf_tick_value = 0.01;						static float usd_tick_value = 0.1;
static int ktbf_krw_value_1pt=1000000;					static int lktbf_krw_value_1pt = 1000000;					static int usd_krw_value_1pt=10000;
static float ktbf_tick_conversion = 1/ktbf_tick_value;	static float lktbf_tick_conversion = 1/lktbf_tick_value;	static float usd_tick_conversion = 1/usd_tick_value;
static float ktbf_tick_diff_of_max_qty = 1.5*ktbf_diff_std * ktbf_tick_conversion;
static float lktbf_tick_diff_of_max_qty = 1.5*lktbf_diff_std * lktbf_tick_conversion;
static float usd_tick_diff_of_max_qty = 1.5*usd_diff_std * usd_tick_conversion;
static int ktbf_edr_trade_qty=0;						static int lktbf_edr_trade_qty = 0;							static int usd_edr_trade_qty=0;
static int ktbf_edr_actual_qty = 0;						static int lktbf_edr_actual_qty = 0;						static int usd_edr_actual_qty = 0;
static int ktbf_edr_pre_qty = 0;						static int lktbf_edr_pre_qty = 0;							static int usd_edr_pre_qty = 0;

static bool ktbf_edr_changed_qty=false;					static bool lktbf_edr_changed_qty=false;					static bool usd_edr_changed_qty=false;

static int ktbf_edr_target_qty=0;						static int lktbf_edr_target_qty=0;							static int usd_edr_target_qty=0;
static int ktbf_edr_pre_target_qty=0;					static int lktbf_edr_pre_target_qty=0;						static int usd_edr_pre_target_qty=0;
static int ktbf_edr_pre_trade_qty_raw=0;				static int lktbf_edr_pre_trade_qty_raw=0;					static int usd_edr_pre_trade_qty_raw=0;
static int ktbf_edr_pre_trade_qty=0;					static int lktbf_edr_pre_trade_qty=0;						static int usd_edr_pre_trade_qty=0;

static bool ktbf_edr_signal;							static bool lktbf_edr_signal;								static bool usd_edr_signal;

static int ktbf_edr_trade_qty_list[10000]={};			static int lktbf_edr_trade_qty_list[10000]={};				static int usd_edr_trade_qty_list[10000]={};
static float ktbf_edr_trade_prc_list[10000]={};			static float lktbf_edr_trade_prc_list[10000]={};			static float usd_edr_trade_prc_list[10000]={};
static int ktbf_edr_trade_num = 0;						static int lktbf_edr_trade_num = 0;							static int usd_edr_trade_num = 0;

static OrderItem ktbf_edr_pendingList[10000]={};		static OrderItem lktbf_edr_pendingList[10000]={};			static OrderItem usd_edr_pendingList[10000]={};
static int ktbf_edr_pendingListIndex=0;					static int lktbf_edr_pendingListIndex=0;					static int usd_edr_pendingListIndex=0;
static int ktbf_edr_pending_sum_qty=0;					static int lktbf_edr_pending_sum_qty=0;						static int usd_edr_pending_sum_qty=0;

/*AF stratagy*/
static CString trading_begins_after = "120000";
static CString trading_begins_before = "152500";
static CString trading_hour_ends = "153500";				

static bool ktbf_af = false;							static bool lktbf_af = false;							static bool usd_af = false;
static int ktbf_product_multiplier = 100;				static int lktbf_product_multiplier = 100;				static int usd_product_multiplier = 10;
static int ktbf_QTY_PER_TRADE = 50;						static int lktbf_QTY_PER_TRADE = 50;					static int usd_QTY_PER_TRADE = 50;
static float ktbf_fast_coeff = 0.1;						static float lktbf_fast_coeff = 0.10;					static float usd_fast_coeff = 0.01;
static float ktbf_slow_coeff = 0.02;					static float lktbf_slow_coeff = 0.02;					static float usd_slow_coeff = 0.02;
static float ktbf_thru = 0.5;							static float lktbf_thru = 0.5;							static float usd_thru = 0.5;
static float ktbf_ema_margin = 0.5;						static float lktbf_ema_margin = 0.5;					static float usd_ema_margin = 0.5;
static float ktbf_lc_hi_lo = 1.0;						static float lktbf_lc_hi_lo = 1.0;						static float usd_lc_hi_lo = 1.0;
static float ktbf_lc_pl = -25;							static float lktbf_lc_pl = -25;							static float usd_lc_pl = -25;
static float ktbf_pt_pl = 25;							static float lktbf_pt_pl = 25;							static float usd_pt_pl = 25;
static float ktbf_pt_draw_down = 0.3;					static float lktbf_pt_draw_down = 0.3;					static float usd_pt_draw_down = 0.3;

static float ktbf_intra_lo = 99999;						static float lktbf_intra_lo = 99999;					static float usd_intra_lo = 99999;
static float ktbf_intra_hi = -99999;					static float lktbf_intra_hi = -99999;					static float usd_intra_hi = -99999;

static bool ktbf_is_losscut_traded;						static bool lktbf_is_losscut_traded;					static bool usd_is_losscut_traded;
static bool ktbf_is_pt_traded;							static bool lktbf_is_pt_traded;							static bool usd_is_pt_traded;
static bool ktbf_is_losscut_traded2;					static bool lktbf_is_losscut_traded2;					static bool usd_is_losscut_traded2;
static bool ktbf_is_pt_traded2;							static bool lktbf_is_pt_traded2;						static bool usd_is_pt_traded2;
static bool ktbf_is_first_done;							static bool lktbf_is_first_done;						static bool usd_is_first_done;
static bool ktbf_is_traded;								static bool lktbf_is_traded;							static bool usd_is_traded;
static bool ktbf_is_traded2;							static bool lktbf_is_traded2;							static bool usd_is_traded2;
static int ktbf_qty;									static int lktbf_qty;									static int usd_qty;
static bool ktbf_af_signal;								static bool lktbf_af_signal;							static bool usd_af_signal;
static OrderItem ktbf_af_pendingList[10000]={};			static OrderItem lktbf_af_pendingList[10000]={};		static OrderItem usd_af_pendingList[10000]={};
static int ktbf_af_pendingListIndex=0;					static int lktbf_af_pendingListIndex=0;					static int usd_af_pendingListIndex=0;

static float ktbf_enter_prc;							static float lktbf_enter_prc;							static float usd_enter_prc;
static float ktbf_pt_prc;								static float lktbf_pt_prc;								static float usd_pt_prc;
static float ktbf_lc_prc;								static float lktbf_lc_prc;								static float usd_lc_prc;
//static DayTraderBook ktbf_af_tr_book=DayTraderBook("KTBF");
//static DayTraderBook lktbf_af_tr_book=DayTraderBook("LKTBF");
//static DayTraderBook usd_af_tr_book=DayTraderBook("USD");;

static CString ktbf_ten_sec_candle[2430]={};			static CString lktbf_ten_sec_candle[2430]={};			static CString usd_ten_sec_candle[2430]={};
//static CString ktbf_one_sec_candle[24300]={};			static CString lktbf_one_sec_candle[24300]={};			static CString usd_one_sec_candle[24300]={};
static float ktbf_std_ref[2430]={};					static float lktbf_std_ref[2430]={};					static float usd_std_ref[2430]={};

static float ktbf_ema_fast =0;							static float lktbf_ema_fast =0;							static float usd_ema_fast =0;
static float ktbf_ema_slow =0;							static float lktbf_ema_slow =0;							static float usd_ema_slow =0;

/*coeff*/
static CString account;
static CString ktb_code = "165S3000";	static CString lktb_code = "167S3000";	static CString usd_code = "175S2000";
//static float ktb_fast_coeff = 0.2;		static float lktb_fast_coeff = 0.2;		static float usd_fast_coeff = 0.2; 
//static float ktb_slow_coeff = 0.05;		static float lktb_slow_coeff = 0.05;	static float usd_slow_coeff = 0.05;

static float tick_conversion = 0; static int max_qty=0; static float tick_cross_margin=0; static float tick_diff_of_max_qty=0; static int max_trade_qty = 5;

const int NUM_HOGASISE = 1000000;
static struct HogaSise mHogaSises[NUM_HOGASISE];
static int numHogaSise = 0;

/*trade*/
static float ktbf_b1_for_a3;			static float lktbf_b1_for_a3;			static float usd_b1_for_a3;
static float ktbf_s1_for_a3;			static float lktbf_s1_for_a3;			static float usd_s1_for_a3;
static float ktbf_price_for_b6;			static float lktbf_price_for_b6;		static float usd_price_for_b6;
static CString ktb_pre_price;			static CString lktb_pre_price;			static CString usd_pre_price;
static CString ktbf_pre_qty;			static CString lktbf_pre_qty;			static CString usd_pre_qty;
static CString ktb_pre_orgordno ="";	static CString lktb_pre_orgordno="";	static CString usd_pre_orgordno="";
static CString ktbf_pre_mmgubun;		static CString lktbf_pre_mmgubun;		static CString usd_pre_mmgubun;
static CString ktbf_start_time;			static CString lktbf_start_time;		static CString usd_start_time;
static int ktbf_h;						static int lktbf_h;						static int usd_h;
static int ktbf_m;						static int lktbf_m;						static int usd_m;

/*candle*/
static int ktb_init_sec = 0;				static int lktbf_init_sec = 0;					static int usd_init_sec = 0;
static int ktbf_pre_sec = 0;				static int lktbf_pre_sec = 0;					static int usd_pre_sec = 0;
static candleSecond ktb_10sec_candle[2500];	static candleSecond lktbf_10sec_candle[2500];	static candleSecond usd_10sec_candle[2500];
//static candleSecond ktb_sec_candle[2500];	static candleSecond lktbf_sec_candle[2500];		static candleSecond usd_sec_candle[2500];
static int ktbf_10sec_index = 0;			static int lktbf_10sec_index = 0;				static int usd_10sec_index = 0;	
//static int ktbf_sec_index = 0;				static int lktbf_sec_index = 0;					static int usd_sec_index = 0;	
static int ktbf_candle_vol = 0;				static int lktbf_candle_vol = 0;				static int usd_candle_vol = 0;
static float ktbf_candle_price = 0;			static float lktbf_candle_price = 0;			static float usd_candle_price = 0;

/*vwap*/
const int NUM_VWAP = 20000;
static float ktb_vwap[NUM_VWAP];		static float lktb_vwap[NUM_VWAP];		static float usd_vwap[NUM_VWAP];
static int ktb_volume[NUM_VWAP];		static int lktb_volume[NUM_VWAP];		static int usd_volume[NUM_VWAP];
static float ktb_trade_price[2000];	static float lktb_trade_price[2000];	static float usd_trade_price[2000];

static int ktb_vol_bin = 200;	static int lktb_vol_bin = 50;	static int usd_vol_bin = 100;
static int ktb_vol_sum = 0;		static int lktb_vol_sum = 0;	static int usd_vol_sum = 0;
static float ktb_prc_sum = 0;	static float lktb_prc_sum = 0;	static float usd_prc_sum = 0;

static int ktb_vwap_num = 0;		static int lktb_vwap_num = 0;		static int usd_vwap_num = 0;
static int ktb_vwap_preindex = 0;	static int lktb_vwap_preindex = 0;	static int usd_vwap_preindex = 0;
static int ktb_trade_num = 0;		static int lktb_trade_num = 0;		static int usd_trade_num = 0;
static int ktb_trade_qty = 0;		static int lktb_trade_qty = 0;		static int usd_trade_qty = 0;
//static int ktb_actual_qty = 0;		static int lktb_actual_qty = 0;		static int usd_actual_qty = 0;
static int tmp = 0;

/*execution*/
static CString state="";
static CString boc_pre_state="";

static CString ktb_urgent_begintime;	static CString lktb_urgent_begintime;	static CString usd_urgent_begintime;
static CString ktb_urgent_endtime;		static CString lktb_urgent_endtime;		static CString usd_urgent_endtime;
static float ktb_urgent_beginprice;		static float lktb_urgent_beginprice;	static float usd_urgent_beginprice;
static float ktb_urgent_endprice;		static float lktb_urgent_endprice;		static float usd_urgent_endprice;

static float ktbf_pre_price_float;		static float lktbf_pre_price_float;		static float usd_pre_price_float;
static CString ktbf_pre_price_str;		static CString lktbf_pre_price_str;		static CString usd_pre_price_str;
static bool ktb_urgent_mode = false;	static bool lktb_urgent_mode = false;	static bool usd_urgent_mode = false;
static CString ktb_urgent_type;			static CString lktb_urgent_type;		static CString usd_urgent_type;

static CString ktbf_che_qty;			static CString lktbf_che_qty;			static CString usd_che_qty;
static CString ktbf_che_mmgubun;		static CString lktbf_che_mmgubun;		static CString usd_che_mmgubun;
/*af*/
//static bool ktb_is_pay_off;
//
//static float ktb_intra_lo = 99999;
//static float ktb_intra_hi = -99999;
//static CString ktb_trading_begins_after = "120000";
//static CString ktb_trading_begins_before = "150000";
//static float ktb_ema_fast_coeff = 0.2;
//static float ktb_ema_slow_coeff = 0.05;
//static float ktb_ema_margin = 0.5;
//static float ktb_lc_hi_lo =1.0;
//static float ktb_lc_pl = -25;
//static float ktb_pt_pl = 25;
//static float ktb_pt_draw_down = 0.3;
//static float ktb_thru = 0.5;
//
//static Trade ktb_uno = {};
//static Trade ktb_dos = {};

