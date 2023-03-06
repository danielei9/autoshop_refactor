import multiprocessing
import time
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
        self.resetMachine = None

    def adaptRequestCB(self,rawPayload):
        print("Adapt request CB ")
        self.router.paymentService.paymentDone = False
        self.lastRequestArrived = RequestController(rawPayload, self.tpv.sendError).requestAdapted
        self.router.setlastRequestArrived(self.lastRequestArrived)
        # enrutar para ejecutar request 
        self.router.enrouteCancelRequest(self.lastRequestArrived)
        self.router.enrouteConfigRequest(self.lastRequestArrived)
        self.router.enrouteConnectedRequest(self.lastRequestArrived)
        self.router.enrouteResetRequest(self.lastRequestArrived)
        self.router.enrouteGetActualConfigRequest(self.lastRequestArrived)

    def initTPVListener(self):
        self.tpv = TpvYsolveMqtt( self.adaptRequestCB )
    
    def startRouterThread(self):
        print("start_async_loop")
        self.router = Router(self.actualProcessingRequest,self.lastRequestArrived, self.tpv)
        asyncio.run(self.initServiceRouter())

    def initServiceRouter(self):
        print("initRouterService")
        try:
            while not stop_event.is_set():
                self.router.routeRequest(self.tpv.setMqttListenerPaused)
        except Exception as e:
            print(e)
            time.sleep(1)
            try:
                self.tpv.sendError(e)
            except Exception as er :
                print ("Error al reportar un error previo. Revisar mqtt")
                print (er)
                pass
            routerThread = threading.Thread(target=self.startRouterThread)
            routerThread.start()

    def run(self, resetMachine,):
        self.resetMachine = resetMachine
        try:
            self.initTPVListener()
            routerThread = threading.Thread(target=self.startRouterThread)
            routerThread.start()
            
            while True:
                time.sleep(.1)
                if(routerThread.is_alive()):
                    pass
                else:
                    time.sleep(3)
                    print("error with router thread")
                    self.tpv.sendError("error with router thread")
                    self.run()

        except Exception as e :
            self.tpv.sendError("Internal error service, if is not reset yet, please reset the machine. " + str(e))
            self.run()


class MainProcess():
    def __init__(self):
        self.service = Main()
        self.process = multiprocessing.Process(target=self.service.run, args=(self.endProcess,))
        self.service.resetMachine = self.endProcess

    def  startProcess(self):
        self.process.start()
        print(f'Process ID: {self.process.pid}')

    def  endProcess(self):
        self.process.terminate()
        print('Process terminated')

p = MainProcess()

while True: 
    if(p.process.is_alive()):
        pass
    else:
        p.startProcess()