#ifndef HBPACKET
#define HBPACKET

#include "../Packet/Packet.h"

// Derivada de la estructura Packet, contiene el formato de
// mensajes de para fordwarding.
struct HbPacket : public Packet
{
    public:
        ushort origin;
        ushort destination;
        uint8_t c;
        ushort SN;
        ushort RN;

        HbPacket(char *);
        ~HbPacket(){};
        uint8_t getProtocol() const override;
        ushort getSize() const override;
        ushort getDestination() const;
        ushort getOrigin() const;
        ushort getMsgNumber() const;
        std::string getPayload() const;
        char * deconstruct() const override;
};
#endif