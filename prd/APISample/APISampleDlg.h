
// APISampleDlg.h : 헤더 파일
//

#pragma once

#include "afxwin.h"
#include "orderpacket.h"
#include "structCollection.h"
#include "coeffs.h"

class ICommHelper;
class ISiseLinkHelper;

//export function type of Tops2API.lib
typedef BOOL				(*FP_INITAPI)(HWND);
typedef void				(*FP_EXITAPI)(void);
typedef ICommHelper*		(*FP_GETCOMMHELPER)(void);
typedef ISiseLinkHelper*	(*FP_GETSISEHELPER)(void);
typedef TCHAR*				(*FP_GETLOGINID)(void);
typedef void				(*FP_REGISTREALORDERS)(HWND);


#define WMU_RECEIVED_DATA				WM_USER + 5
#define WMU_RECEIVED_ORDER_ORDER		WM_USER + 6
#define WMU_RECEIVED_ORDER_ACK			WM_USER + 7
#define WMU_RECEIVED_ORDER_REJECT		WM_USER + 8
#define WMU_RECEIVED_ORDER_JUBSU		WM_USER + 9
#define WMU_RECEIVED_ORDER_CHEGYUL		WM_USER + 10
#define WMU_RECEIVED_ORDER_CONFIRM		WM_USER + 11

#define ORDER_PRICE_LEN				11
#define ORDER_QTY_LEN				10

#define PCIP							_T("PCIP")								// PC IP

struct REGIST_SISE_INFO
{
	REGIST_SISE_INFO()
	{
		memset(this, ' ', sizeof(REGIST_SISE_INFO));
	}
	TCHAR		szCode[12];											
	TCHAR		szPacketType[5];									// 시세 Header Type 길이
	int			nPacketTypeLen;
	HWND		hWnd;
	int			nPriority;
};

// CAPISampleDlg 대화 상자
class CAPISampleDlg : public CDialogEx
{
// 생성입니다.
public:
	CAPISampleDlg(CWnd* pParent = NULL);	// 표준 생성자입니다.

protected:
	void					InitControls();
	BOOL					InitLibrary();
	void					InitVariable();

	void					FillPacketHeader(TCHAR chTranType, LPCTSTR lpszExpCode, LPCTSTR lpszFundNo, CString pre_price);
	//BOOL					FillOrderPacket(TCHAR chTranType, LPCTSTR lpszAccount, LPCTSTR lpszExpCode, 
	//										int nQty, int nPrice, TCHAR chMaemae, TCHAR chOrdType, TCHAR chOrdCond, LPCTSTR lpszOrgOrdNo = NULL);
	BOOL					FillOrderPacket(TCHAR chTranType, LPCTSTR lpszAccount, LPCTSTR lpszExpCode, 
											int nQty, CString nPrice, TCHAR chMaemae, TCHAR chOrdType, TCHAR chOrdCond, LPCTSTR lpszOrgOrdNo = NULL);

	void					Request21001(const CString& strCode);
	void					Request21002(const CString& strCode);
	void					Request21003(const CString& strCode);
	void					Request90025(LPCTSTR lpszLoginID);
	void					RegistSise(const CString strType, const CString strItemCode);
	void					ReleaseSise(const CString strType, const CString strItemCode);
	void					ReleaseSiseAll();

	void					SendOrder(TCHAR chTranType);
	void					SetAccount(TCHAR* , TCHAR );
	void					RecvTr21001(TCHAR* , TCHAR );
	void					SetOrderControlStatus(BOOL bEnable);

	void					Order(TCHAR chTranType, int strQty, float floatPrice, float originPrice, CString strGubun, CString strItemCode, CString preOrgordno, CString jongmok);

// 대화 상자 데이터입니다.
	enum { IDD = IDD_APISAMPLE_DIALOG };
	
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 지원입니다.

	CListBox				m_ctrlTRList;
	CListBox				m_ctrlOrderList;
	CListBox				m_ctrlOrderList2;
	CListBox				m_ctrlSiseList;
	CEdit					m_editTrCode;
	CEdit					m_editSiseCode;
	CEdit					m_editOrderCode;
	CEdit					m_editOrderQty;
	CEdit					m_editOrderPrice;
	CComboBox				m_comboOrderGubun;
	CComboBox				m_comboOrderType;
	CComboBox				m_comboOrderOrd;
	CComboBox				m_comboOrderCond;
	CComboBox				m_comboOrderAccnt;
	CButton					m_chkSiseB6;
	CButton					m_chkSiseG7;
	CButton					m_chkSiseA3;
	CButton					m_chkSiseK200;

