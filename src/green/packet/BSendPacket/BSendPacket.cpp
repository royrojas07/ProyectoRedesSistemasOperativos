#include "BSendPacket.h"

BSendPacket::BSendPacket()
{
    protocol = 100;
    size = 205;
}

BSendPacket::BSendPacket(char *data)
{
    protocol = (uint8_t)data[0];
    memcpy((unsigned char *)&origin, &data[1], 2);
    memcpy((unsigned char *)&msg_num, &data[3], 2);
    payload = std::string(&data[5]);
    size = 205;
}

uint8_t BSendPacket::getProtocol() const
{
    return protocol;
}

ushort BSendPacket::getSize() const
{
    return size;
}
ushort BSendPacket::getOrigin() const
{
    return this->origin;
}

ushort BSendPacket::getMsgNumber() const
{
    return this->msg_num;
}

std::string BSendPacket::getPayload() const
{
    return payload;
}

char *BSendPacket::deconstruct() const
{
    char *buffer = new char[205];
    ushort new_origin = htons(origin);
    ushort new_destino = htons(destino);
    ushort new_msg_num = htons(msg_num);
    memcpy(&buffer[0], &protocol, 1);
    memcpy(&buffer[1], (unsigned char *)&new_origin, 2);
    memcpy(&buffer[3], (unsigned char *)&new_destino, 2);
    memcpy(&buffer[5], (unsigned char *)&new_msg_num, 2);
    strcpy(&buffer[7], payload.c_str());
    return buffer;
}