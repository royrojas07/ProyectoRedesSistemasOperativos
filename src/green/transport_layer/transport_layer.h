#ifndef TRANSPORT_LAYER_H
#define TRANSPORT_LAYER_H
#include <stdlib.h>
#include <stdint.h>
#include <semaphore.h>
#include <pthread.h>
#include <queue>
#include <memory>
#include <unistd.h>	  // for write and read
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h> // for inet_pton
#include "../packet/Packet/PHeaders.h"
//#include "../Headers.h"
#include "../network_layer/NetworkLayer.h"
#include "../agent/RoseAgent.h"
#include "../log/log.h"
#include "../struct/structs.h"
#include <signal.h>
#define NUM_THREADS 3 //total de numero de threads
#define BLUE_MSG_SIZE 207 //total de un msj proveniente del azul

class NetworkLayer;
class RoseAgent;
class TransportLayer
{
    private:
        /*atributos */
        packet_queue blue_snd_queue;
        packet_queue blue_rcv_queue;
        NetworkLayer* network_layer;
        RoseAgent* rose_agent;
        Log* log;
        my_data_t* my_data;
        int blue_sockfd;
        int tcp_socket;
        pthread_t threads[NUM_THREADS];

        /* metodos */

        /* 
        * Efecto: Metodo ejecutado por un thread para escuchar lo que venga del azul
        * Requiere: No aplica
        * Modifica: No aplica 
        * param: Una referencia a si mismo ya que los threads trabajan con metodos estaticos 
        * retorna: no aplica
        */
        static void* blue_recv(void* data);
        /* 
        * Efecto: Metodo ejecutado por un thread que espera que llegue un mensaje para azul y posteriormente lo envia 
        * requiere: No aplica 
        * modifica: NO aplica
        * param: Una referencia a si mismo ya que los threads trabajan con metodos estaticos 
        * return: No aplica
        */
        static void* blue_send(void* data);
        /* 
        * Efecto: Metodo ejecutado por un thread que tiene la funcion de dispatcher para enviarselo al componente necesario
        * requiere: No aplica
        * modifica: NO aplica
        * param: Una referencia a si mismo ya que los threads trabajan con metodos estaticos 
        * return: NO aplica
        */
        static void* blue_assign(void* data);
         /* 
        * Efecto: Evalua que el mensaje sea para alguien diferente de si mismo 
        * requiere: No aplica
        * modifica: No aplica
        * param: Un puntero al paquete que va a ser evaluado 
        * return: Un int que me indica si todo paso de forma exitosa
        */
        int blue_msg_eval(std::shared_ptr<Packet>);
        /* 
        * Efecto: Metodo de store interno, es utilizado por el blue recv para comunicarse con el dispatcher
        * requiere: No aplica
        * modifica: No aplica
        * param: El tipo de paquete que se va a insertar en la cola
        * return: No aplica
        */
        void blue_recv_store(std::shared_ptr<FwPacket>); 
        /* 
        * Efecto: Metodo para establecer la coneccion TCP
        * requiere: No aplica 
        * modifica: No aplica
        * param: No aplica
        * return: No aplica
        */
        int tcp_connect();

        shared_ptr<Packet> recv_construct(char *);
    public:
        /* 
        * Efecto: Metodo constructor
        */
        TransportLayer(){};
        /* 
        * Efecto: Metodo destructor
        */
        ~TransportLayer();
        /* 
        * Efecto: Metodo que asigna las referencias de los componentes con los que se comunica
        * Requiere: que las instancias de Networklayer y my data existan
        * modifica: No aplica
        * param: Componentes externos pasados por referencia de la network layer y my data(contiene vecinos y datos propios)
        * return: No aplica
        */
        void ptr_set(NetworkLayer*, RoseAgent*, my_data_t*, Log *);
        /* 
        * Efecto: Metodo que inicializa los threads de esta capa, para que se mantengan escuchando sus determinadaa colas
        * Requiere: No aplica
        * modifica: No aplica 
        * param: Una referencia a si mismo, con el fin de pasarsela a los threads por ser estaticos
        * return: No aplica
        */
        int threads_init(TransportLayer* t);
        /* 
        * Efecto: Metodo publico por el cual los demas componentes se van a comunicar con este 
        * Requiere: No aplica 
        * modifica: No aplica
        * param: Una referencia a si mismo, con el fin de pasarsela a los threads por ser estaticos
        * return: No aplica
        */
        void blue_send_store(std::shared_ptr<Packet>);
        void sock_shutdown();
}; 
#endif /* TRANSPORT_LAYER_H */