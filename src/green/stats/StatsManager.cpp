#include "StatsManager.h"

StatsManager::StatsManager()
{}

StatsManager::~StatsManager()
{}

int StatsManager::spider_queue_store(std::shared_ptr<Packet> p)
{
    spider_queue.data_push(p);
    return 0;
}
int StatsManager::threads_init(StatsManager * my_class)
{

    if (pthread_create(&threads, 0, spider_assign, (void *)my_class) )
        return 1;
   
    return 0;
}


void StatsManager::ptr_set(RoseAgent* rose_agent, NetworkLayer* network, LinkLayer *ll, my_data_t*my_data, Log* log)
{
    this->rose_agent = rose_agent;
    this->network_layer = network;
	this->link_layer = ll;
	this->my_data = my_data;
	this->log = log;
}

void *StatsManager::spider_assign(void *data)
{

    StatsManager *my_class = (StatsManager *)data;

	while (true)
    {
        shared_ptr<Packet> pack = my_class->spider_queue.data_pop();
        shared_ptr<StatPacket> statPack =std::dynamic_pointer_cast<StatPacket>(pack);
        int request = (int)statPack->getRequest();
        my_data_t* data = my_class->my_data;
        int8_t  spider_id = statPack->getSpiderId();
        int8_t  req = statPack->getRequest();
        switch (request)    
        {
            case FWDTABLE:
            {

                my_class->fwd_table_stat();
                my_class->send_table(my_class->fwd_table, spider_id, req, data);
                break;
            }
            case NGHBLIST:
            {
                my_class->AG_nghb_stat();
                my_class->send_nghb_pack(spider_id, req);
                break;
            }
            case RECVPACKORIGN:
            {
                my_class->recv_packets_stat();
                my_class->send_table(my_class->recv_dest_nghb, spider_id, req, data);
                break;
            }
            case SENDPACK:
            {
                my_class->send_packets_stat();
                my_class->send_table(my_class->send_nghb, spider_id, req, data);
                break;
            }
            case RECVPACKALL:
            {
                my_class->recv_packets_all_stat();
                my_class->send_table(my_class->recv_all_nghb, spider_id, req, data);
                break;
            }
            case BCFWPACK:
            {
                my_class->bcast_fw_stat();
                my_class->send_counts(spider_id, req);
                break;
            }
            
        }
    }
}

void StatsManager::send_table(std::map<ushort, int> table, int8_t spider_id, int8_t request, my_data_t * data)
{
    char init[3];
    int8_t protocol = (int8_t)104;
    memcpy(init, (unsigned char *)&protocol, 1);
    memcpy(&init[1], (unsigned char *)&request, 1);
    memcpy(&init[2], (unsigned char *)&spider_id, 1);
    std::string str;
    int req = (int)request;
    for (auto x: table)
    {
        if(req == 1)
            str += std::to_string(x.first) + ',' + std::to_string(data->nb_data[x.second].id) + ';';
        else
            str += std::to_string(x.first) + ',' + std::to_string(x.second) + ';';
    }
    std::shared_ptr<StatPacket> pack = std::make_shared<StatPacket>(init, str);
    rose_agent->queue_send_store(pack);
    // StatPacket(init, str);
}


void StatsManager::send_counts(int8_t spider_id, int8_t request )
{
    int bc = link_layer->get_bc_packs();
    int fw = link_layer->get_fw_packs();
    char init[3];
    int8_t protocol = (int8_t)104;
    memcpy(init, (unsigned char *)&protocol, 1);
    memcpy(&init[1], (unsigned char *)&request, 1);
    memcpy(&init[2], (unsigned char *)&spider_id, 1);
    std::string str;
    str = to_string(bc) + ',' + to_string(fw) + ','+ '-';
    std::shared_ptr<StatPacket> pack = std::make_shared<StatPacket>(init, str);
    rose_agent->queue_send_store(pack);
}
void StatsManager::send_nghb_pack( int8_t spider_id, int8_t request)
{
    char init[3];
    int8_t protocol = (int8_t)104;
    memcpy(init, (unsigned char *)&protocol, 1);
    memcpy(&init[1], (unsigned char *)&request, 1);
    memcpy(&init[2], (unsigned char *)&spider_id, 1);
    std::string str;
    for (int i = 0; i < bc_table.size(); i++)
    {
        str += std::to_string(bc_table[i]);
        if (i != bc_table.size())
            str += ',';
    }
    
    std::shared_ptr<StatPacket> pack = std::make_shared<StatPacket>(init, str);
    rose_agent->queue_send_store(pack);
}

void StatsManager::neighbors_updt()
{
    // neighbours_id = network_layer->get_fw_table();
    // for(auto x: neighbours_id)
    // {
    //     auto itr = recv_all_nghb.find(x.first);
    //     if (itr == recv_all_nghb.end())
    //     {
    //         recv_all_nghb.insert({x.first, 0});
    //         recv_dest_nghb.insert({x.first, 0});
    //         send_nghb.insert({x.first, 0});
    //     }
    // }
}



void StatsManager::fwd_table_stat()
{
    fwd_table = network_layer->get_fw_table();
}

void StatsManager::AG_nghb_stat()
{
    bc_table = network_layer->get_AG();
}

void StatsManager::recv_packets_all_stat()
{
    recv_all_nghb = network_layer->get_recv_all();
}

void StatsManager::send_packets_stat()
{
    send_nghb = link_layer->get_send();
}

void StatsManager::recv_packets_stat()
{
    recv_dest_nghb = network_layer->get_recv_dest();
}

void StatsManager::bcast_fw_stat()
{
    int bc_recv = link_layer->get_bc_packs();
    int fwd_recv = link_layer->get_fw_packs();
}


void StatsManager::print_stats()
{
    fwd_table_stat();
    AG_nghb_stat();
    recv_packets_all_stat();
    send_packets_stat();
    recv_packets_stat();
    std::cout << "**********************************************"<< std::endl;

    std::cout << std::endl<< "Forward Table " << std::endl;
    std::cout << "< Destino , Ruta >" << std::endl;
    for(auto x: fwd_table)
        std::cout << "< " << x.first << " , " << my_data->nb_data[x.second].id << " >" << std::endl;
  
    std::cout << std::endl<< "Broadcast Table" << std::endl;
    for(auto x: bc_table)
        std::cout << "< " << x << " >" << std::endl;

    std::cout << std::endl<< "Paquetes vistos desde fuente" << std::endl;
    std::cout << "< Fuente, cantidad de paquetes>" << std::endl;
    for(auto x: recv_dest_nghb)
        std::cout << "< " << x.first << " , " << x.second << " >" << std::endl;

    std::cout << std::endl << "Paquetes enviados a vecinos" << std::endl;
    std::cout << "< Vecinos , Enviados >" << std::endl;
    for(auto x: send_nghb)
        std::cout << "< " << x.first << " , " << x.second << " >" << std::endl;
    
    std::cout << std::endl<< "Paquetes vistos por vecinos" << std::endl;
    std::cout << "< Vecinos , Recibidos>" << std::endl;
    for(auto x: recv_all_nghb)
        std::cout << "< " << x.first << " , " << x.second << " >" << std::endl;

    bcast_fw_stat();
    std::cout << "**********************************************"<< std::endl;
    
}
