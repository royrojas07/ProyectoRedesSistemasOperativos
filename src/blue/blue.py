import sys
import struct
import time
import signal
from GreenAgent import GreenAgent
from SpiderBuilder import SpiderBuilder
from log import Log
from interface import Interface

# Autor: Diego Murillo Porras B85526

log = Log()

""" 
    Controlador del host azul. 
 """

def main():
    arguments = len(sys.argv)
    log_file_name = "B"
    try:
        log_file_name = "blue_log" + sys.argv[3] + ".txt"
    except IndexError:
        print( "Missing arguments: <IP> <port#> <log#>" )
        return 1
    log.log_init(log_file_name)
    gA = GreenAgent(sys.argv[1], int(sys.argv[2]), log)
    gA.server_connect()
    gA.thread_init()
    interface = Interface(log)
    spd_builder = SpiderBuilder(log)
    interface.set_instances(gA, spd_builder)
    spd_builder.set_instances(gA)
    spd_builder.thread_init()
    interface.run()

def handler(signum, frame):
    log.log_close()
    print("PROGRAM EXITS.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    main()