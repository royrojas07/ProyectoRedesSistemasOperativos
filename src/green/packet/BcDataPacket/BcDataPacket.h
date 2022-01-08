#ifndef BCDATAPACKET
#define BCDATAPACKET
#include "../Packet/PHeaders.h"
#include "memory"


struct BcDataPacket: public BcPacket{
    ushort origin_nb; 
    uint8_t bc_protocol;
    ushort origin_node;
    std::shared_ptr<FwPacket> data_packet;
    public: 
    BcDataPacket(char *);
    BcDataPacket();
    uint8_t getProtocol() const override;
    void setOriginNb(ushort) override;
    ushort getSize() const override;
    void setTtl(uint8_t) override;
    char *deconstruct() const override;
    uint8_t getTtl() const override;
    void minusTtl() override;
    uint8_t getBcProtocol() const override;
    ushort getOriginNb() const override;
    
};
#endif