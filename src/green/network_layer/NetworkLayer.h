#ifndef NETWORK_LAYER_H // include guard
#define NETWORK_LAYER_H
#include <iostream> // cout
#include "../packet/Packet/PHeaders.h"
#include <memory>
#include "../transport_layer/transport_layer.h"
#include "../link_layer/LinkLayer.h"
#include "../log/log.h"
#include "../agent/RoseAgent.h"
#include "../struct/structs.h"
#include "../stats/StatsManager.h"

#include <map>
#include <utility> // make_pair()
#include <vector>
#include <algorithm> // find
#define NUM_THREADS_NETWORK 4
#define FW_THREAD 1
#define BC_THREAD 2
#define FW_UPD_THREAD 3
#define BC_UPD_THREAD 4
#define TTL_INIT 255
class LinkLayer;
class TransportLayer;
class RoseAgent;
class NetworkLayer
{
private:
    /* Atributos */
    my_data_t *my_data;
    LinkLayer *link_layer;
    RoseAgent * rose_agent;
    TransportLayer *transport_layer;
    StatsManager * stat_manager;

    Log * log;
	char log_msg[100];
    pthread_t threads[NUM_THREADS_NETWORK];

    /* Forwarding */
    std::map</* id */ ushort, /* route */ int> fw_table;
    std::map</* id */ ushort, /*stat */ int> neighbors_stat;
    std::map</* id */ ushort, /*stat */ int> recv_dest;
    std::map</* id */ ushort, /*stat */ int> recv_all;
    packet_queue fw_queue;
    packet_queue fw_upd_queue;
    pthread_mutex_t fw_mutex;
    /* Efecto: es corrido por un hilo, se encarga de enviar los paquetes de forwarding y para el host. 
               Recibe los paquetes a traves de la cola fw_queue
               Se queda dormido hasta que reciba paquetes por la cola. 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    void forward();
    /* Efecto: es corrido por un hilo, se encarga de actualizar fw_table cuando la capa de control se lo indique. 
               Recibe loa paquetes de actualizacion a travez de la cola fw_upd_queue.
               Se queda dormido hasta que reciba paquetes por la cola. 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    void fw_table_upd();
    /* Efecto: funcion objetivo del thread que correra la funcion forwarding.
     * Requiere: refencia a instancia de objeto clase NetworkLayer.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    static void *forward_by_thread(void *);
    /* Efecto: funcion objetivo del thread que correra la funcion fw_table_upd.
     * Requiere: refencia a instancia de objeto clase NetworkLayer.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    static void *fw_upd_by_thread(void *);
    /* Efecto: los mensajes de protocolo forwarding que tienen  destino local, 
               son enviados al host. 
     * Requiere: puntero inteligente de clase FwPacket dervada de Packet.
     * Modifica: No aplica.
     * Retorna: 0 si no hubo errores, 1 si hubo errores. 
     * Autor: Diego Murillo Porras.
     */
    int blue_data_send(shared_ptr<FwPacket>);
    /* Efecto: dado un id de vecino, su busca el indice de la posicion de ese vecino
               en la tabla de vecinos en my_data. 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: indice de la posicion del vecino dado en la tabla de vecinos. 
     * Autor: Diego Murillo Porras.
     */
    int find_nb_i(ushort);
    /* Efecto: inicializa la tabla de forwarding con los vecinos. 
     * Requiere: puntero a my_data inicializado. 
     * Modifica: No aplica.
     * Retorna: 0 si no hubo errores, 1 si hubo errores. 
     * Autor: Diego Murillo Porras.
     */
    int fw_table_init();

    /* Broadcast */ 

