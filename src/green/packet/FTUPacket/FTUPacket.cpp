#include "FTUPacket.h"

FTUPacket::FTUPacket(char * data)
{
    protocol = (uint8_t) data[0];
    nodes_count = (uint8_t) data[1];
    size = 2;
    ushort node_id;
    uint8_t neighbor;
    for( int i = 0, e = 2; i < nodes_count; ++i, e += 3 )
    {
        memcpy(&node_id, &data[e], 2);
        node_id = ntohs(node_id);
        neighbor = data[e+2];
        entries.push_back(std::make_pair(node_id, neighbor));
        size += 3;
    }
}

uint8_t FTUPacket::getProtocol() const
{
    return protocol;
}

ushort FTUPacket::getSize() const
{
    return size;
}

char * FTUPacket::deconstruct() const
{
    ushort node_id;
    uint8_t neighbor;
    char * buffer = new char[getSize()]();
    buffer[0] = protocol;
    buffer[1] = nodes_count;
    for( int i = 0, e = 2; i < nodes_count; ++i, e += 3 )
    {
        node_id = htons(entries[i].first);
        neighbor = entries[i].second;
        memcpy(&buffer[e], (unsigned char *)&node_id, 2);
        buffer[e+2] = neighbor;
    }
    return buffer;
}