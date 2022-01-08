#include "HbPacket.h"
// Designa cada valor respectivo a partir de un strign de bytes.
// Recive: string binario en formato de paquete de heartbeat paquet.
HbPacket::HbPacket(char *data)
{
    protocol = (uint8_t)data[0];
    memcpy((unsigned char *)&origin, &data[1], 2);
    memcpy((unsigned char *)&destination, &data[3], 2);
    memcpy((unsigned char*)&c, &data[5], 1);
    memcpy((unsigned char *)&SN, &data[6], 2);
    memcpy((unsigned char *)&RN, &data[8], 2);
    origin = ntohs(origin);
    destination = ntohs(destination);
    SN = ntohs(SN);
    RN = ntohs(RN);
    size = 10;
}

uint8_t HbPacket::getProtocol() const
{
    return this->protocol;
}

ushort HbPacket::getDestination() const
{
    return this->destination;
}

ushort HbPacket::getOrigin() const
{
    return this->origin;
}

ushort HbPacket::getSize() const
{
    return size; 
}

char *HbPacket::deconstruct() const
{
    char *buffer = new char[10];
    bzero(buffer, 10);
    ushort new_origin = htons(origin);
    ushort new_destination = htons(destination);
    ushort new_SN = htons(SN);
    ushort new_RN = htons(RN);
    memcpy(&buffer[0], (unsigned char *)&protocol, 1);
    memcpy(&buffer[1], (unsigned char *)&new_origin, 2);
    memcpy(&buffer[3], (unsigned char *)&new_destination, 2);
    memcpy(&buffer[5], (unsigned char *)&c, 1);
    memcpy(&buffer[6], (unsigned char *)&new_SN, 2);
    memcpy(&buffer[8], (unsigned char *)&new_RN, 2);
    return buffer;
}