	CButton					m_chkStrategy_ktbfedr;
	CButton					m_chkStrategy_lktbfedr;
	CButton					m_chkStrategy_usdedr;
	CButton					m_chkStrategy_lktbfaf;

	CEdit					m_trd_qty;
	CEdit					m_max_qty;
	CEdit					m_start_time;

// 구현입니다.
protected:
	HINSTANCE				m_hAPILib;
	FP_INITAPI				m_fp_InitAPI;
	FP_EXITAPI				m_fp_ExitAPI;
	FP_GETCOMMHELPER		m_fp_GetCommHelper;
	FP_GETSISEHELPER		m_fp_GetSiseHelper;
	FP_GETLOGINID			m_fp_GetLoginID;
	FP_REGISTREALORDERS		m_fp_RegistRealOrders;

	int						m_nKey;
	ICommHelper*			m_pCommHelper;
	ISiseLinkHelper*		m_pSiseHelper;

	ORDER_PACKET			m_orderpacket;
	TCHAR					m_szTempPrice[ORDER_PRICE_LEN + 1];
	TCHAR					m_szTempQty[ORDER_QTY_LEN + 1];

	CString					m_strIP;
	TCHAR					m_szLoginID[128];
	CString					m_strRunPath;

	HICON m_hIcon;

	// 생성된 메시지 맵 함수
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	afx_msg LRESULT OnReceivedData(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT OnReceivedOrderData(WPARAM wParam, LPARAM lParam);
	afx_msg BOOL OnCopyData(CWnd* pWnd, COPYDATASTRUCT* pCopyDataStruct);
	afx_msg void OnBnClickedButtonInitApi();
	afx_msg void OnBnClickedButtonExitApi();
	afx_msg void OnBnClickedButtonCurrPrice();
	afx_msg void OnBnClickedButtonHoga();
	afx_msg void OnBnClickedButtonChegyulFlow();
	afx_msg void OnClose();
	afx_msg void OnBnClickedButtonClear();
	afx_msg void OnBnClickedButtonSiseRequest();
	afx_msg void OnBnClickedButtonSiseCancel();
	afx_msg void OnBnClickedButtonOrderOrder();
	afx_msg void OnBnClickedButtonSiseClear();
	afx_msg void OnBnClickedButtonOrderModify();
	afx_msg void OnBnClickedButtonOrderCancel();
	afx_msg void OnBnClickedButtonOrderClear();
	afx_msg void OnLbnSelchangeListOrderOut();
	afx_msg void OnLbnSelcancelListOrderOut();
	CButton m_btnModify;
	CButton m_btnCancel;
	CEdit m_editOrgOrdNo;
	afx_msg void OnCbnSelchangeComboOrderType();
	afx_msg void OnLbnSelchangeListTrOut();
	afx_msg void OnLbnSelchangeListSiseOut();

	afx_msg void OnBnClickedCheckStrategyEdrlktbf();
	afx_msg void OnBnClickedCheckStrategyAfusd();


	void setVwap(CString jongmok, struct HogaSise hs);
	void logSise(struct HogaSise hs);
	void CAPISampleDlg::execute_module(CString jongmok, HogaSise hs, int qty, bool new_order);
	int CAPISampleDlg::edrCalTargetQty(int max_qty, int abs_max_short_qty, float tick_diff_now, float tick_cross_margin, float tick_diff_of_max_qty, CString method);

	DayTraderBook ktbf_af_tr_book;
	DayTraderBook lktbf_af_tr_book;
	DayTraderBook usd_af_tr_book;

};





/*input values everyday*/
static CRITICAL_SECTION g_cs;

//static CFile all_udpFileWriter;
//static CFile ktb_siseFileWriter;
static CFile usd_logFileWriter;
static CFile ktb_udpFileWriter;		static CFile lktb_udpFileWriter;		static CFile usd_udpFileWriter;
static CFile ktb_vwapFileWriter;	static CFile lktb_vwapFileWriter;		static CFile usd_vwapFileWriter;
static CFile ktb_cheFileWriter;		static CFile lktb_cheFileWriter;		static CFile usd_cheFileWriter;
static CFile ktbf_af_FileWriter;	static CFile lktbf_af_FileWriter;		static CFile usd_af_FileWriter;
static CFile ktbf_edr_FileWriter;	static CFile lktbf_edr_FileWriter;		static CFile usd_edr_FileWriter;
static CFile errorFileWriter;

static CFile ktb_candleFileWriter;	static CFile lktb_candleFileWriter;

static CFile testFileOpen;






