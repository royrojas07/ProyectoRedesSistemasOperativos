#include "PConstructor.h"

std::shared_ptr<Packet> packet_construct(char *data)
{
    std::shared_ptr<Packet> packet;
    int8_t p = (int8_t)data[0];
    switch (p)
    {
        case FW_PACKET: /* Fordward */
            {
                packet = std::make_shared<FwPacket>(data);
                break;
            }
            
        case BC_PACKET: /* Broadcast */
            {
                int8_t bcP = (int8_t)data[4];
                switch (bcP)
                {
                    case AD_PACKET: /* Adyacentes */
                        {
                            packet = std::make_shared<BcAdyPacket>(data);
                            break;
                        }
                    case BCDATA_PACKET:
                        {
                            packet = std::make_shared<BcDataPacket>(data);
                            break;
                        }
                }
                break;
            }

        case AG_PACKET: /* Arbol Generador */
            {
                packet = std::make_shared<TWHPacket>(data);
                break;
            }

        case HB_PACKET: /* Heartbeat */
            {
                packet = std::make_shared<HbPacket>(data);
                break;
            }

        case BSEND_PACKET:
            {
                packet = std::make_shared<BSendPacket>(data);
                break;
            }
        case BCUPDATE_PACKET:
            {
                packet = std::make_shared<BcUPacket>(data);
                break;
            }
        case FTUPDATE_PACKET:
            {
                packet = std::make_shared<FTUPacket>(data);
                break;
            }
        case BSPIDER_PACKET:
            {
                packet = std::make_shared<BSpiderPacket>(data);
                break;
            }
        case SW_PACKET:
            {
                packet = std::make_shared<SWPacket>(data);
                break;
            }
        case STAT_PACKET:
            {
                packet = std::make_shared<StatPacket>(data);
            }
    }

    return packet;
}

