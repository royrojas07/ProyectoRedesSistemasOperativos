#ifndef BCADYPACKET
#define BCADYPACKET
#include <vector>
#include "../BcPacket/BcPacket.h"
#include <utility>

struct BcAdyPacket : public BcPacket
{
public:
    ushort origin_nb;
    uint8_t nb_count;
    ushort origin_node;
    //Indica las adyacencias.
    std::vector<std::pair</* Node id */ushort, /* Distance */ uint8_t>> adyacencias;
    // Usado para indicar al enviar a un vecino a cuál debe ir.

    BcAdyPacket(char *);
    BcAdyPacket(){};
    ~BcAdyPacket(){};
    uint8_t getProtocol() const override;
    void setOriginNb(ushort) override;
    ushort getSize() const override;
    char *deconstruct() const override;
    uint8_t getTtl() const override;
    void minusTtl() override;
    uint8_t getBcProtocol() const override;
    void setTtl(uint8_t) override;
    ushort getOriginNb() const override;
    uint8_t getNbCount() const;
};


#endif