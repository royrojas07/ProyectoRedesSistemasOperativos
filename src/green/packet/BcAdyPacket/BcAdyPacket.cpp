#include "BcAdyPacket.h"
// Designa cada valor respectivo a partir de un string de bytes.
// Recive: string binario en formato de paquete de broadcast.
BcAdyPacket::BcAdyPacket(char *data)
{
    protocol    = (uint8_t)data[0];
    memcpy((unsigned char *)&origin_nb, &data[1], 2);
    ttl         = (uint8_t)data[3];
    bc_protocol = (uint8_t)data[4];
    memcpy((unsigned char *)&origin_node, &data[5], 2);
    nb_count    = (uint8_t)data[7];
    origin_nb   = ntohs(origin_nb);
    origin_node = ntohs(origin_node);
    size = 8;
    ushort id;
    uint8_t distance;
    for (int i = 0, e = 8; i < nb_count; ++i)
    {
        memcpy((unsigned char *)&id, &data[e], 2);
        id = ntohs(id);
        e = e + 2;
        distance = (uint8_t)data[e];
        e = e + 1;
        adyacencias.push_back(std::make_pair(id, distance));
        size += 3;
    }
}

uint8_t BcAdyPacket::getProtocol() const
{
    return protocol;
}

ushort BcAdyPacket::getSize() const
{
    return size;
}

ushort BcAdyPacket::getOriginNb() const
{
    return this->origin_nb;
}

uint8_t BcAdyPacket::getTtl() const
{
    return ttl;
}

void BcAdyPacket::setTtl(uint8_t ttl)
{
    this->ttl = ttl;
}

void BcAdyPacket::setOriginNb(ushort id)
{
    origin_nb = id;
}

void BcAdyPacket::minusTtl() 
{
    ttl -= 1;
}

uint8_t BcAdyPacket::getBcProtocol() const
{
    return bc_protocol;
}

uint8_t BcAdyPacket::getNbCount() const
{
    return this->nb_count;
}

char *BcAdyPacket::deconstruct() const
{
    ushort id;
    uint8_t distance;
    char *buffer = new char[this->getSize()]();
    ushort new_origin_nb   = htons(this->origin_nb);
    ushort new_origin_node = htons(this->origin_node);
    memcpy(&buffer[0], (unsigned char *)&protocol, 1);
    memcpy(&buffer[1], (unsigned char *)&new_origin_nb, 2);
    memcpy(&buffer[3], (unsigned char *)&ttl, 1);
    memcpy(&buffer[4], (unsigned char *)&bc_protocol, 1);
    memcpy(&buffer[5], (unsigned char *)&new_origin_node, 2);
    memcpy(&buffer[7], (unsigned char *)&nb_count, 1);
    for (int i = 0, e = 8; i < adyacencias.size(); ++i)
    {
        id = htons(adyacencias[i].first);
        distance = adyacencias[i].second;
        memcpy(&buffer[e], (unsigned char *)&id, 2);
        memcpy(&buffer[e + 2], (unsigned char *)&distance, 1);
        e += 3;
    }
    return buffer;
}