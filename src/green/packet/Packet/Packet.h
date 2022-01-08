#ifndef PACKET
#define PACKET
#include <iostream> 
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>

// Estructura base abstracta para cada estructura de paquetes. 
struct Packet {
    public: 
        ushort size; 
        uint8_t protocol;
        
        virtual uint8_t getProtocol() const=0;
         /* Efecto: retrona la longitud de bytes que posee el paquete en el formato binario. 
          * Retorna: longitud de bytes. 
          */
        virtual ushort getSize() const=0;
        /* Efecto: a partir de un formato binario de paquete, instancia los atributos respectivos del paquete. 
        */
        virtual char* deconstruct() const=0;
};


#endif
