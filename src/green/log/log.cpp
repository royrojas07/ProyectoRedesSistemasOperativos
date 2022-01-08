#include "log.h"

Log::Log(int id)
{
    create_log_name(id);
}

void Log::create_log_name(int id)
{
	char id_node[12];
	sprintf(id_node, "%d", id);
	strcat(this->file_name, id_node);
	strcat(this->file_name, ".txt");
    remove(file_name); /* lo remuevo para que cada vez que se llame vuelva a llenar la bitacora */
}

void Log::print_in_log(int code, char* description)
{
    std::ofstream log_file;
    log_file.open(file_name, std::ios::app);
    mtx.lock();
    auto now = high_resolution_clock::now();
    auto time = system_clock::to_time_t(now);
    auto tm = *std::localtime(&time);
    auto epoch = now.time_since_epoch();
    auto us = duration_cast<microseconds>(epoch).count() % 1000000;
    switch (code)
    {
    case SUCESS_MSG:
        log_file << "[" << std::put_time(&tm, "%F %T.") << us << "]" << " Case " << SUCESS_MSG << " " << description << "\n";
        break;
    case SEND_MSG:
        log_file << "[" << std::put_time(&tm, "%F %T.") << us << "]" << " Case " << SEND_MSG <<  " " << description << "\n";
        break;
    case RECV_MSG:
        log_file << "[" << std::put_time(&tm, "%F %T.") << us << "]" << " Case " << RECV_MSG << " " << description << "\n";
        break;
    case ERROR_MSG:
        log_file << "[" << std::put_time(&tm, "%F %T.") << us << "]" << " Case " << ERROR_MSG << " " << description << "\n";
        break;
    }
    mtx.unlock();
    log_file.close();
}
