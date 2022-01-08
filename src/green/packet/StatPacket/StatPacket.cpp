#include "StatPacket.h"
// Designa cada valor respectivo a partir de un strign de bytes.
// Recive: string binario en formato de paquete de fordwarding.
StatPacket::StatPacket(char *data, std::string payload1)
{
    protocol = (int8_t)data[0];
    memcpy((unsigned char *)&spider_id, &data[1], 1);
    memcpy((unsigned char *)&origen_id, &data[2], 1);

    memcpy((unsigned char *)&request, &data[3], 1);
    this->payload = payload1 + '-';

    size = this->payload.size() + 4;    
    // std::cout<<"Print payload"<<std::endl;
    // std::cout<< this->getPayload()<<std::endl;
}

StatPacket::StatPacket(char *data)
{
    protocol = (int8_t)data[0];
    memcpy((unsigned char *)&spider_id, &data[1], 1);
    memcpy((unsigned char *)&origen_id, &data[2], 1);
    memcpy((unsigned char *)&request, &data[3], 1);    
}


char *StatPacket::deconstruct() const
{
    char *buffer = new char[this->getSize()]();
    bzero(buffer, this->getSize());
    memcpy(buffer, (unsigned char *)&protocol, 1);
    memcpy(&buffer[1], (unsigned char *)&spider_id, 1);
    memcpy(&buffer[2], (unsigned char *)&origen_id, 1);

    memcpy(&buffer[3], (unsigned char *)&request, 1);
    strcpy(&buffer[4], payload.c_str());
    buffer[this->getSize()] = '\0';
    // for (size_t i = 0; i < payload.size(); i++)
    // {
    //     std::cout<< buffer [i + 4];
    // }
    // std::cout<< std::endl;

    // std::cout << (int) << std::endl;
    
    return buffer;
}

uint8_t StatPacket::getProtocol() const
{
    return protocol;
}

int8_t StatPacket::getRequest() const
{
    return request;
}

int8_t StatPacket::getSpiderId() const
{
    return spider_id;
}
ushort StatPacket::getSize() const
{
    return size;
}

std::string StatPacket::getPayload() const
{
    return payload;
}
