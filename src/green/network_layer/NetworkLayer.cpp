#include "NetworkLayer.h"

NetworkLayer::NetworkLayer()
{
}

NetworkLayer::~NetworkLayer()
{
    for (int i = 0; i < NUM_THREADS_NETWORK; ++i)
        pthread_kill(threads[i], SIGKILL);
}

void NetworkLayer::ptr_set(LinkLayer *l, TransportLayer *t, RoseAgent *ra, Log *lo, my_data_t *data, StatsManager * stat)
{
    link_layer = l;
    transport_layer = t;
    my_data = data;
    rose_agent = ra;
    log = lo;
    stat_manager = stat;
}


void NetworkLayer::forward()
{
    int rand_num;
    srand(time(NULL));
    while (fw_table_init())
    {};
    while (1)
    {
        std::shared_ptr<Packet> packet = this->fw_queue.data_pop();
        //std::shared_ptr<FwPacket> fw_packet =
          //  std::dynamic_pointer_cast<FwPacket>(packet);
       
        int pprotocol = packet->getProtocol();
        std::shared_ptr<Packet> p;
        ushort destination;    
        if( pprotocol == 0 ){
            std::shared_ptr<FwPacket> pp = std::dynamic_pointer_cast<FwPacket>(packet);
            destination = pp->getDestination();
            p = pp;
            /*****/
            auto itr = recv_dest.find(destination);
            if (itr != recv_dest.end())
                ++itr->second;
            else
                recv_dest.insert(std::make_pair(destination, 1));

            auto itr2 = recv_all.find(pp->getOrigin());
            if (itr2 != recv_all.end())
                ++itr2->second;
            /****/
        }
        else{
            std::shared_ptr<SWPacket> pp = std::dynamic_pointer_cast<SWPacket>(packet);
            destination = pp->getDestination();
            p = pp;
            /*****/
            
            auto itr1 = recv_dest.find(destination);
            if (itr1 != recv_dest.end())
                ++itr1->second;
            else
                recv_dest.insert(std::make_pair(destination, 1));

            auto itr = recv_all.find(pp->getOrigin());
            if (itr != recv_all.end())
                ++itr->second;
            /****/
        }
        rand_num = rand() % 1000;
        if (destination == my_data->id && pprotocol == 0) /* Mensaje para host */
        {
            std::shared_ptr<FwPacket> p = std::dynamic_pointer_cast<FwPacket>(packet);
            blue_data_send(p);
        }
        else if(destination == my_data->id && pprotocol == 5)
        {
            if(rand_num < 950) /* si no se cumple se pierde paquete */
                rose_agent->queue_send_store(p);
            else
                puts("SE PIERDE PAQUETE (DE ENTRADA) DE SW EN FORWARD");
        }
        else /* Mensaje de forwarding */
        {
            if( pprotocol != 5 || rand_num < 950) /* si no se cumple se pierde paquete */
            {
                pthread_mutex_lock(&fw_mutex);
                auto itr = fw_table.find(destination);
                pthread_mutex_unlock(&fw_mutex);
                if (itr != fw_table.end())
                {
                    link_layer->green_send_store(p, itr->second);
                    //sprintf(log_msg, "< NL > < FW > message sent to LL. Origen ( %d ) , Destino ( %d ) ", p->getOrigin(), p->getDestination());
                    log->print_in_log(1, log_msg);
                }
                else
                {
                    log->print_in_log(3, (char *)"< NL > < FW > msg not forwarded, no destination route found.");
                }
            } else
                puts("SE PIERDE PAQUETE (DE SALIDA) DE SW EN FORWARD");
        }
    }
}

int NetworkLayer::blue_data_send(shared_ptr<FwPacket> fw_packet)
{
    if (!fw_packet)
        return 1;
    transport_layer->blue_send_store(fw_packet);
    sprintf(log_msg, "< NL > < FW > msg sent to TL. Origen ( %d )", fw_packet->getOrigin());
    log->print_in_log(1, log_msg);
    return 0;
}

void NetworkLayer::fw_table_upd()
{
    while (1)
    {
        shared_ptr<Packet> packet = fw_upd_queue.data_pop();
        if ((int)packet->getProtocol() == FTUPDATE_PACKET)
        {
            std::shared_ptr<FTUPacket> ftu_packet =
                std::dynamic_pointer_cast<FTUPacket>(packet);
            pthread_mutex_lock(&fw_mutex);
            for (auto x : ftu_packet->entries)
            {
                fw_table.insert(std::make_pair(x.first, x.second));
            }
            pthread_mutex_unlock(&fw_mutex);
            log->print_in_log(1, (char *)"< NL> < FW > fw table got updated.");
        }
    }
}

int NetworkLayer::find_nb_i(ushort nb_id)
{
    for (int nb_i = 0; nb_i < my_data->nb_count; ++nb_i)
        if (my_data->nb_data[nb_i].id == nb_id)
            return nb_i;
    return -1;
}

