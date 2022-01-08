#include "LinkLayer.h"

LinkLayer::LinkLayer(my_data_t* data)
{
    this->node_data = data;
    this->bc_recv = 0;
    this->fwd_recv= 0;
}

LinkLayer::~LinkLayer()
{
    for (int i = 0; i < 3; ++i)
        pthread_kill(threads[i], SIGKILL);
}

int LinkLayer::green_send_store(shared_ptr<Packet> packet, int dest)
{
    green_send_queue.data_push(packet, dest);
    return 0;
}

int LinkLayer::green_assign_store(void *msg)
{
    green_assign_queue.data_push(packet_construct((char *)msg));

    return 0;
}


void LinkLayer::ptr_set(NetworkLayer *network_layer, RoseAgent *rose_agent, Log *log)
{
    this->network_layer = network_layer;
    this->rose_agent = rose_agent;
    this->log = log;
}

void LinkLayer::green_send()
{
    int sock, sockaddr_len, bytes_send, packet_len;
    struct sockaddr_in server, from;
    nb_data_t *nb_data = node_data->nb_data;

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock)
    {
        while (true)
        {
            pair<shared_ptr<Packet>, int> packet = green_send_queue.data_pop();
            if (packet.second != -1)
            {   
                char *packet_bytes = packet.first->deconstruct();
                bzero(&server, sizeof(server));
                server.sin_family = AF_INET;
                inet_pton(AF_INET, nb_data[packet.second].ip_add, &(server.sin_addr));
                server.sin_port = htons(nb_data[packet.second].pt_num);
                sockaddr_len = sizeof(struct sockaddr_in);
                packet_len = packet.first->getSize();
                bytes_send = sendto(sock, packet_bytes, packet_len, 0, (struct sockaddr *)&server, sockaddr_len);
                if (bytes_send < 0)
                    log->print_in_log(3, (char*)"< LL > Error sending via UDP");
                else
                    log->print_in_log(1, (char*)"< LL > Message sent succesfully");
            }
        }
    }
    else
    {
        log->print_in_log(3, (char*)"< LL > Error creating socketfd");
    }
}

void LinkLayer::green_recv()
{
    int sock, fromlen, rcv_bytes;
    struct sockaddr_in server;
    struct sockaddr_in from;
    
    char rcv_msg[4109];

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
        log->print_in_log(3, (char*)"< LL > Error opening green socket fd");
    bzero(&server, sizeof(server));
    server.sin_family = AF_INET;
    inet_pton(AF_INET, node_data->ip_add, &(server.sin_addr));
    server.sin_port = htons(node_data->pt_num);
    if (bind(sock, (struct sockaddr *)&server, sizeof(server)) < 0)
        log->print_in_log( 3,(char*) "< LL > Error binding UDP");

    fromlen = sizeof(struct sockaddr_in);
    while (true)
    {  
        bzero(rcv_msg,sizeof(rcv_msg)); 
        rcv_bytes = recvfrom(sock, rcv_msg, MSGSIZE, 0, (struct sockaddr *)&from, (socklen_t *)&fromlen);
        if (rcv_bytes < 0)
            log->print_in_log( 3,(char*) "< LL > Error reading bytes via UDP"); // error occured
        else if (green_assign_store(rcv_msg))
            log->print_in_log( 3,(char*) "< LL > Error storing to dispatcher"); // error occured
    }
    close(sock);
}

void LinkLayer::green_assign()
{
    while (true)
    {
        shared_ptr<Packet> packet = green_assign_queue.data_pop();


        int protocol = (int)packet->getProtocol();
        switch (protocol)
        {
        case 0:
            network_layer->fw_store(packet);
            log->print_in_log( 0, (char*) "< LL > Dispatching packet to Forward");
            this->fwd_recv += 1;

            break;
        case 1:
            network_layer->bc_store(packet);
            log->print_in_log( 0, (char*) "< LL > Dispatching packet to Broadcast");
            this->bc_recv  += 1;

            break;
        case 2:
            rose_agent->queue_send_store( packet );
            log->print_in_log( 0, (char*) "< LL > Dispatching packet to RoseAgent");
            break;
        case 4:
            rose_agent->queue_send_store( packet );
            log->print_in_log( 0, (char*) "< LL > Dispatching packet to RoseAgent");
            break;
        case 5:
            network_layer->fw_store( packet );
            log->print_in_log( 0, (char*) "< LL > Dispatching packet to NetLayer");
            break;
        default:
            log->print_in_log( 3,(char*) "< LL > Error: bad protocol in dispatcher"); // error occured
        }
    }
}

int LinkLayer::threads_init(LinkLayer *ll)
{
    if (pthread_create(&threads[0], NULL, thread_green_recv, (void *)ll) != 0)
        return 1;
    if (pthread_create(&threads[1], NULL, thread_green_assign, (void *)ll) != 0)
        return 1;
    if (pthread_create(&threads[2], NULL, thread_green_send, (void *)ll) != 0)
        return 1;

    return 0;
}

void *LinkLayer::thread_green_recv(void *data)
{
    LinkLayer *ll = (LinkLayer *)data;
    ll->green_recv();
    return 0;
}

void *LinkLayer::thread_green_assign(void *data)
{
    LinkLayer *ll = (LinkLayer *)data;
    ll->green_assign();
    return 0;
}

void *LinkLayer::thread_green_send(void *data)
{
    LinkLayer *ll = (LinkLayer *)data;
    ll->green_send();
    return 0;
}




std::map<ushort, int> LinkLayer::get_send()
{
    return this->send_nghb;
}

int LinkLayer::get_bc_packs()
{
    return this->bc_recv;
}
int LinkLayer::get_fw_packs()
{
    return this->fwd_recv;
}
