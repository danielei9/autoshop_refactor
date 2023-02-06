# inicializar Mqtt 
# subscribe mqtt
# esperar a obtener un request
# Procesar request
from TpvYsolveMqtt import *
from Model.TPVCommunication.Request.Request import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConfigStackRequest import *
import time
from Controller.RequestController import *
# from Utils.Reques import *
from Router.RouterRequest import *
import threading
import asyncio
stop_event = threading.Event()

class Main():
    def __init__(self):
        print("init")
        self.lastRequestArrived:Request = None
        self.actualProcessingRequest:Request = None
        self.tpv = None
        self.router = None

    def adaptRequestCB(self,rawPayload):
        print("Adapt")
        self.lastRequestArrived = RequestController(rawPayload).requestAdapted
        self.router.setlastRequestArrived(self.lastRequestArrived)

    def initTPVListener(self):
        self.tpv = TpvYsolveMqtt( self.adaptRequestCB )
    
    def startRouterThread(self):
        print("start_async_loop")
        self.router = Router(self.actualProcessingRequest,self.lastRequestArrived)
        asyncio.run(self.initServiceRouter())

    async def initServiceRouter(self):
        print("initRouterService")
        try:
            while not stop_event.is_set():
                self.router.routeRequest()
        except Exception as e:
            print(e)
            time.sleep(1)
            try:
                self.tpv.sendError(e)
                # self.router.setErrorPayingInDisplay(e)
            except Exception as er :
                print ("Error al reportar un error previo. Revisar mqtt")
                print (er)
                pass
            routerThread = threading.Thread(target=self.startRouterThread)
            routerThread.start()

    def run(self):
        print("run")
        # crear hilo para manejar las solicitudes de MQTT
        # tpvListenerThread = threading.Thread(target=self.initTPVListener())
        # tpvListenerThread.start()
        self.initTPVListener()
        # crear hilo para ejecutar el bucle de eventos asíncronos
        routerThread = threading.Thread(target=self.startRouterThread)
        routerThread.start()
         
        # código para manejar las solicitudes de MQTT
        while True:
            # comprobar si se debe cancelar la solicitud
            time.sleep(.1)
            if(routerThread.is_alive()):
                # print("Router is alive")
                pass
            else:
                time.sleep(3)
                print("error with router thread")
            # if(tpvListenerThread.is_alive()):
            #     # print("Tpv Listener is alive")
            #     pass
            # else:
            #     print("error with tpv Listener thread")
            
            if isinstance(self.lastRequestArrived,CancelRequest):
                self.router.setlastRequestArrived(None)
                self.router.setActualProcessingRequest(None)
                self.actualProcessingRequest = None 
                self.lastRequestArrived = None
                # stop_event.set()


service = Main()
service.run()
