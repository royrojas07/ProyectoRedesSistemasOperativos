#ifndef BCUPACKET
#define BCUPACKET

#include "../Packet/Packet.h"

// Derivada de la estructura Packet, contiene el formato de
// mensajes de actualizacion de tabla arbol generador.
struct BcUPacket : public Packet
{
    public:
        ushort Nb_id;

        BcUPacket(char *);
        ~BcUPacket(){};
        uint8_t getProtocol() const override;
        ushort getSize() const override;
        ushort getNbId();
        char* deconstruct()  const override;
};
#endif
