import sys
import os
import datetime

""" 
    Clase encargada de crear y escribir en la bitacora log. 
 """

class Log:
    
    # Efectua: inicializa el archivo log. 
    def log_init(self, log_name):
        self.log_file = open( "blue_logs/"+log_name, "w+")

    # Efectua: encribe un event en el log. 
    def log_event(self, event_type, description ):
        timestamp = datetime.datetime.now()
        event_line = "[%s] Case %d Blue %s\n" % (timestamp, event_type, description)
        self.log_file.write( event_line )
        
    # Efectua: cierra el archivo log. 
    def log_close(self):
        self.log_file.close()