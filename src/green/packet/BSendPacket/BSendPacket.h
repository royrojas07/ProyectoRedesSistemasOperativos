#ifndef BSENDPACKET
#define BSENDPACKET
#include "../Packet/Packet.h"

struct BSendPacket : public Packet
{
    public:
        uint8_t protocol;
        ushort origin;
        ushort msg_num;
        ushort destino;
        std::string payload;
        // Usado para indicar al enviar a un vecino a cuál debe ir.

        BSendPacket(char *);
        BSendPacket();
        ~BSendPacket(){};
        uint8_t getProtocol() const override;
        ushort getSize() const override;
        char *deconstruct() const override;
        ushort getOrigin() const;
        ushort getMsgNumber() const;
        std::string getPayload() const;
};


#endif