#ifndef FWPACKET
#define FWPACKET

#include "../Packet/Packet.h"

// Derivada de la estructura Packet, contiene el formato de
// mensajes de para fordwarding.
struct FwPacket : public Packet
{
    public:
        ushort origin;
        ushort destination;
        ushort msg_num;
        std::string payload;


        FwPacket(char *);
        ~FwPacket(){};
        uint8_t getProtocol() const override;
        ushort getSize() const override;
        char *deconstruct() const override;
        ushort getDestination() const;
        ushort getOrigin() const;
        ushort getMsgNumber() const;
        std::string getPayload() const;
};


#endif