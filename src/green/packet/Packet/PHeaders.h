#include "../FwPacket/FwPacket.h"
#include "../BcAdyPacket/BcAdyPacket.h"
#include "../BSendPacket/BSendPacket.h"
#include "../PConstructor/PConstructor.h"
#include "../HbPacket/HbPacket.h"
#include "../BcUpdatePacket/BcUpdatePacket.h"
#include "../3WayHandshakePacket/ThreeWayPacket.h"
#include "../FTUPacket/FTUPacket.h"
#include "../BcDataPacket/BcDataPacket.h"
#include "../BSpiderPacket/BSpiderPacket.h"
#include "../SWPacket/SWPacket.h"
#include "../StatPacket/StatPacket.h"

#define FW_PACKET       0
#define BC_PACKET       1
#define BCADY_PACKET    3
#define BCDATA_PACKET   0
#define AG_PACKET       2
#define AD_PACKET       3
#define HB_PACKET       4
#define SW_PACKET       5
#define BSEND_PACKET    100
#define FTUPDATE_PACKET 101
#define BCUPDATE_PACKET 102
#define STAT_PACKET     104
#define BSPIDER_PACKET  105
#define BCDEST          65535
