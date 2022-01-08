#ifndef STATS_MANAGER_H // include guard
#define STATS_MANAGER_H
#include <iostream> // cout
#include "../packet/Packet/PHeaders.h"
#include "../transport_layer/transport_layer.h"
#include "../link_layer/LinkLayer.h"
#include "../network_layer/NetworkLayer.h" // NetworkLayer

#include "../log/log.h"
#include "../agent/RoseAgent.h"
#include "../struct/structs.h"
#include <vector>
#include <memory>
#include <fcntl.h>
#include <unistd.h>  
#include <fcntl.h>	
#include <map>
#include <string>
#include <queue>
#include <pthread.h>


#define FWDTABLE 1
#define NGHBLIST 2

#define RECVPACKORIGN 4
#define SENDPACK  5
#define RECVPACKALL 6
#define BCFWPACK 7


class LinkLayer;
class Log;
class TransportLayer;
class RoseAgent;
class NetworkLayer;
class StatsManager
{
private:
    /* Atributos */
    NetworkLayer* network_layer;
    RoseAgent* rose_agent;
	LinkLayer* link_layer;
	// pthread_t assign, send, recv;
	my_data_t* my_data;

    Log* log;
    // std::queue<std::shared_ptr<Packet>> spider_queue;
    packet_queue spider_queue;
    
    pthread_t threads;

    std::vector</* indice en nb_data */ int > bc_table;
    
    std::map</* Node id */ushort, /* Neighbor */ int>  neighbours_id;
    std::map</* Node id */ushort, /* Neighbor */ int>  fwd_table;
    std::map</* Node id */ushort, /* Neighbor */ int>  recv_all_nghb;
    std::map</* Node id */ushort, /* Neighbor */ int> recv_dest_nghb;
    std::map</* Node id */ushort, /* Neighbor */ int> send_nghb;
    
    /* Efecto: Clasifica los paquetes de aranas
     * Requiere: Nada
     * Modifica: cola donde se almacenan los paquetes de aranas.
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    static void * spider_assign(void *data);

    void neighbors_updt();

   /* Efecto: Recolecta la tabla de forwarding
     * Requiere: Map donde almacena la tabla de forward.
     * Modifica: Variable local de la tabla de forward.
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    void fwd_table_stat();

    /* Efecto: Recolecta la tabla de arbol generador
    pthread_mutex_init(&mutex, 0);
     * Requiere: Map donde almacena la tabla de arbol generador
     * Modifica: Variable local de la tabla de arbol generador
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    void AG_nghb_stat();


    /* Efecto: Recolecta la tabla de todos los paquetes recibidos
     * Requiere: Map donde almacena la tabla de todos los paquetes recibidos.
     * Modifica: Variable local de la tabla de todos los paquetes recibidos.
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    void recv_packets_all_stat();

     /* Efecto: Recolecta la tabla de paquetes enviados
     * Requiere: Map donde almacena la tabla de paquetes enviados.
     * Modifica: Variable local de la tabla de paquetes enviados.
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    void send_packets_stat();
    
     /* Efecto: Recolecta ltablea tabla de paquetes destinados a mi nodo
     * Requiere: Map donde almacena la tabla de paquetes destinados a mi nodo.
     * Modifica: Variable local de la tabla de paquetes destinados a mi nodo.
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    void recv_packets_stat();
    
     /* Efecto: Recolecta la cantidad de paquetes forward y broadcast
     * Requiere: variables donde almacena la cantidad de paquetes forward y broadcast.
     * Modifica: Variable local donde almacena la cantidad de paquetes forward y broadcast
     * Retorna: No aplica. 
     * Autor: Pablo Cheng Galdamez
     */
    void bcast_fw_stat();
public:

    StatsManager();
    ~StatsManager();
    
    /* Efecto: Imprime todas las estadisticas
     * Requiere: Nada
     * Modifica: Nada
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    void print_stats();

    /* Efecto: Almacena en la cola, los paquetes de aranas
     * Requiere: Nada
     * Modifica: cola de paquetes
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    int spider_queue_store(std::shared_ptr<Packet> p);

    /* Efecto: Envia paquete de estadisticas con formato
        tabla al rose agent para enviarla al rosado 
     * Requiere: Tabla con estadistica, numero de request 
     *  y el id de la arana 
     * Modifica: Nada.
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    void send_table(std::map<ushort, int>, int8_t , int8_t, my_data_t*);
    
    /* Efecto: Envia paquete de stat con valores a 
        rose agent para enviarla al rosado 
     * Requiere: numero de request 
     *  y el id de la arana 
     * Modifica: Nada.
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    void send_counts( int8_t , int8_t);
        

    /* Efecto: Envia paquete de estadisticas con formato
        hilera al rose agent para enviarla al rosado 
     * Requiere: hilera con estadistica, numero de request 
     *  y el id de la arana 
     * Modifica: Nada.
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    void send_nghb_pack( int8_t , int8_t);
    
    /* Efecto: instancia los objetos de las otras capas
     * Requiere: Nada
     * Modifica: Instancia de la clase
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    void ptr_set(RoseAgent* rose_agent, NetworkLayer* network, LinkLayer *ll, my_data_t*my_data, Log* log);
        
    /* Efecto: Inicializa los hilos responsables de 
        responder las solicitudes
     * Requiere: Nada.
     * Modifica: Nada.
     * Retorna: Nada. 
     * Autor: Pablo Cheng Galdamez
     */
    int threads_init(StatsManager * sm);

};

#endif /* STATS_MANAGER_H */