#include "../../include/TRHeader/orderpacket.h"

typedef struct _ORDER_PACKET
{
	PACKET_HEAD header;
	KRX_ORDER krxorder;
} ORDER_PACKET;