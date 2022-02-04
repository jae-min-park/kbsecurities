
// APISampleDlg.cpp : 구현 파일
//

#include "stdafx.h"
#include "APISample.h"
#include "APISampleDlg.h"
#include "afxdialogex.h"

#include<math.h>
#include<Windows.h>
#include<stdio.h>
#include<stdlib.h>
#include "structCollection.h"
#include<iostream>
#include<string>
#include"DayTraderBook.h"

#include "../../include/TRHeader/TrStruct.h"

#include "../../Main/include/CommHelper.h"
#include "../../Main/include/SiseLinkHelper.h"

#define	ACCOUNT_NO_LEN				12				// 계좌번호

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// CAPISampleDlg 대화 상자
#define API_TITLE			_T("Trade Application")
//#define DEF_ITEM_CODE		_T("KTB LKTB USD")
//#define DEF_ITEM_CODE		_T("167RC000")
#define DEF_ITEM_CODE		_T("")
//#define DEF_EXP_ITEM_CODE	_T("KTB LKTB USD EXPCODE")
//#define DEF_EXP_ITEM_CODE	_T("KR4167RC0003")
#define DEF_EXP_ITEM_CODE	_T("")

using namespace std;


/*
 * 현재 시각을 받아오는 함수
 */
string getTime() {
	SYSTEMTIME lt;
	GetLocalTime(&lt);
	int hour = lt.wHour;
	int min = lt.wMinute;
	int sec = lt.wSecond;
	if (usd_init_sec != sec/10) {
		candleSecond candle;
		candle.hour = hour;
		candle.min = min;
		candle.sec = (sec/10)*10;
		candle.volume = usd_candle_vol;
		candle.price = usd_candle_price;

		usd_10sec_candle[usd_10sec_index++] = candle;

		usd_candle_vol = 0;
		usd_init_sec = sec/10;
	}
	char time[7];
	int len = sprintf(time, "%02d%02d%02d", hour,min,sec);
	string now(time);
	return now;	
}

CAPISampleDlg::CAPISampleDlg(CWnd* pParent /*=NULL*/)
	: CDialogEx(CAPISampleDlg::IDD, pParent)
{
	m_hIcon		= AfxGetApp()->LoadIcon(IDR_MAINFRAME);
	InitVariable();
}

void CAPISampleDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_LIST_TR,			m_ctrlTRList);
	DDX_Control(pDX, IDC_LIST_ORDER,		m_ctrlOrderList);
	DDX_Control(pDX, IDC_LIST_ORDER_OUT2,		m_ctrlOrderList2);
	DDX_Control(pDX, IDC_LIST_SISE,			m_ctrlSiseList);
	DDX_Control(pDX, IDC_EDIT_TR_CODE,		m_editTrCode);
	DDX_Control(pDX, IDC_EDIT_SISE_CODE,	m_editSiseCode);
	DDX_Control(pDX, IDC_EDIT_ORDER_CODE,	m_editOrderCode);
	DDX_Control(pDX, IDC_EDIT_ORDER_QTY,	m_editOrderQty);
	DDX_Control(pDX, IDC_EDIT_ORDER_PRICE,	m_editOrderPrice);
	DDX_Control(pDX, IDC_COMBO_ORDER_GUBUN,	m_comboOrderGubun);
	DDX_Control(pDX, IDC_COMBO_ORDER_TYPE,	m_comboOrderType);
	DDX_Control(pDX, IDC_COMBO_ORDER_COND,	m_comboOrderCond);
	DDX_Control(pDX, IDC_COMBO_ORDER_ACCNT,	m_comboOrderAccnt);
	DDX_Control(pDX, IDC_CHECK_SISE_B6,		m_chkSiseB6);
	DDX_Control(pDX, IDC_CHECK_SISE_G7,		m_chkSiseG7);
	DDX_Control(pDX, IDC_CHECK_SISE_A3,		m_chkSiseA3);
	DDX_Control(pDX, IDC_CHECK_SISE_K200,	m_chkSiseK200);

	DDX_Control(pDX, IDC_CHECK_STRATEGY_KTBFEDR,	m_chkStrategy_ktbfedr);
	DDX_Control(pDX, IDC_CHECK_STRATEGY_LKTBFAF,	m_chkStrategy_lktbfaf);
	DDX_Control(pDX, IDC_CHECK_STRATEGY_LKTBFEDR,	m_chkStrategy_lktbfedr);
	DDX_Control(pDX, IDC_CHECK_STRATEGY_USDEDR,		m_chkStrategy_usdedr);
	
	DDX_Control(pDX, IDC_EDIT_TRD_QTY,		m_trd_qty);
	DDX_Control(pDX, IDC_EDIT_MAX_QTY,		m_max_qty);
	DDX_Control(pDX, IDC_EDIT_START_TIME,		m_start_time);

	DDX_Control(pDX, IDC_BUTTON_ORDER_MODIFY, m_btnModify);
	DDX_Control(pDX, IDC_BUTTON_ORDER_CANCEL, m_btnCancel);
	DDX_Control(pDX, IDC_EDIT_ORDER_ORG_ORDNO, m_editOrgOrdNo);
}

BEGIN_MESSAGE_MAP(CAPISampleDlg, CDialogEx)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_MESSAGE(WMU_RECEIVED_DATA,				OnReceivedData)
	ON_MESSAGE(WMU_RECEIVED_ORDER_ACK,			OnReceivedOrderData)
	ON_MESSAGE(WMU_RECEIVED_ORDER_REJECT,		OnReceivedOrderData)
	ON_MESSAGE(WMU_RECEIVED_ORDER_CHEGYUL,		OnReceivedOrderData)
	ON_MESSAGE(WMU_RECEIVED_ORDER_CONFIRM,		OnReceivedOrderData)
	ON_WM_COPYDATA()
	ON_BN_CLICKED(IDC_BUTTON_INIT_API, &CAPISampleDlg::OnBnClickedButtonInitApi)
	ON_BN_CLICKED(IDC_BUTTON_EXIT_API, &CAPISampleDlg::OnBnClickedButtonExitApi)
	ON_BN_CLICKED(IDC_BUTTON_CURR_PRICE, &CAPISampleDlg::OnBnClickedButtonCurrPrice)
	ON_BN_CLICKED(IDC_BUTTON_HOGA, &CAPISampleDlg::OnBnClickedButtonHoga)
	ON_BN_CLICKED(IDC_BUTTON_CHEGYUL_FLOW, &CAPISampleDlg::OnBnClickedButtonChegyulFlow)
	ON_WM_CLOSE()
	ON_BN_CLICKED(IDC_BUTTON_CLEAR, &CAPISampleDlg::OnBnClickedButtonClear)
	ON_BN_CLICKED(IDC_BUTTON_SISE_REQUEST, &CAPISampleDlg::OnBnClickedButtonSiseRequest)
	ON_BN_CLICKED(IDC_BUTTON_SISE_CANCEL, &CAPISampleDlg::OnBnClickedButtonSiseCancel)
	ON_BN_CLICKED(IDC_BUTTON_ORDER_ORDER, &CAPISampleDlg::OnBnClickedButtonOrderOrder)
	ON_BN_CLICKED(IDC_BUTTON_SISE_CLEAR, &CAPISampleDlg::OnBnClickedButtonSiseClear)
	ON_BN_CLICKED(IDC_BUTTON_ORDER_MODIFY, &CAPISampleDlg::OnBnClickedButtonOrderModify)
	ON_BN_CLICKED(IDC_BUTTON_ORDER_CANCEL, &CAPISampleDlg::OnBnClickedButtonOrderCancel)
	ON_BN_CLICKED(IDC_BUTTON_ORDER_CLEAR, &CAPISampleDlg::OnBnClickedButtonOrderClear)
	ON_LBN_SELCHANGE(IDC_LIST_ORDER_OUT, &CAPISampleDlg::OnLbnSelchangeListOrderOut)
	ON_LBN_SELCANCEL(IDC_LIST_ORDER_OUT, &CAPISampleDlg::OnLbnSelcancelListOrderOut)
	ON_LBN_SELCHANGE(IDC_LIST_ORDER_OUT2, &CAPISampleDlg::OnLbnSelchangeListOrderOut)
	ON_LBN_SELCANCEL(IDC_LIST_ORDER_OUT2, &CAPISampleDlg::OnLbnSelcancelListOrderOut)
	ON_CBN_SELCHANGE(IDC_COMBO_ORDER_TYPE, &CAPISampleDlg::OnCbnSelchangeComboOrderType)
	ON_LBN_SELCHANGE(IDC_LIST_TR_OUT, &CAPISampleDlg::OnLbnSelchangeListTrOut)
	ON_LBN_SELCHANGE(IDC_LIST_SISE_OUT, &CAPISampleDlg::OnLbnSelchangeListSiseOut)


END_MESSAGE_MAP()


// CAPISampleDlg 메시지 처리기

BOOL CAPISampleDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 이 대화 상자의 아이콘을 설정합니다. 응용 프로그램의 주 창이 대화 상자가 아닐 경우에는
	//  프레임워크가 이 작업을 자동으로 수행합니다.
	SetIcon(m_hIcon, TRUE);			// 큰 아이콘을 설정합니다.
	SetIcon(m_hIcon, FALSE);		// 작은 아이콘을 설정합니다.

	// TODO: 여기에 추가 초기화 작업을 추가합니다.
	::InitializeCriticalSection(&g_cs);


	time_t timer;
	struct tm* t;
	timer = time(NULL);
	t = localtime(&timer);
	int year = t->tm_year+1900;
	int mon = t->tm_mon+1;
	int day = t->tm_mday;

		//test.txt
	CString strFile;
	//strFile.Format("logs/%d%d%d_all_udp.log",year,mon,day);
	//all_udpFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_lktb_udp.log",year,mon,day);
	//lktb_udpFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_ktb_udp.log",year,mon,day);
	//ktb_udpFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_usd_udp.log",year,mon,day);
	//usd_udpFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_ktb_vwap.log",year,mon,day);
	//ktb_vwapFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_lktb_vwap.log",year,mon,day);
	//lktb_vwapFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_usd_vwap.log",year,mon,day);
	//usd_vwapFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_error.log",year,mon,day);
	errorFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//strFile.Format("logs/%d%d%d_usd_log.log",year,mon,day);
	//usd_logFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_ktb_che.log",year,mon,day);
	ktb_cheFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_lktb_che.log",year,mon,day);
	lktb_cheFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_usd_che.log",year,mon,day);
	usd_cheFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_ktb_edr.log",year,mon,day);
	ktbf_edr_FileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_lktbf_af.log",year,mon,day);
	lktbf_af_FileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);
	
	strFile.Format("logs/%d%d%d_lktbf_edr.log",year,mon,day);
	lktbf_edr_FileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	strFile.Format("logs/%d%d%d_usd_edr.log",year,mon,day);
	usd_edr_FileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	//HogaSise ktb_hs = {};
	//HogaSise lktb_hs = {};
	//HogaSise usd_hs = {};

	
	ktbf_af_tr_book = DayTraderBook("KTBF");
	lktbf_af_tr_book = DayTraderBook("LKTBF");
	usd_af_tr_book = DayTraderBook("USD");

	
				// AF용 std_ref 파일 리드
	char* pFileName ="./data/std_ref_table.txt";
	//char* pFileName ="./data/std_ref_table_10sec.txt";

	char line[1024];
	char *pLine;
	FILE *fp = fopen(pFileName, "r");
	char * result;
	int num = 0;
	while(!feof(fp)) {
		pLine = fgets(line, 1024, fp);
		if(num >=2) {
			result = strtok(line, "\t");
			//lktbf_one_sec_candle[num-2] = result;
			lktbf_ten_sec_candle[num-2] = result;
			
			result = strtok(NULL, "\t");
			lktbf_std_ref[num-2] = stof(result);
		}
		num++;
	}
	fclose(fp);

	InitControls();
	m_trd_qty.SetWindowText(_T("1"));
	m_max_qty.SetWindowText(_T("10"));
	m_start_time.SetWindowText(_T("0900"));
	/**/
	//CString l;
	//for(int i = 0; i < num; i++) {
	//	l.Format("%s %f\n", lktbf_ten_sec_candle[i].Left(5), lktbf_std_ref[i]);
	//	m_ctrlOrderList2.InsertString(0, l);
	//}

	TCHAR szRunPath[MAX_PATH] = {0,};
	::GetModuleFileName(NULL, szRunPath, MAX_PATH);

	*_tcsrchr(szRunPath, '\\') = '\0';
	m_strRunPath.Format("%s\\", szRunPath);
	return TRUE;  // 포커스를 컨트롤에 설정하지 않으면 TRUE를 반환합니다.
}

// 대화 상자에 최소화 단추를 추가할 경우 아이콘을 그리려면
//  아래 코드가 필요합니다. 문서/뷰 모델을 사용하는 MFC 응용 프로그램의 경우에는
//  프레임워크에서 이 작업을 자동으로 수행합니다.

void CAPISampleDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 그리기를 위한 디바이스 컨텍스트입니다.

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 클라이언트 사각형에서 아이콘을 가운데에 맞춥니다.
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 아이콘을 그립니다.
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

// 사용자가 최소화된 창을 끄는 동안에 커서가 표시되도록 시스템에서
//  이 함수를 호출합니다.
HCURSOR CAPISampleDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

void CAPISampleDlg::InitVariable()
{
	m_hAPILib			= NULL;
	m_fp_InitAPI		= NULL;
	m_fp_ExitAPI		= NULL;
	m_fp_GetCommHelper	= NULL;
	m_fp_GetSiseHelper	= NULL;

	m_pCommHelper		= NULL;
	m_pSiseHelper		= NULL;			

	m_nKey				= -1;
	memset(m_szLoginID, 0, sizeof(m_szLoginID));

	if( m_comboOrderAccnt.GetSafeHwnd() )
	{
		for(int nSel = m_comboOrderAccnt.GetCount() - 1;nSel >= 0 ;--nSel)
		{
			TCHAR* pAccnt = (TCHAR*)m_comboOrderAccnt.GetItemData(nSel);
			if(pAccnt != NULL)
			{
				delete pAccnt;
				pAccnt = NULL;
				m_comboOrderAccnt.SetItemData(nSel, (DWORD_PTR)NULL);
			}			
		}
		m_comboOrderAccnt.ResetContent();

	}
}

BOOL CAPISampleDlg::InitLibrary()
{
	CString strDll;

	ASSERT(m_strRunPath);
	printf(m_strRunPath);
	strDll	=  m_strRunPath + _T("Tops2API.dll");

	m_hAPILib = ::LoadLibrary(strDll);
	if( m_hAPILib == NULL )
	{
		CString strMsg;
		strMsg.Format("Fail to load Tops2API.dll [%d]", GetLastError());
		MessageBox(strMsg, API_TITLE, MB_OK | MB_ICONWARNING);
		return FALSE;
	}

	//get lib function
	m_fp_InitAPI			= (FP_INITAPI)::GetProcAddress(m_hAPILib, _T("InitAPI"));
	m_fp_ExitAPI			= (FP_EXITAPI)::GetProcAddress(m_hAPILib, _T("ExitAPI"));
	m_fp_GetCommHelper		= (FP_GETCOMMHELPER)::GetProcAddress(m_hAPILib, _T("GetCommHelper"));
	m_fp_GetSiseHelper		= (FP_GETSISEHELPER)::GetProcAddress(m_hAPILib, _T("GetSiseHelper"));
	m_fp_GetLoginID			= (FP_GETLOGINID)::GetProcAddress(m_hAPILib, _T("GetLoginID"));
	m_fp_RegistRealOrders	= (FP_REGISTREALORDERS)::GetProcAddress(m_hAPILib, _T("RegistRealOrders"));

	if( m_fp_InitAPI			== NULL ||
		m_fp_ExitAPI			== NULL ||
		m_fp_GetCommHelper		== NULL ||
		m_fp_GetSiseHelper		== NULL ||
		m_fp_GetLoginID			== NULL ||
		m_fp_RegistRealOrders	== NULL )
	{
		MessageBox(_T("Fail to get dll function.\ndll file name : Tops2API.dll"), API_TITLE, MB_OK | MB_ICONWARNING);
		return FALSE;
	}



	return TRUE;
}

void CAPISampleDlg::InitControls()
{
	m_chkSiseA3.SetCheck(1);
	m_chkSiseB6.SetCheck(1);
	m_chkSiseG7.SetCheck(1);

	m_editTrCode.SetWindowText(DEF_ITEM_CODE);
	m_editSiseCode.SetWindowText(DEF_ITEM_CODE);
	m_editOrderCode.SetWindowText(DEF_EXP_ITEM_CODE);
	m_editOrderPrice.SetWindowText(_T("0.00"));
	m_comboOrderGubun.SetCurSel(0);
	m_comboOrderType.SetCurSel(1);
	m_comboOrderCond.SetCurSel(0);
	
	SetOrderControlStatus(TRUE);
}
/*************************************************************/
/** TR INPUT  요청	**/
/** TR PACKET											**/
/*************************************************************/
void CAPISampleDlg::Request21001(const CString& strCode)
{
	ASSERT(m_pCommHelper);
	IN_Q21001 inQ21001;
	memcpy(inQ21001.isu_cd, strCode, min(sizeof(inQ21001.isu_cd), strCode.GetLength()));
	inQ21001.mkt_cls[0] = 'B';  //3년국채 'B', 5년국채 'H',달러 'U'
	m_pCommHelper->RequestData(m_nKey, TR_Q21001, (TCHAR*)&inQ21001, sizeof(inQ21001));
}
///*************************************************************
///  svc2  Q21002(상품선옵 현재가)  Input/Output  정보         *
///             SINGLE PACKET                                  *
///************************************************************ 
void CAPISampleDlg::Request21002(const CString& strCode)
{
	ASSERT(m_pCommHelper);
	IN_Q21002 inQ21002;
	memcpy(inQ21002.isu_cd, strCode, min(sizeof(inQ21002.isu_cd), strCode.GetLength()));
	inQ21002.mkt_cls[0] = 'B';  //3년국채 'B', 5년국채 'H',달러 'U'
	m_pCommHelper->RequestData(m_nKey, TR_Q21002, (TCHAR*)&inQ21002, sizeof(inQ21002));
}
///*********************************************************
// Q21003  Input/Output 정보                                
// (상품선물 시간대별 체결내역)                            
// MULTI PACKET                                             
///*********************************************************
void CAPISampleDlg::Request21003(const CString& strCode)
{
// 	ASSERT(m_pCommHelper);
// 	IN_Q21003 inQ21003;
// 	memcpy(inQ21003.isu_cd, strCode, min(sizeof(inQ21003.isu_cd), strCode.GetLength()));
//	inQ21003.mkt_cls[0] = 'B';  //3년국채 'B', 5년국채 'H',달러 'U'
// 	m_pCommHelper->RequestData(m_nKey, TR_Q21003, (TCHAR*)&inQ21003, sizeof(inQ21003));
}

void CAPISampleDlg::Request90025(LPCTSTR lpszLoginID)
{
	ASSERT(m_pCommHelper);
	IN_Q90025 inQ90025;
	memcpy(inQ90025.login_id, lpszLoginID, min(sizeof(inQ90025.login_id), _tcslen(lpszLoginID)));
	m_pCommHelper->RequestData(m_nKey, TR_Q90025, (TCHAR*)&inQ90025, sizeof(inQ90025));
}

