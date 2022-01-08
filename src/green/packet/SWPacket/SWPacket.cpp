#include "SWPacket.h"

SWPacket::SWPacket(char * data)
{
    payload = new char[MAXSIZE]();
    protocol = (int8_t) data[0];
    memcpy((unsigned char *)&origin, &data[1], 2);
    memcpy((unsigned char *)&destin, &data[3], 2);
    origin = ntohs(origin);
    destin = ntohs(destin);
    swc_id[0] = (int8_t) data[5];
    swc_id[1] = (int8_t) data[6];
    sn = (int8_t) data[7];
    rn = (int8_t) data[8];
    flags = (int8_t) data[9];
    entity = (int8_t) data[10];
    memcpy((unsigned char *)&payload_length, &data[11], 2);
    payload_length = ntohs(payload_length);
    memcpy(payload, &data[13], payload_length);
    size = 13+payload_length;
}

SWPacket::~SWPacket()
{
    delete payload;
}

uint8_t SWPacket::getProtocol() const
{
    return protocol;
}

ushort SWPacket::getSize() const
{
    return size;
}

char * SWPacket::deconstruct() const
{
    char *buffer = new char[MAXSIZE]();
    bzero(buffer, MAXSIZE);
    buffer[0] = protocol;
    short norigin = htons(origin);
    short ndestination = htons(destin);
    memcpy(&buffer[1], (unsigned char *)&norigin, 2);
    memcpy(&buffer[3], (unsigned char *)&ndestination, 2);
    buffer[5] = swc_id[0];
    buffer[6] = swc_id[1];
    buffer[7] = sn;
    buffer[8] = rn;
    buffer[9] = flags;
    buffer[10] = entity;
    short npayload_length = htons(payload_length);
    memcpy(&buffer[11], (unsigned char *)&npayload_length, 2);
    //strcpy(&buffer[12], payload.c_str());
    memcpy(&buffer[13], payload, payload_length);
    //memcpy(&buffer[12], payload, payload_length);
    return buffer;
}

short SWPacket::getDestination() const
{
    return destin;
}

short SWPacket::getOrigin() const
{
    return origin;
}