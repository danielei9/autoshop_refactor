from Model.TPVCommunication.Request.Request import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Services.PaymentService import *

class Router():
    def __init__(self,actualProcessingRequest, lastRequestArrived, sendErrorTPV):
        self.actualProcessingRequest = actualProcessingRequest
        self.lastRequestArrived = lastRequestArrived
        self.paymentService:PaymentService = None
        self.sendErrorTPV = sendErrorTPV
        self.initializePaymentService()
        
    def initializePaymentService(self):
        self.paymentService = PaymentService(self.sendErrorTPV)
    
    def setActualProcessingRequest(self,request):
        self.actualProcessingRequest= request
    def setlastRequestArrived(self,request):
        self.lastRequestArrived = request
    def setErrorPayingInDisplay(self,error):
        self.paymentService.setErrorInDisplay(error)

    def routeRequest(self):

        while True:
            # print(type(self.actualProcessingRequest))
            # print("Arrived request None actual pending")
            self.actualProcessingRequest = self.lastRequestArrived
            
            # Procesar pago
            if( isinstance(self.actualProcessingRequest,PayRequest ) ):
                print("Arrive PayRequest: " + str(self.actualProcessingRequest.price) + " €")
                self.paymentService.startMachinesPayment(self.actualProcessingRequest)
                return True
            
    # Cancelar 
    def enrouteCancelRequest(self,request):
        if( isinstance(request,CancelRequest ) ): 
            print("Arrive paymentDone") 
            #poner el precio de la orden a 0 así realizará la cancelación
            self.actualProcessingRequest = None
            self.lastRequestArrived = None
            self.paymentService.paymentDone = True
            self.paymentService.actualCancelled = True
            return True
        
    def enrouteConfigRequest(self,request):
        if( isinstance(request,ConfigStackRequest ) ): 
            print("Arrive ConfigRequest")
            self.paymentService.billWalletService.bv.configMode(request.stackA, request.stackB)
            return True
           
        