/*************************************************************/
/** TR OUTPUT  정보	**/
/** TR PACKET											**/
/*************************************************************/
LRESULT CAPISampleDlg::OnReceivedData(WPARAM wParam, LPARAM lParam)
{
	int			nLength	= (int)wParam;
	TCHAR*		p		= (TCHAR*)lParam;
	TR_HEAD*	ptrHead	= (TR_HEAD*)lParam;

	if( nLength <= 0 ) return 0L;

	if( ptrHead->trgb[0] == '9' )
	{	// ERROR
		CString strData(p, nLength);
		
		m_ctrlTRList.InsertString(0, strData);
		return 0L;
	}
// 	if(memcpy(ptrHead->trcode, TR_Q21001,sizeof(ptrHead->trcode)) == 0)
// 	{
// 		TRACE("현재가 TR OUTPUT 처리");
// 		RecvTr21001(p + sizeof(TR_HEAD), ptrHead->attr[0]);
// 	}
	if( memcmp(ptrHead->trcode, _T("Q90025"), sizeof(ptrHead->trcode)) == 0)
	{
		SetAccount(p + sizeof(TR_HEAD), ptrHead->attr[0]);

	}
	
	CString strData(p, nLength);
	m_ctrlTRList.InsertString(0, strData);

	return 0L;
}
void CAPISampleDlg::RecvTr21001(TCHAR* pData, TCHAR chAttr)
{
	switch(chAttr)
	{
	case '1':	//START
		break;
	case '2':	//Data
		break;
	case '3':	//End
		break;
	default:
		break;
	}
}
void CAPISampleDlg::SetAccount(TCHAR* pData, TCHAR chAttr)
{
	switch(chAttr)
	{
	case '1':	//START
		break;
	case '2':	//Data
		{
			OUT_Q90025*		pOut		= reinterpret_cast<OUT_Q90025*>(pData);
			OUT_Q90025_SUB*	pOutSub		= reinterpret_cast<OUT_Q90025_SUB*>(pData + sizeof(OUT_Q90025));
			OUT_Q90025_SUB*	pOutSub90025= pOutSub;

			TCHAR szCount[8] = {0,};
			memcpy(szCount, pOut->rcnt, sizeof(pOut->rcnt));
			int nCount = _ttoi(szCount);
			CString strTemp;
			for(int i = 1; i <= nCount; i++)
			{
				if(pOutSub90025->cmdtfo_yn[0] == '1')
				{
					CString strFundName(pOutSub90025->fund_nm, sizeof(pOutSub90025->fund_nm));
					CString strFundNo(pOutSub90025->fund_no, sizeof(pOutSub90025->fund_no));

					strTemp.Format("%s ( %s )",strFundNo,strFundName);
					int nSel = m_comboOrderAccnt.AddString(strTemp);
					TCHAR *pAccnt = new TCHAR[ACCOUNT_NO_LEN + 3];
					memcpy(pAccnt, pOutSub90025->accnt_no,ACCOUNT_NO_LEN);
					memcpy(pAccnt + sizeof(pOutSub90025->accnt_no),pOutSub90025->fund_ty,2);
					pAccnt[ACCOUNT_NO_LEN + 2] = NULL;
					m_comboOrderAccnt.SetItemData(nSel,(DWORD_PTR)pAccnt);

					// my code 
					account = strTemp;
				}
				

				pOutSub90025	= pOutSub + i;
			}
		}
		break;
	case '3':	//End
		break;
	default:
		break;
	}
}
/*************************************************************/
/** 주문실시간 데이터  정보	**/
/** PACKET											**/
/*************************************************************/
LRESULT CAPISampleDlg::OnReceivedOrderData(WPARAM wParam, LPARAM lParam)
{
	int		nLen	= (int)wParam;
	TCHAR*	pData	= (TCHAR*)lParam;
	CString strData(pData, nLen);

	CString log;
	string now = getTime();

	//m_ctrlOrderList2.InsertString(0, strData);
	 
	CString receivedType = strData.Left(5);
	CString receivedData = strData.Mid(60);

	if(strData.Left(5) == "DATAR") {
		log.Format("%c%c:%c%c:%c%c, datar Error :",now[0],now[1],now[2],now[3],now[4],now[5]);
		log = log + strData.Mid(30,4);
		log = log + "\n";
		m_ctrlOrderList.InsertString(0, log);
		if(usd_edr) {
			usd_edr_FileWriter.Write(log, strlen(log));
		} else if (ktbf_edr) {
			ktbf_edr_FileWriter.Write(log,strlen(log));
		}

		return 0L;
	}
	KRX_CH01 mReceivedCheData;
	KRX_HO01 mReceivedOrderData;


	if (receivedType == "DATAH") {
		memcpy(mReceivedOrderData.hseq,				receivedData.Left(11),		sizeof(mReceivedOrderData.hseq));	// 일련번호
		memcpy(mReceivedOrderData.trans_code,		receivedData.Mid(11,11),	sizeof(mReceivedOrderData.trans_code));	// 트랜잭션코드
		memcpy(mReceivedOrderData.me_grp_no,		receivedData.Mid(22,2),		sizeof(mReceivedOrderData.me_grp_no));	// 매칭 그룹별 일련번호
		memcpy(mReceivedOrderData.board_id,			receivedData.Mid(24,2),		sizeof(mReceivedOrderData.board_id));	// 보드 id
		memcpy(mReceivedOrderData.memberno,			receivedData.Mid(26,5),		sizeof(mReceivedOrderData.memberno));	// 회원번호
		memcpy(mReceivedOrderData.bpno,				receivedData.Mid(31,5),		sizeof(mReceivedOrderData.bpno));	// 지점번호
		memcpy(mReceivedOrderData.ordno,			receivedData.Mid(36,10),	sizeof(mReceivedOrderData.ordno));	// 주문번호
		memcpy(mReceivedOrderData.orgordno,			receivedData.Mid(46,10),	sizeof(mReceivedOrderData.orgordno));	// 원주문번호
		memcpy(mReceivedOrderData.code,				receivedData.Mid(56,12),	sizeof(mReceivedOrderData.code));	// 표준종목코드
		memcpy(mReceivedOrderData.mmgubun,			receivedData.Mid(68,1),		sizeof(mReceivedOrderData.mmgubun));	// 매도매수구분코드
		memcpy(mReceivedOrderData.hogagb,			receivedData.Mid(69,1),		sizeof(mReceivedOrderData.hogagb));	// 정정취소구분코드
		memcpy(mReceivedOrderData.gyejwa,			receivedData.Mid(70,12),	sizeof(mReceivedOrderData.gyejwa));	// 계좌번호
		memcpy(mReceivedOrderData.cnt,				receivedData.Mid(82,10),	sizeof(mReceivedOrderData.cnt));	// 호가수량
		memcpy(mReceivedOrderData.price,			receivedData.Mid(92,11),	sizeof(mReceivedOrderData.price));	// 호가가격
		memcpy(mReceivedOrderData.ord_type,			receivedData.Mid(103,1),	sizeof(mReceivedOrderData.ord_type));	// 호가유형코드
		memcpy(mReceivedOrderData.ord_cond,			receivedData.Mid(104,1),	sizeof(mReceivedOrderData.ord_cond));	// 호가조건코드
		memcpy(mReceivedOrderData.market_ord_num,	receivedData.Mid(105,11),	sizeof(mReceivedOrderData.market_ord_num));	// 시장조성자호가구분번호
		memcpy(mReceivedOrderData.stock_state_id,	receivedData.Mid(116,5),	sizeof(mReceivedOrderData.stock_state_id));	// 자사주신고서ID
		memcpy(mReceivedOrderData.stock_trade_code,	receivedData.Mid(121,1),	sizeof(mReceivedOrderData.stock_state_id));	// 자사주매매방법코드
		memcpy(mReceivedOrderData.medo_type_code,	receivedData.Mid(122,2),	sizeof(mReceivedOrderData.medo_type_code));	// 매도유형코드
		memcpy(mReceivedOrderData.singb,			receivedData.Mid(124,2),	sizeof(mReceivedOrderData.singb));	// 신용구분코드
		memcpy(mReceivedOrderData.witak,			receivedData.Mid(126,2),	sizeof(mReceivedOrderData.witak));	// 위탁자기구분코드
		memcpy(mReceivedOrderData.witakcomp_num,	receivedData.Mid(128,5),	sizeof(mReceivedOrderData.witakcomp_num));	// 위탁사번호
		memcpy(mReceivedOrderData.pt_type_code,		receivedData.Mid(133,2),	sizeof(mReceivedOrderData.pt_type_code));	// pt구분코드
		memcpy(mReceivedOrderData.sub_stock_gyejwa,	receivedData.Mid(135,12),	sizeof(mReceivedOrderData.sub_stock_gyejwa));	// 대용주권계좌번호
		memcpy(mReceivedOrderData.gyejwa_type_code,	receivedData.Mid(147,2),	sizeof(mReceivedOrderData.gyejwa_type_code));	// 계좌구분코드
		memcpy(mReceivedOrderData.gyejwa_margin_cod,receivedData.Mid(149,2),	sizeof(mReceivedOrderData.gyejwa_margin_cod));	// 계좌증거금유형코드
		memcpy(mReceivedOrderData.kukga,			receivedData.Mid(151,3),	sizeof(mReceivedOrderData.kukga));	// 국가코드
		memcpy(mReceivedOrderData.tocode,			receivedData.Mid(154,4),	sizeof(mReceivedOrderData.tocode));	// 투자자구분코드
		memcpy(mReceivedOrderData.foreign,			receivedData.Mid(158,2),	sizeof(mReceivedOrderData.foreign));	// 외국인투자자구분코드
		memcpy(mReceivedOrderData.meache_gb,		receivedData.Mid(160,1),	sizeof(mReceivedOrderData.meache_gb));	// 주문매체구분코드
		memcpy(mReceivedOrderData.term_no,			receivedData.Mid(161,12),	sizeof(mReceivedOrderData.term_no));	// 주문자식별번호
		memcpy(mReceivedOrderData.mac_addr,			receivedData.Mid(173,12),	sizeof(mReceivedOrderData.mac_addr));	// mac address
		memcpy(mReceivedOrderData.ord_date,			receivedData.Mid(185,8),	sizeof(mReceivedOrderData.ord_date));	// 호가일자
		memcpy(mReceivedOrderData.ord_time,			receivedData.Mid(193,9),	sizeof(mReceivedOrderData.ord_time));	// 회원사주문시각
		memcpy(mReceivedOrderData.hoiwon,			receivedData.Mid(202,60),	sizeof(mReceivedOrderData.hoiwon));	// 회원사용영역
		memcpy(mReceivedOrderData.acpt_time,		receivedData.Mid(262,9),	sizeof(mReceivedOrderData.acpt_time));	// 호가접수시각
		memcpy(mReceivedOrderData.jungcnt,			receivedData.Mid(271,10),	sizeof(mReceivedOrderData.jungcnt));	// 실정정취소호가수량
		memcpy(mReceivedOrderData.auto_canl_type,	receivedData.Mid(281,1),	sizeof(mReceivedOrderData.auto_canl_type));	// 자동처리구분코드
		memcpy(mReceivedOrderData.rejcode,			receivedData.Mid(282,4),	sizeof(mReceivedOrderData.rejcode));	// 호가거부사유코드
		memcpy(mReceivedOrderData.pgm_gongsi_gb,	receivedData.Mid(286,1),	sizeof(mReceivedOrderData.pgm_gongsi_gb));	// 프로그램호가 신고 구분코드


		if(receivedData.Mid(69,1) == "1") { // 신규
			if (receivedData.Mid(59,8) == ktb_code && ktbf_edr) {
				ktb_pre_price = receivedData.Mid(92,11);
				ktb_pre_orgordno = receivedData.Mid(36,10);
				ktbf_pre_qty = receivedData.Mid(82,10);
				ktbf_pre_mmgubun = receivedData.Mid(68,1);

				OrderItem item;
				item.orgordno = ktb_pre_orgordno;
				item.floatPrice = _tstof(ktb_pre_price);
				item.strItemCode = receivedData.Mid(56,12);
				item.strGubun = ktbf_pre_mmgubun;

				if (item.strGubun == "2") {
					item.intQty = _ttoi(receivedData.Mid(82,10));
				} else if (item.strGubun == "1") {
					item.intQty = -_ttoi(receivedData.Mid(82,10));
				}

				log.Format("[[qty : %d]]", item.intQty);
				m_ctrlOrderList.InsertString(0,log);

				item.jongmok = "KTBF";

				ktbf_edr_pendingList[ktbf_edr_pendingListIndex++] = item;

				if (ktbf_pre_mmgubun == "1") {
					ktbf_edr_pending_sum_qty -= _ttoi(receivedData.Mid(82,10));
				} else if ( usd_pre_mmgubun == "2" ) {
					ktbf_edr_pending_sum_qty += _ttoi(receivedData.Mid(82,10));
				}
				
				string now = getTime();
				CString log;
				log.Format("%c%c:%c%c:%c%c ☆DATAH NEW / pre_prc:%.3f, qty:%d, gubun:%s, orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(ktb_pre_price), _ttoi(ktbf_pre_qty), ktbf_pre_mmgubun, ktb_pre_orgordno);
				ktbf_edr_FileWriter.Write(log, strlen(log));
				m_ctrlOrderList2.InsertString(0,log);
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_af) {
				lktb_pre_price = receivedData.Mid(92,11);
				lktb_pre_orgordno = receivedData.Mid(36,10);
				lktbf_pre_qty = receivedData.Mid(82,10);
				lktbf_pre_mmgubun = receivedData.Mid(68,1);

				lktbf_enter_prc = _tstof(lktb_pre_price);
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_edr) {
				lktb_pre_price = receivedData.Mid(92,11);
				lktb_pre_orgordno = receivedData.Mid(36,10);
				lktbf_pre_qty = receivedData.Mid(82,10);
				lktbf_pre_mmgubun = receivedData.Mid(68,1);

				OrderItem item;
				item.orgordno = lktb_pre_orgordno;
				item.floatPrice = _tstof(lktb_pre_price);
				item.strItemCode = receivedData.Mid(56,12);
				item.strGubun = lktbf_pre_mmgubun;

				if (item.strGubun == "2") {
					item.intQty = _ttoi(receivedData.Mid(82,10));
				} else if (item.strGubun == "1") {
					item.intQty = -_ttoi(receivedData.Mid(82,10));
				}

				log.Format("[[qty : %d]]", item.intQty);
				m_ctrlOrderList.InsertString(0,log);

				item.jongmok = "LKTBF";

				lktbf_edr_pendingList[lktbf_edr_pendingListIndex++] = item;

				if (lktbf_pre_mmgubun == "1") {
					lktbf_edr_pending_sum_qty -= _ttoi(receivedData.Mid(82,10));
				} else if ( usd_pre_mmgubun == "2" ) {
					lktbf_edr_pending_sum_qty += _ttoi(receivedData.Mid(82,10));
				}
				
				string now = getTime();
				CString log;
				log.Format("%c%c:%c%c:%c%c ☆DATAH NEW / pre_prc:%.3f, qty:%d, gubun:%s, orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(lktb_pre_price), _ttoi(lktbf_pre_qty), lktbf_pre_mmgubun, lktb_pre_orgordno);
				lktbf_edr_FileWriter.Write(log, strlen(log));
				m_ctrlOrderList2.InsertString(0,log);
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_edr) {
				lktb_pre_price = receivedData.Mid(92,11);
				lktb_pre_orgordno = receivedData.Mid(36,10);
				lktbf_pre_qty = receivedData.Mid(82,10);
				lktbf_pre_mmgubun = receivedData.Mid(68,1);

				OrderItem item;
				item.orgordno = lktb_pre_orgordno;
				item.floatPrice = _tstof(lktb_pre_price);
				item.strItemCode = receivedData.Mid(56,12);
				item.strGubun = lktbf_pre_mmgubun;

				if (item.strGubun == "2") {
					item.intQty = _ttoi(receivedData.Mid(82,10));
				} else if (item.strGubun == "1") {
					item.intQty = -_ttoi(receivedData.Mid(82,10));
				}

				log.Format("[[qty : %d]]", item.intQty);
				m_ctrlOrderList.InsertString(0,log);

				item.jongmok = "LKTBF";

				lktbf_edr_pendingList[lktbf_edr_pendingListIndex++] = item;

				if (lktbf_pre_mmgubun == "1") {
					lktbf_edr_pending_sum_qty -= _ttoi(receivedData.Mid(82,10));
				} else if ( usd_pre_mmgubun == "2" ) {
					lktbf_edr_pending_sum_qty += _ttoi(receivedData.Mid(82,10));
				}
				
				string now = getTime();
				CString log;
				log.Format("%c%c:%c%c:%c%c ☆DATAH NEW / pre_prc:%.3f, qty:%d, gubun:%s, orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(lktb_pre_price), _ttoi(lktbf_pre_qty), lktbf_pre_mmgubun, lktb_pre_orgordno);
				lktbf_edr_FileWriter.Write(log, strlen(log));
				m_ctrlOrderList2.InsertString(0,log);
			} else if (receivedData.Mid(59,8) == usd_code && usd_edr) {
				usd_pre_price = receivedData.Mid(92,11);
				usd_pre_orgordno = receivedData.Mid(36,10);
				usd_pre_qty = receivedData.Mid(82,10);
				usd_pre_mmgubun = receivedData.Mid(68,1);
				
				OrderItem item;
				item.orgordno = usd_pre_orgordno;
				item.floatPrice = _tstof(usd_pre_price);
				item.strItemCode = receivedData.Mid(56,12);
				item.strGubun = usd_pre_mmgubun;

				if (item.strGubun == "2") {
					item.intQty = _ttoi(usd_pre_qty);
				} else if (item.strGubun == "1") {
					item.intQty = -_ttoi(usd_pre_qty);
				}

				log.Format("[[qty : %d]]", item.intQty);
				m_ctrlOrderList.InsertString(0,log);

				item.jongmok = "USD";

				usd_edr_pendingList[usd_edr_pendingListIndex++] = item;

				if (usd_pre_mmgubun == "1") {
					usd_edr_pending_sum_qty -= _ttoi(usd_pre_qty);
				} else if ( usd_pre_mmgubun == "2" ) {
					usd_edr_pending_sum_qty += _ttoi(usd_pre_qty);
				}
				
				string now = getTime();
				CString log;
				log.Format("%c%c:%c%c:%c%c ☆DATAH NEW / pre_prc:%.3f, qty:%d, gubun:%s, orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(usd_pre_price), _ttoi(usd_pre_qty), usd_pre_mmgubun, usd_pre_orgordno);
				usd_edr_FileWriter.Write(log, strlen(log));
				m_ctrlOrderList2.InsertString(0,log);
			}

		} else if(receivedData.Mid(69,1) == "2") { // 정정
			if (receivedData.Mid(59,8) == ktb_code && ktbf_edr) {
				if (receivedData.Mid(282,4) == "0000" ) {	// 에러코드 없이 성공했을때
					ktb_pre_price = receivedData.Mid(92,11);
					ktb_pre_orgordno = receivedData.Mid(36,10);
					ktbf_pre_qty = receivedData.Mid(82,10);
					ktbf_pre_mmgubun= receivedData.Mid(68,1);
					m_editOrgOrdNo.SetWindowText(receivedData.Mid(36,10)); // 주문번호 edittext에 세팅

					for(int i = 0; i < ktbf_edr_pendingListIndex; i++) {
						if (ktbf_edr_pendingList[i].orgordno == receivedData.Mid(46,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH modify i:%d/ pre_prc:%.3f, pre_qty:%d, gubun:%s, ordno:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],i, _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10), receivedData.Mid(46,10)) ;
							ktbf_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							
							OrderItem item;
							item.orgordno = ktb_pre_orgordno;
							item.floatPrice = _tstof(ktb_pre_price);
							item.strItemCode = receivedData.Mid(56,12);
							item.strGubun = ktbf_pre_mmgubun;

							item.intQty = ktbf_edr_pendingList[i].intQty;
							//if (item.strGubun == "2") {
							//	item.intQty = _ttoi(ktbf_pre_qty);
							//} else if (item.strGubun == "1") {
							//	item.intQty = -_ttoi(ktbf_pre_qty);
							//}

							log.Format("[[qty : %d]]", item.intQty);
							m_ctrlOrderList.InsertString(0,log);

							item.jongmok = "KTBF";		
							ktbf_edr_pendingList[i] = item;

							//for(int j=1; j < ktbf_edr_pendingListIndex-i; j++) {
							//	ktbf_edr_pendingList[i+j-1] = ktbf_edr_pendingList[i+j];
							//}
							break;
						}
					}

			
					//ktbf_edr_pendingList[ktbf_edr_pendingListIndex-1] = item;

	
					log.Format("%c%c:%c%c:%c%c ☆DATAH modify / pre_prc:%.3f, pre_qty:%d, gubun:%s, orgordno:%s, pre_orgno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(ktb_pre_price), _ttoi(ktbf_pre_qty), ktbf_pre_mmgubun, ktb_pre_orgordno, receivedData.Mid(46,10));
					ktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
				}
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_af) {
				if (receivedData.Mid(282,4) == "0000" ) {
					lktb_pre_price = receivedData.Mid(92,11);
					lktb_pre_orgordno = receivedData.Mid(36,10);
					lktbf_pre_qty = receivedData.Mid(82,10);
					lktbf_pre_mmgubun= receivedData.Mid(68,1);
					m_editOrgOrdNo.SetWindowText(receivedData.Mid(36,10)); // 주문번호 edittext에 세팅
				}
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_edr) {
				if (receivedData.Mid(282,4) == "0000" ) {
					lktb_pre_price = receivedData.Mid(92,11);
					lktb_pre_orgordno = receivedData.Mid(36,10);
					lktbf_pre_qty = receivedData.Mid(82,10);
					lktbf_pre_mmgubun= receivedData.Mid(68,1);
					m_editOrgOrdNo.SetWindowText(receivedData.Mid(36,10)); // 주문번호 edittext에 세팅


					for(int i = 0; i < lktbf_edr_pendingListIndex; i++) {
						if (lktbf_edr_pendingList[i].orgordno == receivedData.Mid(46,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH modify i%d/ pre_prc:%.3f, pre_qty:%d, gubun:%s, orgno:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],i, _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10), receivedData.Mid(46,10)) ;
							lktbf_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);

							OrderItem item;
							item.orgordno = lktb_pre_orgordno;
							item.floatPrice = _tstof(lktb_pre_price);
							item.strItemCode = receivedData.Mid(56,12);
							item.strGubun = lktbf_pre_mmgubun;

							item.intQty = lktbf_edr_pendingList[i].intQty;
							//if (item.strGubun == "2") {
							//	item.intQty = _ttoi(lktbf_pre_qty);
							//} else if (item.strGubun == "1") {
							//	item.intQty = -_ttoi(lktbf_pre_qty);
							//}

							log.Format("[[qty : %d]]", item.intQty);
							m_ctrlOrderList.InsertString(0,log);

							item.jongmok = "LKTBF";
							lktbf_edr_pendingList[i] = item;

							//for(int j=1; j < lktbf_edr_pendingListIndex-i; j++) {
							//	lktbf_edr_pendingList[i+j-1] = lktbf_edr_pendingList[i+j];
							//}
							break;
						}
					}


					//lktbf_edr_pendingList[lktbf_edr_pendingListIndex-1] = item;

	
					log.Format("%c%c:%c%c:%c%c ☆DATAH modify / pre_prc:%.3f, pre_qty:%d, gubun:%s, orgno:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(lktb_pre_price), _ttoi(lktbf_pre_qty), lktbf_pre_mmgubun, receivedData.Mid(36,10), lktb_pre_orgordno);
					lktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
				}

			} else if (receivedData.Mid(59,8) == usd_code && usd_edr) {
				if (receivedData.Mid(282,4) == "0000" ) {
					usd_pre_price = receivedData.Mid(92,11);
					usd_pre_price_float = _tstof(usd_pre_price);
					usd_pre_orgordno = receivedData.Mid(36,10);
					usd_pre_qty = receivedData.Mid(82,10);
					usd_pre_mmgubun = receivedData.Mid(68,1);
					m_editOrgOrdNo.SetWindowText(receivedData.Mid(36,10)); // 주문번호 edittext에 세팅

					for(int i = 0; i < usd_edr_pendingListIndex; i++) {
						if (usd_edr_pendingList[i].orgordno == receivedData.Mid(46,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH modify i:%d/ pre_prc:%.3f, pre_qty:%d, gubun:%s, orgno:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],i, _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10), receivedData.Mid(46,10)) ;
							usd_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							//for(int j=1; j < usd_edr_pendingListIndex-i; j++) {
							//	usd_edr_pendingList[i+j-1] = usd_edr_pendingList[i+j];
							//}
							OrderItem item;
							item.orgordno = usd_pre_orgordno;
							item.floatPrice = _tstof(usd_pre_price);
							item.strItemCode = receivedData.Mid(56,12);
							item.strGubun = usd_pre_mmgubun;

							item.intQty = usd_edr_pendingList[i].intQty;

							//if (item.strGubun == "2") {
							//	item.intQty = + _ttoi(usd_pre_qty);
							//} else if (item.strGubun == "1") {
							//	item.intQty = -_ttoi(usd_pre_qty);
							//}

							log.Format("[[qty : %d]]", item.intQty);
							m_ctrlOrderList.InsertString(0,log);

							item.jongmok = "USD";					
							usd_edr_pendingList[i] = item;
							break;
						}
					}
					//usd_edr_pendingList[usd_edr_pendingListIndex-1] = item;

	
					log.Format("%c%c:%c%c:%c%c ☆DATAH modify / pre_prc:%.3f, pre_qty:%d, gubun:%s, orgno:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(usd_pre_price), _ttoi(usd_pre_qty), usd_pre_mmgubun, receivedData.Mid(36,10), receivedData.Mid(46,10));
					usd_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);

				}
			}

		} else if (receivedData.Mid(69,1) == "3") { //취소
			m_ctrlOrderList.InsertString(0,receivedData.Mid(282,4));
			log.Format("%c%c:%c%c:%c%c ☆DATAH cancel / pre_prc:%.3f, pre_qty:%d, gubun:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10)) ;
			m_ctrlOrderList2.InsertString(0,log);
			if(ktbf_edr) {
				ktbf_edr_FileWriter.Write(log, strlen(log));
			} else if(lktbf_edr){
				lktbf_edr_FileWriter.Write(log, strlen(log));
			}else if(usd_edr) {
				usd_edr_FileWriter.Write(log, strlen(log));
			}

			if (receivedData.Mid(59,8) == ktb_code && ktbf_edr) {
				if (receivedData.Mid(282,4) == "0000" ) {
					ktbf_edr_FileWriter.Write(log, strlen(log));
					for(int i = 0; i < ktbf_edr_pendingListIndex; i++) {
						if (ktbf_edr_pendingList[ktbf_edr_pendingListIndex].orgordno == receivedData.Mid(36,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH cancel-eachitem / pre_prc:%.3f, pre_qty:%d, gubun:%c, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10)) ;
							ktbf_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							for(int j=1; j < ktbf_edr_pendingListIndex-i; j++) {
								ktbf_edr_pendingList[i+j-1] = ktbf_edr_pendingList[i+j];
							}
							break;
						}
					}
					OrderItem n = {};
					ktbf_edr_pendingList[ktbf_edr_pendingListIndex-1] = n;
					ktbf_edr_pendingListIndex--;
					for(int i = 0 ; i < ktbf_edr_pendingListIndex; i++) {
						log.Format("222 idx:%d, i:%d, prc:%f, qty:%d, gubun:%c, org:%s\n",ktbf_edr_pendingListIndex, i, ktbf_edr_pendingList[i].floatPrice, ktbf_edr_pendingList[i].intQty, ktbf_edr_pendingList[i].strGubun[0] ,ktbf_edr_pendingList[i].orgordno);
						m_ctrlOrderList.InsertString(0,log);
						ktbf_edr_FileWriter.Write(log,strlen(log));
					}
				}
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_af) {
				if (receivedData.Mid(282,4) == "0000" ) {
					lktbf_edr_FileWriter.Write(log, strlen(log));
					for(int i = 0; i < lktbf_edr_pendingListIndex; i++) {
						if (lktbf_edr_pendingList[lktbf_edr_pendingListIndex].orgordno == receivedData.Mid(36,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH cancel-eachitem / pre_prc:%.3f, pre_qty:%d, gubun:%c, pre_orgordno:%s",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10)) ;
							lktbf_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							for(int j=1; j < lktbf_edr_pendingListIndex-i; j++) {
								lktbf_edr_pendingList[i+j-1] = lktbf_edr_pendingList[i+j];
							}
							break;
						}
					}
					OrderItem n = {};
					lktbf_edr_pendingList[lktbf_edr_pendingListIndex-1] = n;
					lktbf_edr_pendingListIndex--;
					for(int i = 0 ; i < lktbf_edr_pendingListIndex; i++) {
						log.Format("222 idx:%d, i:%d, prc:%f, qty:%d, gubun:%c, org:%s\n",lktbf_edr_pendingListIndex, i, lktbf_edr_pendingList[i].floatPrice, lktbf_edr_pendingList[i].intQty, lktbf_edr_pendingList[i].strGubun[0] ,lktbf_edr_pendingList[i].orgordno);
						m_ctrlOrderList.InsertString(0,log);
						lktbf_edr_FileWriter.Write(log,strlen(log));
					}
				}
			} else if (receivedData.Mid(59,8) == lktb_code && lktbf_edr) {
				if (receivedData.Mid(282,4) == "0000" ) {
					lktbf_edr_FileWriter.Write(log, strlen(log));
					for(int i = 0; i < lktbf_edr_pendingListIndex; i++) {
						if (lktbf_edr_pendingList[lktbf_edr_pendingListIndex].orgordno == receivedData.Mid(36,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH cancel-eachitem / pre_prc:%.3f, pre_qty:%d, gubun:%c, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10)) ;
							lktbf_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							for(int j=1; j < lktbf_edr_pendingListIndex-i; j++) {
								lktbf_edr_pendingList[i+j-1] = lktbf_edr_pendingList[i+j];
							}
							break;
						}
					}
					OrderItem n = {};
					lktbf_edr_pendingList[lktbf_edr_pendingListIndex-1] = n;
					lktbf_edr_pendingListIndex--;
					for(int i = 0 ; i < lktbf_edr_pendingListIndex; i++) {
						log.Format("222 idx:%d, i:%d, prc:%f, qty:%d, gubun:%c, org:%s\n",lktbf_edr_pendingListIndex, i, lktbf_edr_pendingList[i].floatPrice, lktbf_edr_pendingList[i].intQty, lktbf_edr_pendingList[i].strGubun[0] ,lktbf_edr_pendingList[i].orgordno);
						m_ctrlOrderList.InsertString(0,log);
						lktbf_edr_FileWriter.Write(log,strlen(log));
					}
				}
			} else if (receivedData.Mid(59,8) == usd_code && usd_edr) {
				if (receivedData.Mid(282,4) == "0000" ) {
					usd_edr_FileWriter.Write(log, strlen(log));
					for(int i = 0; i < usd_edr_pendingListIndex; i++) {
						if (usd_edr_pendingList[usd_edr_pendingListIndex].orgordno == receivedData.Mid(36,10)) {
							log.Format("%c%c:%c%c:%c%c ☆DATAH cancel-eachitem / pre_prc:%.3f, pre_qty:%d, gubun:%c, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(receivedData.Mid(92,11)), _ttoi(receivedData.Mid(82,10)), receivedData.Mid(68,1), receivedData.Mid(36,10)) ;
							usd_edr_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							for(int j=1; j < usd_edr_pendingListIndex-i; j++) {
								usd_edr_pendingList[i+j-1] = usd_edr_pendingList[i+j];
							}
							break;
						}
					}
					OrderItem n = {};
					usd_edr_pendingList[usd_edr_pendingListIndex-1] = n;
					usd_edr_pendingListIndex--;
					for(int i = 0 ; i < usd_edr_pendingListIndex; i++) {
						log.Format("222 idx:%d, i:%d, prc:%f, qty:%d, gubun:%c, org:%s\n",usd_edr_pendingListIndex, i, usd_edr_pendingList[i].floatPrice, usd_edr_pendingList[i].intQty, usd_edr_pendingList[i].strGubun[0] ,usd_edr_pendingList[i].orgordno);
						m_ctrlOrderList.InsertString(0,log);
						usd_edr_FileWriter.Write(log,strlen(log));
					}
				}
			}
		}



	} else if (receivedType == "DATAC") {
		memcpy(mReceivedCheData.hseq,				receivedData.Left(11),		sizeof(mReceivedCheData.hseq));	// 일련번호
		memcpy(mReceivedCheData.trans_code,		receivedData.Mid(11,11),	sizeof(mReceivedCheData.trans_code));	// 트랜잭션코드
		memcpy(mReceivedCheData.me_grp_no,		receivedData.Mid(22,2),		sizeof(mReceivedCheData.hseq));	// 매칭 그룹별 일련번호
		memcpy(mReceivedCheData.board_id,			receivedData.Mid(24,2),		sizeof(mReceivedCheData.board_id));	// 매칭 그룹별 일련번호
		memcpy(mReceivedCheData.memberno,			receivedData.Mid(26,5),		sizeof(mReceivedCheData.memberno));	// 회원번호
		memcpy(mReceivedCheData.bpno,				receivedData.Mid(31,5),		sizeof(mReceivedCheData.bpno));	// 지점번호
		memcpy(mReceivedCheData.ordno,			receivedData.Mid(36,10),	sizeof(mReceivedCheData.ordno));	// 주문번호
		memcpy(mReceivedCheData.orgordno,			receivedData.Mid(46,10),	sizeof(mReceivedCheData.orgordno));	// 원주문번호
		memcpy(mReceivedCheData.code,				receivedData.Mid(56,12),	sizeof(mReceivedCheData.code));	// 표준종목코드
		memcpy(mReceivedCheData.che_no,			receivedData.Mid(68,11),	sizeof(mReceivedCheData.che_no));	//체결번호
		memcpy(mReceivedCheData.che_price,		receivedData.Mid(79,11),	sizeof(mReceivedCheData.che_price));	// 체결가격
		memcpy(mReceivedCheData.che_qty,			receivedData.Mid(90,10),	sizeof(mReceivedCheData.che_qty));	// 체결수량
		memcpy(mReceivedCheData.session_id,		receivedData.Mid(100,2),	sizeof(mReceivedCheData.session_id));	// 세션 ID
		memcpy(mReceivedCheData.che_date,			receivedData.Mid(102,8),	sizeof(mReceivedCheData.che_date));	// 체결일자
		memcpy(mReceivedCheData.che_time,			receivedData.Mid(110,9),	sizeof(mReceivedCheData.che_time));	// 체결시간
		memcpy(mReceivedCheData.pyakprice,		receivedData.Mid(119,11),	sizeof(mReceivedCheData.pyakprice));	// 근월물체결가격
		memcpy(mReceivedCheData.nyakprice,		receivedData.Mid(130,11),	sizeof(mReceivedCheData.nyakprice));	// 원월물체결가격
		memcpy(mReceivedCheData.mmgubun,			receivedData.Mid(141,1),	sizeof(mReceivedCheData.mmgubun));	// 매도매수구분코드
		memcpy(mReceivedCheData.gyejwa,			receivedData.Mid(142,12),	sizeof(mReceivedCheData.gyejwa));	// 계좌번호
		memcpy(mReceivedCheData.market_ord_num,	receivedData.Mid(154,11),	sizeof(mReceivedCheData.pyakprice));	// 시장조성자호가구분번호
		memcpy(mReceivedCheData.witakcomp_num,	receivedData.Mid(165,5),	sizeof(mReceivedCheData.witakcomp_num));	// 위탁사번호
		memcpy(mReceivedCheData.sub_stock_gyejwa,	receivedData.Mid(170,12),	sizeof(mReceivedCheData.sub_stock_gyejwa));	// 대용주권계좌번호
		memcpy(mReceivedCheData.hoiwon,			receivedData.Mid(182,60),	sizeof(mReceivedCheData.hoiwon));	// 회원사 사용영역

		CString code = receivedData.Mid(59,8);

		if (code==ktb_code && ktbf_edr) {
			m_ctrlOrderList2.InsertString(0,receivedData.Mid(36,10));
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			log.Format("★ktbf / DATE:%s TIME:%s GUBUN:%s ORDNO:%s ORGRDNO:%s CHE_PRICE:%f CHE_QTY:%d\n", receivedData.Mid(102,8), receivedData.Mid(110,9), receivedData.Mid(141,1), receivedData.Mid(36,10), receivedData.Mid(46,10), _tstof(receivedData.Mid(79,11)), _ttoi(receivedData.Mid(90,10)));
			ktbf_edr_FileWriter.Write(log,strlen(log));
			m_ctrlOrderList2.InsertString(0,log);
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			ktbf_che_qty = receivedData.Mid(90,10);
			log.Format("★ktbf ktbf_che_qty:%d, ktbf_edr_pendingListIndex:%d recorgno:%s\n", _ttoi(ktbf_che_qty), ktbf_edr_pendingListIndex, receivedData.Mid(36,10));
			ktbf_edr_FileWriter.Write(log,strlen(log));
			m_ctrlOrderList2.InsertString(0,log);
			ktbf_che_mmgubun= receivedData.Mid(141,1);
			ktbf_pre_qty = '0';
			ktb_pre_orgordno="";
			ktbf_pre_mmgubun = "";
			ktbf_pre_price_str="";
			ktbf_pre_price_float=0;
			ktbf_edr_signal = false;

			ktbf_edr_trade_prc_list[ktbf_edr_trade_num]=_tstof(receivedData.Mid(79,11));
			
			bool erased = false;
			for(int i = 0; i < ktbf_edr_pendingListIndex; i++) {
				if (ktbf_edr_pendingList[i].orgordno == receivedData.Mid(36,10)) {
					log.Format("%c%c:%c%c:%c%c i:%d, DATAC che / pre_prc:%.3f, pre_qty:%d / %s, gubun:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], i, _tstof(receivedData.Mid(79,11)), _ttoi(receivedData.Mid(90,10)),receivedData.Mid(90,10), receivedData.Mid(141,1), receivedData.Mid(36,10)) ;
					ktbf_edr_FileWriter.Write(log,strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					if (receivedData.Mid(141,1) == "1") {
						ktbf_edr_pendingList[i].intQty += _ttoi(receivedData.Mid(90,10));
					} else {
						ktbf_edr_pendingList[i].intQty -= _ttoi(receivedData.Mid(90,10));
					}
					log.Format("%c%c:%c%c:%c%c i:%d, DATAC che / ktbf_edr_pendingList.intQty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], i, ktbf_edr_pendingList[i].intQty) ;
					ktbf_edr_FileWriter.Write(log,strlen(log));
					if(ktbf_edr_pendingList[i].intQty == 0) {
						erased = true;
						for(int j=1; j < ktbf_edr_pendingListIndex-i; j++) {
							ktbf_edr_pendingList[i+j-1] = ktbf_edr_pendingList[i+j];
						}
						break;
					}
				}
			}
			if (erased) {
				OrderItem n = {};
				ktbf_edr_pendingList[ktbf_edr_pendingListIndex-1] = n;
				ktbf_edr_pendingListIndex--;
			}

			log.Format("%c%c:%c%c:%c%c DATAC che / ktbf_edr_pendingListIndex:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_pendingListIndex) ;
			ktbf_edr_FileWriter.Write(log,strlen(log));

			if(ktbf_che_mmgubun == '1') {
				ktbf_edr_pending_sum_qty += _ttoi(receivedData.Mid(90,10));

				ktbf_edr_actual_qty -=_ttoi(receivedData.Mid(90,10));
				ktbf_che_qty = "";
				ktbf_che_mmgubun = "";
				ktbf_edr_trade_qty_list[ktbf_edr_trade_num]=-_ttoi(receivedData.Mid(90,10));
			} else if(ktbf_che_mmgubun == '2'){
				ktbf_edr_pending_sum_qty -= _ttoi(receivedData.Mid(90,10));

				ktbf_edr_actual_qty +=_ttoi(receivedData.Mid(90,10));
				ktbf_che_qty = "";
				ktbf_che_mmgubun = "";
				ktbf_edr_trade_qty_list[ktbf_edr_trade_num]=_ttoi(receivedData.Mid(90,10));
			}
			ktbf_edr_trade_num++;


		} else if (code == lktb_code && lktbf_af) {

			m_ctrlOrderList2.InsertString(0,receivedData.Mid(36,10));
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			log.Format("★LKTBF / DATE:%s TIME:%s GUBUN:%s ORDNO:%s ORGRDNO:%s CHE_PRICE:%s CHE_QTY:%s\n", receivedData.Mid(102,8), receivedData.Mid(110,9), receivedData.Mid(141,1), receivedData.Mid(36,10), receivedData.Mid(46,10), receivedData.Mid(79,11), receivedData.Mid(90,10));
			m_ctrlOrderList2.InsertString(0,log);
			lktb_cheFileWriter.Write(log,strlen(log));
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			lktbf_che_qty = receivedData.Mid(90,10);
			lktbf_che_mmgubun= receivedData.Mid(141,1);
			lktbf_pre_qty = '0';
			lktb_pre_orgordno="";
			lktbf_pre_mmgubun = "";
			lktbf_pre_price_str="";
			lktbf_pre_price_float=0;
			lktbf_af_signal = false;
		} else if (code == lktb_code && lktbf_edr) {
			m_ctrlOrderList2.InsertString(0,receivedData.Mid(36,10));
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			log.Format("★LKTBF / DATE:%s TIME:%s GUBUN:%s ORDNO:%s ORGRDNO:%s CHE_PRICE:%s CHE_QTY:%d\n", receivedData.Mid(102,8), receivedData.Mid(110,9), receivedData.Mid(141,1), receivedData.Mid(36,10), receivedData.Mid(46,10), receivedData.Mid(79,11), _ttoi(receivedData.Mid(90,10)));
			lktb_cheFileWriter.Write(log,strlen(log));
			m_ctrlOrderList2.InsertString(0,log);
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			lktbf_che_qty = receivedData.Mid(90,10);
			lktbf_che_mmgubun= receivedData.Mid(141,1);
			lktbf_pre_qty = '0';
			lktb_pre_orgordno="";
			lktbf_pre_mmgubun = "";
			lktbf_pre_price_str="";
			lktbf_pre_price_float=0;
			lktbf_edr_signal = false;

			lktbf_edr_trade_prc_list[lktbf_edr_trade_num]=_tstof(receivedData.Mid(79,11));

			bool erased = false;
			for(int i = 0; i < lktbf_edr_pendingListIndex; i++) {
				if (lktbf_edr_pendingList[i].orgordno == receivedData.Mid(36,10)) {
					log.Format("%c%c:%c%c:%c%c DATAC che / pre_prc:%.3f, pre_qty:%d, gubun:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], _tstof(receivedData.Mid(79,11)), _ttoi(receivedData.Mid(90,10)), receivedData.Mid(141,1), receivedData.Mid(36,10)) ;
					lktbf_edr_FileWriter.Write(log,strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					if (receivedData.Mid(141,1) == "1") {
						lktbf_edr_pendingList[i].intQty += _ttoi(receivedData.Mid(90,10));
					} else {
						lktbf_edr_pendingList[i].intQty -= _ttoi(receivedData.Mid(90,10));
					}
					
					log.Format("%c%c:%c%c:%c%c i:%d, DATAC che / lktbf_edr_pendingList.intQty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], i, lktbf_edr_pendingList[i].intQty) ;
					lktbf_edr_FileWriter.Write(log,strlen(log));
					if(lktbf_edr_pendingList[i].intQty == 0) {
						erased = true;
						for(int j=1; j < lktbf_edr_pendingListIndex-i; j++) {
							lktbf_edr_pendingList[i+j-1] = lktbf_edr_pendingList[i+j];
						}
						break;
					}
				}
			}
			if (erased) {
				OrderItem n = {};
				lktbf_edr_pendingList[lktbf_edr_pendingListIndex-1] = n;
				lktbf_edr_pendingListIndex--;
			}
			if(lktbf_che_mmgubun == '1') {
				lktbf_edr_pending_sum_qty += _ttoi(lktbf_che_qty);

				lktbf_edr_actual_qty -=_ttoi(lktbf_che_qty);
				lktbf_che_qty = "";
				lktbf_che_mmgubun = "";
				lktbf_edr_trade_qty_list[lktbf_edr_trade_num]=-_ttoi(lktbf_che_qty);
			} else if(lktbf_che_mmgubun == '2'){
				lktbf_edr_pending_sum_qty -= _ttoi(lktbf_che_qty);

				lktbf_edr_actual_qty +=_ttoi(lktbf_che_qty);
				lktbf_che_qty = "";
				lktbf_che_mmgubun = "";
				lktbf_edr_trade_qty_list[lktbf_edr_trade_num]=_ttoi(lktbf_che_qty);
			}
			lktbf_edr_trade_num++;
		} else if (code == usd_code && usd_edr) {
			m_ctrlOrderList2.InsertString(0,receivedData.Mid(36,10));
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			log.Format("★USD / DATE:%s TIME:%s GUBUN:%s ORDNO:%s ORGRDNO:%s CHE_PRICE:%s CHE_QTY:%d\n", receivedData.Mid(102,8), receivedData.Mid(110,9), receivedData.Mid(141,1), receivedData.Mid(36,10), receivedData.Mid(46,10), receivedData.Mid(79,11), _ttoi(receivedData.Mid(90,10)));
			usd_edr_FileWriter.Write(log,strlen(log));
			m_ctrlOrderList2.InsertString(0,log);
			log.Format("★★★★★★★★★★");
			m_ctrlOrderList2.InsertString(0, log);
			usd_che_qty = receivedData.Mid(90,10);
			usd_che_mmgubun= receivedData.Mid(141,1);
			usd_pre_qty = '0';
			usd_pre_orgordno="";
			usd_pre_mmgubun = "";
			usd_pre_price_str="";
			usd_pre_price_float=0;
			usd_edr_signal = false;

			usd_edr_trade_prc_list[usd_edr_trade_num]=_tstof(receivedData.Mid(79,11));

			bool erased = false;
			for(int i = 0; i < usd_edr_pendingListIndex; i++) {
				if (usd_edr_pendingList[i].orgordno == receivedData.Mid(36,10)) {
					log.Format("%c%c:%c%c:%c%c 00 i:%d DATAC che / pre_prc:%.3f, pre_qty:%d, gubun:%s, pre_orgordno:%s\n",now[0],now[1],now[2],now[3],now[4],now[5], i, _tstof(receivedData.Mid(79,11)), _ttoi(receivedData.Mid(90,10)), receivedData.Mid(141,1), receivedData.Mid(36,10)) ;
					usd_edr_FileWriter.Write(log,strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					if (receivedData.Mid(141,1) == "1") {
						usd_edr_pendingList[i].intQty += _ttoi(receivedData.Mid(90,10));
						log.Format("%c%c:%c%c:%c%c 11 i:%d, DATAC che / usd_edr_pendingList.intQty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], i, usd_edr_pendingList[i].intQty) ;
						usd_edr_FileWriter.Write(log,strlen(log));
					} else if (receivedData.Mid(141,1) == "2"){
						usd_edr_pendingList[i].intQty -= _ttoi(receivedData.Mid(90,10));
						log.Format("%c%c:%c%c:%c%c 22 i:%d, DATAC che / usd_edr_pendingList.intQty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], i, usd_edr_pendingList[i].intQty) ;
						usd_edr_FileWriter.Write(log,strlen(log));
					}
					log.Format("%c%c:%c%c:%c%c 33 i:%d, DATAC che / usd_edr_pendingList.intQty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], i, usd_edr_pendingList[i].intQty) ;
					usd_edr_FileWriter.Write(log,strlen(log));
					if(usd_edr_pendingList[i].intQty == 0) {
						erased = true;
						for(int j=1; j < usd_edr_pendingListIndex-i; j++) {
							usd_edr_pendingList[i+j-1] = usd_edr_pendingList[i+j];
						}
						break;
					}
				}
			}
			if (erased) {
				OrderItem n = {};
				usd_edr_pendingList[usd_edr_pendingListIndex-1] = n;
				usd_edr_pendingListIndex--;
			}

			if(usd_che_mmgubun == '1') {
				usd_edr_pending_sum_qty += _ttoi(usd_che_qty);

				usd_edr_actual_qty -=_ttoi(usd_che_qty);
				usd_che_qty = "";
				usd_che_mmgubun = "";
				usd_edr_trade_qty_list[usd_edr_trade_num]=-_ttoi(usd_che_qty);
			} else if(usd_che_mmgubun == '2'){
				usd_edr_pending_sum_qty -= _ttoi(usd_che_qty);

				usd_edr_actual_qty +=_ttoi(usd_che_qty);
				usd_che_qty = "";
				usd_che_mmgubun = "";
				usd_edr_trade_qty_list[usd_edr_trade_num]=_ttoi(usd_che_qty);
			}
			usd_edr_trade_num++;

		}
		
	}		
	return 0L;
}



void CAPISampleDlg::RegistSise(const CString strType, const CString strItemCode)
{
	ASSERT( m_pSiseHelper );
	REGIST_SISE_INFO	info;

	memcpy(info.szCode,			strItemCode,	strItemCode.GetLength());
	memcpy(info.szPacketType,	strType,		min(strType.GetLength(), info.nPacketTypeLen));
	info.nPacketTypeLen	= strType.GetLength();
	info.hWnd			= m_hWnd;

	m_pSiseHelper->Regist((void*)&info);
}

void CAPISampleDlg::ReleaseSise(const CString strType, const CString strItemCode)
{
	ASSERT( m_pSiseHelper );
	REGIST_SISE_INFO	info;

	memcpy(info.szCode,			strItemCode,	strItemCode.GetLength());
	memcpy(info.szPacketType,	strType,		min(sizeof(info.szPacketType), info.nPacketTypeLen));
	info.nPacketTypeLen	= strType.GetLength();
	info.hWnd			= m_hWnd;

	m_pSiseHelper->Release((void*)&info);
}

void CAPISampleDlg::ReleaseSiseAll()
{
	ASSERT( m_pSiseHelper );
	REGIST_SISE_INFO	info;

	info.hWnd			= m_hWnd;

	m_pSiseHelper->ReleaseAll((void*)&info);
}

bool isSamePrice(float a, float b) {
	int a_1000 = a * 1000;
	int b_1000 = b * 1000;

	if(a_1000 % 10 == 9) {
		a_1000 +=1;
	}
	if(b_1000 % 10 == 9) {
		b_1000 +=1;
	}

	return a_1000 == b_1000;
}

float getStd(candleSecond* data, int len) {
	int sum = 0;
	for(int i = 0; i < len; i++) {
		sum+=data[i].price;
	}
	float avg = sum/len;
	for(int i = 0; i < len; i++) {
		sum+=(data[i].price-avg)*(data[i].price-avg);
	}
	float var = sum/(float)(len-1);
	return sqrt(var);
}

int CAPISampleDlg::edrCalTargetQty(int max_qty, int abs_max_short_qty, float tick_diff_now, float tick_cross_margin, float tick_diff_of_max_qty, CString method){
	int target_qty = 0;
	
	CString log;
	string now = getTime();
	if ( ((tick_diff_now>0)?tick_diff_now:-tick_diff_now) <= tick_cross_margin ) {
		//z.Format("%c%c:%c%c:%c%c,11 edrCalTargetQty, tick_cross_margin:%.3f, tick_diff_now:%.3f", now[0],now[1],now[2],now[3],now[4],now[5], tick_cross_margin,tick_diff_now);
		//m_ctrlOrderList.InsertString(0,log);
		target_qty = 0;
	/*롱 시그널*/
	} else if (tick_diff_now > tick_cross_margin ) {
		//z.Format("%c%c:%c%c:%c%c, ☆22 long edrCalTargetQty", now[0],now[1],now[2],now[3],now[4],now[5]);
		//m_ctrlOrderList.InsertString(0,z);

		if (method == "linear") {
			float target_qty_raw = max_qty * tick_diff_now / tick_diff_of_max_qty;
			target_qty = (target_qty_raw < max_qty)? target_qty_raw : max_qty;
		} else if (method == "power") {
			float target_qty_raw = max_qty * (tick_diff_now / tick_diff_of_max_qty)*(tick_diff_now / tick_diff_of_max_qty);
			target_qty = (target_qty_raw < max_qty)? target_qty_raw : max_qty;
		} else {
			throw ERROR("wrong method long");
			errorFileWriter.Write("wrong method long",strlen("wrong method long"));
		}
	/*숏 시그널*/
	} else if (tick_diff_now < -tick_cross_margin) {
		//z.Format("%c%c:%c%c:%c%c, ☆33 short edrCalTargetQty", now[0],now[1],now[2],now[3],now[4],now[5]);
		//m_ctrlOrderList.InsertString(0,z);

		if (method == "linear") {
			float target_qty_raw = abs_max_short_qty * tick_diff_now / tick_diff_of_max_qty;
			target_qty = (-target_qty_raw < abs_max_short_qty)? target_qty_raw : -abs_max_short_qty;
		} else if (method == "power") {
			float target_qty_raw = -abs_max_short_qty * (tick_diff_now / tick_diff_of_max_qty)*(tick_diff_now / tick_diff_of_max_qty);
			target_qty = (-target_qty_raw < abs_max_short_qty)? target_qty_raw : -abs_max_short_qty;
		} else {
			throw ERROR("wrong method short");
			errorFileWriter.Write("wrong method short",strlen("wrong method short"));
		}
	} else {
		throw ERROR("Unexpected tick_diff_now status");
		errorFileWriter.Write("Unexpected tick_diff_now status",strlen("Unexpected tick_diff_now status"));
	}

	return target_qty;
}
/**
 *  ema_fast와 ema_slow 를 비교하여 attached / above / below 중에 하나를 리턴
 */
string crossTest(float ema_fast, float ema_slow, float margin) {
	string cross_status;
	if (100*abs(ema_fast - ema_slow) <= margin) {
		cross_status = "attached";
	} else if (ema_fast > ema_slow) {
		cross_status = "above";
	} else if (ema_fast < ema_slow) {
		cross_status ="below";
	} else {
		throw ERROR("Unexpected. check margine value!");
		errorFileWriter.Write("Unexpected. check margine value!",strlen("Unexpected. check margine value!"));
	}
	return cross_status;
}


/*************************************************************/
/** 실시간 시세 정보	**/
/** PACKET											**/
/*************************************************************/
bool traded = false;
BOOL CAPISampleDlg::OnCopyData(CWnd* pWnd, COPYDATASTRUCT* pCopyDataStruct)
{	
	try {
		if(pCopyDataStruct->dwData == 8282)
		{
			::EnterCriticalSection(&g_cs);	

			// cbData로 넘어오는 데이타의 마지막이 0x00으로 온다
			CString strSiseData((TCHAR*)pCopyDataStruct->lpData, (INT)pCopyDataStruct->cbData);
			CString log;

			string siseData = strSiseData;
			string code = siseData.substr(8,8);
			m_ctrlSiseList.InsertString(0, strSiseData);

			/* 전체 udp를 받아 파일에 저장하는 코드 주석처리 */
			//CString udp = strSiseData+'\n';
			//all_udpFileWriter.Write(udp, strlen(udp));
			if (code.compare(ktb_code) == 0) {

				string dataType = siseData.substr(0,2);
				HogaSise hs = {};

				if (dataType.compare("A3") == 0) {
					hs.type = "A3";
					hs.code = siseData.substr(5,12).c_str();
					hs.price = stof(siseData.substr(23,8))/100;
					ktbf_price_for_b6 = hs.price;
					if (hs.price != 0) 
						ktbf_last_prc = hs.price;

					hs.c_price = stoi(siseData.substr(23,8));

					ktbf_candle_price = hs.price;

					hs.volume = stoi(siseData.substr(31,6));
					ktbf_candle_vol += hs.volume;
					hs.time = siseData.substr(39,8).c_str();

					hs.pre_price = stof(siseData.substr(91,8))/100;
					hs.sell_or_buy = siseData.substr(135,1).c_str();

					hs.buy_hoga1_price = ktbf_b1_for_a3;
					hs.sell_hoga1_price = ktbf_s1_for_a3;
					/* vwap 계산 || 시세 파일에 기록*/
					if(ktbf_edr) 
						setVwap("KTBF", hs);
					//logSise(hs);
			
				} else if (dataType.compare("B6") == 0){
					hs.type = "B6";
					hs.code = siseData.substr(5,12).c_str();

					hs.price = ktbf_price_for_b6;

					hs.buy_hoga1_price = stof(siseData.substr(32,8))/100;
					hs.buy_hoga1_balance = stoi(siseData.substr(40,6));
					ktbf_b1_for_a3 = hs.buy_hoga1_price;

					hs.buy_hoga2_price = stof(siseData.substr(47,8))/100;
					hs.buy_hoga2_balance = stoi(siseData.substr(55,6));

					hs.sell_hoga1_price = stof(siseData.substr(114,8))/100;
					hs.sell_hoga1_balance = stoi(siseData.substr(122,6));
					ktbf_s1_for_a3 = hs.sell_hoga1_price;
			
					hs.sell_hoga2_price = stof(siseData.substr(129,8))/100;
					hs.sell_hoga2_balance = stoi(siseData.substr(137,6));

					hs.buy_hoga1_count = stoi(siseData.substr(193,4));
					hs.buy_hoga2_count = stoi(siseData.substr(197,4));
					hs.sell_hoga1_count = stoi(siseData.substr(218,4));
					hs.sell_hoga2_count = stoi(siseData.substr(222,4));

					hs.time = siseData.substr(238,8).c_str();
					
					/* 시세 파일에 기록 */
					//logSise(hs);

				} else if (dataType.compare("G7") == 0){
					hs.type = "G7";
					hs.code = siseData.substr(5,12).c_str();
					hs.price = stof(siseData.substr(23,8))/100;
					ktbf_price_for_b6 = hs.price;
					if (hs.price != 0) 
						ktbf_last_prc = hs.price;

					hs.c_price = stoi(siseData.substr(23,8));

					ktbf_candle_price = hs.price;
					hs.volume = stoi(siseData.substr(31,6));
					ktbf_candle_vol += hs.volume;
					hs.time = siseData.substr(39,8).c_str();

					hs.pre_price = stof(siseData.substr(91,8))/100;
					hs.sell_or_buy = siseData.substr(135,1).c_str();

					hs.buy_hoga1_price = stof(siseData.substr(144,8))/100;
					hs.buy_hoga1_balance = stoi(siseData.substr(152,6));
					ktbf_b1_for_a3 = hs.buy_hoga1_price;

					hs.buy_hoga2_price = stof(siseData.substr(159,8))/100;
					hs.buy_hoga2_balance = stoi(siseData.substr(167,6));

					hs.sell_hoga1_price = stof(siseData.substr(226,8))/100;
					hs.sell_hoga1_balance = stoi(siseData.substr(234,6));
					ktbf_s1_for_a3 = hs.sell_hoga1_price;

					hs.sell_hoga2_price = stof(siseData.substr(241,8))/100;
					hs.sell_hoga2_balance = stoi(siseData.substr(249,6));

					hs.buy_hoga1_count = 0;
					hs.buy_hoga2_count = 0;
					hs.sell_hoga1_count = 0;
					hs.sell_hoga2_count = 0;
					hs.buy_hoga1_count = stoi(siseData.substr(305,4));
					hs.buy_hoga2_count = stoi(siseData.substr(309,4));
					hs.sell_hoga1_count = stoi(siseData.substr(330,4));
					hs.sell_hoga2_count = stoi(siseData.substr(334,4));

					/* vwap 계산 || 시세 파일에 기록 */
					if(ktbf_edr) 
						setVwap("KTBF",hs);
					//logSise(hs);

				} else {
				}
				///*ktbf 10초봉*/
				SYSTEMTIME lt;
				GetLocalTime(&lt);
				int hour = lt.wHour;
				int min = lt.wMinute;
				int sec = lt.wSecond;
				if (ktb_init_sec != sec/10) {
					candleSecond candle;
					candle.hour = hour;
					candle.min = min;
					candle.sec = (sec/10)*10;
					candle.volume = ktbf_candle_vol;
					candle.price = ktbf_candle_price;

					ktb_10sec_candle[ktbf_10sec_index++] = candle;

					ktbf_candle_vol = 0;
					ktb_init_sec = sec/10;
				}
				char time[7];
				int len = sprintf(time, "%02d%02d%02d", hour,min,sec);
				string now(time);

				if(ktbf_edr) {
					if (ktbf_edr_ema_fast == 0 && hour==ktbf_h, min == ktbf_m) {ktbf_edr_ema_fast = ktbf_candle_price;}
					if (ktbf_edr_ema_slow == 0 && hour==ktbf_h, min == ktbf_m) {ktbf_edr_ema_slow = ktbf_candle_price;}

					if (ktbf_edr_ema_fast == 0 && ktbf_edr_ema_slow == 0) {
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
					}
					/*vol봉이 올라왔을때 동작하도록*/
					if (ktb_vwap_preindex != ktb_vwap_num) {
						if(hs.price != 0) {
							ktbf_edr_ema_fast = ktbf_edr_fast_coeff * hs.price + (1 - ktbf_edr_fast_coeff) * ktbf_edr_ema_fast;
							ktbf_edr_ema_slow = ktbf_edr_slow_coeff * hs.price + (1 - ktbf_edr_slow_coeff) * ktbf_edr_ema_slow;
						}
						
						int qty = 0;
						for(int i =0; i < ktbf_edr_trade_num; i++) {
							qty += ktbf_edr_trade_qty_list[i];
							log.Format("%c%c:%c%c:%c%c, i:%d , ith qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],i,ktbf_edr_trade_qty_list[i]);
						}
						log.Format("%c%c:%c%c:%c%c, ktbf_edr_trade_num:%d, qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_trade_num,qty);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						//log.Format("%c%c:%c%c:%c%c, NEW ktbf vol prc:%.3f, ema_fast:%.3f, ema_slow_:%.3f",now[0],now[1],now[2],now[3],now[4],now[5],hs.price, ktbf_edr_ema_fast,ktbf_edr_ema_slow);

						m_ctrlOrderList.InsertString(0,log);

						ktb_vwap_preindex = ktb_vwap_num;

						//ktbf_edr_actual_qty = ktbf_edr_trade_qty + ktbf_edr_actual_qty;
						ktbf_edr_trade_qty = 0;

						float diff_now = ktbf_edr_ema_fast - ktbf_edr_ema_slow;
						float tick_diff_now = ktbf_tick_conversion * diff_now;
						float abs_tick_diff_now = (tick_diff_now>0)?tick_diff_now:-tick_diff_now;

						if (abs_tick_diff_now > ktbf_tick_diff_of_max_qty) {
							ktbf_tick_diff_of_max_qty = abs_tick_diff_now;
						}
						
						ktbf_edr_target_qty = edrCalTargetQty(ktbf_edr_max_qty, ktbf_abs_max_short_qty, tick_diff_now, ktbf_edr_tick_cross_margin, ktbf_tick_diff_of_max_qty, "linear");

						if (ktbf_edr_target_qty != ktbf_edr_pre_target_qty) {
							ktbf_edr_changed_qty = true;
						}
						ktbf_edr_pre_target_qty = ktbf_edr_target_qty;
					//}
					int pending_qty = 0;
					for (int i = 0 ; i < ktbf_edr_pendingListIndex; i++) {
						pending_qty += ktbf_edr_pendingList[i].intQty;
					}

					int trade_qty_raw = (int)(ktbf_edr_target_qty - ktbf_edr_actual_qty - pending_qty);
					log.Format("%c%c:%c%c:%c%c, ktbf_edr_trade_num:%d, trade_qty_raw:%d, ktbf_edr_target_qty:%d, ktbf_edr_actual_qty:%d,pending_qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_trade_num, trade_qty_raw, ktbf_edr_target_qty, ktbf_edr_actual_qty, pending_qty);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);

					if (trade_qty_raw != ktbf_edr_pre_trade_qty_raw) {
						ktbf_edr_changed_qty = true;
					}
					ktbf_edr_pre_trade_qty_raw = trade_qty_raw;

					if (trade_qty_raw >=0) {
						ktbf_edr_trade_qty = (ktbf_edr_max_trade_qty < trade_qty_raw)? ktbf_edr_max_trade_qty : trade_qty_raw;
					} else {
						ktbf_edr_trade_qty = (ktbf_edr_max_trade_qty < -trade_qty_raw)? -ktbf_edr_max_trade_qty : trade_qty_raw;
					}
					if (ktbf_edr_trade_qty != ktbf_edr_pre_trade_qty) {
						ktbf_edr_changed_qty = true;
					}
					ktbf_edr_pre_trade_qty = ktbf_edr_trade_qty;

					if (ktbf_edr_changed_qty) {
						log.Format("%c%c:%c%c:%c%c, target_qty:%d, trade_qty_raw:%d, ktbf_edr_trade_qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_target_qty,trade_qty_raw,ktbf_edr_trade_qty);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						m_ctrlOrderList.InsertString(0,log);
					}
					ktbf_edr_changed_qty = false;

					/*9시 0분전에는 아무 매매도 하지말자*/
					if (ktbf_trading_time_start != "") {
						if (now.compare(ktbf_trading_time_start) < 0) {
							ktbf_edr_trade_qty = 0;
							return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
						}
					}

					/*1계약으로 수정하기 위한 로직*/
					//if (ktbf_edr_trade_qty > 0) {
					//	ktbf_edr_trade_qty = ktbf_edr_trade_qty/ktbf_edr_trade_qty;
					//} else if(ktbf_edr_trade_qty<0) {
					//	ktbf_edr_trade_qty = -ktbf_edr_trade_qty/ktbf_edr_trade_qty;
					//}

					/*pl 계산*/
					int sum_pl=0;
					int sum_commission=0;
					for(int i = 0; i < ktbf_edr_trade_num; i++) {
						sum_pl += ktbf_edr_trade_qty_list[i]*(ktbf_last_prc - ktbf_edr_trade_prc_list[i]);
						sum_commission += (ktbf_krw_commission_per_contract * (ktbf_edr_trade_qty_list[i]>0)?ktbf_edr_trade_qty_list[i]:-ktbf_edr_trade_qty_list[i]);
					}
					int net_pl = ktbf_krw_value_1pt*sum_pl - sum_commission;

					log.Format("%c%c:%c%c:%c%c,fast_coeff:%.3f, slow_coeff:.3%f, price:%.3f\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_fast_coeff, ktbf_edr_slow_coeff, hs.price);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					//log.Format("%c%c:%c%c:%c%c, net_pl:%d, ktbf_edr_losscut:%d, now-ends :%d", now[0],now[1],now[2],now[3],now[4],now[5], net_pl, ktbf_edr_losscut, now.compare(trading_hour_ends));
					log.Format("%c%c:%c%c:%c%c, net_pl:%d, ktbf_edr_losscut:%d, now-ends :%d\n", now[0],now[1],now[2],now[3],now[4],now[5], net_pl, ktbf_edr_losscut, now.compare(trading_hour_ends));
					ktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					log.Format("%c%c:%c%c:%c%c, ktbf trdqty:%d, targetqty:%d, act_qty:%d, ema_fast:%.3f, ema_slow:%.3f\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_trade_qty, ktbf_edr_target_qty, ktbf_edr_actual_qty, ktbf_edr_ema_fast, ktbf_edr_ema_slow);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0, log);
						
					/*손절*/
					if (net_pl < ktbf_edr_losscut) {
						for(int i = 0; i < ktbf_edr_trade_num; i++) {
							log.Format("%c%c:%c%c:%c%c, i:%d, qty:%d, prc:%.3f,comm:%d ",now[0],now[1],now[2],now[3],now[4],now[5],i, ktbf_edr_trade_qty_list[i],ktbf_edr_trade_prc_list[i], (ktbf_krw_commission_per_contract * (ktbf_edr_trade_qty_list[i]>0)?ktbf_edr_trade_qty_list[i]:-ktbf_edr_trade_qty_list[i]));
							m_ctrlOrderList2.InsertString(0, log);
							ktbf_edr_FileWriter.Write(log, strlen(log));
						}
						ktbf_edr_signal = true;
						int qty = 0;
						for(int i =0; i < ktbf_edr_trade_num; i++) {
							qty += ktbf_edr_trade_qty_list[i];
						}
						qty = ktbf_edr_actual_qty;
						log.Format("%c%c:%c%c:%c%c, ktbf losscut, sum_pl:%d, sum_comm:%d",now[0],now[1],now[2],now[3],now[4],now[5], sum_pl, sum_commission);
						m_ctrlOrderList2.InsertString(0, log);
						execute_module("KTBF",hs, -qty, true);
						ktbf_edr = false; // 매매종료
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);

					/*시그널 일반 매매*/
					} else if (ktbf_edr_trade_qty != 0) {
						ktbf_edr_signal = true;
						execute_module("KTBF", hs, ktbf_edr_trade_qty, true);
					} else {
						/*비시그널 호가변경 추종 매매로직을 넣어도 될까 싶음*/
						//log.Format("ktbf_edr_trade_qty is zero at udp data down");
						//m_ctrlOrderList2.InsertString(0,log);
					}
					} // 여기지워

					/*비시그널 호가변경 추종 매매로직*/
					if (ktbf_edr_pendingListIndex !=0) {
						execute_module("KTBF",hs, ktbf_edr_pendingList[0].intQty, false);
					}

					/*청산*/
					if (now.compare(trading_hour_ends) >= 0) {

						/* 주문 - 개수 설정 필요*/
						ktbf_edr_signal = true;
						int qty = 0;
						for(int i =0; i < ktbf_edr_trade_num; i++) {
							qty += ktbf_edr_trade_qty_list[i];
						}
						qty = - ktbf_edr_actual_qty;
						log.Format("%c%c:%c%c:%c%c, ktbf cheongsan qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], qty);
						m_ctrlOrderList2.InsertString(0, log);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						/*order를 away로 지정한다*/

						if (qty>0) {
							Order('1', qty, ktbf_last_prc-0.4, 0, "1", hs.code, "", "KTBF");
							log.Format("%c%c:%c%c:%c%c, ktbf cheongsan prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_last_prc-0.4);
							m_ctrlOrderList2.InsertString(0, log);
							lktbf_edr_FileWriter.Write(log, strlen(log));
						} else if (qty<0) {
							Order('1', qty, ktbf_last_prc+0.4, 0, "2", hs.code,"",  "KTBF");
							log.Format("%c%c:%c%c:%c%c, ktbf cheongsan prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_last_prc-0.4);
							m_ctrlOrderList2.InsertString(0, log);
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}

						//if (dataType.compare("A3") != 0) {
						//	if (qty>0) {
						//		Order('1', qty, hs.buy_hoga2_price-0.4, 0, "1", hs.code, "", "KTBF");
						//	} else if (qty<0) {
						//		Order('1', qty, hs.sell_hoga2_price+0.4, 0, "2", hs.code,"",  "KTBF");
						//	}
						//} else {
						//	if (qty>0) {
						//		Order('1', qty, hs.buy_hoga2_price-0.4, 0, "1", hs.code,"", "KTBF");
						//	} else if (qty<0) {
						//		Order('1', qty, hs.sell_hoga2_price+0.4, 0, "2", hs.code,"", "KTBF");
						//	}
						//}
						ktbf_edr = false; // 매매종료
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
					}
				}

			} else if (code.compare(lktb_code) == 0) {
				/* udp 그대로 읽고 저장하기*/
				//CString udp = strSiseData+'\n';
				//lktb_udpFileWriter.Write(udp, strlen(udp));

				string dataType = siseData.substr(0,2);
				
				HogaSise hs = {};

				if (dataType.compare("A3") == 0) {
					hs.type = "A3";
					hs.code = siseData.substr(5,12).c_str();
					hs.price = stof(siseData.substr(23,8))/100;
					lktbf_price_for_b6 = hs.price;
					if (hs.price != 0) 
						lktbf_last_prc = hs.price;

					hs.c_price = stoi(siseData.substr(23,8));

					lktbf_candle_price = hs.price;

					hs.volume = stoi(siseData.substr(31,6));
					lktbf_candle_vol += hs.volume;
					hs.time = siseData.substr(39,8).c_str();

					hs.pre_price = stof(siseData.substr(91,8))/100;
					hs.sell_or_buy = siseData.substr(135,1).c_str();

					hs.buy_hoga1_price = lktbf_b1_for_a3;
					hs.sell_hoga1_price = lktbf_s1_for_a3;

					/* vwap 계산 || 시세 파일에 기록*/
					if(lktbf_edr)
						setVwap("LKTBF", hs);
					//logSise(hs);
				} else if (dataType.compare("B6") == 0){
					hs.type = "B6";
					hs.code = siseData.substr(5,12).c_str();

					hs.price = lktbf_price_for_b6;

					hs.buy_hoga1_price = stof(siseData.substr(32,8))/100;
					hs.buy_hoga1_balance = stoi(siseData.substr(40,6));
					lktbf_b1_for_a3 = hs.buy_hoga1_price;


					hs.buy_hoga2_price = stof(siseData.substr(47,8))/100;
					hs.buy_hoga2_balance = stoi(siseData.substr(55,6));

					hs.sell_hoga1_price = stof(siseData.substr(114,8))/100;
					hs.sell_hoga1_balance = stoi(siseData.substr(122,6));
					lktbf_s1_for_a3 = hs.sell_hoga1_price;
			
					hs.sell_hoga2_price = stof(siseData.substr(129,8))/100;
					hs.sell_hoga2_balance = stoi(siseData.substr(137,6));

					hs.buy_hoga1_count = stoi(siseData.substr(193,4));
					hs.buy_hoga2_count = stoi(siseData.substr(197,4));
					hs.sell_hoga1_count = stoi(siseData.substr(218,4));
					hs.sell_hoga2_count = stoi(siseData.substr(222,4));

					hs.time = siseData.substr(238,8).c_str();
					
					/* 시세 파일에 기록*/
					//logSise(hs);

				} else if (dataType.compare("G7") == 0){
					hs.type = "G7";
					hs.code = siseData.substr(5,12).c_str();
					hs.price = stof(siseData.substr(23,8))/100;
					if (hs.price != 0) 
						lktbf_last_prc = hs.price;

					lktbf_price_for_b6 = hs.price;

					hs.c_price = stoi(siseData.substr(23,8));

					lktbf_candle_price = hs.price;
					hs.volume = stoi(siseData.substr(31,6));
					lktbf_candle_vol += hs.volume;
					hs.time = siseData.substr(39,8).c_str();

					hs.pre_price = stof(siseData.substr(91,8))/100;
					hs.sell_or_buy = siseData.substr(135,1).c_str();

					hs.buy_hoga1_price = stof(siseData.substr(144,8))/100;
					hs.buy_hoga1_balance = stoi(siseData.substr(152,6));
					lktbf_b1_for_a3 = hs.buy_hoga1_price;

					hs.buy_hoga2_price = stof(siseData.substr(159,8))/100;
					hs.buy_hoga2_balance = stoi(siseData.substr(167,6));

					hs.sell_hoga1_price = stof(siseData.substr(226,8))/100;
					hs.sell_hoga1_balance = stoi(siseData.substr(234,6));
					lktbf_s1_for_a3 = hs.sell_hoga1_price;

					hs.sell_hoga2_price = stof(siseData.substr(241,8))/100;
					hs.sell_hoga2_balance = stoi(siseData.substr(249,6));

					hs.buy_hoga1_count = 0;
					hs.buy_hoga2_count = 0;
					hs.sell_hoga1_count = 0;
					hs.sell_hoga2_count = 0;
					hs.buy_hoga1_count = stoi(siseData.substr(305,4));
					hs.buy_hoga2_count = stoi(siseData.substr(309,4));
					hs.sell_hoga1_count = stoi(siseData.substr(330,4));
					hs.sell_hoga2_count = stoi(siseData.substr(334,4));

					/* vwap 계산 || 시세 파일에 기록*/
					if(lktbf_edr)
						setVwap("LKTBF",hs);
					//logSise(hs);

				} else {
				}

				/*LKTBF 10초봉*/
				SYSTEMTIME lt;
				GetLocalTime(&lt);
				int hour = lt.wHour;
				int min = lt.wMinute;
				int sec = lt.wSecond;
				if (lktbf_init_sec != sec/10) {
					candleSecond candle;
					candle.hour = hour;
					candle.min = min;
					candle.sec = (sec/10)*10;
					candle.volume = lktbf_candle_vol;
					candle.price = lktbf_candle_price;

					lktbf_10sec_candle[lktbf_10sec_index++] = candle;

					lktbf_candle_vol = 0;
					lktbf_init_sec = sec/10;
				}

				/*LKTBF 1초봉*/
				//if (lktbf_init_sec != sec) {
				//	candleSecond candle;
				//	candle.hour = hour;
				//	candle.min = min;
				//	candle.sec = sec;
				//	candle.volume = lktbf_candle_vol;
				//	candle.price = lktbf_candle_price;

				//	lktbf_sec_candle[lktbf_sec_index++] = candle;

				//	lktbf_candle_vol = 0;
				//	lktbf_init_sec = sec;
				//}
				char time[7];
				int len = sprintf(time, "%02d%02d%02d", hour,min,sec);
				string now(time);

				if(lktbf_edr) {
					if (lktbf_edr_ema_fast == 0 && hour==lktbf_h, min == lktbf_m) {lktbf_edr_ema_fast = lktbf_candle_price;}
					if (lktbf_edr_ema_slow == 0 && hour==lktbf_h, min == lktbf_m) {lktbf_edr_ema_slow = lktbf_candle_price;}

					if (lktbf_edr_ema_fast == 0 && lktbf_edr_ema_slow == 0) {
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
					}

					/*vol봉이 올라왔을때 동작하도록*/
					if (lktb_vwap_preindex != lktb_vwap_num) {
						if(hs.price != 0) {
							lktbf_edr_ema_fast = lktbf_edr_fast_coeff * hs.price + (1 - lktbf_edr_fast_coeff) * lktbf_edr_ema_fast;
							lktbf_edr_ema_slow = lktbf_edr_slow_coeff * hs.price + (1 - lktbf_edr_slow_coeff) * lktbf_edr_ema_slow;
						}
						
						int qty = 0;
						for(int i =0; i < lktbf_edr_trade_num; i++) {
							qty += lktbf_edr_trade_qty_list[i];
						}
						log.Format("%c%c:%c%c:%c%c, lktb_edr_trade_num:%d, qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_trade_num,qty);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						//log.Format("%c%c:%c%c:%c%c, NEW lktb vol prc:%.3f, ema_fast:%.3f, ema_slow_:%.3f",now[0],now[1],now[2],now[3],now[4],now[5],hs.price, lktb_edr_ema_fast,lktb_edr_ema_slow);

						m_ctrlOrderList.InsertString(0,log);

						lktb_vwap_preindex = lktb_vwap_num;

						//lktb_edr_actual_qty = lktb_edr_trade_qty + lktb_edr_actual_qty;
						lktbf_edr_trade_qty = 0;

						float diff_now = lktbf_edr_ema_fast - lktbf_edr_ema_slow;
						float tick_diff_now = lktbf_tick_conversion * diff_now;
						float abs_tick_diff_now = (tick_diff_now>0)?tick_diff_now:-tick_diff_now;

						if (abs_tick_diff_now > lktbf_tick_diff_of_max_qty) {
							lktbf_tick_diff_of_max_qty = abs_tick_diff_now;
						}
						
						lktbf_edr_target_qty = edrCalTargetQty(lktbf_edr_max_qty, lktbf_abs_max_short_qty, tick_diff_now, lktbf_edr_tick_cross_margin, lktbf_tick_diff_of_max_qty, "linear");

						if (lktbf_edr_target_qty != lktbf_edr_pre_target_qty) {
							ktbf_edr_changed_qty = true;
						}
						lktbf_edr_pre_target_qty = lktbf_edr_target_qty;
					//}
					int pending_qty = 0;
					for (int i = 0 ; i < lktbf_edr_pendingListIndex; i++) {
						pending_qty += lktbf_edr_pendingList[i].intQty;
					}

					int trade_qty_raw = (int)(lktbf_edr_target_qty - lktbf_edr_actual_qty - pending_qty);
					log.Format("%c%c:%c%c:%c%c, lktbf_edr_trade_num:%d, trade_qty_raw:%d, lktbf_edr_target_qty:%d, lktbf_edr_actual_qty:%d,pending_qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_trade_num, trade_qty_raw, lktbf_edr_target_qty, lktbf_edr_actual_qty, pending_qty);
					lktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);

					if (trade_qty_raw != lktbf_edr_pre_trade_qty_raw) {
						lktbf_edr_changed_qty = true;
					}
					lktbf_edr_pre_trade_qty_raw = trade_qty_raw;

					if (trade_qty_raw >=0) {
						lktbf_edr_trade_qty = (lktbf_edr_max_trade_qty < trade_qty_raw)? lktbf_edr_max_trade_qty : trade_qty_raw;
					} else {
						lktbf_edr_trade_qty = (lktbf_edr_max_trade_qty < -trade_qty_raw)? -lktbf_edr_max_trade_qty : trade_qty_raw;
					}
					if (lktbf_edr_trade_qty != lktbf_edr_pre_trade_qty) {
						lktbf_edr_changed_qty = true;
					}
					lktbf_edr_pre_trade_qty = lktbf_edr_trade_qty;

					if (lktbf_edr_changed_qty) {
						log.Format("%c%c:%c%c:%c%c, target_qty:%d, trade_qty_raw:%d, lktb_edr_trade_qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_edr_target_qty,trade_qty_raw,lktbf_edr_trade_qty);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						m_ctrlOrderList.InsertString(0,log);
					}
					lktbf_edr_changed_qty = false;

					/*9시 10분전에는 아무 매매도 하지말자*/
					if (lktbf_trading_time_start != "") {
						if (now.compare(lktbf_trading_time_start) < 0) {
							lktbf_edr_trade_qty = 0;
							return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
						}
					}

					/*1계약으로 수정하기 위한 로직*/
					if (lktbf_edr_trade_qty > 0) {
						lktbf_edr_trade_qty = lktbf_edr_trade_qty/lktbf_edr_trade_qty;
					} else if(lktbf_edr_trade_qty<0) {
						lktbf_edr_trade_qty = -lktbf_edr_trade_qty/lktbf_edr_trade_qty;
					}

					/*pl 계산*/
					int sum_pl=0;
					int sum_commission=0;
					for(int i = 0; i < lktbf_edr_trade_num; i++) {
						sum_pl += lktbf_edr_trade_qty_list[i]*(lktbf_last_prc - lktbf_edr_trade_prc_list[i]);
						sum_commission += (lktbf_krw_commission_per_contract * (lktbf_edr_trade_qty_list[i]>0)?lktbf_edr_trade_qty_list[i]:-lktbf_edr_trade_qty_list[i]);
					}
					int net_pl = lktbf_krw_value_1pt*sum_pl - sum_commission;

					log.Format("%c%c:%c%c:%c%c,fast_coeff:%.3f, slow_coeff:.3%f, price:%.3f\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_edr_fast_coeff, lktbf_edr_slow_coeff, hs.price);
					lktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					//log.Format("%c%c:%c%c:%c%c, net_pl:%d, lktb_edr_losscut:%d, now-ends :%d", now[0],now[1],now[2],now[3],now[4],now[5], net_pl, lktb_edr_losscut, now.compare(trading_hour_ends));
					log.Format("%c%c:%c%c:%c%c, net_pl:%f, lktb_edr_losscut:%d, now-ends :%d\n", now[0],now[1],now[2],now[3],now[4],now[5], net_pl, lktbf_edr_losscut, now.compare(trading_hour_ends));
					lktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					log.Format("%c%c:%c%c:%c%c,lktbf trdqty:%d, targetqty:%d, act_qty:%d, ema_fast:%.3f, ema_slow:%.3f\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_edr_trade_qty, lktbf_edr_target_qty, lktbf_edr_actual_qty, lktbf_edr_ema_fast, lktbf_edr_ema_slow);
					lktbf_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0, log);
						
					/*손절*/
					if (net_pl < lktbf_edr_losscut) {
						lktbf_edr_signal = true;
						int qty = 0;
						for(int i =0; i < lktbf_edr_trade_num; i++) {
							qty += lktbf_edr_trade_qty_list[i];
						}
						log.Format("%c%c:%c%c:%c%c, lktb losscut",now[0],now[1],now[2],now[3],now[4],now[5]);
						m_ctrlOrderList2.InsertString(0, log);
						execute_module("LKTBF",hs, -qty, true);
						lktbf_edr = false; // 매매종료
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);

					/*시그널 일반 매매*/
					} else if (lktbf_edr_trade_qty != 0) {
						lktbf_edr_signal = true;
						execute_module("LKTBF", hs, lktbf_edr_trade_qty, true);
					} else {
						/*비시그널 호가변경 추종 매매로직을 넣어도 될까 싶음*/
						//log.Format("lktb_edr_trade_qty is zero at udp data down");
						//m_ctrlOrderList2.InsertString(0,log);
					}
					} // 여기지워

					/*비시그널 호가변경 추종 매매로직*/
					if (lktbf_edr_pendingListIndex !=0) {
						execute_module("LKTBF",hs, lktbf_edr_pendingList[0].intQty, false);
					}

					/*청산*/
					if (now.compare(trading_hour_ends) >= 0) {

						/* 주문 - 개수 설정 필요*/
						lktbf_edr_signal = true;
						int qty = 0;
						for(int i =0; i < lktbf_edr_trade_num; i++) {
							qty += lktbf_edr_trade_qty_list[i];
						}
						qty = -lktbf_edr_actual_qty;
						log.Format("%c%c:%c%c:%c%c, lktbf cheongsan qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], qty);
						m_ctrlOrderList2.InsertString(0, log);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						/*order를 away로 지정한다*/
						if (qty>0) {
							Order('1', qty, lktbf_last_prc-0.4, 0, "1", hs.code, "", "LKTBF");
							log.Format("%c%c:%c%c:%c%c, lktbf cheongsan prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_last_prc-0.4);
							m_ctrlOrderList2.InsertString(0, log);
							lktbf_edr_FileWriter.Write(log, strlen(log));
						} else if (qty<0) {
							Order('1', qty, lktbf_last_prc+0.4, 0, "2", hs.code,"",  "LKTBF");
							log.Format("%c%c:%c%c:%c%c, lktbf cheongsan prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_last_prc+0.4);
							m_ctrlOrderList2.InsertString(0, log);
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
						//if (dataType.compare("A3") != 0) {
						//	if (qty>0) {
						//		Order('1', qty, hs.buy_hoga2_price-15, 0, "1", hs.code, "", "LKTBF");
						//	} else if (qty<0) {
						//		Order('1', qty, hs.sell_hoga2_price+15, 0, "2", hs.code,"",  "LKTBF");
						//	}
						//} else {
						//	if (qty>0) {
						//		Order('1', qty, hs.buy_hoga2_price-15, 0, "1", hs.code,"", "LKTBF");
						//	} else if (qty<0) {
						//		Order('1', qty, hs.sell_hoga2_price+15, 0, "2", hs.code,"", "LKTBF");
						//	}
						//}
						lktbf_edr = false; // 매매종료
					}
				}
				//------------------------------------------------------------------------------------------------------------------
				//------------------------------------------------------------------------------------------------------------------
				if(lktbf_af) {
					float last_price = lktbf_candle_price;
					string time_break("154500");
					if( lktbf_pre_sec != sec/10) {
						lktbf_pre_sec = sec/10;

						if (lktbf_ema_fast == 0 && hour==9, min ==0) {lktbf_ema_fast = lktbf_candle_price;}
						if (lktbf_ema_slow == 0 && hour==9, min ==0) {lktbf_ema_slow = lktbf_candle_price;}

						if (last_price !=0) {
							lktbf_ema_fast = lktbf_fast_coeff * last_price + (1-lktbf_fast_coeff) * lktbf_ema_fast;
							lktbf_ema_slow = lktbf_slow_coeff * last_price + (1-lktbf_slow_coeff) * lktbf_ema_slow;
						}

						log.Format("%c%c:%c%c:%c%c, ema_fast:%.3f, ema_slow:%.3f ent_prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_ema_fast, lktbf_ema_slow, ktbf_enter_prc);
						m_ctrlOrderList2.InsertString(0,log);
					}

					string tested_status = crossTest(lktbf_ema_fast, lktbf_ema_slow, 0.5);

					/*매매시간대 이전 장중 저가 및 고가 기록*/
					if (now.compare(trading_begins_after) < 0 ) {
						if (last_price != 0) {
							lktbf_intra_lo = (lktbf_intra_lo < last_price)? lktbf_intra_lo: last_price;
							lktbf_intra_hi = (lktbf_intra_hi > last_price)? lktbf_intra_hi: last_price;
						}
					} else if ( now.compare(trading_begins_after) >= 0 && now.compare(trading_begins_before) < 0 && !lktbf_is_first_done) {
						/*트리거 되면서 바로 매매 실행 --> 최초진입실행*/
						CString n_time;
						n_time.Format("%c%c%c%c%c",now[0],now[1],now[2],now[3],now[4]);
						if (last_price <(lktbf_intra_lo - lktbf_thru/lktbf_product_multiplier) && (tested_status.compare("below") == 0) && !lktbf_is_traded) {
							float std_tilnow = getStd(lktbf_10sec_candle, lktbf_10sec_index);
							float std_tilnow_ref = 0;
							for (int i =0; i< 2430; i++) {
								//if (now.compare(lktbf_ten_sec_candle[i]) == 0) {
								if (n_time.Left(5) == lktbf_ten_sec_candle[i].Left(5)) {
									std_tilnow_ref = lktbf_std_ref[i];
								}
							}
							
							float std_factor1 = std_tilnow / std_tilnow_ref;
							lktbf_qty = -ktbf_QTY_PER_TRADE * std_factor1;

							log.Format("%c%c:%c%c:%c%c, std_tilnow:%f, std_tilnow_ref:%f, std_factor1:%f \n",now[0],now[1],now[2],now[3],now[4],now[5], std_tilnow, std_tilnow_ref, std_factor1);
							lktbf_af_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							log.Format("%c%c:%c%c:%c%c,**f.o part //lktbf_qty:%d, std_factor1:%.3f, tested_status: %c **\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_qty,std_factor1, tested_status[0]);
							lktbf_af_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							

							/*1계약으로 수정하기 위한 로직*/
							if (lktbf_qty > 0) {
								lktbf_qty = lktbf_qty/lktbf_qty;
							} else if (lktbf_qty <0){
								lktbf_qty = -lktbf_qty/lktbf_qty;
							}

							lktbf_af_signal = true;
							//* 주문 */
							execute_module("LKTBF", hs, lktbf_qty, true);

							lktbf_af_tr_book.logTrade(now.c_str(),last_price, lktbf_qty, "ini", now.c_str(), last_price, "");

							log.Format("%c%c:%c%c:%c%c, lktbf_af_tr_book.getOpenPositionQty - init %d", now[0],now[1],now[2],now[3],now[4],now[5], lktbf_af_tr_book.getOpenPositionQty());
							lktbf_af_FileWriter.Write(log, strlen(log));
							m_ctrlOrderList2.InsertString(0,log);
							


							lktbf_is_traded = true;
						}
					}
					

					if (lktbf_is_traded && !lktbf_is_first_done) {
						float pl = lktbf_af_tr_book.getOpenPnl(last_price, "krw");
						if (pl > lktbf_af_tr_book.max_gain) {
							lktbf_af_tr_book.max_gain = pl;
							lktbf_af_tr_book.max_gain_price = last_price;
						}

						if (lktbf_af_tr_book.max_gain !=0) {
							lktbf_af_tr_book.draw_down = 1 - pl/lktbf_af_tr_book.max_gain;
						} else {
							lktbf_af_tr_book.draw_down = 0;
						}

						/*손절로직*/
						bool is_lc_intra_hilo = pl < lktbf_product_multiplier*lktbf_lc_hi_lo *(lktbf_intra_hi-lktbf_intra_lo)*lktbf_af_tr_book.krw_value_1pt/100*lktbf_qty;
						bool is_lc_pl = pl < lktbf_lc_pl * lktbf_af_tr_book.krw_value_1pt/100*lktbf_qty;

						if((is_lc_intra_hilo || is_lc_pl) && !(lktbf_is_losscut_traded && lktbf_is_pt_traded)) {
							/* 주문 - 개수 설정 필요*/
							//if (lktbf_che_mmgubun=="2") {
							//	lktbf_qty = -_ttoi(lktbf_che_qty);
							//} else {
							//	lktbf_qty = _ttoi(lktbf_che_qty);
							//}

							lktbf_qty = _ttoi(lktbf_che_qty);

							log.Format("%c%c:%c%c:%c%c, lktbf_af losscutt qty:%d", now[0],now[1],now[2],now[3],now[4],now[5], lktbf_qty);
							lktbf_af_FileWriter.Write(log, strlen(log));

							lktbf_af_signal = true;
							execute_module("LKTBF", hs, lktbf_qty, true);

							lktbf_af_tr_book.exitOpenPosition(now.c_str(), last_price,"1st trds lc", last_price);
							lktbf_is_losscut_traded = true;
							time_break = string(now);
							lktbf_is_first_done = true;
						}

						/*익절로직*/
						bool is_pt_pl = lktbf_af_tr_book.max_gain > -lktbf_pt_pl * lktbf_af_tr_book.krw_value_1pt / 100 * lktbf_qty;
						bool is_draw_down = lktbf_af_tr_book.draw_down > lktbf_pt_draw_down;
						
						if(is_pt_pl && is_draw_down && !(lktbf_is_losscut_traded && lktbf_is_pt_traded)) {
							/* 주문 - 개수 설정 필요*/
							if (lktbf_che_mmgubun=="2") {
								lktbf_qty = -_ttoi(lktbf_che_qty);
							} else {
								lktbf_qty = _ttoi(lktbf_che_qty);
							}

							log.Format("%c%c:%c%c:%c%c, lktbf_af pt qty:%d", now[0],now[1],now[2],now[3],now[4],now[5], lktbf_qty);
							lktbf_af_FileWriter.Write(log, strlen(log));

							lktbf_af_signal = true;
							execute_module("LKTBF", hs, lktbf_qty,true);

							lktbf_af_tr_book.exitOpenPosition(now.c_str(), last_price,"1st trds pt", last_price);
							lktbf_is_pt_traded = true;
							time_break = string(now);
							lktbf_is_first_done = true;
						}
					}

					/*2nd loop 시작*/
					if (time_break.compare(trading_begins_before) <0 && lktbf_is_first_done) {
						float entry = lktbf_af_tr_book.max_gain_price;
						if (last_price < entry && tested_status.compare("below") ==0 && !lktbf_is_traded2) {
							float std_tilnow = getStd(lktbf_10sec_candle, lktbf_10sec_index);
							float std_tilnow_ref = 0;
							for (int i =0; i< 2430; i++) {
								if (now.compare(lktbf_ten_sec_candle[i]) == 0) {
									std_tilnow_ref = lktbf_std_ref[i];
								}
							}
							
							float std_factor2 = std_tilnow / std_tilnow_ref;
							lktbf_qty = -lktbf_QTY_PER_TRADE * std_factor2;

							log.Format("%c%c:%c%c:%c%c, lktbf_af 2nd ent qty:%d", now[0],now[1],now[2],now[3],now[4],now[5], lktbf_qty);
							lktbf_af_FileWriter.Write(log, strlen(log));

							/* 주문 - 개수 설정 필요*/
							lktbf_af_signal = true;
							execute_module("LKTBF", hs, lktbf_qty,true);
							lktbf_af_tr_book.logTrade(now.c_str(),last_price, lktbf_qty, "ini", now.c_str(), last_price, "");
							lktbf_is_losscut_traded2 = true;
						}

						if (lktbf_is_traded2) {
							float pl = lktbf_af_tr_book.getOpenPnl(last_price, "krw");
							lktbf_af_tr_book.max_gain = pl;
							lktbf_af_tr_book.max_gain_price = last_price;

							if (lktbf_af_tr_book.max_gain !=0) {
								lktbf_af_tr_book.draw_down = 1 - pl/lktbf_af_tr_book.max_gain;
							} else {
								lktbf_af_tr_book.draw_down = 0;
							}

							/*손절로직 : 새 open position 의 lc에서 50%만큼 손실나면*/
							bool is_lc_pl = pl<-0.5*lktbf_lc_pl*lktbf_af_tr_book.krw_value_1pt/100*lktbf_qty;
							if (is_lc_pl) {
								/* 주문 - 개수 설정 필요*/
								//if (lktbf_che_mmgubun=="2") {
								//	lktbf_qty = -_ttoi(lktbf_che_qty);
								//} else {
								//	lktbf_qty = _ttoi(lktbf_che_qty);
								//}

								lktbf_qty = _ttoi(lktbf_che_qty);
								log.Format("%c%c:%c%c:%c%c, lktbf_af 2nd lc qty:%d", now[0],now[1],now[2],now[3],now[4],now[5], lktbf_qty);
								lktbf_af_FileWriter.Write(log, strlen(log));

								lktbf_af_signal = true;
								execute_module("LKTBF", hs, lktbf_qty,true);
								lktbf_af_tr_book.exitOpenPosition(now.c_str(), last_price, "2nd trds lc", last_price);
								lktbf_is_pt_traded2 = true;
								lktbf_af = false; // 매매종료
								return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
							}

							/* 익절로직1 : max_gain 이 ?? 틱 이상 -> first position trade의 50%
								* 익절로직2 : drawdown %% 이상 발생 --> first position trade의 1.5배
								*/
							bool is_pt_pl = lktbf_af_tr_book.max_gain > -0.5 * lktbf_pt_pl * lktbf_af_tr_book.krw_value_1pt/100*lktbf_qty;
							bool is_draw_down = lktbf_af_tr_book.draw_down > 1.5* lktbf_pt_draw_down * lktbf_af_tr_book.krw_value_1pt / 100;
							if (is_pt_pl && is_draw_down) {
								/* 주문 - 개수 설정 필요*/
								//if (lktbf_che_mmgubun=="2") {
								//	lktbf_qty = -_ttoi(lktbf_che_qty);
								//} else {
								//	lktbf_qty = _ttoi(lktbf_che_qty);
								//}
								lktbf_qty = _ttoi(lktbf_che_qty);
								log.Format("%c%c:%c%c:%c%c, lktbf_af 2nd pt qty:%d", now[0],now[1],now[2],now[3],now[4],now[5], lktbf_qty);
								lktbf_af_FileWriter.Write(log, strlen(log));
								lktbf_af_signal = true;
								execute_module("LKTBF", hs, lktbf_qty,true);
								lktbf_af_tr_book.exitOpenPosition(now.c_str(), last_price, "2nd trds pt", last_price);
								lktbf_is_pt_traded2 = true;
								lktbf_af = false; // 매매종료
								return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
							}
						}
					}
					

					if (now.compare(trading_hour_ends) > 0) {
						CString log;
						log.Format("lktbf_af_tr_book.getOpenPositionQty - close %d", lktbf_af_tr_book.getOpenPositionQty());
						m_ctrlOrderList2.InsertString(0,log);
						lktbf_af_FileWriter.Write(log, strlen(log));

						if (lktbf_af_tr_book.getOpenPositionQty() != 0) {						
							/* 주문 - 개수 설정 필요*/
							lktbf_af_signal = true;
							/*order를 away로 지정한다*/
							int qty = lktbf_af_tr_book.getCurQty();
							if (dataType.compare("A3") != 0) {
								if (qty>0) {
									Order('1', qty, hs.buy_hoga2_price-1.5,0, "1", hs.code, "", "LKTBF");
								} else if (qty<0) {
									Order('1', qty, hs.sell_hoga2_price+1.5,0, "2", hs.code, "", "LKTBF");
								}
							} else {
								if (qty>0) {
									Order('1', qty, hs.price-1.5,0,"1", hs.code, "", "LKTBF");
								} else if (qty<0) {
									Order('1', qty, hs.price+1.5,0, "2", hs.code, "", "LKTBF");
								}
							}
							lktbf_af_tr_book.exitOpenPosition(now.c_str(), lktbf_candle_price, "jongga", lktbf_candle_price);
							lktbf_af = false; // 매매종료
							return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
						}
					}

					execute_module("LKTBF", hs, lktbf_qty,false);
				}
				return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);

			} else if (code.compare(usd_code) == 0) {
				/* udp 그대로 읽고 저장하기*/
				//CString udp = strSiseData+'\n';
				//usd_udpFileWriter.Write(udp, strlen(udp));

				string dataType = siseData.substr(0,2);
				HogaSise hs = {};

				if (dataType.compare("A3") == 0) {
					hs.type = "A3";
					hs.code = siseData.substr(5,12).c_str();
					hs.price = stof(siseData.substr(23,8))/100;
					usd_price_for_b6 = hs.price;
					if (hs.price != 0) 
						usd_last_prc = hs.price;

					hs.c_price = stoi(siseData.substr(23,8));

					usd_candle_price = hs.price;

					hs.volume = stoi(siseData.substr(31,6));
					usd_candle_vol += hs.volume;
					hs.time = siseData.substr(39,8).c_str();

					hs.pre_price = stof(siseData.substr(91,8))/100;
					hs.sell_or_buy = siseData.substr(135,1).c_str();

					hs.buy_hoga1_price = usd_b1_for_a3;
					hs.sell_hoga1_price = usd_s1_for_a3;
					/* vwap 계산 || 시세 파일에 기록*/
					if(usd_edr) 
						setVwap("USD", hs);
					//logSise(hs);
			
				} else if (dataType.compare("B6") == 0){
					hs.type = "B6";
					hs.code = siseData.substr(5,12).c_str();

					hs.price = usd_price_for_b6;

					hs.buy_hoga1_price = stof(siseData.substr(32,8))/100;
					hs.buy_hoga1_balance = stoi(siseData.substr(40,6));
					usd_b1_for_a3 = hs.buy_hoga1_price;

					hs.buy_hoga2_price = stof(siseData.substr(47,8))/100;
					hs.buy_hoga2_balance = stoi(siseData.substr(55,6));

					hs.sell_hoga1_price = stof(siseData.substr(114,8))/100;
					hs.sell_hoga1_balance = stoi(siseData.substr(122,6));
					usd_s1_for_a3 = hs.sell_hoga1_price;
			
					hs.sell_hoga2_price = stof(siseData.substr(129,8))/100;
					hs.sell_hoga2_balance = stoi(siseData.substr(137,6));

					hs.buy_hoga1_count = stoi(siseData.substr(193,4));
					hs.buy_hoga2_count = stoi(siseData.substr(197,4));
					hs.sell_hoga1_count = stoi(siseData.substr(218,4));
					hs.sell_hoga2_count = stoi(siseData.substr(222,4));

					hs.time = siseData.substr(238,8).c_str();
					
					/* 시세 파일에 기록 */
					//logSise(hs);

				} else if (dataType.compare("G7") == 0){
					hs.type = "G7";
					hs.code = siseData.substr(5,12).c_str();
					hs.price = stof(siseData.substr(23,8))/100;
					usd_price_for_b6 = hs.price;
					if (hs.price != 0) 
						usd_last_prc = hs.price;

					hs.c_price = stoi(siseData.substr(23,8));

					usd_candle_price = hs.price;
					hs.volume = stoi(siseData.substr(31,6));
					usd_candle_vol += hs.volume;
					hs.time = siseData.substr(39,8).c_str();

					hs.pre_price = stof(siseData.substr(91,8))/100;
					hs.sell_or_buy = siseData.substr(135,1).c_str();

					hs.buy_hoga1_price = stof(siseData.substr(144,8))/100;
					hs.buy_hoga1_balance = stoi(siseData.substr(152,6));
					usd_b1_for_a3 = hs.buy_hoga1_price;

					hs.buy_hoga2_price = stof(siseData.substr(159,8))/100;
					hs.buy_hoga2_balance = stoi(siseData.substr(167,6));

					hs.sell_hoga1_price = stof(siseData.substr(226,8))/100;
					hs.sell_hoga1_balance = stoi(siseData.substr(234,6));
					usd_s1_for_a3 = hs.sell_hoga1_price;

					hs.sell_hoga2_price = stof(siseData.substr(241,8))/100;
					hs.sell_hoga2_balance = stoi(siseData.substr(249,6));

					hs.buy_hoga1_count = 0;
					hs.buy_hoga2_count = 0;
					hs.sell_hoga1_count = 0;
					hs.sell_hoga2_count = 0;
					hs.buy_hoga1_count = stoi(siseData.substr(305,4));
					hs.buy_hoga2_count = stoi(siseData.substr(309,4));
					hs.sell_hoga1_count = stoi(siseData.substr(330,4));
					hs.sell_hoga2_count = stoi(siseData.substr(334,4));

					/* vwap 계산 || 시세 파일에 기록 */
					if(usd_edr) 
						setVwap("USD",hs);
					//logSise(hs);

				} else {
				}
				///*USD 10초봉*/
				SYSTEMTIME lt;
				GetLocalTime(&lt);
				int hour = lt.wHour;
				int min = lt.wMinute;
				int sec = lt.wSecond;
				if (usd_init_sec != sec/10) {
					candleSecond candle;
					candle.hour = hour;
					candle.min = min;
					candle.sec = (sec/10)*10;
					candle.volume = usd_candle_vol;
					candle.price = usd_candle_price;

					usd_10sec_candle[usd_10sec_index++] = candle;

					usd_candle_vol = 0;
					usd_init_sec = sec/10;
				}
				char time[7];
				int len = sprintf(time, "%02d%02d%02d", hour,min,sec);
				string now(time);

				if(usd_edr) {
					if (usd_edr_ema_fast == 0 && hour==usd_h, min == usd_m) {usd_edr_ema_fast = usd_candle_price;}
					if (usd_edr_ema_slow == 0 && hour==usd_h, min == usd_m) {usd_edr_ema_slow = usd_candle_price;}

					if (usd_edr_ema_fast == 0 && usd_edr_ema_slow == 0) {
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
					}
					/*vol봉이 올라왔을때 동작하도록*/
					if (usd_vwap_preindex != usd_vwap_num) {
						if(hs.price != 0) {
							usd_edr_ema_fast = usd_edr_fast_coeff * hs.price + (1 - usd_edr_fast_coeff) * usd_edr_ema_fast;
							usd_edr_ema_slow = usd_edr_slow_coeff * hs.price + (1 - usd_edr_slow_coeff) * usd_edr_ema_slow;
						}
						
						int qty = 0;
						for(int i =0; i < usd_edr_trade_num; i++) {
							qty += usd_edr_trade_qty_list[i];
						}
						log.Format("%c%c:%c%c:%c%c, usd_edr_trade_num:%d, qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_trade_num,qty);
						usd_edr_FileWriter.Write(log, strlen(log));
						//log.Format("%c%c:%c%c:%c%c, NEW usd vol prc:%.3f, ema_fast:%.3f, ema_slow_:%.3f",now[0],now[1],now[2],now[3],now[4],now[5],hs.price, usd_edr_ema_fast,usd_edr_ema_slow);

						m_ctrlOrderList.InsertString(0,log);

						usd_vwap_preindex = usd_vwap_num;

						//usd_edr_actual_qty = usd_edr_trade_qty + usd_edr_actual_qty;
						usd_edr_trade_qty = 0;

						float diff_now = usd_edr_ema_fast - usd_edr_ema_slow;
						float tick_diff_now = usd_tick_conversion * diff_now;
						float abs_tick_diff_now = (tick_diff_now>0)?tick_diff_now:-tick_diff_now;

						if (abs_tick_diff_now > usd_tick_diff_of_max_qty) {
							usd_tick_diff_of_max_qty = abs_tick_diff_now;
						}
						
						usd_edr_target_qty = edrCalTargetQty(usd_edr_max_qty, usd_abs_max_short_qty, tick_diff_now, usd_edr_tick_cross_margin, usd_tick_diff_of_max_qty, "linear");

						if (usd_edr_target_qty != usd_edr_pre_target_qty) {
							ktbf_edr_changed_qty = true;
						}
						usd_edr_pre_target_qty = usd_edr_target_qty;
					//}
					int pending_qty = 0;
					for (int i = 0 ; i < usd_edr_pendingListIndex; i++) {
						pending_qty += usd_edr_pendingList[i].intQty;
					}

					int trade_qty_raw = (int)(usd_edr_target_qty - usd_edr_actual_qty - pending_qty);
					log.Format("%c%c:%c%c:%c%c, usd_edr_trade_num:%d, trade_qty_raw:%d, usd_edr_target_qty:%d, usd_edr_actual_qty:%d,pending_qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_trade_num, trade_qty_raw, usd_edr_target_qty, usd_edr_actual_qty, pending_qty);
					usd_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);

					if (trade_qty_raw != usd_edr_pre_trade_qty_raw) {
						usd_edr_changed_qty = true;
					}
					usd_edr_pre_trade_qty_raw = trade_qty_raw;

					if (trade_qty_raw >=0) {
						usd_edr_trade_qty = (usd_edr_max_trade_qty < trade_qty_raw)? usd_edr_max_trade_qty : trade_qty_raw;
					} else {
						usd_edr_trade_qty = (usd_edr_max_trade_qty < -trade_qty_raw)? -usd_edr_max_trade_qty : trade_qty_raw;
					}
					if (usd_edr_trade_qty != usd_edr_pre_trade_qty) {
						usd_edr_changed_qty = true;
					}
					usd_edr_pre_trade_qty = usd_edr_trade_qty;

					if (usd_edr_changed_qty) {
						log.Format("%c%c:%c%c:%c%c, target_qty:%d, trade_qty_raw:%d, usd_edr_trade_qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], usd_edr_target_qty,trade_qty_raw,usd_edr_trade_qty);
						usd_edr_FileWriter.Write(log, strlen(log));
						m_ctrlOrderList.InsertString(0,log);
					}
					usd_edr_changed_qty = false;

					/*9시 0분전에는 아무 매매도 하지말자*/
					if (usd_trading_time_start != "") {
						if (now.compare(usd_trading_time_start) < 0) {
							usd_edr_trade_qty = 0;
							return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
						}
					}

					/*1계약으로 수정하기 위한 로직*/
					//if (usd_edr_trade_qty > 0) {
					//	usd_edr_trade_qty = usd_edr_trade_qty/usd_edr_trade_qty;
					//} else if(usd_edr_trade_qty<0) {
					//	usd_edr_trade_qty = -usd_edr_trade_qty/usd_edr_trade_qty;
					//}

					/*pl 계산*/
					int sum_pl=0;
					int sum_commission=0;
					for(int i = 0; i < usd_edr_trade_num; i++) {
						sum_pl += usd_edr_trade_qty_list[i]*(usd_last_prc - usd_edr_trade_prc_list[i]);
						sum_commission += (usd_krw_commission_per_contract * (usd_edr_trade_qty_list[i]>0)?usd_edr_trade_qty_list[i]:-usd_edr_trade_qty_list[i]);
					}
					int net_pl = usd_krw_value_1pt*sum_pl - sum_commission;

					log.Format("%c%c:%c%c:%c%c,fast_coeff:%.3f, slow_coeff:.3%f, price:%.3f\n",now[0],now[1],now[2],now[3],now[4],now[5], usd_edr_fast_coeff, usd_edr_slow_coeff, hs.price);
					usd_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					//log.Format("%c%c:%c%c:%c%c, net_pl:%d, usd_edr_losscut:%d, now-ends :%d", now[0],now[1],now[2],now[3],now[4],now[5], net_pl, usd_edr_losscut, now.compare(trading_hour_ends));
					log.Format("%c%c:%c%c:%c%c, net_pl:%d, usd_edr_losscut:%d, now-ends :%d\n", now[0],now[1],now[2],now[3],now[4],now[5], net_pl, usd_edr_losscut, now.compare(trading_hour_ends));
					usd_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0,log);
					log.Format("%c%c:%c%c:%c%c,usd trdqty:%d, targetqty:%d, act_qty:%d, ema_fast:%.3f, ema_slow:%.3f\n",now[0],now[1],now[2],now[3],now[4],now[5], usd_edr_trade_qty, usd_edr_target_qty, usd_edr_actual_qty, usd_edr_ema_fast, usd_edr_ema_slow);
					usd_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList2.InsertString(0, log);
						
					/*손절*/
					if (net_pl < usd_edr_losscut) {
						usd_edr_signal = true;
						int qty = 0;
						for(int i =0; i < usd_edr_trade_num; i++) {
							qty += usd_edr_trade_qty_list[i];
						}
						log.Format("%c%c:%c%c:%c%c, USD losscut",now[0],now[1],now[2],now[3],now[4],now[5]);
						m_ctrlOrderList2.InsertString(0, log);
						execute_module("USD",hs, -qty, true);
						usd_edr = false; // 매매종료
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);

					/*시그널 일반 매매*/
					} else if (usd_edr_trade_qty != 0) {
						usd_edr_signal = true;
						execute_module("USD", hs, usd_edr_trade_qty, true);
					} else {
						/*비시그널 호가변경 추종 매매로직을 넣어도 될까 싶음*/
						//log.Format("usd_edr_trade_qty is zero at udp data down");
						//m_ctrlOrderList2.InsertString(0,log);
					}
					} // 여기지워

					/*비시그널 호가변경 추종 매매로직*/
					if (usd_edr_pendingListIndex !=0) {
						execute_module("USD",hs, usd_edr_pendingList[0].intQty, false);
					}

					/*청산*/
					if (now.compare(trading_hour_ends) >= 0) {

						/* 주문 - 개수 설정 필요*/
						usd_edr_signal = true;
						int qty = 0;
						for(int i =0; i < usd_edr_trade_num; i++) {
							qty += usd_edr_trade_qty_list[i];
							log.Format("%c%c:%c%c:%c%c, tested USD cheongsan i:%d, usd_edr_trade_num:%d, plus:%d, qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], i, usd_edr_trade_num, usd_edr_trade_qty_list[i], qty);
							m_ctrlOrderList2.InsertString(0, log);
							usd_edr_FileWriter.Write(log, strlen(log));
						}

						qty = -usd_edr_actual_qty;

						log.Format("%c%c:%c%c:%c%c, USD cheongsan usd_edr_trade_num:%d, qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], usd_edr_trade_num, qty);
						m_ctrlOrderList2.InsertString(0, log);
						usd_edr_FileWriter.Write(log, strlen(log));
						/*order를 away로 지정한다*/
						if (qty>0) {
							Order('1', qty, usd_last_prc-10, 0, "1", hs.code, "", "USD");
							log.Format("%c%c:%c%c:%c%c, usd cheongsan prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5], usd_last_prc-0.4);
							m_ctrlOrderList2.InsertString(0, log);
							lktbf_edr_FileWriter.Write(log, strlen(log));
						} else if (qty<0) {
							Order('1', qty, usd_last_prc+10, 0, "2", hs.code,"",  "USD");
							log.Format("%c%c:%c%c:%c%c, usd cheongsan prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5], usd_last_prc-0.4);
							m_ctrlOrderList2.InsertString(0, log);
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
						//if (dataType.compare("A3") != 0) {
						//	if (qty>0) {
						//		Order('1', qty, hs.buy_hoga2_price-15, 0, "1", hs.code, "", "USD");
						//	} else if (qty<0) {
						//		Order('1', qty, hs.sell_hoga2_price+15, 0, "2", hs.code,"",  "USD");
						//	}
						//} else {
						//	if (qty>0) {
						//		Order('1', qty, hs.buy_hoga2_price-15, 0, "1", hs.code,"", "USD");
						//	} else if (qty<0) {
						//		Order('1', qty, hs.sell_hoga2_price+15, 0, "2", hs.code,"", "USD");
						//	}
						//}
						usd_edr = false; // 매매종료
						return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
					}
				}
			} else {
				//CString udp = strSiseData+'\n';
				//errorFileWriter.Write(udp,strlen(udp));
			}
			::LeaveCriticalSection(&g_cs);
		}
	} catch (exception e) {	
		CString strLog;
		strLog.Format("!!!! exception : %s\n", e);
		errorFileWriter.Write(strLog,strlen(strLog));
	}
	
	return CDialogEx::OnCopyData(pWnd, pCopyDataStruct);
}

void CAPISampleDlg::execute_module(CString jongmok, HogaSise hs, int qty, bool new_order) {

	string now = getTime();
	CString log;
	now = getTime();
	float bid_offer_coeff = (float)(hs.buy_hoga1_balance - hs.sell_hoga1_balance) / (hs.buy_hoga1_balance + hs.sell_hoga1_balance);

	boc_pre_state = state;
	if (bid_offer_coeff < -0.5) {
		state = "offerish";
	} else if (bid_offer_coeff > 0.5) {
		state = "bidish";
	} else {
		state = "balanced";
	}

	float diff_sell_buy_hoga = hs.sell_hoga1_price - hs.buy_hoga1_price;
	//if ((int)(diff_sell_buy_hoga * 1000)%10 == 9) {
	//	diff_sell_buy_hoga += 0.001;
	//}

	CString str_diff_sell_buy_hoga = "0.01";
	str_diff_sell_buy_hoga.Format("%04.2f",diff_sell_buy_hoga);

	if (lktbf_af) {
		if (str_diff_sell_buy_hoga != "0.01") {
			log.Format("%c%c:%c%c:%c%c, ex state: empty %s, diff:%s, b_o_coeff : %.3f, i-hi : %.3f, i-lo : %.3f, qty:%d signal!!!!!\n", now[0],now[1],now[2],now[3],now[4],now[5],state, str_diff_sell_buy_hoga, bid_offer_coeff, lktbf_intra_hi, lktbf_intra_lo, qty);
		} else {
			log.Format("%c%c:%c%c:%c%c, ex state: %s, b_o_coeff : %.3f, i-hi : %.3f, i-lo : %.3f, qty:%d signal!!!!!\n", now[0],now[1],now[2],now[3],now[4],now[5],state, bid_offer_coeff, lktbf_intra_hi, lktbf_intra_lo, qty);
		}
		lktbf_af_FileWriter.Write(log, strlen(log));
		m_ctrlOrderList.InsertString(0,log);
	} 
	/*else {
		log.Format("%c%c:%c%c:%c%c, ex state: %s, b_o_coeff : %.3f, qty:%d\n", now[0],now[1],now[2],now[3],now[4],now[5],state, qty);
	}*/
	
	if (usd_edr) {
		log.Format("%c%c:%c%c:%c%c, USD EXECUTE qty:%d \n",now[0],now[1],now[2],now[3],now[4],now[5],qty);
		usd_edr_FileWriter.Write(log, strlen(log));
	} else if (ktbf_edr) {
		log.Format("%c%c:%c%c:%c%c, KTBF EXECUTE qty:%d \n",now[0],now[1],now[2],now[3],now[4],now[5],qty);
		ktbf_edr_FileWriter.Write(log, strlen(log));
	} else if (lktbf_edr) {
		log.Format("%c%c:%c%c:%c%c, LKTBF EXECUTE qty:%d \n",now[0],now[1],now[2],now[3],now[4],now[5],qty);
		lktbf_edr_FileWriter.Write(log, strlen(log));
	}
	//m_ctrlOrderList.InsertString(0,log);
	
	if (jongmok == "KTBF") {
		/* float 값 보정*/
		float diff_sell_buy_hoga = hs.sell_hoga1_price - hs.buy_hoga1_price;
		if ((int)(diff_sell_buy_hoga * 1000)%10 == 9) {
			diff_sell_buy_hoga += 0.001;
		}
		CString str_diff_sell_buy_hoga;
		str_diff_sell_buy_hoga.Format("%04.2f",diff_sell_buy_hoga);

		log.Format("%c%c:%c%c:%c%c, EXECUTE ktbf diffhoga:%s, %.3f,%.3f, pending_index:%d qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],str_diff_sell_buy_hoga,hs.sell_hoga1_price,hs.buy_hoga1_price,ktbf_edr_pendingListIndex, qty);
		ktbf_edr_FileWriter.Write(log, strlen(log));

		/*매수*/
		if (qty > 0) {
			/* 신규 주문으로 (시그널이 와서) Buy 1호가에 대놓을때*/
			if(ktbf_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.01" && new_order) {
				log.Format("%c%c:%c%c:%c%c,ktbf LONG NEW ORDER 00\n",now[0],now[1],now[2],now[3],now[4],now[5]);
				ktbf_edr_FileWriter.Write(log, strlen(log));

				Order('1', qty, hs.buy_hoga1_price, 0, "2", hs.code, "", "KTBF"); // 신규주문내기
				log.Format("%c%c:%c%c:%c%c,ktbf LONG NEW ORDER 11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
				ktbf_edr_FileWriter.Write(log, strlen(log));

				m_ctrlOrderList.InsertString(0,log);
				ktbf_af_signal = false;
			} else {
				/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 buy1+1틱 호가에 대놓음 -> 즉시 매수*/
				if (str_diff_sell_buy_hoga != "0.01") {
					ktb_urgent_begintime = hs.time;
					//ktbf_urgent_beginprice = hs.buy_hoga1_price+ktbf_tick_value;
					ktb_urgent_mode = true;
					ktb_urgent_type = state;
					log.Format("%c%c:%c%c:%c%c,ktbf LONG empty urgent idx:%d 22\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));

					OrderItem temp_list[1000];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = ktbf_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = ktbf_edr_pendingList[i];
						//temp_qty += ktbf_edr_pendingList[i].intQty;
						if(temp_list[i].strGubun == "2") {
							temp_qty += ktbf_edr_pendingList[i].intQty;
						} else {
							temp_qty -= ktbf_edr_pendingList[i].intQty;
						}
						if (temp_list[i].strGubun != "2") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,ktbf LONG is_opposite idx:%d 33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, ktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							ktbf_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "KTBF");
						}
						qty = qty+temp_qty;
						if(qty !=0 && ktbf_edr_pendingListIndex == 0) {
							Order('1', qty, hs.buy_hoga1_price+ktbf_tick_value, 0, "2", hs.code,"", "KTBF"); // pending 다 취소하고 신규주문내기
						}
					} else {
						log.Format("%c%c:%c%c:%c%c,ktbf LONG just modify idx:%d 44\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						float modify_price = hs.buy_hoga1_price+ktbf_tick_value;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,ktbf LONG just modify idx:%d 44-n55\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						ktbf_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, ktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							ktbf_edr_FileWriter.Write(log, strlen(log));
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "KTBF"); // 그냥 주문수정
							}
						}
					}

					/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
					log.Format("●URGENT buy ktbf type:%s begin:%s prc:%.3f, qty:%d\n", ktb_urgent_type, ktb_urgent_begintime, hs.buy_hoga1_price+ktbf_tick_value, qty );
					m_ctrlOrderList2.InsertString(0,log);
					ktbf_edr_FileWriter.Write(log,strlen(log));
					ktbf_af_signal = false;
					ktb_pre_orgordno == "";

				/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매수*/
				} else if (!ktb_urgent_mode && state == "bidish" && isSamePrice(hs.price,hs.sell_hoga1_price)) { //bidish and 현재가는 매도1호가
					ktb_urgent_begintime = hs.time;
					//ktbf_urgent_beginprice = hs.sell_hoga1_price;
					ktb_urgent_mode = true;
					ktb_urgent_type = state;
					
					log.Format("%c%c:%c%c:%c%c,ktbf LONG urgent idx:%d 55\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					
					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = ktbf_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = ktbf_edr_pendingList[i];
						if(temp_list[i].strGubun == "2") {
							temp_qty += ktbf_edr_pendingList[i].intQty;
						} else {
							temp_qty -= ktbf_edr_pendingList[i].intQty;
						}
						//temp_qty += ktbf_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "2") {
							is_opposite = true;
						}
					}
					if (is_opposite) {

						log.Format("%c%c:%c%c:%c%c,ktbf LONG urgent isopposite idx:%d 66\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							log.Format("666 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s\n",i, ktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno);
							ktbf_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice,temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "KTBF");
						}
						qty = qty+temp_qty;
						if (ktbf_edr_pendingListIndex ==0)
							Order('1', qty, hs.sell_hoga1_price, 0, "2", hs.code, "", "KTBF"); // pending 다 취소하고 신규주문내기
					} else {
						log.Format("%c%c:%c%c:%c%c,ktbf LONG urgent justmodify idx:%d 77\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						float modify_price = hs.sell_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "KTBF"); // 그냥 주문수정
							}
						}
					}
					///*화면에 execute 상황을 기록하기 위한 코드 */
					log.Format("●URGENT buy ktbf type:%s begin:%s prc:%.3f, qty:%d\n", ktb_urgent_type, ktb_urgent_begintime, hs.sell_hoga1_price, qty );
					m_ctrlOrderList2.InsertString(0,log);
					ktbf_edr_FileWriter.Write(log,strlen(log));
					ktbf_af_signal = false;
					ktb_pre_orgordno == "";

				} else if (!isSamePrice(ktbf_pre_price_float,hs.price) || boc_pre_state != state) {
					/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/
					log.Format("ktbf LONG ORDER HOGA CHANGE 0 / ktbf_pre_price:%.3f, hs.price:%.3f, boc_pre_state:%s, state:%s", ktbf_pre_price_float, hs.price, boc_pre_state, state);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					log.Format("%c%c:%c%c:%c%c,ktbf LONG change price idx:%d 88\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));

					m_ctrlOrderList.InsertString(0,log);

					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = ktbf_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = ktbf_edr_pendingList[i];
						if(temp_list[i].strGubun == "2") {
							temp_qty += ktbf_edr_pendingList[i].intQty;
						} else {
							temp_qty -= ktbf_edr_pendingList[i].intQty;
						}
						//temp_qty += ktbf_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "2") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,ktbf LONG change price opposite idx:%d 99\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, ktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							ktbf_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "KTBF");
						}
						qty = qty+temp_qty;
						if(qty != 0 && ktbf_edr_pendingListIndex==0) {
							Order('1', qty, hs.buy_hoga1_price,0, "2", hs.code, "","KTBF"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.buy_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,ktbf LONG just change price idx:%d 1010\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code,temp_list[i].orgordno, "KTBF"); // 그냥 주문수정
							}
						}
					}
				} else {
					log.Format("KTBF LONG DIDNT CHANGE URGENT or HOGA!!\n");
					log.Format("%c%c:%c%c:%c%c,ktbf LONG didn't change urgent or hoga!!",now[0],now[1],now[2],now[3],now[4],now[5]);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					//m_ctrlOrderList.InsertString(0,log);
				}
			}
		/* 매도 */
		} else if (qty < 0) {
			/* 신규 주문으로 (시그널이 와서) Sell 1호가에 대놓을때*/
			if (ktbf_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.01" && new_order) {
				log.Format("%c%c:%c%c:%c%c,ktbf SHORT NEW ORDER -11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
				ktbf_edr_FileWriter.Write(log, strlen(log));
				Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "KTBF"); // 신규주문내기
				m_ctrlOrderList.InsertString(0,log);
				ktbf_af_signal = false;
			} else {
			/*이미 매매가 하나 올라가 있을때*/
				/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 sell1-1틱 호가에 대놓음 -> 즉시 매수*/
				if (str_diff_sell_buy_hoga != "0.01") {
					ktb_urgent_begintime = hs.time;
					//ktbf_urgent_beginprice = hs.sell_hoga1_price-ktbf_tick_value;
					ktb_urgent_mode = true;
					ktb_urgent_type = state;

					log.Format("%c%c:%c%c:%c%c,ktbf SHORT empty urgent idx:%d -22\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));

					OrderItem temp_list[1000];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = ktbf_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = ktbf_edr_pendingList[i];
						if(temp_list[i].strGubun == "1") {
							temp_qty += ktbf_edr_pendingList[i].intQty;
						} else {
							temp_qty -= ktbf_edr_pendingList[i].intQty;
						}
						//temp_qty += ktbf_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "1") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,ktbf SHORT empty urgent opposite idx:%d -33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							log.Format("3333 short i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, ktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							ktbf_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "KTBF");
							
						}
						qty = qty+temp_qty;
						if (qty != 0 && ktbf_edr_pendingListIndex==0) {
							Order('1', qty, hs.sell_hoga1_price-ktbf_tick_value, 0, "1", hs.code,"", "KTBF"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.sell_hoga1_price-ktbf_tick_value;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,ktbf SHORT empty urgent just modify idx:%d -44\n",now[0],now[1],now[2],now[3],now[4],now[5], ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "KTBF"); // 그냥 주문수정
							}
						}
					}

					/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
					log.Format("●URGENT sell ktbf type:%s begin:%s prc:%.3f, qty:%d\n", ktb_urgent_type, ktb_urgent_begintime, hs.sell_hoga1_price, qty );
					m_ctrlOrderList2.InsertString(0,log);
					ktbf_edr_FileWriter.Write(log,strlen(log));
					ktbf_af_signal = false;
					ktb_pre_orgordno == "";

				/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매도*/
				}else if (!ktb_urgent_mode && state == "offerish" && isSamePrice(hs.price,hs.buy_hoga1_price)) { //bidish and 현재가는 매도1호가
					ktb_urgent_begintime = hs.time;
					//ktbf_urgent_beginprice = hs.sell_hoga1_price;
					ktb_urgent_mode = true;
					ktb_urgent_type = state;

					log.Format("%c%c:%c%c:%c%c,ktbf SHORT urgent idx:%d -55\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));

					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = ktbf_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = ktbf_edr_pendingList[i];
						temp_qty += ktbf_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "1") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,ktbf SHORT urgent opposited idx:%d -66\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							log.Format("%c%c:%c%c:%c%c,ktbf SHORT urgent opposited idx:%d floatprc:%04.2f gubun:%s,orgno:%s -66~77\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex, temp_list[i].floatPrice,temp_list[i].strGubun,temp_list[i].orgordno);
							ktbf_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "KTBF");
						}
						qty = qty+temp_qty;
						if(qty != 0 && ktbf_edr_pendingListIndex ==0) {
							Order('1', qty, hs.buy_hoga1_price, 0, "1", hs.code, "", "KTBF"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.buy_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,ktbf SHORT urgent just modify idx:%d -77\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "KTBF"); // 그냥 주문수정
							}
						}
					}
					/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
					log.Format("●URGENT sell ktbf type:%s begin:%s prc:%.3f, qty:%d\n", ktb_urgent_type, ktb_urgent_begintime, hs.sell_hoga1_price, qty );
					m_ctrlOrderList2.InsertString(0,log);
					ktbf_af_signal = false;
					ktb_pre_orgordno == "";

				} else if (!isSamePrice(ktbf_pre_price_float,hs.price) || boc_pre_state != state) {
					/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/

					log.Format("%c%c:%c%c:%c%c,ktbf SHORT modify price idx:%d -88\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = ktbf_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = ktbf_edr_pendingList[i];
						temp_qty += ktbf_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "1") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,ktbf SHORT modify price opposite idx:%d -99\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "KTBF");
						}
						qty = qty+temp_qty;
						if(qty != 0 && ktbf_edr_pendingListIndex==0) {
							Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "KTBF"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.sell_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);
						log.Format("%c%c:%c%c:%c%c,ktbf SHORT just modify price idx:%d -1010\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
						ktbf_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "KTBF"); // 그냥 주문수정
							}
						}
					}

					log.Format("%c%c:%c%c:%c%c,ktbf SHORT ORDER HOGA CHANGE QTY:%d, prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5],qty, hs.sell_hoga1_price);
					m_ctrlOrderList.InsertString(0,log);
				} else {
					log.Format("%c%c:%c%c:%c%c,ktbf SHORT DIDNT CHANGE URGENT or HOGA!! idx:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],ktbf_edr_pendingListIndex);
					ktbf_edr_FileWriter.Write(log, strlen(log));
					//m_ctrlOrderList.InsertString(0,log);
				}
			}
		} else {

		}

	} else if (jongmok == "LKTBF") {
		/* float 값 보정*/
		float diff_sell_buy_hoga = hs.sell_hoga1_price - hs.buy_hoga1_price;
		if ((int)(diff_sell_buy_hoga * 1000)%10 == 9) {
			diff_sell_buy_hoga += 0.001;
		}
		CString str_diff_sell_buy_hoga;
		str_diff_sell_buy_hoga.Format("%04.2f",diff_sell_buy_hoga);

		log.Format("%c%c:%c%c:%c%c, EXECUTE lktbf diffhoga:%s, %.3f,%.3f, pending_index:%d qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],str_diff_sell_buy_hoga,hs.sell_hoga1_price,hs.buy_hoga1_price,lktbf_af_pendingListIndex, qty);
		if(lktbf_af) {
			lktbf_af_FileWriter.Write(log, strlen(log));
		} else if(lktbf_edr) {
			lktbf_edr_FileWriter.Write(log, strlen(log));
		}

		if(lktbf_af) {
			/*매수*/
			if (qty > 0) {
				/* 신규 주문으로 (시그널이 와서) Buy 1호가에 대놓을때*/
				if(lktbf_af_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.01" && new_order) {
					log.Format("%c%c:%c%c:%c%c,lktb LONG NEW ORDER 00\n",now[0],now[1],now[2],now[3],now[4],now[5]);
					if(lktbf_af) {
						lktbf_af_FileWriter.Write(log, strlen(log));
					} else if(lktbf_edr) {
						lktbf_edr_FileWriter.Write(log, strlen(log));
					}

					Order('1', qty, hs.buy_hoga1_price, 0, "2", hs.code, "", "LKTBF"); // 신규주문내기
					log.Format("%c%c:%c%c:%c%c,lktb LONG NEW ORDER 11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
					if(lktbf_af) {
						lktbf_af_FileWriter.Write(log, strlen(log));
					} else if(lktbf_edr) {
						lktbf_edr_FileWriter.Write(log, strlen(log));
					}		

					m_ctrlOrderList.InsertString(0,log);
					lktbf_af_signal = false;
				} else {
					/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 buy1+1틱 호가에 대놓음 -> 즉시 매수*/
					if (str_diff_sell_buy_hoga != "0.01") {
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.buy_hoga1_price+lktbf_tick_value;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;
						log.Format("%c%c:%c%c:%c%c,lktb LONG empty urgent idx:%d 22\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}

						OrderItem temp_list[1000];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_af_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_af_pendingList[i];
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if(temp_list[i].strGubun == "2") {
								temp_qty += lktbf_af_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_af_pendingList[i].intQty;
							}
							if (temp_list[i].strGubun != "2") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb LONG is_opposite idx:%d 33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							for (int i = 0; i< temp_index; i++) {
								log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, lktbf_af_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);

								if(lktbf_af) {
									lktbf_af_FileWriter.Write(log, strlen(log));
								} else if(lktbf_edr) {
									lktbf_edr_FileWriter.Write(log, strlen(log));
								}
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty !=0 && lktbf_af_pendingListIndex == 0) {
								Order('1', qty, hs.buy_hoga1_price+lktbf_tick_value, 0, "2", hs.code,"", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							log.Format("%c%c:%c%c:%c%c,lktb LONG just modify idx:%d 44\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							float modify_price = hs.buy_hoga1_price+lktbf_tick_value;
							//if ((int)(modify_price * 1000)%10 == 9) {
							//	modify_price += 0.001;
							//}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb LONG just modify idx:%d 44-n55\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								//if ((int)(origin_price * 1000)%10 == 9) {
								//	origin_price += 0.001;
								//}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, lktbf_af_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								if(lktbf_af) {
									lktbf_af_FileWriter.Write(log, strlen(log));
								} else if(lktbf_edr) {
									lktbf_edr_FileWriter.Write(log, strlen(log));
								}
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}

						/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
						log.Format("●URGENT buy lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.buy_hoga1_price+lktbf_tick_value, qty );
						m_ctrlOrderList2.InsertString(0,log);
						//lktb_urgentFileWriter.Write(log,strlen(log));
						lktbf_af_signal = false;
						lktb_pre_orgordno == "";

					/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매수*/
					} else if (!lktb_urgent_mode && state == "bidish" && isSamePrice(hs.price,hs.sell_hoga1_price)) { //bidish and 현재가는 매도1호가
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.sell_hoga1_price;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;
					
						log.Format("%c%c:%c%c:%c%c,lktb LONG urgent idx:%d 55\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
					
						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_af_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_af_pendingList[i];
							if(temp_list[i].strGubun == "2") {
								temp_qty += lktbf_af_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_af_pendingList[i].intQty;
							}
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "2") {
								is_opposite = true;
							}
						}
						if (is_opposite) {

							log.Format("%c%c:%c%c:%c%c,lktb LONG urgent isopposite idx:%d 66\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}

							for (int i = 0; i< temp_index; i++) {
								log.Format("666 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s\n",i, lktbf_af_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno);
								if(lktbf_af) {
									lktbf_af_FileWriter.Write(log, strlen(log));
								} else if(lktbf_edr) {
									lktbf_edr_FileWriter.Write(log, strlen(log));
								}
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice,temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if (lktbf_af_pendingListIndex ==0)
								Order('1', qty, hs.sell_hoga1_price, 0, "2", hs.code, "", "LKTBF"); // pending 다 취소하고 신규주문내기
						} else {
							log.Format("%c%c:%c%c:%c%c,lktb LONG urgent justmodify idx:%d 77\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							float modify_price = hs.sell_hoga1_price;
							//if ((int)(modify_price * 1000)%10 == 9) {
							//	modify_price += 0.001;
							//}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								//if ((int)(origin_price * 1000)%10 == 9) {
								//	origin_price += 0.001;
								//}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}
						///*화면에 execute 상황을 기록하기 위한 코드 */
						log.Format("●URGENT buy lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.sell_hoga1_price, qty );
						m_ctrlOrderList2.InsertString(0,log);
						//lktb_urgentFileWriter.Write(log,strlen(log));
						lktbf_af_signal = false;
						lktb_pre_orgordno == "";

					} else if (!isSamePrice(lktbf_pre_price_float,hs.price) || boc_pre_state != state) {
						/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/
						log.Format("lktb LONG ORDER HOGA CHANGE 0 / usd_pre_price:%.3f, hs.price:%.3f, boc_pre_state:%s, state:%s", lktbf_pre_price_float, hs.price, boc_pre_state, state);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						log.Format("%c%c:%c%c:%c%c,lktb LONG change price idx:%d 88\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}

						m_ctrlOrderList.InsertString(0,log);

						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_af_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_af_pendingList[i];
							if(temp_list[i].strGubun == "2") {
								temp_qty += lktbf_af_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_af_pendingList[i].intQty;
							}
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "2") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb LONG change price opposite idx:%d 99\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							for (int i = 0; i< temp_index; i++) {
								log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s, qty:%d\n",i, lktbf_af_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								if(lktbf_af) {
									lktbf_af_FileWriter.Write(log, strlen(log));
								} else if(lktbf_edr) {
									lktbf_edr_FileWriter.Write(log, strlen(log));
								}
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty != 0 && lktbf_af_pendingListIndex==0) {
								Order('1', qty, hs.buy_hoga1_price,0, "2", hs.code, "","LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.buy_hoga1_price;
							//if ((int)(modify_price * 1000)%10 == 9) {
							//	modify_price += 0.001;
							//}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb LONG just change price idx:%d 1010\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								//if ((int)(origin_price * 1000)%10 == 9) {
								//	origin_price += 0.001;
								//}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code,temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}
					} else {
						log.Format("lktb LONG DIDNT CHANGE URGENT or HOGA!!");
						log.Format("%c%c:%c%c:%c%c,lktb LONG didn't change urgent or hoga!!",now[0],now[1],now[2],now[3],now[4],now[5]);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
						//m_ctrlOrderList.InsertString(0,log);
					}
				}
			/* 매도 */
			} else if (qty < 0) {
				log.Format("%c%c:%c%c:%c%c,lktb SHORT NEW ORDER new_order:%d diff:%s -00 idx:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], new_order, str_diff_sell_buy_hoga,lktbf_af_pendingListIndex);
				m_ctrlOrderList2.InsertString(0,log);
				if(lktbf_af) {
					lktbf_af_FileWriter.Write(log, strlen(log));
				} else if(lktbf_edr) {
					lktbf_edr_FileWriter.Write(log, strlen(log));
				}
				/* 신규 주문으로 (시그널이 와서) Sell 1호가에 대놓을때*/
				if (lktbf_af_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.01" && new_order) {
					log.Format("%c%c:%c%c:%c%c,lktb SHORT NEW ORDER -11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
					if(lktbf_af) {
						lktbf_af_FileWriter.Write(log, strlen(log));
					} else if(lktbf_edr) {
						lktbf_edr_FileWriter.Write(log, strlen(log));
					}
					Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "LKTBF"); // 신규주문내기
					m_ctrlOrderList.InsertString(0,log);
					lktbf_af_signal = false;
				} else {
				/*이미 매매가 하나 올라가 있을때*/
					/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 sell1-1틱 호가에 대놓음 -> 즉시 매수*/
					if (str_diff_sell_buy_hoga != "0.01") {
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.sell_hoga1_price-lktbf_tick_value;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;

						log.Format("%c%c:%c%c:%c%c,lktb SHORT empty urgent idx:%d -22\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}

						OrderItem temp_list[1000];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_af_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_af_pendingList[i];
							if(temp_list[i].strGubun == "1") {
								temp_qty += lktbf_af_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_af_pendingList[i].intQty;
							}
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "1") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb SHORT empty urgent opposite idx:%d -33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							for (int i = 0; i< temp_index; i++) {
								log.Format("3333 short i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, lktbf_af_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								if(lktbf_af) {
									lktbf_af_FileWriter.Write(log, strlen(log));
								} else if(lktbf_edr) {
									lktbf_edr_FileWriter.Write(log, strlen(log));
								}
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							
							}
							qty = qty+temp_qty;
							if (qty != 0 && lktbf_af_pendingListIndex==0) {
								Order('1', qty, hs.sell_hoga1_price-lktbf_tick_value, 0, "1", hs.code,"", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.sell_hoga1_price-lktbf_tick_value;
							//if ((int)(modify_price * 1000)%10 == 9) {
							//	modify_price += 0.001;
							//}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb SHORT empty urgent just modify idx:%d -44\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								//if ((int)(origin_price * 1000)%10 == 9) {
								//	origin_price += 0.001;
								//}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}

						/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
						log.Format("●URGENT sell lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.sell_hoga1_price, qty );
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
						m_ctrlOrderList2.InsertString(0,log);
						//lktb_urgentFileWriter.Write(log,strlen(log));
						lktbf_af_signal = false;
						lktb_pre_orgordno == "";

					/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매도*/
					}else if (!lktb_urgent_mode && state == "offerish" && isSamePrice(hs.price,hs.buy_hoga1_price)) { //bidish and 현재가는 매도1호가
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.sell_hoga1_price;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;

						log.Format("%c%c:%c%c:%c%c,lktb SHORT urgent idx:%d -55\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}

						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_af_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_af_pendingList[i];
							temp_qty += lktbf_af_pendingList[i].intQty;
							if (temp_list[i].strGubun != "1") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktbf SHORT urgent opposited idx:%d -66\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}

							for (int i = 0; i< temp_index; i++) {
								log.Format("%c%c:%c%c:%c%c,lktb SHORT urgent opposited idx:%d floatprc:%04.2f gubun:%s,orgno:%s -66~77\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex, temp_list[i].floatPrice,temp_list[i].strGubun,temp_list[i].orgordno);
								if(lktbf_af) {
									lktbf_af_FileWriter.Write(log, strlen(log));
								} else if(lktbf_edr) {
									lktbf_edr_FileWriter.Write(log, strlen(log));
								}
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty != 0 && lktbf_af_pendingListIndex ==0) {
								Order('1', qty, hs.buy_hoga1_price, 0, "1", hs.code, "", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.buy_hoga1_price;
							//if ((int)(modify_price * 1000)%10 == 9) {
							//	modify_price += 0.001;
							//}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb SHORT urgent just modify idx:%d -77\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								//if ((int)(origin_price * 1000)%10 == 9) {
								//	origin_price += 0.001;
								//}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}
						/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
						log.Format("●URGENT sell lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.sell_hoga1_price, qty );
						m_ctrlOrderList2.InsertString(0,log);
						lktbf_af_signal = false;
						lktb_pre_orgordno == "";

					} else if (!isSamePrice(lktbf_pre_price_float,hs.price) || boc_pre_state != state) {
						/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/

						log.Format("%c%c:%c%c:%c%c,lktb SHORT modify price idx:%d -88\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_af_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_af_pendingList[i];
							temp_qty += lktbf_af_pendingList[i].intQty;
							if (temp_list[i].strGubun != "1") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb SHORT modify price opposite idx:%d -99\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}
							for (int i = 0; i< temp_index; i++) {
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty != 0 && lktbf_af_pendingListIndex==0) {
								Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.sell_hoga1_price;
							//if ((int)(modify_price * 1000)%10 == 9) {
							//	modify_price += 0.001;
							//}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);
							log.Format("%c%c:%c%c:%c%c,lktb SHORT just modify price idx:%d -1010\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
							if(lktbf_af) {
								lktbf_af_FileWriter.Write(log, strlen(log));
							} else if(lktbf_edr) {
								lktbf_edr_FileWriter.Write(log, strlen(log));
							}

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								//if ((int)(origin_price * 1000)%10 == 9) {
								//	origin_price += 0.001;
								//}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}

						log.Format("lktb SHORT ORDER HOGA CHANGE QTY:%d, prc:%.3f",qty, hs.sell_hoga1_price);
						m_ctrlOrderList.InsertString(0,log);
					} else {
						log.Format("%c%c:%c%c:%c%c,lktb SHORT DIDNT CHANGE URGENT or HOGA!! idx:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_af_pendingListIndex);
						if(lktbf_af) {
							lktbf_af_FileWriter.Write(log, strlen(log));
						} else if(lktbf_edr) {
							lktbf_edr_FileWriter.Write(log, strlen(log));
						}
						m_ctrlOrderList.InsertString(0,log);
					}
				}
			}
		} else if(lktbf_edr) {
			/*매수*/
			if (qty > 0) {
				/* 신규 주문으로 (시그널이 와서) Buy 1호가에 대놓을때*/
				if(lktbf_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.01" && new_order) {
					log.Format("%c%c:%c%c:%c%c,lktb LONG NEW ORDER 00\n",now[0],now[1],now[2],now[3],now[4],now[5]);
					lktbf_edr_FileWriter.Write(log, strlen(log));

					Order('1', qty, hs.buy_hoga1_price, 0, "2", hs.code, "", "LKTBF"); // 신규주문내기
					log.Format("%c%c:%c%c:%c%c,lktb LONG NEW ORDER 11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
					lktbf_edr_FileWriter.Write(log, strlen(log));

					m_ctrlOrderList.InsertString(0,log);
					lktbf_edr_signal = false;
				} else {
					/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 buy1+1틱 호가에 대놓음 -> 즉시 매수*/
					if (str_diff_sell_buy_hoga != "0.01") {
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.buy_hoga1_price+lktbf_tick_value;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;
						log.Format("%c%c:%c%c:%c%c,lktb LONG empty urgent idx:%d 22\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));

						OrderItem temp_list[1000];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_edr_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_edr_pendingList[i];
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if(temp_list[i].strGubun == "2") {
								temp_qty += lktbf_edr_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_edr_pendingList[i].intQty;
							}
							if (temp_list[i].strGubun != "2") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb LONG is_opposite idx:%d 33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							lktbf_edr_FileWriter.Write(log, strlen(log));
							for (int i = 0; i< temp_index; i++) {
								log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s, qty:%d\n",i, lktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								lktbf_edr_FileWriter.Write(log, strlen(log));
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty !=0 && lktbf_edr_pendingListIndex == 0) {
								Order('1', qty, hs.buy_hoga1_price+lktbf_tick_value, 0, "2", hs.code,"", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							log.Format("%c%c:%c%c:%c%c,lktb LONG just modify idx:%d 44\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							lktbf_edr_FileWriter.Write(log, strlen(log));
							float modify_price = hs.buy_hoga1_price+lktbf_tick_value;
							if ((int)(modify_price * 1000)%10 == 9) {
								modify_price += 0.001;
							}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb LONG just modify idx:%d 44-n55\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								if ((int)(origin_price * 1000)%10 == 9) {
									origin_price += 0.001;
								}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s, qty:%d\n",i, lktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								lktbf_edr_FileWriter.Write(log, strlen(log));
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}

						/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
						log.Format("●URGENT buy lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.buy_hoga1_price+lktbf_tick_value, qty );
						m_ctrlOrderList2.InsertString(0,log);
						lktbf_edr_FileWriter.Write(log,strlen(log));
						lktbf_edr_signal = false;
						lktb_pre_orgordno == "";

					/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매수*/
					} else if (!lktb_urgent_mode && state == "bidish" && isSamePrice(hs.price,hs.sell_hoga1_price)) { //bidish and 현재가는 매도1호가
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.sell_hoga1_price;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;
					
						log.Format("%c%c:%c%c:%c%c,lktb LONG urgent idx:%d 55\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));
					
						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_edr_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_edr_pendingList[i];
							if(temp_list[i].strGubun == "2") {
								temp_qty += lktbf_edr_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_edr_pendingList[i].intQty;
							}
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "2") {
								is_opposite = true;
							}
						}
						if (is_opposite) {

							log.Format("%c%c:%c%c:%c%c,lktb LONG urgent isopposite idx:%d 66\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								log.Format("666 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s\n",i, lktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno);
								lktbf_edr_FileWriter.Write(log, strlen(log));
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice,temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if (lktbf_edr_pendingListIndex ==0)
								Order('1', qty, hs.sell_hoga1_price, 0, "2", hs.code, "", "LKTBF"); // pending 다 취소하고 신규주문내기
						} else {
							log.Format("%c%c:%c%c:%c%c,lktb LONG urgent justmodify idx:%d 77\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));
							float modify_price = hs.sell_hoga1_price;
							if ((int)(modify_price * 1000)%10 == 9) {
								modify_price += 0.001;
							}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								if ((int)(origin_price * 1000)%10 == 9) {
									origin_price += 0.001;
								}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}
						///*화면에 execute 상황을 기록하기 위한 코드 */
						log.Format("●URGENT buy lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.sell_hoga1_price, qty );
						m_ctrlOrderList2.InsertString(0,log);
						lktbf_edr_FileWriter.Write(log,strlen(log));
						lktbf_edr_signal = false;
						lktb_pre_orgordno == "";

					} else if (!isSamePrice(lktbf_pre_price_float,hs.price) || boc_pre_state != state) {
						/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/
						log.Format("lktb LONG ORDER HOGA CHANGE 0 / lktbf_pre_price:%.3f, hs.price:%.3f, boc_pre_state:%s, state:%s", lktbf_pre_price_float, hs.price, boc_pre_state, state);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						log.Format("%c%c:%c%c:%c%c,lktb LONG change price idx:%d 88\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));

						m_ctrlOrderList.InsertString(0,log);

						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_edr_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_edr_pendingList[i];
							if(temp_list[i].strGubun == "2") {
								temp_qty += lktbf_edr_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_edr_pendingList[i].intQty;
							}
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "2") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb LONG change price opposite idx:%d 99\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));
							for (int i = 0; i< temp_index; i++) {
								log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, lktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								lktbf_edr_FileWriter.Write(log, strlen(log));
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty != 0 && lktbf_edr_pendingListIndex==0) {
								Order('1', qty, hs.buy_hoga1_price,0, "2", hs.code, "","LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.buy_hoga1_price;
							if ((int)(modify_price * 1000)%10 == 9) {
								modify_price += 0.001;
							}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb LONG just change price idx:%d 1010\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								if ((int)(origin_price * 1000)%10 == 9) {
									origin_price += 0.001;
								}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code,temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}
					} else {
						log.Format("lktb LONG DIDNT CHANGE URGENT or HOGA!!");
						log.Format("%c%c:%c%c:%c%c,lktb LONG didn't change urgent or hoga!!",now[0],now[1],now[2],now[3],now[4],now[5]);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						//m_ctrlOrderList.InsertString(0,log);
					}
				}
			/* 매도 */
			} else if (qty < 0) {
				log.Format("%c%c:%c%c:%c%c,lktb SHORT NEW ORDER new_order:%d diff:%s -00 idx:%d\n",now[0],now[1],now[2],now[3],now[4],now[5], new_order, str_diff_sell_buy_hoga,lktbf_edr_pendingListIndex);
				m_ctrlOrderList2.InsertString(0,log);
				lktbf_edr_FileWriter.Write(log, strlen(log));
				/* 신규 주문으로 (시그널이 와서) Sell 1호가에 대놓을때*/
				if (lktbf_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.01" && new_order) {
					log.Format("%c%c:%c%c:%c%c,lktb SHORT NEW ORDER -11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
					lktbf_edr_FileWriter.Write(log, strlen(log));
					Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "LKTBF"); // 신규주문내기
					m_ctrlOrderList.InsertString(0,log);
					lktbf_edr_signal = false;
				} else {
				/*이미 매매가 하나 올라가 있을때*/
					/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 sell1-1틱 호가에 대놓음 -> 즉시 매수*/
					if (str_diff_sell_buy_hoga != "0.01") {
						lktb_urgent_begintime = hs.time;
						lktb_urgent_beginprice = hs.sell_hoga1_price-lktbf_tick_value;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;

						log.Format("%c%c:%c%c:%c%c,lktb SHORT empty urgent idx:%d -22\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						
						OrderItem temp_list[1000];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_edr_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_edr_pendingList[i];
							if(temp_list[i].strGubun == "1") {
								temp_qty += lktbf_edr_pendingList[i].intQty;
							} else {
								temp_qty -= lktbf_edr_pendingList[i].intQty;
							}
							//temp_qty += lktb_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "1") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb SHORT empty urgent opposite idx:%d -33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
							lktbf_edr_FileWriter.Write(log, strlen(log));
							for (int i = 0; i< temp_index; i++) {
								log.Format("3333 short i:%d, fprc:%04.2f, gubun:%s, orgordno:%s, qty:%d\n",i, lktbf_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
								lktbf_edr_FileWriter.Write(log, strlen(log));
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							
							}
							qty = qty+temp_qty;
							if (qty != 0 && lktbf_edr_pendingListIndex==0) {
								Order('1', qty, hs.sell_hoga1_price-lktbf_tick_value, 0, "1", hs.code,"", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.sell_hoga1_price-lktbf_tick_value;
							if ((int)(modify_price * 1000)%10 == 9) {
								modify_price += 0.001;
							}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb SHORT empty urgent just modify idx:%d -44\n",now[0],now[1],now[2],now[3],now[4],now[5], lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								if ((int)(origin_price * 1000)%10 == 9) {
									origin_price += 0.001;
								}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}

						/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
						log.Format("●URGENT sell lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.sell_hoga1_price, qty );
						lktbf_edr_FileWriter.Write(log, strlen(log));
						m_ctrlOrderList2.InsertString(0,log);
						lktbf_edr_FileWriter.Write(log,strlen(log));
						lktbf_edr_signal = false;
						lktb_pre_orgordno == "";

					/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매도*/
					}else if (!lktb_urgent_mode && state == "offerish" && isSamePrice(hs.price,hs.buy_hoga1_price)) { //bidish and 현재가는 매도1호가
						lktb_urgent_begintime = hs.time;
						//lktb_urgent_beginprice = hs.sell_hoga1_price;
						lktb_urgent_mode = true;
						lktb_urgent_type = state;

						log.Format("%c%c:%c%c:%c%c,lktb SHORT urgent idx:%d -55\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));

						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_edr_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_edr_pendingList[i];
							temp_qty += lktbf_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "1") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktbf SHORT urgent opposited idx:%d -66\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								log.Format("%c%c:%c%c:%c%c,lktb SHORT urgent opposited idx:%d floatprc:%04.2f gubun:%s,orgno:%s -66~77\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex, temp_list[i].floatPrice,temp_list[i].strGubun,temp_list[i].orgordno);
								lktbf_edr_FileWriter.Write(log, strlen(log));
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty != 0 && lktbf_edr_pendingListIndex ==0) {
								Order('1', qty, hs.buy_hoga1_price, 0, "1", hs.code, "", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.buy_hoga1_price;
							if ((int)(modify_price * 1000)%10 == 9) {
								modify_price += 0.001;
							}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);

							log.Format("%c%c:%c%c:%c%c,lktb SHORT urgent just modify idx:%d -77\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								if ((int)(origin_price * 1000)%10 == 9) {
									origin_price += 0.001;
								}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}
						/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
						log.Format("●URGENT sell lktb type:%s begin:%s prc:%.3f, qty:%d\n", lktb_urgent_type, lktb_urgent_begintime, hs.sell_hoga1_price, qty );
						m_ctrlOrderList2.InsertString(0,log);
						lktbf_edr_signal = false;
						lktb_pre_orgordno == "";

					} else if (!isSamePrice(lktbf_pre_price_float,hs.price) || boc_pre_state != state) {
						/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/

						log.Format("%c%c:%c%c:%c%c,lktb SHORT modify price idx:%d -88\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						OrderItem temp_list[100];
						bool is_opposite = false;
						int temp_qty = 0;
						int temp_index = lktbf_edr_pendingListIndex;
						for (int i = 0; i< temp_index; i++) {
							temp_list[i] = lktbf_edr_pendingList[i];
							temp_qty += lktbf_edr_pendingList[i].intQty;
							if (temp_list[i].strGubun != "1") {
								is_opposite = true;
							}
						}
						if (is_opposite) {
							log.Format("%c%c:%c%c:%c%c,lktb SHORT modify price opposite idx:%d -99\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));
							for (int i = 0; i< temp_index; i++) {
								Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "LKTBF");
							}
							qty = qty+temp_qty;
							if(qty != 0 && lktbf_edr_pendingListIndex==0) {
								Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "LKTBF"); // pending 다 취소하고 신규주문내기
							}
						} else {
							float modify_price = hs.sell_hoga1_price;
							if ((int)(modify_price * 1000)%10 == 9) {
								modify_price += 0.001;
							}
							CString str_modify_price;
							str_modify_price.Format("%04.2f",modify_price);
							log.Format("%c%c:%c%c:%c%c,lktb SHORT just modify price idx:%d -1010\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
							lktbf_edr_FileWriter.Write(log, strlen(log));

							for (int i = 0; i< temp_index; i++) {
								float origin_price = temp_list[i].floatPrice;
								if ((int)(origin_price * 1000)%10 == 9) {
									origin_price += 0.001;
								}
								CString str_origin_price;
								str_origin_price.Format("%04.2f",origin_price);
							
								log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
								if (str_modify_price != str_origin_price) {
									Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "LKTBF"); // 그냥 주문수정
								}
							}
						}

						log.Format("lktb SHORT ORDER HOGA CHANGE QTY:%d, prc:%.3f",qty, hs.sell_hoga1_price);
						m_ctrlOrderList.InsertString(0,log);
					} else {
						log.Format("%c%c:%c%c:%c%c,lktb SHORT DIDNT CHANGE URGENT or HOGA!! idx:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],lktbf_edr_pendingListIndex);
						lktbf_edr_FileWriter.Write(log, strlen(log));
						//m_ctrlOrderList.InsertString(0,log);
					}
				}
			}
		} else {

		}

	} else if (jongmok == "USD") {
		/* float 값 보정*/
		float diff_sell_buy_hoga = hs.sell_hoga1_price - hs.buy_hoga1_price;
		if ((int)(diff_sell_buy_hoga * 1000)%10 == 9) {
			diff_sell_buy_hoga += 0.001;
		}
		CString str_diff_sell_buy_hoga;
		str_diff_sell_buy_hoga.Format("%04.2f",diff_sell_buy_hoga);

		log.Format("%c%c:%c%c:%c%c, EXECUTE USD diffhoga:%s, %.3f,%.3f, pending_index:%d qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],str_diff_sell_buy_hoga,hs.sell_hoga1_price,hs.buy_hoga1_price,usd_edr_pendingListIndex, qty);
		usd_edr_FileWriter.Write(log, strlen(log));

		/*매수*/
		if (qty > 0) {
			/* 신규 주문으로 (시그널이 와서) Buy 1호가에 대놓을때*/
			//if(usd_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.10" && new_order) {
			if(usd_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.10" && new_order) {
				log.Format("%c%c:%c%c:%c%c,usd LONG NEW ORDER 00\n",now[0],now[1],now[2],now[3],now[4],now[5]);
				usd_edr_FileWriter.Write(log, strlen(log));

				Order('1', qty, hs.buy_hoga1_price, 0, "2", hs.code, "", "USD"); // 신규주문내기
				log.Format("%c%c:%c%c:%c%c,usd LONG NEW ORDER 11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
				usd_edr_FileWriter.Write(log, strlen(log));

				m_ctrlOrderList.InsertString(0,log);
				usd_af_signal = false;
			} else {
				/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 buy1+1틱 호가에 대놓음 -> 즉시 매수*/
				if (str_diff_sell_buy_hoga != "0.10") {
					usd_urgent_begintime = hs.time;
					//usd_urgent_beginprice = hs.buy_hoga1_price+usd_tick_value;
					usd_urgent_mode = true;
					usd_urgent_type = state;
					log.Format("%c%c:%c%c:%c%c,usd LONG empty urgent idx:%d 22\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));

					OrderItem temp_list[1000];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = usd_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = usd_edr_pendingList[i];
						//temp_qty += usd_edr_pendingList[i].intQty;
						if(temp_list[i].strGubun == "2") {
							temp_qty += usd_edr_pendingList[i].intQty;
						} else {
							temp_qty -= usd_edr_pendingList[i].intQty;
						}
						if (temp_list[i].strGubun != "2") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,usd LONG is_opposite idx:%d 33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						usd_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, usd_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							usd_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "USD");
						}
						qty = qty+temp_qty;
						if(qty !=0 && usd_edr_pendingListIndex == 0) {
							Order('1', qty, hs.buy_hoga1_price+usd_tick_value, 0, "2", hs.code,"", "USD"); // pending 다 취소하고 신규주문내기
						}
					} else {
						log.Format("%c%c:%c%c:%c%c,usd LONG just modify idx:%d 44\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						usd_edr_FileWriter.Write(log, strlen(log));
						float modify_price = hs.buy_hoga1_price+usd_tick_value;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,usd LONG just modify idx:%d 44-n55\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						usd_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, usd_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							usd_edr_FileWriter.Write(log, strlen(log));
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "USD"); // 그냥 주문수정
							}
						}
					}

					/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
					log.Format("●URGENT buy usd type:%s begin:%s prc:%.3f, qty:%d\n", usd_urgent_type, usd_urgent_begintime, hs.buy_hoga1_price+usd_tick_value, qty );
					m_ctrlOrderList2.InsertString(0,log);
					//usd_edr_FileWriter.Write(log,strlen(log));
					usd_af_signal = false;
					usd_pre_orgordno == "";

				/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매수*/
				} else if (!usd_urgent_mode && state == "bidish" && isSamePrice(hs.price,hs.sell_hoga1_price)) { //bidish and 현재가는 매도1호가
					usd_urgent_begintime = hs.time;
					//usd_urgent_beginprice = hs.sell_hoga1_price;
					usd_urgent_mode = true;
					usd_urgent_type = state;
					
					log.Format("%c%c:%c%c:%c%c,usd LONG urgent idx:%d 55\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));
					
					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = usd_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = usd_edr_pendingList[i];
						if(temp_list[i].strGubun == "2") {
							temp_qty += usd_edr_pendingList[i].intQty;
						} else {
							temp_qty -= usd_edr_pendingList[i].intQty;
						}
						//temp_qty += usd_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "2") {
							is_opposite = true;
						}
					}
					if (is_opposite) {

						log.Format("%c%c:%c%c:%c%c,usd LONG urgent isopposite idx:%d 66\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							log.Format("666 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s\n",i, usd_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno);
							usd_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice,temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "USD");
						}
						qty = qty+temp_qty;
						if (usd_edr_pendingListIndex ==0)
							Order('1', qty, hs.sell_hoga1_price, 0, "2", hs.code, "", "USD"); // pending 다 취소하고 신규주문내기
					} else {
						log.Format("%c%c:%c%c:%c%c,usd LONG urgent justmodify idx:%d 77\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));
						float modify_price = hs.sell_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code, temp_list[i].orgordno, "USD"); // 그냥 주문수정
							}
						}
					}
					///*화면에 execute 상황을 기록하기 위한 코드 */
					log.Format("●URGENT buy usd type:%s begin:%s prc:%.3f, qty:%d\n", usd_urgent_type, usd_urgent_begintime, hs.sell_hoga1_price, qty );
					m_ctrlOrderList2.InsertString(0,log);
					//usd_edr_FileWriter.Write(log,strlen(log));
					usd_af_signal = false;
					usd_pre_orgordno == "";

				} else if (!isSamePrice(usd_pre_price_float,hs.price) || boc_pre_state != state) {
					/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/
					log.Format("usd LONG ORDER HOGA CHANGE 0 / usd_pre_price:%.3f, hs.price:%.3f, boc_pre_state:%s, state:%s", usd_pre_price_float, hs.price, boc_pre_state, state);
					usd_edr_FileWriter.Write(log, strlen(log));
					log.Format("%c%c:%c%c:%c%c,usd LONG change price idx:%d 88\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));

					m_ctrlOrderList.InsertString(0,log);

					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = usd_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = usd_edr_pendingList[i];
						if(temp_list[i].strGubun == "2") {
							temp_qty += usd_edr_pendingList[i].intQty;
						} else {
							temp_qty -= usd_edr_pendingList[i].intQty;
						}
						//temp_qty += usd_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "2") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,usd LONG change price opposite idx:%d 99\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							log.Format("3333 long i:%d, fprc:%04.2f, gubun:%s, orgordno:%s qty:%d\n",i, usd_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							usd_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "USD");
						}
						qty = qty+temp_qty;
						if(qty != 0 && usd_edr_pendingListIndex==0) {
							Order('1', qty, hs.buy_hoga1_price,0, "2", hs.code, "","USD"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.buy_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,usd LONG just change price to %s idx:%d 1010\n",now[0],now[1],now[2],now[3],now[4],now[5], str_modify_price, usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "2", hs.code,temp_list[i].orgordno, "USD"); // 그냥 주문수정
							}
						}
					}
				} else {
					log.Format("usd LONG DIDNT CHANGE URGENT or HOGA!!\n");
					log.Format("%c%c:%c%c:%c%c,usd LONG didn't change urgent or hoga!!",now[0],now[1],now[2],now[3],now[4],now[5]);
					usd_edr_FileWriter.Write(log, strlen(log));
					//m_ctrlOrderList.InsertString(0,log);
				}
			}
		/* 매도 */
		} else if (qty < 0) {
			/* 신규 주문으로 (시그널이 와서) Sell 1호가에 대놓을때*/
			if (usd_edr_pendingListIndex == 0 && str_diff_sell_buy_hoga == "0.10" && new_order) {
				log.Format("%c%c:%c%c:%c%c,usd SHORT NEW ORDER -11\n",now[0],now[1],now[2],now[3],now[4],now[5]);
				usd_edr_FileWriter.Write(log, strlen(log));
				Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "USD"); // 신규주문내기
				m_ctrlOrderList.InsertString(0,log);
				usd_af_signal = false;
			} else {
			/*이미 매매가 하나 올라가 있을때*/
				/* Buy1호가와 Sell1호가 사이가 비었을 경우 URGENT 로 전환하여 sell1-1틱 호가에 대놓음 -> 즉시 매수*/
				if (str_diff_sell_buy_hoga != "0.10") {
					usd_urgent_begintime = hs.time;
					//usd_urgent_beginprice = hs.sell_hoga1_price-usd_tick_value;
					usd_urgent_mode = true;
					usd_urgent_type = state;

					log.Format("%c%c:%c%c:%c%c,usd SHORT empty urgent idx:%d -22\n",now[0],now[1],now[2],now[3],now[4],now[5], usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));

					OrderItem temp_list[1000];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = usd_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = usd_edr_pendingList[i];
						if(temp_list[i].strGubun == "1") {
							temp_qty += usd_edr_pendingList[i].intQty;
						} else {
							temp_qty -= usd_edr_pendingList[i].intQty;
						}
						//temp_qty += usd_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "1") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,usd SHORT empty urgent opposite idx:%d -33\n",now[0],now[1],now[2],now[3],now[4],now[5],temp_index);
						usd_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							log.Format("3333 short i:%d, fprc:%04.2f, gubun:%s, orgordno:%s, qty:%d\n",i, usd_edr_pendingList[i].floatPrice, temp_list[i].strGubun, temp_list[i].orgordno, temp_list[i].intQty);
							usd_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "USD");
							
						}
						qty = qty+temp_qty;
						if (qty != 0 && usd_edr_pendingListIndex==0) {
							Order('1', qty, hs.sell_hoga1_price-usd_tick_value, 0, "1", hs.code,"", "USD"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.sell_hoga1_price-usd_tick_value;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,usd SHORT empty urgent just modify idx:%d -44\n",now[0],now[1],now[2],now[3],now[4],now[5], usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "USD"); // 그냥 주문수정
							}
						}
					}

					/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
					log.Format("●URGENT sell usd type:%s begin:%s prc:%.3f, qty:%d\n", usd_urgent_type, usd_urgent_begintime, hs.sell_hoga1_price, qty );
					m_ctrlOrderList2.InsertString(0,log);
					//usd_edr_FileWriter.Write(log,strlen(log));
					usd_af_signal = false;
					usd_pre_orgordno == "";

				/*URGENT 로 전환하여 buy1 호가에 대놓음 -> 즉시 매도*/
				}else if (!usd_urgent_mode && state == "offerish" && isSamePrice(hs.price,hs.buy_hoga1_price)) { //bidish and 현재가는 매도1호가
					usd_urgent_begintime = hs.time;
					//usd_urgent_beginprice = hs.sell_hoga1_price;
					usd_urgent_mode = true;
					usd_urgent_type = state;

					log.Format("%c%c:%c%c:%c%c,usd SHORT urgent idx:%d -55\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));

					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = usd_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = usd_edr_pendingList[i];
						temp_qty += usd_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "1") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,usd SHORT urgent opposited idx:%d -66\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							log.Format("%c%c:%c%c:%c%c,usd SHORT urgent opposited idx:%d floatprc:%04.2f gubun:%s,orgno:%s -66~77\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex, temp_list[i].floatPrice,temp_list[i].strGubun,temp_list[i].orgordno);
							usd_edr_FileWriter.Write(log, strlen(log));
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice, temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "USD");
						}
						qty = qty+temp_qty;
						if(qty != 0 && usd_edr_pendingListIndex ==0) {
							Order('1', qty, hs.buy_hoga1_price, 0, "1", hs.code, "", "USD"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.buy_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);

						log.Format("%c%c:%c%c:%c%c,usd SHORT urgent just modify idx:%d -77\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "USD"); // 그냥 주문수정
							}
						}
					}
					/*화면과 파일에 urgent execute 상황을 기록하기 위한 코드.*/
					log.Format("●URGENT sell usd type:%s begin:%s prc:%.3f, qty:%d\n", usd_urgent_type, usd_urgent_begintime, hs.sell_hoga1_price, qty );
					m_ctrlOrderList2.InsertString(0,log);
					usd_af_signal = false;
					usd_pre_orgordno == "";

				} else if (!isSamePrice(usd_pre_price_float,hs.price) || boc_pre_state != state) {
					/*urgent는 아니지만 상태가 바뀌거나 현재가가 바뀔때 호가 추종*/

					log.Format("%c%c:%c%c:%c%c,usd SHORT modify price idx:%d -88\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));
					OrderItem temp_list[100];
					bool is_opposite = false;
					int temp_qty = 0;
					int temp_index = usd_edr_pendingListIndex;
					for (int i = 0; i< temp_index; i++) {
						temp_list[i] = usd_edr_pendingList[i];
						temp_qty += usd_edr_pendingList[i].intQty;
						if (temp_list[i].strGubun != "1") {
							is_opposite = true;
						}
					}
					if (is_opposite) {
						log.Format("%c%c:%c%c:%c%c,usd SHORT modify price opposite idx:%d -99\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));
						for (int i = 0; i< temp_index; i++) {
							Order('3', (temp_list[i].intQty>0)? temp_list[i].intQty:-temp_list[i].intQty, temp_list[i].floatPrice,temp_list[i].floatPrice, temp_list[i].strGubun, hs.code, temp_list[i].orgordno, "USD");
						}
						qty = qty+temp_qty;
						if(qty != 0 && usd_edr_pendingListIndex==0) {
							Order('1', qty, hs.sell_hoga1_price, 0, "1", hs.code, "", "USD"); // pending 다 취소하고 신규주문내기
						}
					} else {
						float modify_price = hs.sell_hoga1_price;
						if ((int)(modify_price * 1000)%10 == 9) {
							modify_price += 0.001;
						}
						CString str_modify_price;
						str_modify_price.Format("%04.2f",modify_price);
						log.Format("%c%c:%c%c:%c%c,usd SHORT just modify price idx:%d -1010\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
						usd_edr_FileWriter.Write(log, strlen(log));

						for (int i = 0; i< temp_index; i++) {
							float origin_price = temp_list[i].floatPrice;
							if ((int)(origin_price * 1000)%10 == 9) {
								origin_price += 0.001;
							}
							CString str_origin_price;
							str_origin_price.Format("%04.2f",origin_price);
							
							log.Format("%c%c:%c%c:%c%c,orig_prc:%s,modify_price_prc:%s \n", now[0],now[1],now[2],now[3],now[4],now[5],str_origin_price,str_modify_price);
							if (str_modify_price != str_origin_price) {
								Order('2', temp_list[i].intQty, modify_price, origin_price, "1", hs.code, temp_list[i].orgordno, "USD"); // 그냥 주문수정
							}
						}
					}

					log.Format("%c%c:%c%c:%c%c,usd SHORT ORDER HOGA CHANGE QTY:%d, prc:%.3f",now[0],now[1],now[2],now[3],now[4],now[5],qty, hs.sell_hoga1_price);
					m_ctrlOrderList.InsertString(0,log);
				} else {
					log.Format("%c%c:%c%c:%c%c,usd SHORT DIDNT CHANGE URGENT or HOGA!! idx:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex);
					usd_edr_FileWriter.Write(log, strlen(log));
					m_ctrlOrderList.InsertString(0,log);
				}
			}
		} else {

		}

	} else {
	}

	/*화면에 execute 되는 종목, 시간, 가격을 표시하기 위한 코드*/
	//CString tmp;
	//tmp.Format("%s / time : %d, price : %.2f", jongmok, hs.time, hs.price);
	//m_ctrlOrderList.InsertString(0,tmp);
}

/*vwap 을 계산한다*/
void CAPISampleDlg::setVwap(CString jongmok, struct HogaSise hs) {

	string now = getTime();
	SYSTEMTIME lt;
	GetLocalTime(&lt);
	if (jongmok == "KTBF") {
		if(hs.volume >= usd_vol_bin) {
			ktb_volume[ktb_vwap_num] = hs.volume;
			ktb_vwap[ktb_vwap_num] = hs.price;
			
			if (ktbf_edr) {
				CString strLog;
				strLog.Format("%c%c:%c%c:%c%c, usd vol / %02d:%02d:%d.%d  / %d / %.3f \n",now[0],now[1],now[2],now[3],now[4],now[5], lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, usd_volume[usd_vwap_num], usd_vwap[usd_vwap_num]);
				m_ctrlOrderList2.InsertString(0,strLog);
			}
			//usd_vwapFileWriter.Write(strLog, strlen(strLog));

			ktb_vwap_num += 1;
		} else {
			ktb_vol_sum += hs.volume;
			ktb_prc_sum += hs.price * hs.volume;
			if (ktb_vol_sum >= ktb_vol_bin) {
				ktb_vwap[ktb_vwap_num] = ktb_prc_sum / ktb_vol_sum;

				CString strLog;
				strLog.Format("%c%c:%c%c:%c%c, !ktbf vol/ %02d:%02d:%02d.%d / %d / %.3f \n",now[0],now[1],now[2],now[3],now[4],now[5],lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, usd_vol_sum, usd_vwap[usd_vwap_num]);
				m_ctrlOrderList2.InsertString(0,strLog);
				//usd_vwapFileWriter.Write(strLog, strlen(strLog));

				ktb_vwap_num += 1;
				ktb_vol_sum = 0;
				ktb_prc_sum = 0;
			}
		}
	} else if (jongmok == "LKTBF") {
		if(hs.volume >= lktb_vol_bin) {
			lktb_volume[lktb_vwap_num] = hs.volume;
			lktb_vwap[lktb_vwap_num] = hs.price;
			
			CString strLog;
			strLog.Format("lktb / %02d:%02d:%d.%d  / %d / %.3f \n",lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, lktb_volume[lktb_vwap_num], lktb_vwap[lktb_vwap_num]);
			//lktb_vwapFileWriter.Write(strLog, strlen(strLog));

			lktb_vwap_num += 1;
		} else {
			lktb_vol_sum += hs.volume;
			lktb_prc_sum += hs.price * hs.volume;
			if (lktb_vol_sum >= lktb_vol_bin) {
				lktb_vwap[lktb_vwap_num] = lktb_prc_sum / lktb_vol_sum;

				CString strLog;
				strLog.Format("lktb / %02d:%02d:%02d.%d / %d / %.3f \n",lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, lktb_vol_sum, lktb_vwap[lktb_vwap_num]);
				//lktb_vwapFileWriter.Write(strLog, strlen(strLog));

				lktb_vwap_num += 1;
				lktb_vol_sum = 0;
				lktb_prc_sum = 0;
			}
			//} else if (final) {
			//	vwap[j_vwap_num] = prc_sum / vol_sum;
			//}
		}
	} else if (jongmok == "USD") {
		if(hs.volume >= usd_vol_bin) {
			usd_volume[usd_vwap_num] = hs.volume;
			usd_vwap[usd_vwap_num] = hs.price;
			
			if (usd_edr) {
				CString strLog;
				strLog.Format("%c%c:%c%c:%c%c, usd vol / %02d:%02d:%d.%d  / %d / %.3f \n",now[0],now[1],now[2],now[3],now[4],now[5], lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, usd_volume[usd_vwap_num], usd_vwap[usd_vwap_num]);
				m_ctrlOrderList2.InsertString(0,strLog);
			}
			//usd_vwapFileWriter.Write(strLog, strlen(strLog));

			usd_vwap_num += 1;
		} else {
			usd_vol_sum += hs.volume;
			usd_prc_sum += hs.price * hs.volume;
			if (usd_vol_sum >= usd_vol_bin) {
				usd_vwap[usd_vwap_num] = usd_prc_sum / usd_vol_sum;

				CString strLog;
				strLog.Format("%c%c:%c%c:%c%c, !usd vol/ %02d:%02d:%02d.%d / %d / %.3f \n",now[0],now[1],now[2],now[3],now[4],now[5],lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, usd_vol_sum, usd_vwap[usd_vwap_num]);
				m_ctrlOrderList2.InsertString(0,strLog);
				//usd_vwapFileWriter.Write(strLog, strlen(strLog));

				usd_vwap_num += 1;
				usd_vol_sum = 0;
				usd_prc_sum = 0;
			}
			//} else if (final) {
			//	vwap[j_vwap_num] = prc_sum / vol_sum;
			//}
		}
	}
}

/* 옛날 vwap */
//void CAPISampleDlg::setVwap(struct HogaSise hs) {
//
//
//	SYSTEMTIME lt;
//	GetLocalTime(&lt);
//
//	if(hs.volume >= vol_bin) {
//		bin_num= hs.volume / vol_bin;		
//
//		for (int mv = vwap_num; mv < vwap_num + bin_num; mv++) {
//			vwap[mv] = hs.price;
//			
//			CString strLog;
//			strLog.Format("%02d:%02d:%d.%d %d %f ! \n",lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, hs.volume, vwap[mv]);
//			ktb_vwapFileWriter.Write(strLog, strlen(strLog));
//
//			tmp = mv+1;
//		}
//		vwap_num = tmp;
//	} else {
//		vol_sum += hs.volume;
//		prc_sum += hs.price * hs.volume;
//		if (vol_sum >= vol_bin) {
//			bin_num = vol_sum / vol_bin;
//
//			for (int mv = vwap_num; mv < vwap_num + bin_num; mv++) {
//				vwap[mv] = prc_sum/vol_sum;
//
//				CString strLog;
//				strLog.Format("%02d:%02d:%02d.%d %d %f !! \n",lt.wHour, lt.wMinute, lt.wSecond, lt.wMilliseconds, vol_sum, vwap[mv]);
//				ktb_vwapFileWriter.Write(strLog, strlen(strLog));
//
//				tmp = mv+1;
//			}
//			vwap_num = tmp;
//			vol_sum = 0;
//			prc_sum = 0;
//		}
//		//} else if (final) {
//		//	vwap[j_vwap_num] = prc_sum / vol_sum;
//		//}
//	}
//}


int calTargetQuantity(float tick_diff_now){ 
	int target_qty = 0;
	float abs_diff_now = (tick_diff_now>0)? tick_diff_now : -tick_diff_now;

	if (abs_diff_now <= tick_cross_margin) {
	} else if(abs_diff_now > tick_cross_margin) {
		float target_qty_raw = max_qty * tick_diff_now / tick_diff_of_max_qty;
		target_qty = (target_qty_raw < max_qty)? target_qty_raw : max_qty;
	} else if (tick_diff_now < -tick_cross_margin){ 
		float target_qty_raw = max_qty * tick_diff_now / tick_diff_of_max_qty;
		target_qty = (-target_qty_raw < max_qty)? target_qty_raw : -max_qty;
	}
	return target_qty;
}


/* 각 종목별 시세를 파일에 기록하는 함수 */ 
//void CAPISampleDlg::logSise(struct HogaSise hs) {
//	CString csText = "------------------------------------------\n";
//	ktb_siseFileWriter.Write(csText, strlen(csText));
//
//	CString strLog;
//
//	strLog.Format("time: %d\n",hs.time);
//	ktb_siseFileWriter.Write(strLog, strlen(strLog));
//
//	strLog.Format("type: %s\n",hs.type);
//	ktb_siseFileWriter.Write(strLog, strlen(strLog));
//
//	strLog.Format("price: %f\n",hs.price);
//	ktb_siseFileWriter.Write(strLog, strlen(strLog));
//
//	strLog.Format("vol: %d\n",hs.volume);
//	ktb_siseFileWriter.Write(strLog, strlen(strLog));
//
//	if (hs.sell_or_buy == 1) {
//		strLog = "sell or buy: sell\n";
//	} else if (hs.sell_or_buy == 2) {
//		strLog = "sell or buy: buy\n";
//	} else {
//		strLog = "begin\n";
//	}
//	ktb_siseFileWriter.Write(strLog, strlen(strLog));
//}

void CAPISampleDlg::OnBnClickedButtonInitApi()
{

	if( InitLibrary() )
	{
		if( m_fp_InitAPI(this->GetSafeHwnd()) )
		{
			// 로그인이 정상이면...
			m_pCommHelper = m_fp_GetCommHelper();
			m_pSiseHelper = m_fp_GetSiseHelper();

			ASSERT( m_pCommHelper );
			ASSERT( m_pSiseHelper );

			m_nKey = m_pCommHelper->AddHwnd(this->GetSafeHwnd(), _T("API_Sample"));
			ASSERT(m_nKey != -1);

			TCHAR* pID = m_fp_GetLoginID();
			ASSERT(pID);
			int nLen = _tcslen(pID);
			memcpy(m_szLoginID, pID, nLen);
			m_szLoginID[nLen] = NULL;

			m_fp_RegistRealOrders(this->GetSafeHwnd());

			Request90025(m_szLoginID);
		}
		else
		{
			MessageBox(_T("fail to initAPI"), API_TITLE, MB_OK | MB_ICONWARNING);
		}
	}
}

void CAPISampleDlg::OnBnClickedButtonExitApi()
{
	if( m_fp_ExitAPI )
	{
		m_fp_ExitAPI();
	}

	InitVariable();
	InitControls();
	OnBnClickedButtonSiseClear();
	OnBnClickedButtonOrderClear();
	OnBnClickedButtonClear();
}

void CAPISampleDlg::OnBnClickedButtonCurrPrice()
{

	CString strItemCode;
	m_editTrCode.GetWindowText(strItemCode);
	Request21002(strItemCode);
}

void CAPISampleDlg::OnBnClickedButtonHoga()
{
	CString strItemCode;
	m_editTrCode.GetWindowText(strItemCode);
	Request21001(strItemCode);
}

void CAPISampleDlg::OnBnClickedButtonChegyulFlow()
{

	CString strItemCode;
	m_editTrCode.GetWindowText(strItemCode);
	Request21003(strItemCode);
}

void CAPISampleDlg::OnClose()
{

	if( m_hAPILib )
	{
		::FreeLibrary(m_hAPILib);
		m_hAPILib = NULL;
	}

	CString strOrgOrdNo;
	int		nSelFund;
	nSelFund = m_comboOrderAccnt.GetCurSel();

	TCHAR* pszAccnt = (TCHAR*)(m_comboOrderAccnt.GetItemData(nSelFund));

	m_editOrgOrdNo.GetWindowText(strOrgOrdNo);


	//cFileWriter.Write(strOrgOrdNo, strlen(strOrgOrdNo));

	CString hLog;
	CString tchr;
	hLog.Format("%d\n",numHogaSise);
	//tchr.Format("%s\n",pszAccnt);
	
	//cFileWriter.Write(hLog, strlen(hLog));
	//cFileWriter.Write(account, strlen(tchr));
	//cFileWriter.Write(account, strlen(account));

	//CString tLog;
	//tLog.Format("%d\n",vwap_num);
	//ktb_udpFileWriter.Write(tLog, strlen(tLog));

	

	//if( all_udpFileWriter ) {
	//	all_udpFileWriter.Close();
	//}
	//if ( cFileWriter ) {
	//	cFileWriter.Close();
	//}
	//if ( ktb_siseFileWriter ) {
	//	ktb_siseFileWriter.Close();
	//}
	//if ( lktb_udpFileWriter ) lktb_udpFileWriter.Close();
	//if ( ktb_udpFileWriter ) ktb_udpFileWriter.Close();
	//if ( usd_udpFileWriter ) usd_udpFileWriter.Close();

	//if ( ktb_vwapFileWriter ) ktb_vwapFileWriter.Close();
	//if ( lktb_vwapFileWriter ) lktb_vwapFileWriter.Close();
	//if ( usd_vwapFileWriter ) usd_vwapFileWriter.Close();


	string now = getTime();
	CString log;
	log.Format("\n%c%c:%c%c:%c%c, usd_edr_pendingListIndex:%d, usd_edr_trade_num:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_edr_pendingListIndex,usd_edr_trade_num);
	usd_edr_FileWriter.Write(log, strlen(log));

//	if ( usd_logFileWriter ) usd_logFileWriter.Close();

	if ( ktb_cheFileWriter ) ktb_cheFileWriter.Close();
	if ( lktb_cheFileWriter ) lktb_cheFileWriter.Close();
	if ( usd_cheFileWriter ) usd_cheFileWriter.Close();

	if ( ktbf_edr_FileWriter ) ktbf_edr_FileWriter.Close();
	if ( lktbf_af_FileWriter ) lktbf_af_FileWriter.Close();
	if ( lktbf_edr_FileWriter ) lktbf_edr_FileWriter.Close();
	if ( usd_edr_FileWriter ) usd_edr_FileWriter.Close();

	if ( errorFileWriter ) errorFileWriter.Close();
	
	/*10초봉 파일에 출력코드*/
	time_t timer;
	struct tm* t;
	timer = time(NULL);
	t = localtime(&timer);
	int year = t->tm_year+1900;
	int mon = t->tm_mon+1;
	int day = t->tm_mday;

	CString strFile;
	strFile.Format("logs/%d%d%d_ktb_candle.log",year,mon,day);
	ktb_candleFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	for(int i = 0 ; i < ktbf_10sec_index; i++) {
		CString strLog;
		strLog.Format("ktb / %02d:%02d:%02d / %d / %f \n",ktb_10sec_candle[i].hour, ktb_10sec_candle[i].min, ktb_10sec_candle[i].sec, ktb_10sec_candle[i].volume, ktb_10sec_candle[i].price);
		ktb_candleFileWriter.Write(strLog, strlen(strLog));
	}

	strFile.Format("logs/%d%d%d_lktb_candle.log",year,mon,day);
	lktb_candleFileWriter.Open(strFile, CFile::modeCreate | CFile::modeWrite);

	for(int i = 0 ; i < lktbf_10sec_index; i++) {
		CString strLog;
		strLog.Format("lktb / %02d:%02d:%02d / %d / %f \n",lktbf_10sec_candle[i].hour, lktbf_10sec_candle[i].min, lktbf_10sec_candle[i].sec, lktbf_10sec_candle[i].volume, lktbf_10sec_candle[i].price);
		lktb_candleFileWriter.Write(strLog, strlen(strLog));
	}
	if ( ktb_candleFileWriter ) ktb_candleFileWriter.Close();
	if ( lktb_candleFileWriter ) lktb_candleFileWriter.Close();

	::DeleteCriticalSection(&g_cs);
	CDialogEx::OnClose();
}

void CAPISampleDlg::OnBnClickedButtonClear()
{
	m_ctrlTRList.ResetContent();
}
/*************************************************************/
/** 시세 요청 정보	**/
/** PACKET											**/
/*************************************************************/
void CAPISampleDlg::OnBnClickedButtonSiseRequest()
{

//	CString strItemCode;
//	m_editSiseCode.GetWindowText(strItemCode);
	
	m_ctrlSiseList.InsertString(0, _T(ktb_code + " ") + _T(lktb_code + " ") + _T(usd_code));
	//시세요청
	//if(strItemCode.GetLength() > 0)
	//{

		if( m_chkStrategy_ktbfedr.GetCheck() ) { ktbf_edr = true; } else { ktbf_edr=false; } ;
		if( m_chkStrategy_lktbfaf.GetCheck() ) { lktbf_af = true; } else { lktbf_af=false; } ;
		if( m_chkStrategy_lktbfedr.GetCheck() ) { lktbf_edr = true; } else { lktbf_edr=false; } ;
		if( m_chkStrategy_usdedr.GetCheck() ) { usd_edr=true; } else { usd_edr = false; };

		if ( ktbf_edr ) {
			CString trd_qty;	CString max_qty;
			m_start_time.GetWindowText(ktbf_start_time);
			m_trd_qty.GetWindowText(trd_qty);
			m_max_qty.GetWindowText(max_qty);
			ktbf_edr_max_trade_qty = _ttoi(trd_qty);
			ktbf_edr_max_qty = _ttoi(max_qty);
			ktbf_abs_max_short_qty = _ttoi(max_qty);
			ktbf_h = _ttoi(ktbf_start_time.Left(2));
			ktbf_m = _ttoi(ktbf_start_time.Mid(2,2));
		} 
		if ( lktbf_edr ) {
			CString trd_qty;	CString max_qty;
			m_start_time.GetWindowText(lktbf_start_time);
			m_trd_qty.GetWindowText(trd_qty);
			m_max_qty.GetWindowText(max_qty);
			lktbf_edr_max_trade_qty = _ttoi(trd_qty);
			lktbf_edr_max_qty = _ttoi(max_qty);
			lktbf_abs_max_short_qty = _ttoi(max_qty);
			lktbf_h = _ttoi(lktbf_start_time.Left(2));
			lktbf_m = _ttoi(lktbf_start_time.Mid(2,2));
		} 
		if ( usd_edr ) {
			CString trd_qty;	CString max_qty;
			m_start_time.GetWindowText(usd_start_time);
			m_trd_qty.GetWindowText(trd_qty);
			m_max_qty.GetWindowText(max_qty);
			usd_edr_max_trade_qty = _ttoi(trd_qty);
			usd_edr_max_qty = _ttoi(max_qty);
			usd_abs_max_short_qty = _ttoi(max_qty);
			usd_h = _ttoi(usd_start_time.Left(2));
			usd_m = _ttoi(usd_start_time.Mid(2,2));
		}


		if( m_chkSiseB6.GetCheck() ) {	RegistSise(_T("B6016"), _T(lktb_code));	RegistSise(_T("B6016"),_T(ktb_code));	RegistSise(_T("B6016"), _T(usd_code));} // 호가
		if( m_chkSiseA3.GetCheck() ) {	RegistSise(_T("A3016"), _T(lktb_code));	RegistSise(_T("A3016"),_T(ktb_code));	RegistSise(_T("A3016"), _T(usd_code));}// 체결
		if( m_chkSiseG7.GetCheck() ) {	RegistSise(_T("G7016"), _T(lktb_code));	RegistSise(_T("G7016"),_T(ktb_code));	RegistSise(_T("G7016"), _T(usd_code));}// 체결 + 호가
	//}

	if( m_chkSiseK200.GetCheck() ) 
	{
		RegistSise(_T("D2011"), _T("029"));	//코스피 200지수
	}
}

void CAPISampleDlg::OnBnClickedButtonSiseCancel()
{

	//수신하고 있는 전체 시세 중단
	ReleaseSiseAll();


	//특정시세만을 중단
	// 	CString strItemCode;
	// 	GetDlgItemText(IDC_EDIT_ITEMCODE, strItemCode);
	// 
	// 	if(strItemCode.GetLength() > 0)
	// 	{
	// 		ReleaseSise(_T("B6016"), strItemCode);	// 호가
	// 		ReleaseSise(_T("A3016"), strItemCode);	// 체결
	// 		ReleaseSise(_T("G7016"), strItemCode);	// 체결 + 호가
	// 	}
}

void CAPISampleDlg::OnBnClickedButtonOrderOrder()
{
	CString strItemCode, strQty, strPrice, strGubun, strType, strCond, strFund, strOrgOrdNo;
	int		nSelType, nSelGubun, nSelCond, nSelFund;

	m_editOrderCode.GetWindowText(strItemCode);
	m_editOrderQty.GetWindowText(strQty);
	m_editOrderPrice.GetWindowText(strPrice);
	//strPrice.Remove('.');

	nSelGubun = m_comboOrderGubun.GetCurSel();
	if(nSelGubun == CB_ERR)	MessageBox(_T("select the gubun"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderGubun.GetLBText(nSelGubun, strGubun);

	nSelType = m_comboOrderType.GetCurSel();
	if(nSelType == CB_ERR)	MessageBox(_T("select the type"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderType.GetLBText(nSelType, strType);

	nSelCond = m_comboOrderCond.GetCurSel();
	if(nSelCond == CB_ERR)	MessageBox(_T("select the condition"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderCond.GetLBText(nSelCond, strCond);

	nSelFund = m_comboOrderAccnt.GetCurSel();
	if(nSelFund == CB_ERR)	MessageBox(_T("select the fund"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderAccnt.GetLBText(nSelFund, strFund);
	TCHAR* pszAccnt = (TCHAR*)(m_comboOrderAccnt.GetItemData(nSelFund));

	Order('1', _ttoi(strQty), _tstof(strPrice),0, strGubun, strItemCode,"", "USD");
	//SendOrder('1');
}
void CAPISampleDlg::OnBnClickedButtonSiseClear()
{
	m_ctrlSiseList.ResetContent();
}

void CAPISampleDlg::OnBnClickedButtonOrderModify()
{
	CString strItemCode, strQty, strPrice, strGubun, strType, strCond, strFund, strOrgOrdNo;
	int		nSelType, nSelGubun, nSelCond, nSelFund;

	m_editOrderCode.GetWindowText(strItemCode);
	m_editOrderQty.GetWindowText(strQty);
	m_editOrderPrice.GetWindowText(strPrice);
	//strPrice.Remove('.');

	nSelGubun = m_comboOrderGubun.GetCurSel();
	if(nSelGubun == CB_ERR)	MessageBox(_T("select the gubun"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderGubun.GetLBText(nSelGubun, strGubun);

	nSelType = m_comboOrderType.GetCurSel();
	if(nSelType == CB_ERR)	MessageBox(_T("select the type"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderType.GetLBText(nSelType, strType);

	nSelCond = m_comboOrderCond.GetCurSel();
	if(nSelCond == CB_ERR)	MessageBox(_T("select the condition"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderCond.GetLBText(nSelCond, strCond);

	nSelFund = m_comboOrderAccnt.GetCurSel();
	if(nSelFund == CB_ERR)	MessageBox(_T("select the fund"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderAccnt.GetLBText(nSelFund, strFund);
	TCHAR* pszAccnt = (TCHAR*)(m_comboOrderAccnt.GetItemData(nSelFund));

	if(usd_edr) {
		for (int i = 0; i< usd_edr_pendingListIndex; i++ ) {
			usd_edr_pendingList[i].orgordno;
			
			
			Order('2',usd_edr_pendingList[i].intQty, usd_edr_pendingList[i].floatPrice, _tstof(strPrice), usd_edr_pendingList[i].strGubun, usd_edr_pendingList[i].strItemCode, usd_edr_pendingList[i].orgordno, "USD");
		}
	}

	//Order('2', _ttoi(strQty), _tstof(strPrice), strGubun, strItemCode, "KTBF");
}

void CAPISampleDlg::OnBnClickedButtonOrderCancel()
{
	CString strItemCode, strQty, strPrice, strGubun, strType, strCond, strFund, strOrgOrdNo;
	int		nSelType, nSelGubun, nSelCond, nSelFund;

	m_editOrderCode.GetWindowText(strItemCode);
	m_editOrderQty.GetWindowText(strQty);
	m_editOrderPrice.GetWindowText(strPrice);
	//strPrice.Remove('.');

	nSelGubun = m_comboOrderGubun.GetCurSel();
	if(nSelGubun == CB_ERR)	MessageBox(_T("select the gubun"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderGubun.GetLBText(nSelGubun, strGubun);

	nSelType = m_comboOrderType.GetCurSel();
	if(nSelType == CB_ERR)	MessageBox(_T("select the type"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderType.GetLBText(nSelType, strType);

	nSelCond = m_comboOrderCond.GetCurSel();
	if(nSelCond == CB_ERR)	MessageBox(_T("select the condition"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderCond.GetLBText(nSelCond, strCond);

	nSelFund = m_comboOrderAccnt.GetCurSel();
	if(nSelFund == CB_ERR)	MessageBox(_T("select the fund"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderAccnt.GetLBText(nSelFund, strFund);
	TCHAR* pszAccnt = (TCHAR*)(m_comboOrderAccnt.GetItemData(nSelFund));

	for(int i = 0; i< usd_edr_pendingListIndex; i++) {
		Order('3', _ttoi(strQty), _tstof(strPrice),_tstof(strPrice), strGubun, strItemCode, usd_edr_pendingList[i].orgordno, "KTBF");
	}
	
}

//void CAPISampleDlg::SendOrder(TCHAR chTranType)
//{
//	CString strItemCode, strQty, strPrice, strGubun, strType, strCond, strFund, strOrgOrdNo;
//	int		nSelType, nSelGubun, nSelCond, nSelFund;
//
//	m_editOrderCode.GetWindowText(strItemCode);
//	m_editOrderQty.GetWindowText(strQty);
//	m_editOrderPrice.GetWindowText(strPrice);
//	strPrice.Remove('.');
//
//	nSelGubun = m_comboOrderGubun.GetCurSel();
//	if(nSelGubun == CB_ERR)	MessageBox(_T("select the gubun"), API_TITLE, MB_OK | MB_ICONWARNING);
//	m_comboOrderGubun.GetLBText(nSelGubun, strGubun);
//
//	nSelType = m_comboOrderType.GetCurSel();
//	if(nSelType == CB_ERR)	MessageBox(_T("select the type"), API_TITLE, MB_OK | MB_ICONWARNING);
//	m_comboOrderType.GetLBText(nSelType, strType);
//
//	nSelCond = m_comboOrderCond.GetCurSel();
//	if(nSelCond == CB_ERR)	MessageBox(_T("select the condition"), API_TITLE, MB_OK | MB_ICONWARNING);
//	m_comboOrderCond.GetLBText(nSelCond, strCond);
//
//	nSelFund = m_comboOrderAccnt.GetCurSel();
//	if(nSelFund == CB_ERR)	MessageBox(_T("select the fund"), API_TITLE, MB_OK | MB_ICONWARNING);
//	m_comboOrderAccnt.GetLBText(nSelFund, strFund);
//	TCHAR* pszAccnt = (TCHAR*)(m_comboOrderAccnt.GetItemData(nSelFund));
//
//	m_editOrgOrdNo.GetWindowText(strOrgOrdNo);
//
//	FillPacketHeader(chTranType, strItemCode, strFund.Left(6));
//
//	//if(FillOrderPacket(chTranType, pszAccnt, strItemCode, _ttoi(strQty), _ttoi(strPrice), 
//	//				   strGubun.GetAt(0), strType.GetAt(0), strCond.GetAt(0), strOrgOrdNo ))
//	{
//		//주문전송
//		//	m_pCommHelper->SendKospiFOOrder(m_nKey, (LPCTSTR)&m_OrderPacket, sizeof(m_OrderPacket));
//	}
//
//	
//}

void CAPISampleDlg::Order(TCHAR chTranType, int intQty, float floatPrice, float prePrice, CString strGubun, CString strItemCode, CString preOrgordno, CString jongmok)
{
	CString strType, strCond, strFund, strOrgOrdNo;
	int		nSelFund;
	CString log;
	string now = getTime();
	/* float 값 보정*/
	//if ((int)(floatPrice * 1000)%10 == 9) {
	//	floatPrice += 0.001;
	//}
	//if ((int)(prePrice * 1000)%10 == 9) {
	//	prePrice += 0.001;
	//}

	/*intQty값 보정*/
	if (intQty < 0) {
		intQty = -intQty;
		strGubun = "1";
	}

	CString str_price;
	CString str_pre_price;
	str_price.Format("%011.2f",floatPrice);
	str_pre_price.Format("%011.2f",prePrice);

	
	//log.Format("%c%c:%c%c:%c%c, order init qty:%d, type:%s, str_price:%s, str_preprice:%s\n", now[0],now[1],now[2],now[3],now[4],now[5],intQty, chTranType, str_price, str_pre_price);
	log.Format("%c%c:%c%c:%c%c order init qty:%d\n",now[0],now[1],now[2],now[3],now[4],now[5],intQty);
	if(lktbf_af) {
		lktbf_af_FileWriter.Write(log, strlen(log));
	} else if (lktbf_edr) {
		lktbf_edr_FileWriter.Write(log, strlen(log));
	} else if (usd_edr) {
		usd_edr_FileWriter.Write(log, strlen(log));
	}
	//if(jongmok == "LKTBF") {
	//	lktb_gentFileWriter.Write(log, strlen(log));
	//} else if (jongmok == "USD") {
	//	usd_edr_FileWriter.Write(log,strlen(log));
	//}

	//if (str_price == str_pre_price) {
	//	return;
	//}

	strType = "2";//지정가
	//strCond="3"; //IOC
	
	nSelFund = m_comboOrderAccnt.GetCurSel();
	if(nSelFund == CB_ERR)	MessageBox(_T("select the fund"), API_TITLE, MB_OK | MB_ICONWARNING);
	m_comboOrderAccnt.GetLBText(nSelFund, strFund);
	TCHAR* pszAccnt = (TCHAR*)(m_comboOrderAccnt.GetItemData(nSelFund));

	// my code
	//TCHAR* pszAccnt = (TCHAR*)(LPCTSTR)account;

	/*if (jongmok == "KTBF") {
		ktbf_pre_price_float = floatPrice;
		m_editOrgOrdNo.GetWindowText(ktb_pre_orgordno);
	} else if (jongmok =="LKTBF") {
		log.Format("%c%c:%c%c:%c%c,lktb_pre_orgordno:%s, jm:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],lktb_pre_orgordno,jongmok);
		lktb_urgentFileWriter.Write(log, strlen(log));
	} else if (jongmok == "USD") {
		log.Format("%c%c:%c%c:%c%c,usd_pre_orgordno:%s, jm:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_pre_orgordno,jongmok);
		usd_edr_FileWriter.Write(log,strlen(log));
	}*/

	if(lktbf_af) {
		log.Format("%c%c:%c%c:%c%c,lktb_pre_orgordno:%s, jm:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],lktb_pre_orgordno,jongmok);
		lktbf_af_FileWriter.Write(log, strlen(log));
	} else if (lktbf_edr) {
		log.Format("%c%c:%c%c:%c%c,lktb_pre_orgordno:%s, jm:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],lktb_pre_orgordno,jongmok);
		lktbf_edr_FileWriter.Write(log, strlen(log));
	} else if (usd_edr) {
		log.Format("%c%c:%c%c:%c%c,usd_pre_orgordno:%s, jm:%s\n",now[0],now[1],now[2],now[3],now[4],now[5],usd_pre_orgordno,jongmok);
		usd_edr_FileWriter.Write(log, strlen(log));
	}


	log.Format("▶▶▶▶▶▶▶▶▶▶▶▶");
	m_ctrlOrderList2.InsertString(0,log);

	log.Format("%c%c:%c%c:%c%c,▶type:%c, Order %s, at %.3f %s amount %d, gubun(%s)\n", now[0],now[1],now[2],now[3],now[4],now[5],chTranType, jongmok, floatPrice, str_price, intQty,strGubun);
	m_ctrlOrderList2.InsertString(0,log);
	//if(jongmok == "LKTBF") {
	//	lktb_urgentFileWriter.Write(log, strlen(log));
	//} else if (jongmok == "USD") {
	//	usd_edr_FileWriter.Write(log,strlen(log));
	//}
	if(lktbf_af) {
		lktbf_af_FileWriter.Write(log, strlen(log));
	} else if (lktbf_edr) {
		lktbf_edr_FileWriter.Write(log, strlen(log));
	} else if (usd_edr) {
		usd_edr_FileWriter.Write(log, strlen(log));
	}
	log.Format("▶▶▶▶▶▶▶▶▶▶▶▶");
	m_ctrlOrderList2.InsertString(0,log);

	for(int i = 0 ; i < usd_edr_pendingListIndex; i++) {
		log.Format("111 idx:%d, i:%d, prc:%f, qty:%d, gubun:%c, org:%s\n",usd_edr_pendingListIndex, i, usd_edr_pendingList[i].floatPrice, usd_edr_pendingList[i].intQty, usd_edr_pendingList[i].strGubun[0] ,usd_edr_pendingList[i].orgordno);
		m_ctrlOrderList.InsertString(0,log);
		//if(jongmok == "LKTBF") {
		//	lktb_urgentFileWriter.Write(log, strlen(log));
		//} else if (jongmok == "USD") {
		//	usd_edr_FileWriter.Write(log,strlen(log));
		//}
		if(lktbf_af) {
			lktbf_af_FileWriter.Write(log, strlen(log));
		} else if (lktbf_edr) {
			lktbf_edr_FileWriter.Write(log, strlen(log));
		} else if (usd_edr) {
			usd_edr_FileWriter.Write(log, strlen(log));
		}
	}

	FillPacketHeader(chTranType, strItemCode, strFund.Left(6), str_pre_price);

	if(FillOrderPacket(chTranType, pszAccnt, strItemCode, intQty, str_price, 
					   strGubun.GetAt(0), strType.GetAt(0), strCond.GetAt(0), preOrgordno ))

	{
		if(jongmok == "KTBF") {
			ktbf_pre_price_str= str_price;
		} else if (jongmok == "LKTBF") {
			lktbf_pre_price_str= str_price;
		} else if (jongmok == "USD") {
			usd_pre_price_str= str_price;
		}
		
		//주문전송
		char t = m_pCommHelper->SendKospiFOOrder(m_nKey, (LPCTSTR)&m_orderpacket, sizeof(m_orderpacket));
		CString z;
		z.Format("@ %c",t);
		m_ctrlOrderList2.InsertString(0, z);
	}
}

/*************************************************************/
/** 주문헤더패킷**/
/** PACKET													**/
/*************************************************************/
void CAPISampleDlg::FillPacketHeader(TCHAR chTranType, LPCTSTR lpszExpCode, LPCTSTR lpszFundNo, CString pre_price)
{
	CString log;
	string now = getTime();
	ASSERT(lpszExpCode);
	ASSERT(lpszFundNo);

	memcpy(m_orderpacket.header.tr_code, _T("DATA"), sizeof(m_orderpacket.header.tr_code));	// 그냥 DATA
	memset(m_orderpacket.header.ack_gubun, 0x20, sizeof(m_orderpacket.header.ack_gubun));	// 구분. 스페이스는 주문
	memcpy(m_orderpacket.header.seq_no, _T("000000000"), sizeof(m_orderpacket.header.seq_no));	// 일련번호
	memcpy(m_orderpacket.header.emp_no, _T("0SE21121"), sizeof(m_orderpacket.header.emp_no));	// 로그인아이디. 사번
	memcpy(m_orderpacket.header.fund_no, _T(lpszFundNo), sizeof(m_orderpacket.header.fund_no));	// 펀드번호. 020043
	memcpy(m_orderpacket.header.mkt_l_cls, _T("C"), sizeof(m_orderpacket.header.mkt_l_cls));	// 시장구분. 상품선옵 C
	memcpy(m_orderpacket.header.com_gb, _T("1"), sizeof(m_orderpacket.header.com_gb));	// 단말구분. 1 TOPS
	memset(m_orderpacket.header.res_code, 0x20, sizeof(m_orderpacket.header.res_code));	// 거부코드. 정상은 space
	if (chTranType == '1') {
		memset(m_orderpacket.header.org_ord_prc, 0x20, sizeof(m_orderpacket.header.org_ord_prc));	// 원주문가격. space
	} else if (chTranType == '2' || chTranType == '3') {
		memcpy(m_orderpacket.header.org_ord_prc, _T(pre_price), sizeof(m_orderpacket.header.org_ord_prc));	// 원주문가격. prePrice
	}
	memset(m_orderpacket.header.mysvr_gb, 0x20, sizeof(m_orderpacket.header.mysvr_gb));	// 타 tops 주문인지 표시
	memset(m_orderpacket.header.mkt_kind, 0x20, sizeof(m_orderpacket.header.mkt_kind));	// 일단 space...
	memset(m_orderpacket.header.mkt_offset, 0x20, sizeof(m_orderpacket.header.mkt_offset));	// 일단 space...
	memset(m_orderpacket.header.filler, 0x20, sizeof(m_orderpacket.header.filler));	// 필터. space

	//char t[1];

	//LPCTSTR a = (LPCTSTR)chTranType;
	//memcpy(t,a,1);

	m_ctrlOrderList.InsertString(0,log);
	usd_edr_FileWriter.Write(log,strlen(log));

	//usd_logFileWriter.Write(t, strlen(t));
	//usd_logFileWriter.Write(m_orderpacket.header.tr_code, strlen(m_orderpacket.header.tr_code));
	//usd_logFileWriter.Write(m_orderpacket.header.ack_gubun, strlen(m_orderpacket.header.ack_gubun));
	//usd_logFileWriter.Write(m_orderpacket.header.seq_no, strlen(m_orderpacket.header.seq_no));
	//usd_logFileWriter.Write(m_orderpacket.header.emp_no, strlen(m_orderpacket.header.emp_no));
	//usd_logFileWriter.Write(m_orderpacket.header.fund_no, strlen(m_orderpacket.header.fund_no));
	//usd_logFileWriter.Write(m_orderpacket.header.mkt_l_cls, strlen(m_orderpacket.header.mkt_l_cls));
	//usd_logFileWriter.Write(m_orderpacket.header.com_gb, strlen(m_orderpacket.header.com_gb));
	//usd_logFileWriter.Write(m_orderpacket.header.res_code, strlen(m_orderpacket.header.res_code));
	//usd_logFileWriter.Write(m_orderpacket.header.org_ord_prc, strlen(m_orderpacket.header.org_ord_prc));
	//usd_logFileWriter.Write(m_orderpacket.header.mysvr_gb, strlen(m_orderpacket.header.mysvr_gb));
	//usd_logFileWriter.Write(m_orderpacket.header.mkt_kind, strlen(m_orderpacket.header.mkt_kind));
	//usd_logFileWriter.Write(m_orderpacket.header.mkt_offset, strlen(m_orderpacket.header.mkt_offset));
	//usd_logFileWriter.Write(m_orderpacket.header.filler, strlen(m_orderpacket.header.filler));
	//usd_logFileWriter.Write("\n", strlen("\n"));
	//usd_logFileWriter.Write("\n", strlen("\n"));

	m_ctrlOrderList.InsertString(0,log);
	usd_edr_FileWriter.Write(log,strlen(log));

//	memcpy(m_OrderPacket.header.emp_no, m_szLoginID, sizeof(m_OrderPacket.header.emp_no));
//	memcpy(m_OrderPacket.header.fund_no, lpszFundNo, sizeof(m_OrderPacket.header.fund_no));
}
/*************************************************************/
/** 주문패킷**/
/** PACKET													**/
/*************************************************************/
BOOL CAPISampleDlg::FillOrderPacket(TCHAR chTranType, LPCTSTR lpszAccount, LPCTSTR lpszExpCode, int nQty, CString nPrice, TCHAR chMaemae, TCHAR chOrdType, TCHAR chOrdCond, LPCTSTR lpszOrgOrdNo)
{
	// Order Struct에 데이타를 채울때 선언된 순서에 따라 값을 채운다.
	CString strQty;
	strQty.Format("%010d",nQty);

	// 수량이 0 보다 작은 주문은 없다.
	if( nQty <= 0 ) return FALSE;


	/*패킷에 현재 날자를 보내야 한다*/
	time_t timer;
	struct tm* t;
	timer = time(NULL);
	t = localtime(&timer);
	int year = t->tm_year+1900;
	int mon = t->tm_mon+1;
	int day = t->tm_mday;
	CString strDate;
	strDate.Format("%04d%02d%02d",year,mon,day);

	switch(chTranType)
	{
	case _T('1'):
		memcpy(m_orderpacket.krxorder.hseq,				_T("00000000000"),		_countof(m_orderpacket.krxorder.hseq)); // 정규장
		memcpy(m_orderpacket.krxorder.trans_code,		_T("TCHODR10001"),		_countof(m_orderpacket.krxorder.trans_code)); // 정규장
		memcpy(m_orderpacket.krxorder.board_id,			_T("G1"),				_countof(m_orderpacket.krxorder.board_id)); // 정규장
		memcpy(m_orderpacket.krxorder.memberno,			_T("00017"),			_countof(m_orderpacket.krxorder.memberno)); // kb
		memcpy(m_orderpacket.krxorder.bpno,				_T("00999"),			_countof(m_orderpacket.krxorder.bpno)); // kb
		memcpy(m_orderpacket.krxorder.ordno,			_T("0000000000"),		_countof(m_orderpacket.krxorder.ordno)); // 신규
		memset(m_orderpacket.krxorder.orgordno,			0x20,					_countof(m_orderpacket.krxorder.orgordno)); // 신규

		memcpy(m_orderpacket.krxorder.code, lpszExpCode, sizeof(m_orderpacket.krxorder.code));	// 종목코드 ex) kr4165rc0003
		m_orderpacket.krxorder.mmgubun[0]					= chMaemae;		// 매매구분1 매도 , 2 매수
		m_orderpacket.krxorder.hogagb[0]					= chTranType;		// 신규주문 1 신규, 2 정정, 3 취소
		memcpy(m_orderpacket.krxorder.gyejwa, lpszAccount, sizeof(m_orderpacket.krxorder.gyejwa));// 계좌번호
		_stprintf_s(m_szTempQty, sizeof(m_szTempQty),	_T("%010d"),	nQty);			// 주문수량
		memcpy(m_orderpacket.krxorder.cnt,		m_szTempQty,	ORDER_QTY_LEN);		// 주문수량
		memcpy(m_orderpacket.krxorder.price,			nPrice,				_countof(m_orderpacket.krxorder.price)); // 주문가격 소수점 포함 우측정렬. 앞에는 0 채우기
		memcpy(m_orderpacket.krxorder.ord_type,			_T("2"),				_countof(m_orderpacket.krxorder.ord_type)); // 호가유형코드 지정가.  1.시장가, i 조건부지정가, x 최유리지정가
		memcpy(m_orderpacket.krxorder.ord_cond,			_T("0"),				_countof(m_orderpacket.krxorder.ord_cond)); // 호가조건코드. 0 일반, 3 ioc, 4 fok
		memcpy(m_orderpacket.krxorder.market_ord_num,	_T("00000000000"),		_countof(m_orderpacket.krxorder.market_ord_num));//시장조성자호가구분번호. 일반
		memcpy(m_orderpacket.krxorder.stock_state_id,	_T("0    "),			_countof(m_orderpacket.krxorder.stock_state_id)); // 자사주신고서id. 해당없음
		memcpy(m_orderpacket.krxorder.stock_trade_code,	_T("0"),				_countof(m_orderpacket.krxorder.stock_trade_code)); // 자사주매매방법코드. 해당없음
		memcpy(m_orderpacket.krxorder.medo_type_code,	_T("00"),				_countof(m_orderpacket.krxorder.medo_type_code)); // 매도유행코드. 해당없음
		memcpy(m_orderpacket.krxorder.singb,			_T("10"),				_countof(m_orderpacket.krxorder.singb)); // 신용구분코드. 보통(일반)
		memcpy(m_orderpacket.krxorder.witak,			_T("31"),				_countof(m_orderpacket.krxorder.witak)); // 위탁자기구분코드. 호가입력회원의 자기거래
		memset(m_orderpacket.krxorder.witakcomp_num,	0x20,					_countof(m_orderpacket.krxorder.witakcomp_num)); // 위탁사번호
		memcpy(m_orderpacket.krxorder.pt_type_code,		_T("00"),				_countof(m_orderpacket.krxorder.pt_type_code)); // pt 구분코드 일반.
		memset(m_orderpacket.krxorder.sub_stock_gyejwa,	0x20,					_countof(m_orderpacket.krxorder.sub_stock_gyejwa)); // 대용주권계좌번호
		memcpy(m_orderpacket.krxorder.gyejwa_type_code,	_T("41"),				_countof(m_orderpacket.krxorder.gyejwa_type_code)); // 계좌구분코드 : 41 자기일반, 61 알고리즘계좌
		memcpy(m_orderpacket.krxorder.gyejwa_margin_cod,_T("11"),				_countof(m_orderpacket.krxorder.gyejwa_margin_cod)); // 계좌증거금유형코드 : 11 사후증거금
		memcpy(m_orderpacket.krxorder.kukga,			_T("410"),				_countof(m_orderpacket.krxorder.kukga)); // 국가코드 410 한국
		memcpy(m_orderpacket.krxorder.tocode,			_T("1000"),				_countof(m_orderpacket.krxorder.tocode)); // 투자자구분코드
		memcpy(m_orderpacket.krxorder.foreign,			_T("00"),				_countof(m_orderpacket.krxorder.foreign)); // 외국인투자자구분코드
		memcpy(m_orderpacket.krxorder.meache_gb,		_T("1"),				_countof(m_orderpacket.krxorder.meache_gb)); // 주문매체구분코드
		memcpy(m_orderpacket.krxorder.term_no,			_T("192168020222"),		_countof(m_orderpacket.krxorder.term_no)); // 주문자식별정보. 사용자pc ip : 192.168.20.222 -> 192168020222
		memcpy(m_orderpacket.krxorder.mac_addr,			_T("AAAAAA008324"),		_countof(m_orderpacket.krxorder.mac_addr)); // 사용자pc mac : aa-aa-aa-00-83-24 -> aaaaaa008324
		memcpy(m_orderpacket.krxorder.ord_date,			strDate,				sizeof(m_orderpacket.krxorder.ord_date));
		memset(m_orderpacket.krxorder.ord_time,			0x20,					_countof(m_orderpacket.krxorder.ord_time)); // 회원사주문시각. 일단 space로
		memset(m_orderpacket.krxorder.hoiwon,			0x20,					_countof(m_orderpacket.krxorder.hoiwon)); // 회원사용영역. 일단 space로
		memset(m_orderpacket.krxorder.pgm_gongsi_gb,	0x20,					_countof(m_orderpacket.krxorder.pgm_gongsi_gb)); // 프로그램호가 신고 구분코드. 일단 space
		
		break;

/*		
// 원주문번호			- 신규주문은 SPACE로 
		memset(m_OrderPacket.KrxOrder.org_ord_no,	' ',			_countof(m_OrderPacket.KrxOrder.org_ord_no));
		// 호가가격			- 스프레드 가격이 -인 경우 고려
		_stprintf_s(m_szTempPrice, sizeof(m_szTempPrice),	_T("%04.2f"),		nPrice / 100.0);	// 가격
		memcpy(m_OrderPacket.KrxOrder.price, m_szTempPrice, ORDER_PRICE_LEN);
		if( nPrice < 0 ) m_OrderPacket.KrxOrder.price[0] = '-';

		memset(m_OrderPacket.header.org_ord_prc,	' ',						_countof(m_OrderPacket.header.org_ord_prc));

		memcpy(m_OrderPacket.KrxOrder.stock_state_id,		_T("0    "),		_countof(m_OrderPacket.KrxOrder.stock_state_id));
		m_OrderPacket.KrxOrder.stock_trade_code[0]			= '0';
		memcpy(m_OrderPacket.KrxOrder.medo_type_code,		_T("00"),			_countof(m_OrderPacket.KrxOrder.medo_type_code));
		memcpy(m_OrderPacket.KrxOrder.singb,				_T("10"),			_countof(m_OrderPacket.KrxOrder.singb));
		memcpy(m_OrderPacket.KrxOrder.gyejwa_type_code,		_T("41"),			_countof(m_OrderPacket.KrxOrder.gyejwa_type_code));
		memcpy(m_OrderPacket.KrxOrder.gyejwa_margin_cod,	_T("11"),			_countof(m_OrderPacket.KrxOrder.gyejwa_margin_cod));
		memcpy(m_OrderPacket.KrxOrder.kukga,				_T("410"),			_countof(m_OrderPacket.KrxOrder.kukga));
		memcpy(m_OrderPacket.KrxOrder.tocode,				_T("1000"),			_countof(m_OrderPacket.KrxOrder.tocode));
		memcpy(m_OrderPacket.KrxOrder.foreign,				_T("00"),			_countof(m_OrderPacket.KrxOrder.foreign));
		memcpy(m_OrderPacket.KrxOrder.witak,				_T("31"),			_countof(m_OrderPacket.KrxOrder.witak));
		m_OrderPacket.KrxOrder.ord_type[0]					= chOrdType;
		m_OrderPacket.KrxOrder.ord_cond[0]					= chOrdCond;*/
		break;
	case _T('2'):
		m_editOrgOrdNo.SetWindowText(lpszOrgOrdNo);

		memcpy(m_orderpacket.krxorder.hseq,				_T("00000000000"),		_countof(m_orderpacket.krxorder.hseq)); // 정규장
		memcpy(m_orderpacket.krxorder.trans_code,		_T("TCHODR10002"),		_countof(m_orderpacket.krxorder.trans_code)); // 정규장
		memcpy(m_orderpacket.krxorder.board_id,			_T("G1"),				_countof(m_orderpacket.krxorder.board_id)); // 정규장
		memcpy(m_orderpacket.krxorder.memberno,			_T("00017"),			_countof(m_orderpacket.krxorder.memberno)); // kb
		memcpy(m_orderpacket.krxorder.bpno,				_T("00999"),			_countof(m_orderpacket.krxorder.bpno)); // kb
		memcpy(m_orderpacket.krxorder.ordno,			_T("0000000000"),			_countof(m_orderpacket.krxorder.ordno)); // 신규
		memcpy(m_orderpacket.krxorder.orgordno,			lpszOrgOrdNo,			_countof(m_orderpacket.krxorder.orgordno)); // 신규

		memcpy(m_orderpacket.krxorder.code, lpszExpCode, sizeof(m_orderpacket.krxorder.code));	// 종목코드 ex) kr4165rc0003
		m_orderpacket.krxorder.mmgubun[0]					= chMaemae;		// 매매구분1 매도 , 2 매수
		m_orderpacket.krxorder.hogagb[0]					= chTranType;		// 신규주문 1 신규, 2 정정, 3 취소
		memcpy(m_orderpacket.krxorder.gyejwa, lpszAccount, sizeof(m_orderpacket.krxorder.gyejwa));// 계좌번호
		_stprintf_s(m_szTempQty, sizeof(m_szTempQty),	_T("%010d"),	nQty);			// 주문수량
		memcpy(m_orderpacket.krxorder.cnt,		m_szTempQty,	ORDER_QTY_LEN);		// 주문수량
		memcpy(m_orderpacket.krxorder.price,			nPrice,				_countof(m_orderpacket.krxorder.price)); // 주문가격 소수점 포함 우측정렬. 앞에는 0 채우기
		memcpy(m_orderpacket.krxorder.ord_type,			_T("2"),				_countof(m_orderpacket.krxorder.ord_type)); // 지정가.  1.시장가, i 조건부지정가, x 최유리지정가
		memcpy(m_orderpacket.krxorder.ord_cond,			_T("0"),				_countof(m_orderpacket.krxorder.ord_cond)); // 호가조건코드. 0 일반, 3 ioc, 4 fok
		memcpy(m_orderpacket.krxorder.market_ord_num,	_T("00000000000"),		_countof(m_orderpacket.krxorder.market_ord_num));//시장조성자호가구분번호. 일반
		memset(m_orderpacket.krxorder.stock_state_id,	0x20,			_countof(m_orderpacket.krxorder.stock_state_id)); // 자사주신고서id. 해당없음
		memset(m_orderpacket.krxorder.stock_trade_code,	0x20,				_countof(m_orderpacket.krxorder.stock_trade_code)); // 자사주매매방법코드. 해당없음
		memset(m_orderpacket.krxorder.medo_type_code,	0x20,				_countof(m_orderpacket.krxorder.medo_type_code)); // 매도유행코드. 해당없음
		memset(m_orderpacket.krxorder.singb,			0x20,				_countof(m_orderpacket.krxorder.singb)); // 신용구분코드. 보통(일반)
		memcpy(m_orderpacket.krxorder.witak,			_T("31"),				_countof(m_orderpacket.krxorder.witak)); // 위탁자기구분코드. 호가입력회원의 자기거래
		memset(m_orderpacket.krxorder.witakcomp_num,	0x20,					_countof(m_orderpacket.krxorder.witakcomp_num)); // 위탁사번호
		memcpy(m_orderpacket.krxorder.pt_type_code,		_T("00"),				_countof(m_orderpacket.krxorder.pt_type_code)); // pt 구분코드 일반.
		memset(m_orderpacket.krxorder.sub_stock_gyejwa,	0x20,					_countof(m_orderpacket.krxorder.sub_stock_gyejwa)); // 대용주권계좌번호
		memset(m_orderpacket.krxorder.gyejwa_type_code,	0x20,				_countof(m_orderpacket.krxorder.gyejwa_type_code)); // 계좌구분코드 : 41 자기일반, 61 알고리즘계좌
		memset(m_orderpacket.krxorder.gyejwa_margin_cod,0x20,				_countof(m_orderpacket.krxorder.gyejwa_margin_cod)); // 계좌증거금유형코드 : 11 사후증거금
		memset(m_orderpacket.krxorder.kukga,			0x20,				_countof(m_orderpacket.krxorder.kukga)); // 국가코드 410 한국
		memset(m_orderpacket.krxorder.tocode,			0x20,				_countof(m_orderpacket.krxorder.tocode)); // 투자자구분코드
		memset(m_orderpacket.krxorder.foreign,			0x20,				_countof(m_orderpacket.krxorder.foreign)); // 외국인투자자구분코드
		memcpy(m_orderpacket.krxorder.meache_gb,		_T("1"),				_countof(m_orderpacket.krxorder.meache_gb)); // 주문매체구분코드
		memcpy(m_orderpacket.krxorder.term_no,			_T("192168020222"),		_countof(m_orderpacket.krxorder.term_no)); // 주문자식별정보. 사용자pc ip : 192.168.20.222 -> 192168020222
		memcpy(m_orderpacket.krxorder.mac_addr,			_T("AAAAAA008324"),		_countof(m_orderpacket.krxorder.mac_addr)); // 사용자pc mac : aa-aa-aa-00-83-24 -> aaaaaa008324
		memcpy(m_orderpacket.krxorder.ord_date,			strDate,				sizeof(m_orderpacket.krxorder.ord_date));
		memset(m_orderpacket.krxorder.ord_time,			0x20,					_countof(m_orderpacket.krxorder.ord_time)); // 회원사주문시각. 일단 space로
		memset(m_orderpacket.krxorder.hoiwon,			0x20,					_countof(m_orderpacket.krxorder.hoiwon)); // 회원사용영역. 일단 space로
		memset(m_orderpacket.krxorder.pgm_gongsi_gb,	0x20,					_countof(m_orderpacket.krxorder.pgm_gongsi_gb)); // 프로그램호가 신고 구분코드. 일단 space
		
		break;
/*		// 원주문번호
		memcpy(m_OrderPacket.KrxOrder.org_ord_no,	lpszOrgOrdNo,	_countof(m_OrderPacket.KrxOrder.org_ord_no));
		// 호가가격			- 스프레드 가격이 -인 경우 고려
		_stprintf_s(m_szTempPrice, sizeof(m_szTempPrice),	_T("%04.2f"),		nPrice / 100.0);	// 가격
		memcpy(m_OrderPacket.KrxOrder.price, m_szTempPrice, ORDER_PRICE_LEN);
		if( nPrice < 0 ) m_OrderPacket.KrxOrder.price[0] = '-';

		memset(m_OrderPacket.header.org_ord_prc,	' ',						_countof(m_OrderPacket.header.org_ord_prc));

		memset(m_OrderPacket.KrxOrder.stock_state_id,		0x20,				_countof(m_OrderPacket.KrxOrder.stock_state_id));
		memset(m_OrderPacket.KrxOrder.stock_trade_code,		0x20,				_countof(m_OrderPacket.KrxOrder.stock_trade_code));
		memset(m_OrderPacket.KrxOrder.medo_type_code,		0x20,				_countof(m_OrderPacket.KrxOrder.medo_type_code));
		memset(m_OrderPacket.KrxOrder.singb,				0x20,				_countof(m_OrderPacket.KrxOrder.singb));
		memset(m_OrderPacket.KrxOrder.gyejwa_type_code,		0x20,				_countof(m_OrderPacket.KrxOrder.gyejwa_type_code));
		memset(m_OrderPacket.KrxOrder.gyejwa_margin_cod,	0x20,				_countof(m_OrderPacket.KrxOrder.gyejwa_margin_cod));
		memset(m_OrderPacket.KrxOrder.kukga,				0x20,				_countof(m_OrderPacket.KrxOrder.kukga));
		memset(m_OrderPacket.KrxOrder.tocode,				0x20,				_countof(m_OrderPacket.KrxOrder.tocode));
		memset(m_OrderPacket.KrxOrder.foreign,				0x20,				_countof(m_OrderPacket.KrxOrder.foreign));
		memcpy(m_OrderPacket.KrxOrder.witak,				_T("31"),			_countof(m_OrderPacket.KrxOrder.witak));

		m_OrderPacket.KrxOrder.ord_type[0]					= chOrdType;
		m_OrderPacket.KrxOrder.ord_cond[0]					= chOrdCond;*/
		break;
	case _T('3'):
		m_editOrgOrdNo.SetWindowText(lpszOrgOrdNo);

		memcpy(m_orderpacket.krxorder.hseq,				_T("00000000000"),		_countof(m_orderpacket.krxorder.hseq)); // 정규장
		memcpy(m_orderpacket.krxorder.trans_code,		_T("TCHODR10003"),		_countof(m_orderpacket.krxorder.trans_code)); // 정규장
		memcpy(m_orderpacket.krxorder.board_id,			_T("G1"),				_countof(m_orderpacket.krxorder.board_id)); // 정규장
		memcpy(m_orderpacket.krxorder.memberno,			_T("00017"),			_countof(m_orderpacket.krxorder.memberno)); // kb
		memcpy(m_orderpacket.krxorder.bpno,				_T("00999"),			_countof(m_orderpacket.krxorder.bpno)); // kb
		memcpy(m_orderpacket.krxorder.ordno,			_T("0000000000"),			_countof(m_orderpacket.krxorder.ordno)); // 신규
		memcpy(m_orderpacket.krxorder.orgordno,			lpszOrgOrdNo,			_countof(m_orderpacket.krxorder.orgordno)); // 신규

		memcpy(m_orderpacket.krxorder.code, lpszExpCode, sizeof(m_orderpacket.krxorder.code));	// 종목코드 ex) kr4165rc0003
		m_orderpacket.krxorder.mmgubun[0]					= chMaemae;		// 매매구분1 매도 , 2 매수
		m_orderpacket.krxorder.hogagb[0]					= chTranType;		// 신규주문 1 신규, 2 정정, 3 취소
		memcpy(m_orderpacket.krxorder.gyejwa, lpszAccount, sizeof(m_orderpacket.krxorder.gyejwa));// 계좌번호
		_stprintf_s(m_szTempQty, sizeof(m_szTempQty),	_T("%010d"),	nQty);			// 주문수량
		memcpy(m_orderpacket.krxorder.cnt,		m_szTempQty,	ORDER_QTY_LEN);		// 주문수량
		memcpy(m_orderpacket.krxorder.price,			_T("00000000.00"),		_countof(m_orderpacket.krxorder.price)); // 주문가격 소수점 포함 우측정렬. 앞에는 0 채우기
		memset(m_orderpacket.krxorder.ord_type,			0x20,				_countof(m_orderpacket.krxorder.ord_type)); // 지정가.  1.시장가, i 조건부지정가, x 최유리지정가
		memset(m_orderpacket.krxorder.ord_cond,			0x20,				_countof(m_orderpacket.krxorder.ord_cond)); // 호가조건코드. 0 일반, 3 ioc, 4 fok
		memcpy(m_orderpacket.krxorder.market_ord_num,	_T("00000000000"),		_countof(m_orderpacket.krxorder.market_ord_num));//시장조성자호가구분번호. 일반
		memset(m_orderpacket.krxorder.stock_state_id,	0x20,			_countof(m_orderpacket.krxorder.stock_state_id)); // 자사주신고서id. 해당없음
		memset(m_orderpacket.krxorder.stock_trade_code,	0x20,				_countof(m_orderpacket.krxorder.stock_trade_code)); // 자사주매매방법코드. 해당없음
		memset(m_orderpacket.krxorder.medo_type_code,	0x20,				_countof(m_orderpacket.krxorder.medo_type_code)); // 매도유행코드. 해당없음
		memset(m_orderpacket.krxorder.singb,			0x20,				_countof(m_orderpacket.krxorder.singb)); // 신용구분코드. 보통(일반)
		memset(m_orderpacket.krxorder.witak,			0x20,				_countof(m_orderpacket.krxorder.witak)); // 위탁자기구분코드. 호가입력회원의 자기거래
		memset(m_orderpacket.krxorder.witakcomp_num,	0x20,					_countof(m_orderpacket.krxorder.witakcomp_num)); // 위탁사번호
		memcpy(m_orderpacket.krxorder.pt_type_code,		_T("00"),				_countof(m_orderpacket.krxorder.pt_type_code)); // pt 구분코드 일반.
		memset(m_orderpacket.krxorder.sub_stock_gyejwa,	0x20,					_countof(m_orderpacket.krxorder.sub_stock_gyejwa)); // 대용주권계좌번호
		memset(m_orderpacket.krxorder.gyejwa_type_code,	0x20,				_countof(m_orderpacket.krxorder.gyejwa_type_code)); // 계좌구분코드 : 41 자기일반, 61 알고리즘계좌
		memset(m_orderpacket.krxorder.gyejwa_margin_cod,0x20,				_countof(m_orderpacket.krxorder.gyejwa_margin_cod)); // 계좌증거금유형코드 : 11 사후증거금
		memset(m_orderpacket.krxorder.kukga,			0x20,				_countof(m_orderpacket.krxorder.kukga)); // 국가코드 410 한국
		memset(m_orderpacket.krxorder.tocode,			0x20,				_countof(m_orderpacket.krxorder.tocode)); // 투자자구분코드
		memset(m_orderpacket.krxorder.foreign,			0x20,				_countof(m_orderpacket.krxorder.foreign)); // 외국인투자자구분코드
		memcpy(m_orderpacket.krxorder.meache_gb,		_T("1"),				_countof(m_orderpacket.krxorder.meache_gb)); // 주문매체구분코드
		memcpy(m_orderpacket.krxorder.term_no,			_T("192168020222"),		_countof(m_orderpacket.krxorder.term_no)); // 주문자식별정보. 사용자pc ip : 192.168.20.222 -> 192168020222
		memcpy(m_orderpacket.krxorder.mac_addr,			_T("AAAAAA008324"),		_countof(m_orderpacket.krxorder.mac_addr)); // 사용자pc mac : aa-aa-aa-00-83-24 -> aaaaaa008324
		memcpy(m_orderpacket.krxorder.ord_date,			strDate,				sizeof(m_orderpacket.krxorder.ord_date));
		memset(m_orderpacket.krxorder.ord_time,			0x20,					_countof(m_orderpacket.krxorder.ord_time)); // 회원사주문시각. 일단 space로
		memset(m_orderpacket.krxorder.hoiwon,			0x20,					_countof(m_orderpacket.krxorder.hoiwon)); // 회원사용영역. 일단 space로
		memset(m_orderpacket.krxorder.pgm_gongsi_gb,	0x20,					_countof(m_orderpacket.krxorder.pgm_gongsi_gb)); // 프로그램호가 신고 구분코드. 일단 space

/*		// 원주문번호
		memcpy(m_OrderPacket.KrxOrder.org_ord_no,	lpszOrgOrdNo,	_countof(m_OrderPacket.KrxOrder.org_ord_no));
		// 호가가격			- 취소주문은 가격이 0
		memcpy(m_OrderPacket.KrxOrder.price,		_T("00000000.00"),	sizeof(m_OrderPacket.KrxOrder.price));	// 가격

		memset(m_OrderPacket.header.org_ord_prc,	' ',						_countof(m_OrderPacket.header.org_ord_prc));

		memset(m_OrderPacket.KrxOrder.stock_state_id,		0x20,				_countof(m_OrderPacket.KrxOrder.stock_state_id));
		memset(m_OrderPacket.KrxOrder.stock_trade_code,		0x20,				_countof(m_OrderPacket.KrxOrder.stock_trade_code));
		memset(m_OrderPacket.KrxOrder.medo_type_code,		0x20,				_countof(m_OrderPacket.KrxOrder.medo_type_code));
		memset(m_OrderPacket.KrxOrder.singb,				0x20,				_countof(m_OrderPacket.KrxOrder.singb));
		memset(m_OrderPacket.KrxOrder.gyejwa_type_code,		0x20,				_countof(m_OrderPacket.KrxOrder.gyejwa_type_code));
		memset(m_OrderPacket.KrxOrder.gyejwa_margin_cod,	0x20,				_countof(m_OrderPacket.KrxOrder.gyejwa_margin_cod));
		memset(m_OrderPacket.KrxOrder.kukga,				0x20,				_countof(m_OrderPacket.KrxOrder.kukga));
		memset(m_OrderPacket.KrxOrder.tocode,				0x20,				_countof(m_OrderPacket.KrxOrder.tocode));
		memset(m_OrderPacket.KrxOrder.foreign,				0x20,				_countof(m_OrderPacket.KrxOrder.foreign));
		memset(m_OrderPacket.KrxOrder.witak,				0x20,				_countof(m_OrderPacket.KrxOrder.witak));
		memset(m_OrderPacket.KrxOrder.ord_type,				0x20,				_countof(m_OrderPacket.KrxOrder.ord_type));
		memset(m_OrderPacket.KrxOrder.ord_cond,				0x20,				_countof(m_OrderPacket.KrxOrder.ord_cond));
*/
		break;
	default:
		ASSERT(FALSE);
		return FALSE;
		break;
	}
/*	// 일련번호				- 기본값 0으로 Setting
	// 트랜잭션코드
	m_OrderPacket.KrxOrder.trans_code[10]				= chTranType;		// 신규
	// 정규시간외구분코드		- 선물옵션은 무조건 정규장 Setting
	// 회원번호				- 기본값 Setting
	// 지점번호				- 계좌번호에서 구하네, 계좌변경시 Settting
	// 주문번호				- 기본값 0으로 Setting
	// 원주문번호			- 위 Switch에서 Setting
	// 표준종목코드
	memcpy(m_OrderPacket.KrxOrder.code, lpszExpCode, sizeof(m_OrderPacket.KrxOrder.code));
	// 매도/매수 구분
	m_OrderPacket.KrxOrder.mmgubun[0]					= chMaemae;		// 매매구분
	// 신규/정정/취소 구분
	m_OrderPacket.KrxOrder.hogagb[0]					= chTranType;		// 신규주문
	// 계좌번호
	memcpy(m_OrderPacket.KrxOrder.gyejwa, lpszAccount, sizeof(m_OrderPacket.KrxOrder.gyejwa));
	// 호가수량
	_stprintf_s(m_szTempQty, sizeof(m_szTempQty),	_T("%010d"),	nQty);			// 주문수량
	memcpy(m_OrderPacket.KrxOrder.cnt,		m_szTempQty,	ORDER_QTY_LEN);	// 주문수량

	// 호가가격				- 위 Switch에서 Setting	
	// 시장조성자호가구분번호	- 기본값 0으로 Setting
	// 자사주신고서ID			- 기본값 0으로 Setting
	// 자사주매매방법코드		- 기본값 0으로 Setting
	// 매도유형코드			- 기본값 0으로 Setting
	// 신용구분코드			- 기본값 10으로 Setting
	// 위탁자기구분코드		- 기본값 11으로 Setting
	// 위탁사번호			- 파생상품의 경우 미사용
	// PT 구분코드			- 기본값 0으로 Setting
	// 대용주권계좌번호
	// 계좌구분코드			- 기본값 31으로 Setting
	// 계좌증거금유형코드		- 기본값 10으로 Setting
	// 국가코드				- 기본값 410으로 Setting
	// 투자자구분코드
	// 외국인투자자구분코드	- 기본값 0으로 Setting
	// 주문매체구분코드		- 기본값 4로 Setting
	// 주문자식별정보		- 사용자 PC IP Setting

	// 호가일자				- 현재일자 Setting
	CTime t = CTime::GetCurrentTime();
	CString strDate;
	strDate.Format(_T("%04d%02d%02d"), t.GetYear(), t.GetMonth(), t.GetDay());
	memcpy(m_OrderPacket.KrxOrder.ord_date, strDate, sizeof(m_OrderPacket.KrxOrder.ord_date));*/
	// 회원사주문시각

	return TRUE;
}
void CAPISampleDlg::OnBnClickedButtonOrderClear()
{
	m_ctrlOrderList.ResetContent();
}

void CAPISampleDlg::OnLbnSelchangeListOrderOut()
{

	CString strMsg, strOrgOrdNo;

	//int nSel = m_ctrlOrderList.GetCurSel();
	//if(nSel == CB_ERR)
	//{
	//	OnLbnSelcancelListOrderOut();
	//	return;
	//}	
	//m_ctrlOrderList.GetText(nSel, strMsg);
	//if(strMsg.IsEmpty() || strMsg.GetLength() <= 5)
	//	return;
	
	int nSel2 = m_ctrlOrderList2.GetCurSel();
	if(nSel2 == CB_ERR)
	{
		OnLbnSelcancelListOrderOut();
		return;
	}	
	m_ctrlOrderList2.GetText(nSel2, strMsg);
	if(strMsg.IsEmpty() || strMsg.GetLength() <= 5)
		return;
	
	SetDlgItemText(IDC_EDIT_SELECT, strMsg);
	
	//주문패킷에서 주문번호를 가져온다.
	{

	}
	
	if( !strOrgOrdNo.IsEmpty() )
	{
		SetOrderControlStatus(TRUE);
		m_editOrgOrdNo.SetWindowText(strOrgOrdNo);
	}
	else
	{
		SetOrderControlStatus(TRUE);
		m_editOrgOrdNo.SetWindowText(_T(""));
	}
}

void CAPISampleDlg::OnLbnSelcancelListOrderOut()
{

	SetOrderControlStatus(TRUE);
	m_editOrgOrdNo.SetWindowText(_T(""));
}

void CAPISampleDlg::SetOrderControlStatus(BOOL bEnable)
{
	m_comboOrderType.EnableWindow(FALSE);
	m_comboOrderCond.EnableWindow(FALSE);
	
	m_editOrgOrdNo.EnableWindow(bEnable);
	m_btnModify.EnableWindow(bEnable);
	m_btnCancel.EnableWindow(bEnable);
	
}

void CAPISampleDlg::OnCbnSelchangeComboOrderType()
{

	CString strType;
	int nSel = m_comboOrderType.GetCurSel();
	if(nSel == CB_ERR)		return;
	m_comboOrderType.GetLBText(nSel, strType);
	if( strType.Left(1) == _T("X") || strType.Left(1) == _T("1") )
	{
		m_editOrderPrice.SetWindowText(_T("0.00"));
		m_editOrderPrice.EnableWindow(FALSE);
	}
	else
	{
		m_editOrderPrice.EnableWindow(TRUE);
	}

	if( strType.Left(1) == _T("I") )
	{
		m_comboOrderCond.SetCurSel(0);
		m_comboOrderCond.EnableWindow(FALSE);
	}
	else
	{
		m_comboOrderCond.EnableWindow(TRUE);
	}
}


void CAPISampleDlg::OnLbnSelchangeListTrOut()
{
	// TODO: 여기에 컨트롤 알림 처리기 코드를 추가합니다.
	int nSel = m_ctrlTRList.GetCurSel();
	if( nSel != CB_ERR )
	{
		CString strMsg;
		m_ctrlTRList.GetText(nSel,strMsg);
		SetDlgItemText(IDC_EDIT_SELECT, strMsg);
	}
}


void CAPISampleDlg::OnLbnSelchangeListSiseOut()
{

	int nSel = m_ctrlSiseList.GetCurSel();
	if( nSel != CB_ERR )
	{
		CString strMsg;
		m_ctrlSiseList.GetText(nSel,strMsg);
		SetDlgItemText(IDC_EDIT_SELECT, strMsg);
	}
}


