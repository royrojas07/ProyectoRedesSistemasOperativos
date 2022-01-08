 #include "BcUpdatePacket.h"
 
 BcUPacket::BcUPacket(char* data)
 {
      protocol = (uint8_t)data[0];
      memcpy((unsigned char *)&Nb_id, &data[1], 2);
      Nb_id = htons(Nb_id);
      size = 3;
 }

uint8_t BcUPacket::getProtocol() const
{
    return protocol;
}

ushort BcUPacket::getSize() const
{
     return size;
}

ushort BcUPacket::getNbId()
{
    return Nb_id;
}

char* BcUPacket::deconstruct() const
{
    char *buffer = new char[3]();
    memcpy(&buffer, (unsigned char *)&protocol, 1);
    ushort new_Nb_id = htons(Nb_id);
    memcpy(&buffer[1], (unsigned char *)&new_Nb_id, 2);
    return buffer;
}