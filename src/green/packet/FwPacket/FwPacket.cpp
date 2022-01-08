#include "FwPacket.h"
// Designa cada valor respectivo a partir de un strign de bytes.
// Recive: string binario en formato de paquete de fordwarding.
FwPacket::FwPacket(char *data)
{
    protocol = (uint8_t)data[0];
    memcpy((unsigned char *)&origin, &data[1], 2);
    memcpy((unsigned char *)&destination, &data[3], 2);
    memcpy((unsigned char *)&msg_num, &data[5], 2);
    origin   = ntohs(origin);
    destination = ntohs(destination);
    msg_num = ntohs(msg_num);
    payload = std::string(&data[9]);
    size = 9 + payload.size();
}

uint8_t FwPacket::getProtocol() const
{
    return protocol;
}

ushort FwPacket::getSize() const
{
    return size;
}

ushort FwPacket::getDestination() const
{
    return this->destination;
}

ushort FwPacket::getOrigin() const
{
    return this->origin;
}

ushort FwPacket::getMsgNumber() const
{
    return this->msg_num;
}

std::string FwPacket::getPayload() const
{
    return payload;
}

char *FwPacket::deconstruct() const
{
    char *buffer = new char[209]();
    bzero(buffer, 209);
    memcpy(buffer, (unsigned char *)&protocol, 1);
    ushort new_origin = htons(origin);
    ushort new_destination = htons(destination);
    ushort new_msg_num = htons(msg_num);
    memcpy(&buffer[1], (unsigned char *)&new_origin, 2);
    memcpy(&buffer[3], (unsigned char *)&new_destination, 2);
    memcpy(&buffer[5], (unsigned char *)&new_msg_num, 2);
    strcpy(&buffer[9], payload.c_str());
    return buffer;
}