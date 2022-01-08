#include "ThreeWayPacket.h"
TWHPacket::TWHPacket(char* data)
{
    protocol = (uint8_t)data[0];
    action = (uint8_t)data[1];
    memcpy((unsigned char *)&origin, &data[2], 2);
    memcpy((unsigned char *)&destination, &data[4], 2);
    memcpy((unsigned char *)&SN, &data[6], 2);
    memcpy((unsigned char *)&RN, &data[8], 2);
    origin = ntohs(origin);
    destination = ntohs(destination);
    SN = ntohs(SN);
    RN = ntohs(RN);
    size = 10;
}

uint8_t TWHPacket::getProtocol() const 
{
    return protocol;
}

uint8_t TWHPacket::getAction()
{
    return action;
}

ushort TWHPacket::getSize() const 
{
    return size;
}
        
char* TWHPacket::deconstruct() const 
{
    char *buffer = new char[10]();
    //bzero(buffer, 10);
    memcpy(&buffer[0], (unsigned char *)&protocol, 1);
    unsigned short n_origin = htons(origin);
    unsigned short n_destination = htons(destination);
    unsigned short n_SN = htons(SN);
    unsigned short n_RN = htons(RN);
    memcpy(&buffer[1], (unsigned char *)&action, 1);
    memcpy(&buffer[2], (unsigned char *)&n_origin, 2);
    memcpy(&buffer[4], (unsigned char *)&n_destination, 2);
    memcpy(&buffer[6], (unsigned char *)&n_SN, 2);
    memcpy(&buffer[8], (unsigned char *)&n_RN, 2);
    return buffer;
}

ushort TWHPacket::getDestination() const
{
    return destination;
}

ushort TWHPacket::getOrigin() const
{
    return origin;
}

ushort TWHPacket::getSN() const
{
    return SN;
}

ushort TWHPacket::getRN() const
{
    return RN;
}