    std::vector</* indice en nb_data */ int > bc_table;
    packet_queue bc_queue;
    packet_queue bc_upd_queue;
    pthread_mutex_t bc_mutex;
    /* Efecto: es corrido por un hilo, se encarga de enviar los paquetes de broadcast. 
               Recibe loa paquetes a traves de la cola bc_queue
               Se queda dormido hasta que reciba paquetes por la cola. 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    void broadcast();
    /* Efecto: es corrido por un hilo, se encarga de actualizar bc_table cuando la capa de control se lo indique. 
               Recibe loa paquetes de actualizacion a travez de la cola bc_upd_queue.
               Se queda dormido hasta que reciba paquetes por la cola. 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    void bc_table_upd();
    /* Efecto: funcion objetivo del thread que correra la funcion broacast.
     * Requiere: refencia a instancia de objeto clase NetworkLayer.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    static void *broadcast_by_thread(void *);
    /* Efecto: funcion objetivo del thread que correra la funcion bc_table_upd.
     * Requiere: refencia a instancia de objeto clase NetworkLayer.
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    static void *bc_upd_by_thread(void *);
    /* Efecto: se encarga de enviar los mensajes de protocolo broadcast a los demas hilos que 
               necesiten del paquete. 
     * Requiere: puntero inteligente de clase BcPacket. 
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    void bc_local_send(shared_ptr<BcPacket>);



public:
    NetworkLayer();
    ~NetworkLayer();
    /* Efecto:  Inicializa los threads que estaran atendiendo los servicios de la clase. 
     * Requiere: instancia objeto de clase propia(NetworkLayer) 
     *           en el cual el thread utiliza para correr sobre. 
     * Modifica: No aplica
     * Retorna: 0 si no hubo errores, 1 si hubo errores. 
     * Autor: Diego Murillo Porras.
     */
     int threads_init(NetworkLayer *);
     /* Efecto: Asigna las referencias a las demas clases del programa y a mis datos. 
     * Requiere: referencias a instancias de objetos clase de tipo LinkLayer, TransportLayer,
     *           RoseAgent, my_data_t. 
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    void ptr_set(LinkLayer*, TransportLayer*, RoseAgent*, Log*, my_data_t*, StatsManager *);
    /* Efecto:  Metodo publica que usan los demas componentes para almacenar paquetes 
                de potocolo broadcast que seran utilizados en la funcionalidad de broadcast. 
     * Requiere: puntero inteligente de clase BcPacket derivada de Packet. 
     * Modifica: No aplica.
     * Retorna: 0 si no hubo errores, 1 si hubo errores. 
     * Autor: Diego Murillo Porras.
     */
    int bc_store(std::shared_ptr<Packet>);
    /* Efecto: Metodo publica que usan los demas componentes para almacenar paquetes 
               que seran utilizados en la funcionalidad de broadcast, no necesariamente
               deben ser de protocolo frodwarding, que seran utilizados por la funcionalidad 
               forwarding. 
     * Requiere: puntero inteligente de clase FwPacket derivada de Packet. 
     * Modifica: No aplica.
     * Retorna: 0 si no hubo errores, 1 si hubo errores. 
     * Autor: Diego Murillo Porras.
     */
    int fw_store(std::shared_ptr<Packet>);
    /* Efecto: Metodo publica que usan los demas componentes para almacenar paquetes 
               de protocolo broadcast table update que seran utilizados para actualizar la
               tablas de broadcast que seran utilizados por la funcionalidad bc_table_upd.
     * Requiere: puntero inteligente de clase BcUpdPacket derivada de Packet. 
     * Modifica: No aplica.
     * Retorna: No aplica.
     * Autor: Diego Murillo Porras.
     */
    int bc_upd_store(std::shared_ptr<Packet>);
    /* Efecto: Metodo publica que usan los demas componentes para almacenar paquetes 
               de protocolo forward table update que seran utilizados para actualizar la
               tablas de forwarding que seran utilizados por la funcionalidad fw_table_upd.
     * Requiere: puntero inteligente de clase FwUpdPacket derivada de Packet. 
     * Modifica: No aplica
     * Retorna: 0 si no hubo errores, 1 si hubo errores. 
     * Autor: Diego Murillo Porras.
     */
    int fw_upd_store(std::shared_ptr<Packet>);

     /* Efecto: Devuelve la tabla de forward
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: Tabla de forward en formado map. 
     * Autor: Pablo Cheng Galdamez
     */
    std::map<ushort, int > get_fw_table();

    /* Efecto: Devuelve la tabla de arbol generador
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: Tabla de arbol generador en formado map. 
     * Autor: Pablo Cheng Galdamez
     */
    std::vector< int > get_AG();

    /* Efecto: Devuelve la tabla de todos los mensajes recibidos para mi
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: Tabla de todos los mensajes recibidos para mi
     * Autor: Pablo Cheng Galdamez
     */
    std::map<ushort, int> get_recv_dest();

    /* Efecto: Devuelve la tabla de todos los mensajes recibidos 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: Tabla de todos los mensajes recibidos 
     * Autor: Pablo Cheng Galdamez
     */
    std::map<ushort, int> get_recv_all();
   

};

#endif /* NETWORK_LAYER_H */