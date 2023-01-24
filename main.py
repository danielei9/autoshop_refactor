# inicializar Mqtt 
# subscribe mqtt
# esperar a obtener un request
# Procesar request
from TpvYsolveMqtt import *
from Model.TPVCommunication.Request.Request import *
import time
from Controller.RequestController import *
class Main():
    def __init__(self):
        print("init")
        self.request:Request = None

    def adaptRequestCB(self,rawPayload):
        self.request = RequestController(rawPayload).requestAdapted
        print(self.request)

    def run(self):
        print("run")
        tpv = TpvYsolveMqtt(self.adaptRequestCB)
        while True:
            time.sleep(1)


service = Main()
service.run()