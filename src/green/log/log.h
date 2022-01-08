#ifndef LOG_H 
#define LOG_H
#include <iostream>
#include <fstream>
#include <mutex>  
#include <chrono> //para el time
#include <iomanip> //para el time
#include <cstring> // strcat
#define SUCESS_MSG 0
#define SEND_MSG 1
#define RECV_MSG 2
#define ERROR_MSG 3

using namespace std::chrono;

class Log
{
    private:
    char file_name[30] = "log/green_logs/green_log";
    void create_log_name(int);
    std::mutex mtx; 
    public:
    Log(int);
    ~Log(){};
    void print_in_log(int,char*);
};
#endif 