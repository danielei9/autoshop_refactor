from Model.TPVCommunication.Request.Request import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Services.PaymentService import *

class Router():
    def __init__(self,actualProcessingRequest, lastRequestArrived):
        self.actualProcessingRequest = actualProcessingRequest
        self.lastRequestArrived = lastRequestArrived
        self.paymentService:PaymentService = None

    def initializePaymentService(self):
        self.paymentService = PaymentService()
    
    def setActualProcessingRequest(self,request):
        self.actualProcessingRequest= request
    def setlastRequestArrived(self,request):
        self.lastRequestArrived = request
    def setErrorPayingInDisplay(self,error):
        self.paymentService.setErrorInDisplay(error)

    async def routeRequest(self):
        self.initializePaymentService()

         # TODO: PONER actualProcessingRequest en None al finalizar la orden
         # Si actualmente esta libre, NO hay request pendiente de pago y esta esperando uno y  acepta la request que venga
        while True:
            # print(type(self.actualProcessingRequest))
            # print(type(self.lastRequestArrived))
            if(self.actualProcessingRequest == None and self.lastRequestArrived != None):
                print("Arrived request None actual pending")
                self.actualProcessingRequest = self.lastRequestArrived
                
                # Procesar pago
                if( isinstance(self.actualProcessingRequest,PayRequest ) ):
                    print("Arrive PayRequest: " + str(self.actualProcessingRequest.price) + " €")
                    await self.paymentService.startMachinesPayment(self.actualProcessingRequest.price)
                    self.actualProcessingRequest = None
                    return True
                
                # Cancelar 
                if( isinstance(self.actualProcessingRequest,CancelRequest ) ): 
                    print("Arrive CancelRequest") 
                    #poner el precio de la orden a 0 así realizará la cancelación
                    self.actualProcessingRequest = None
                    self.lastRequestArrived = None
                    # await self.paymentService.startMachinesPayment()
                    return True
                # Configurar
                if( isinstance(self.actualProcessingRequest,ConfigStackRequest ) ):
                    print("Arrive ConfigRequest")
                    # self.initializePaymentService()
                    await self.paymentService.startMachinesConfig(self.actualProcessingRequest.stackA,self.actualProcessingRequest.stackB)
                    # self.paymentService.inhibitCoins()
                    return True
            if(self.actualProcessingRequest == None and self.lastRequestArrived == None):
                 # Procesar pago
                if( isinstance(self.actualProcessingRequest,PayRequest ) ):
                    print("Arrive PayRequest: " + str(self.actualProcessingRequest.price) + " €")
                    # self.initializePaymentService()
                    await self.paymentService.startMachinesPayment()
                    return True
                # Configurar
                if( isinstance(self.actualProcessingRequest,ConfigStackRequest ) ):
                    print("Arrive ConfigRequest")
                    # self.initializePaymentService()
                    await self.paymentService.startMachinesConfig(self.actualProcessingRequest.stackA,self.actualProcessingRequest.stackB)
                    # self.paymentService.inhibitCoins()
                    return True
            # Si  hay alguna request pendiente de pago, Esta OCUPADO, solo puede aceptar Cancelación
            else:
                if( isinstance(self.lastRequestArrived,CancelRequest ) ):
                    print("Arrive CancelRequest") 
                    #poner el precio de la orden a 0 así realizará la cancelación
                    self.actualProcessingRequest.price = 0
                    # self.initializePaymentService()
                    await self.paymentService.startMachinesPayment()
                    return True
            time.sleep(0.5)
        