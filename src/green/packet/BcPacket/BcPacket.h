#ifndef BCPACKET
#define BCPACKET

#include "../Packet/Packet.h"
#include <memory> 

// Derivada de la estructura Packet.
// Struct abstracto base para paquetes de broadcast. 
struct BcPacket: public Packet {
    public: 
        uint8_t bc_protocol;
        uint8_t ttl;

        virtual uint8_t getProtocol() const=0;
        virtual ushort getSize() const=0;
        virtual ushort getOriginNb() const=0;
        virtual uint8_t getBcProtocol() const=0;
        virtual void setOriginNb(ushort)=0;
        virtual void minusTtl()=0;
        virtual uint8_t getTtl() const=0;
        virtual void setTtl(uint8_t)=0;
        virtual char *deconstruct() const=0;
};
#endif