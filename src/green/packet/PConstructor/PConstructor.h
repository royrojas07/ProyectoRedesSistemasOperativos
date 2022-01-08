#ifndef PCONS
#define PCONS
#include "../Packet/PHeaders.h"
#include <memory>
#include <stdint.h>

std::shared_ptr<Packet> packet_construct(char *data);

#endif

