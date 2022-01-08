#ifndef TWHPACKET
#define TWHPACKET

#include "../Packet/Packet.h"

// Derivada de la estructura Packet, contiene el formato de
// mensajes de para fordwarding.
struct TWHPacket : public Packet
{
    private:
        uint8_t action;
        unsigned short origin;
        unsigned short destination;
        unsigned short SN;
        unsigned short RN;
    public:



        TWHPacket(char *);
        ~TWHPacket(){};
        uint8_t getProtocol() const override;
        uint8_t getAction();
        ushort getSize() const override;
        char *deconstruct() const override;
        ushort getDestination() const;
        ushort getOrigin() const;
        ushort getSN() const;
        ushort getRN() const;
        
};
#endif