void NetworkLayer::broadcast()
{
    while (1)
    {
        std::shared_ptr<BcPacket> bc_packet =
            std::dynamic_pointer_cast<BcPacket>(this->bc_queue.data_pop());
        auto itr = std::find(bc_table.begin(), bc_table.end(), bc_packet->getOriginNb());
        if (bc_packet->getOriginNb() == my_data->id)
        { /* Asigname el valor incial del ttl. */
            bc_packet->setTtl(TTL_INIT);
        }
        if (itr != bc_table.end() || bc_packet->getOriginNb() == my_data->id) /* Vecino de origen pertenece al arbol  */
        {
            if(bc_packet->getOriginNb() != my_data->id)
                bc_local_send(bc_packet);
            bc_packet->minusTtl();
            if (bc_packet->getTtl()) /* Aun puede vivir. */
            {
                int broadcasted = 0;
                for (auto itr2 : bc_table)
                {
                    if (bc_packet->getOriginNb() != itr2) /* No lo envie por donde vino */
                    {
                        bc_packet->setOriginNb(my_data->id);
                        int nb_i = find_nb_i(itr2);
                        link_layer->green_send_store(bc_packet, nb_i);
                        broadcasted = 1;
                    }
                }
                if(broadcasted)
                    sprintf(log_msg, "< NL > < BC > msg broadcasted. OriginNb( %d )", bc_packet->getOriginNb());
                log->print_in_log(1, log_msg);
            }
            else
            {
                log->print_in_log(1, (char *)"< NL > < BC > msg has no longer ttl.");
            }
        }
        else
        {
            log->print_in_log(3, (char *)"< NL > < BC > got msg from non spanning tree neighbour.");
        }
    }
}

void NetworkLayer::bc_local_send(shared_ptr<BcPacket> bc_packet)
{
    if (!bc_packet)
        return;
    int8_t bc_protocol = bc_packet->getBcProtocol();
    switch (bc_protocol)
    {
    case FW_PACKET:
    {
        std::shared_ptr<BcDataPacket> bc_data_packet =
            std::dynamic_pointer_cast<BcDataPacket>(bc_packet);
        blue_data_send(bc_data_packet->data_packet);
        break;
    }
    case BCADY_PACKET:
    {
        std::shared_ptr<BcAdyPacket> bc_ady_packet =
            std::dynamic_pointer_cast<BcAdyPacket>(bc_packet);
        if (bc_ady_packet->origin_node != my_data->id) /* Envie al rosado si no es mi adyacencia */
        {
            rose_agent->queue_send_store(bc_ady_packet);
            sprintf(log_msg, "< NL > < BC > adjacencies msg sent to RA. Origen < %d >", bc_ady_packet->origin_node);
            log->print_in_log(1, log_msg);
        }
        break;
    }
    }
}

void NetworkLayer::bc_table_upd()
{
    while (1)
    {
        shared_ptr<Packet> packet = bc_upd_queue.data_pop();
        if (packet->getProtocol() == BCUPDATE_PACKET)
        {
            std::shared_ptr<BcUPacket> bcu_packet =
                std::dynamic_pointer_cast<BcUPacket>(packet);
            ushort id = bcu_packet->getNbId();
            pthread_mutex_lock(&bc_mutex);
            bc_table.push_back(id);

            recv_all.insert(std::make_pair(id, 0));

            pthread_mutex_unlock(&bc_mutex);
            log->print_in_log(1, (char *)"< NL > < BC > bc_table got updated.");
        }
    }
}

int NetworkLayer::fw_table_init()
{
    if (!my_data)
        return 1;
    /* Inicializa la tabla con solo los vecinos. */
    for (int i = 0; i < my_data->nb_count; ++i)
        fw_table.insert(std::make_pair(my_data->nb_data[i].id, i));
    return 0;
}

int NetworkLayer::threads_init(NetworkLayer *nl)
{
    pthread_mutex_init(&fw_mutex, 0);
    pthread_mutex_init(&bc_mutex, 0);

    if (pthread_create(&threads[FW_THREAD], 0, forward_by_thread, (void *)nl) != 0)
        return 1;
    if (pthread_create(&threads[BC_THREAD], 0, broadcast_by_thread, (void *)nl) != 0)
        return 1;
    if (pthread_create(&threads[FW_UPD_THREAD], 0, fw_upd_by_thread, (void *)nl) != 0)
        return 1;
    if (pthread_create(&threads[BC_UPD_THREAD], 0, bc_upd_by_thread, (void *)nl) != 0)
        return 1;
    return 0;
}

void *NetworkLayer::forward_by_thread(void *data)
{
    NetworkLayer *nl = (NetworkLayer *)data;
    nl->forward();
}

void *NetworkLayer::broadcast_by_thread(void *data)
{
    NetworkLayer *nl = (NetworkLayer *)data;
    nl->broadcast();
}

void *NetworkLayer::fw_upd_by_thread(void *data)
{
    NetworkLayer *nl = (NetworkLayer *)data;
    nl->fw_table_upd();
}

void *NetworkLayer::bc_upd_by_thread(void *data)
{
    NetworkLayer *nl = (NetworkLayer *)data;
    nl->bc_table_upd();
}

int NetworkLayer::bc_store(std::shared_ptr<Packet> p)
{
    bc_queue.data_push(p);
    return 0;
}

int NetworkLayer::fw_store(std::shared_ptr<Packet> p)
{
    fw_queue.data_push(p);
    return 0;
}

int NetworkLayer::fw_upd_store(std::shared_ptr<Packet> p)
{
    fw_upd_queue.data_push(p);
    return 0;
}

int NetworkLayer::bc_upd_store(std::shared_ptr<Packet> p)
{
    bc_upd_queue.data_push(p);
    return 0;
}


std::map<ushort, int> NetworkLayer::get_fw_table()
{
    // for(auto x: fw_table)
        // neighbors_stat.insert({x.first, 0});   
     
    return fw_table;
}

std::vector< int > NetworkLayer::get_AG()
{
    // for(auto x: fw_table)
        // neighbors_stat.insert({x.first, 0});    
    return bc_table;
}
std::map<ushort, int> NetworkLayer::get_recv_dest()
{
    return this->recv_dest;
}

std::map<ushort, int> NetworkLayer::get_recv_all()
{
    return this->recv_all;
}


