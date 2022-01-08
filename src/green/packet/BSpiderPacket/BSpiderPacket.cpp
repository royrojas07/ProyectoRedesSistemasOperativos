#include "BSpiderPacket.h"

BSpiderPacket::BSpiderPacket()
{
    protocol = 105;
    size = 9;
}

BSpiderPacket::BSpiderPacket(char *data)
{
    protocol = (uint8_t)data[0];
    std::cout << &data[1] << std::endl;
    strcpy(payload, &data[1]);
    size = 1 + strlen(payload);
}

uint8_t BSpiderPacket::getProtocol() const
{
    return protocol;
}

ushort BSpiderPacket::getSize() const
{
    return size;
}

char *BSpiderPacket::deconstruct() const
{
    char *buffer = new char[this->size];
    memcpy(&buffer[0], &protocol, 1);
    strcpy(&buffer[1], payload);
    return buffer;
}