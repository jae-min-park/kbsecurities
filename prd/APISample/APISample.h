
// APISample.h : PROJECT_NAME ���� ���α׷��� ���� �� ��� �����Դϴ�.
//

#pragma once

#ifndef __AFXWIN_H__
	#error "PCH�� ���� �� ������ �����ϱ� ���� 'stdafx.h'�� �����մϴ�."
#endif

#include "resource.h"		// �� ��ȣ�Դϴ�.


// CAPISampleApp:
// �� Ŭ������ ������ ���ؼ��� APISample.cpp�� �����Ͻʽÿ�.
//

class CAPISampleApp : public CWinApp
{
public:
	CAPISampleApp();

// �������Դϴ�.
public:
	virtual BOOL InitInstance();

// �����Դϴ�.

	DECLARE_MESSAGE_MAP()
};

extern CAPISampleApp theApp;
