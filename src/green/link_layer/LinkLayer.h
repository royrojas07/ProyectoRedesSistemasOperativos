#ifndef LINK_LAYER_H // include guard
#define LINK_LAYER_H
#include <stdlib.h>
#include <sys/types.h> // socket()
#include <sys/socket.h> // socket()
#include <netinet/in.h> // sockaddr_in
#include <arpa/inet.h> // inet_pton()
#include "../network_layer/NetworkLayer.h" // NetworkLayer
//#include "../agent/RoseAgent.h" // RoseAgent
#include "../struct/structs.h" // my_data_t, packet_queue, packet_construct()
#include "../packet/Packet/PHeaders.h"
// #include "../Headers.h"
#include <pthread.h> // pthread_create()
#include <signal.h> // pthread_kill()
#include "../log/log.h"
#include <map>
#define MSGSIZE 4109

using namespace std;
class NetworkLayer;
class RoseAgent;
class LinkLayer
{
    private:
        NetworkLayer * network_layer;
        my_data_t *node_data;
        packet_queue green_assign_queue;
        link_queue green_send_queue;
        RoseAgent * rose_agent;
        pthread_t threads[3];
        Log * log;

        int bc_recv;
        int fwd_recv;
        int pack_send;
        std::map</* Node id */ushort, /* Neighbor */ int>  recv_all_nghb;
        std::map</* Node id */ushort, /* Neighbor */ int> send_nghb;
     
        /* Efecto: envía mensaje por UDP.
         *         Recibe mensajes a través de green_send_queue,
         *         si no tiene paquetes en la cola se queda dormido.
         * Requiere: No aplica.
         * Modifica: No aplica.
         * Retorna: No aplica.
         */
        void green_send();
        /* Efecto: recibe mensaje por UDP.
         * Requiere: No aplica.
         * Modifica: No aplica.
         * Retorna: No aplica.
         */
        void green_recv();
        /* Efecto: Metodo dispatcher que verifica a cual componente tiene que enviarle el paquete
         * Requiere: No aplica.
         * Modifica: No aplica
         * Retorna: No aplica.
         */
        void green_assign();
        /* Efecto: Metodo que guarda en la cola de de assig_green para despertalo y que envie el dato 
         * Requiere: puntero al buffer de datos a guardar en la cola.
         * Modifica: green_assign_queue.
         * Retorna: 1 si se guardo satisfactoriamente.
         */
        int green_assign_store( void * );
        /* Efecto: Metodo que llama al thread a que pase escuchando en el green_recv
         * Requiere: Una referencia a si mismo, ya que el metodo es estatico para que lo ejecute el thread
         * Modifica: No aplica.
         * Retorna: No aplica.
         */
        static void * thread_green_recv( void * );
        /* Efecto: Metodo que llama al thread a que pase escuchando en el green_assign
         * Requiere: Una referencia a si mismo, ya que el metodo es estatico para que lo ejecute el thread
         * Modifica: No aplica.
         * Retorna: No aplica.
         */
        static void * thread_green_assign( void * );
         /* Efecto: Metodo que llama al thread a que pase escuchando en el green_send
         * Requiere: Una referencia a si mismo, ya que el metodo es estatico para que lo ejecute el thread
         * Modifica: No aplica.
         * Retorna: No aplica.
         */
        static void * thread_green_send( void * );
        
    public:
        LinkLayer( my_data_t *);
        ~LinkLayer();
        /* Efecto: Metodo publico que usan otros componentes para comunicarse con este
                    Deposita en una cola que posteriormente sera leida por un thread 
         * Requiere: puntero inteligente a Packet y un entero que representa la posicion
         *           de un vecino en el arreglo de vecinos. Ese vecino corresponde al que
         *           sera enviado el paquete.
         * Modifica: No aplica
         * Retorna: Un entero que verifica que todo haya salido bien 
         */
        int green_send_store( shared_ptr<Packet>, int );
        /* Efecto: asigna valor a atributos network_layer y rose_agent.
         * Requiere: puntero a NetworkLayer, RoseAgent y Log.
         * Modifica: atributos network_layer, rose_agent y log.
         * Retorna: No aplica.
         */
        void ptr_set( NetworkLayer *, RoseAgent *, Log *);
        /* Efecto: Inicializa los threads que estaran atendiendo los servicios de la clase
         * Requiere: (LinkLayer *) Puntero a instancia de LinkLayer.
         * Modifica: No aplica.
         * Retorna: Un entero que verifica que todo ha salido bien
         */
        int threads_init( LinkLayer * );


        /* Efecto: Devuelve la tabla de paquetes enviados a cada vecino
        * Requiere: No aplica.
        * Modifica: No aplica.
        * Retorna: Tabla de paquetes enviados a cada vecino en formado map. 
        * Autor: Pablo Cheng Galdamez
        */
        std::map<ushort, int> get_send();
        
         /* Efecto: Devuelve cantidad de paquetes enviados  forward a cada vecino
        * Requiere: No aplica.
        * Modifica: No aplica.
        * Retorna: Devuelve cantidad de paquetes enviados  forward a cada vecino
        * Autor: Pablo Cheng Galdamez
        */
        int get_fw_packs();
        
        /* Efecto: Devuelve cantidad de paquetes enviados  broadcast a cada vecino
        * Requiere: No aplica.
        * Modifica: No aplica.
        * Retorna: Devuelve cantidad de paquetes enviados  broadcast a cada vecino
        * Autor: Pablo Cheng Galdamez
        */
        int get_bc_packs();
};

#endif /* LINK_LAYER_H */
