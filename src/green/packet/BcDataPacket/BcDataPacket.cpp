#include "BcDataPacket.h"
// Designa cada valor respectivo a partir de un string de bytes.
// Recive: string binario en formato de paquete de broadcast.
BcDataPacket::BcDataPacket(char *data)
{
   memcpy((unsigned char *)&protocol, data, 1);
   memcpy((unsigned char *)&origin_nb, &data[1], 2);
   origin_nb = ntohs(origin_nb);
   memcpy((unsigned char *)&ttl, &data[3], 1);
   data_packet = std::make_shared<FwPacket>(&data[4]);
   size = 4 + data_packet->getSize(); 
}

uint8_t BcDataPacket::getProtocol() const
{
    return protocol;
}

ushort BcDataPacket::getSize() const
{
    return size;
}

ushort BcDataPacket::getOriginNb() const
{
    return this->origin_nb;
}

uint8_t BcDataPacket::getTtl() const
{
    return ttl;
}

void BcDataPacket::setOriginNb(ushort id)
{
    origin_nb = id;
}

void BcDataPacket::minusTtl() 
{
    ttl -= 1;
}


void BcDataPacket::setTtl(uint8_t ttl)
{
    this->ttl = ttl;
}

uint8_t BcDataPacket::getBcProtocol() const
{
    return data_packet->getProtocol();
}


char *BcDataPacket::deconstruct() const
{
    char *buffer = new char[this->getSize()]();
    ushort new_origin_nb = htons(origin_nb);
    memcpy(&buffer[0], (unsigned char *)&protocol, 1);
	memcpy(&buffer[1], (unsigned char *)&new_origin_nb, 2);
	memcpy(&buffer[3], (unsigned char *)&ttl, 1);
    char *data = data_packet->deconstruct();
    memcpy(&buffer[4], data, data_packet->getSize());

    delete [] data; 
    return buffer;
}