#ifndef FTUPACKET
#define FTUPACKET
#include <vector>
#include "../BcPacket/BcPacket.h"
#include <utility>

struct FTUPacket : public Packet
{
public:
    uint8_t nodes_count;
    // Usado para indicar al enviar a un nodo por cuál vecino se debe ir.
    std::vector<std::pair</* Node id */ushort, /* Neighbor */ uint8_t>> entries;

    FTUPacket(char *);
    FTUPacket(){};
    ~FTUPacket(){};
    uint8_t getProtocol() const override;
    ushort getSize() const override;
    char *deconstruct() const override;
};

#endif