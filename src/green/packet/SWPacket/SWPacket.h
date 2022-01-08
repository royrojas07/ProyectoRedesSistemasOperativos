#ifndef SWPACKET
#define SWPACKET
#include <utility>
#include "../Packet/Packet.h"

#define MAXSIZE 4096

struct SWPacket : public Packet
{
public:
    short origin;
    short destin;
    /* Identificador de la conexion stop/wait */
    int8_t swc_id[2];
    int8_t sn;
    int8_t rn;
    /* banderas SYN, FIN, ACK */
    int8_t flags;
    int8_t entity;
    /* Tamano del payload */
    short payload_length;
    char *payload;
    //char payload[MAXSIZE];

    SWPacket(char *);
    SWPacket(){};
    ~SWPacket();
    uint8_t getProtocol() const override;
    ushort getSize() const override;
    char *deconstruct() const override;
    short getDestination() const;
    short getOrigin() const;
};

#endif