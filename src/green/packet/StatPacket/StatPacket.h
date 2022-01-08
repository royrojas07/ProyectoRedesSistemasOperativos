#ifndef STATPACKET
#define STATPACKET

#include "../Packet/Packet.h"

// Derivada de la estructura Packet, contiene el formato de
// mensajes de para fordwarding.
struct StatPacket : public Packet
{
    public:

        int8_t request;
        int8_t spider_id;
        int8_t origen_id;
        std::string payload;

        StatPacket(char *, std::string  );
        StatPacket(char*);
        ~StatPacket(){};
        char *deconstruct() const override;
        
        uint8_t getProtocol() const override;
        ushort getSize() const override;
        
        int8_t getSpiderId() const;
        int8_t getRequest() const;
        std::string getPayload() const;
};


#endif