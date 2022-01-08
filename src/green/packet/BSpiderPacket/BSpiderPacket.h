#ifndef BSPIDERPACKET
#define BSPIDERPACKET
#include "../Packet/Packet.h"

struct BSpiderPacket : public Packet
{
    public:
        char payload[100]; 
        // Usado para indicar al enviar a un vecino a cuál debe ir.

        BSpiderPacket(char *);
        BSpiderPacket();
        ~BSpiderPacket(){};
        uint8_t getProtocol() const override;
        ushort getSize() const override;
        char *deconstruct() const override;

};


#endif