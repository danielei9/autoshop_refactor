from Model.TPVCommunication.Request.Request import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Model.TPVCommunication.Request.ConnectedRequest import *
from Services.PaymentService import * 
from TpvYsolveMqtt import *
from utils.RequestCodes import *
class Router():
    def __init__(self,actualProcessingRequest, lastRequestArrived, tpvComm:TpvYsolveMqtt):
        self.actualProcessingRequest = actualProcessingRequest
        self.lastRequestArrived = lastRequestArrived
        self.paymentService:PaymentService = None
        self.sendErrorTPV = tpvComm.sendError
        self.sendDataTPV = tpvComm.sendData
        self.initializePaymentService()
        
    def initializePaymentService(self):
        self.paymentService = PaymentService(self.sendErrorTPV,self.sendDataTPV)
    
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
                self.paymentService.paymentDone = True
                self.actualProcessingRequest = None
                self.lastRequestArrived = None
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
            self.paymentService.sendAckRequest(STATUS_MACHINES_ORDER_CANCELLED_OK,request.idOrder)
            return True
        
    def enrouteConfigRequest(self,request):
        if( isinstance(request,ConfigStackRequest ) ): 
            print("Arrive ConfigRequest")
            self.paymentService.billWalletService.bv.configMode(request.stackA, request.stackB)
            return True
        
    def enrouteConnectedRequest(self,request):
        if( isinstance(request,ConnectedRequest ) ): 
            print("Arrive ConfigRequest")
            self.sendDataTPV('{"typeRequest":'+str(TYPE_CONNECTED_REQUEST)+',"stackA":' + str(self.paymentService.billWalletService.bv.stackA )+ ',"stackB":'+str(self.paymentService.billWalletService.bv.stackB)+'}')
            return True