from Model.TPVCommunication.Request.Request import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Model.TPVCommunication.Request.ConnectedRequest import *
from Model.TPVCommunication.Request.ResetRequest import *
from Model.TPVCommunication.Request.GetActualConfigRequest import *
from Services.PaymentService import * 
from TpvYsolveMqtt import *
from utils.RequestCodes import *

class Router():
    def __init__(self,actualProcessingRequest, lastRequestArrived, tpvComm:TpvYsolveMqtt):
        self.routeInitialized = False
        self.actualProcessingRequest = actualProcessingRequest
        self.lastRequestArrived = lastRequestArrived
        self.paymentService:PaymentService = None
        self.sendErrorTPV = tpvComm.sendError
        self.sendDataTPV = tpvComm.sendData
        self.setMqttListenerPaused = None
        self.initializePaymentService()
        
    def initializePaymentService(self):
        self.paymentService = PaymentService(self.sendErrorTPV,self.sendDataTPV)
    
    def setActualProcessingRequest(self,request):
        self.actualProcessingRequest= request
    def setlastRequestArrived(self,request):
        self.lastRequestArrived = request
    def setErrorPayingInDisplay(self,error):
        self.paymentService.setErrorInDisplay(error)

    def routeRequest(self, setMqttListenerPaused):
        self.setMqttListenerPaused = setMqttListenerPaused
        self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.doneStatus)
        self.paymentService.displayController.setWelcomePage()
        self.routeInitialized = True
        self.setMqttListenerPaused(False)
        while True:
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
        if( isinstance(request,CancelRequest ) and self.routeInitialized): 
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.cancelStatus)
            time.sleep(1)
            print("Arrive paymentDone")
            # poner el precio de la orden a 0 así realizará la cancelación
            self.actualProcessingRequest = None
            self.lastRequestArrived = None
            self.paymentService.paymentDone = True
            self.paymentService.setCancelledStatus(True)
            self.paymentService.sendAckRequest(STATUS_MACHINES_ORDER_CANCELLED_OK,request.idOrder)
            time.sleep(1)
            self.paymentService.displayController.setWelcomePage()
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.doneStatus)
            return True
    
    # Request de configuracion 
    def enrouteConfigRequest(self,request):
        if( isinstance(request,ConfigStackRequest ) and self.routeInitialized ):
            if(self.paymentService.isPaying):
                self.sendErrorTPV("Error: No se puede configurar mientras un pedido pendiente. Termine la orden pendiente.")
                return False
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.configStatus)

            print("Arrive ConfigRequest")
            self.paymentService.billWalletService.bv.configMode(request.stackA, request.stackB,request.quantityStackA,request.quantityStackB)
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.doneStatus)
            return True

    # Request de reset 
    def enrouteResetRequest(self,request):
        if( isinstance(request,ResetRequest ) and self.routeInitialized): 
            print("Arrive ResetRequest")
        
    # Request de conexión 
    def enrouteConnectedRequest(self,request):
        if( isinstance(request,ConnectedRequest)): 
            if(not self.routeInitialized ):
                self.sendErrorTPV("Error: No se puede conectar mientras se está configurando.")
                return False
            if(self.paymentService.isPaying):
                self.sendErrorTPV("Error: No se puede configurar mientras tiene un pedido pendiente. Termine o cancele la orden pendiente.")
                return False
                
            print("Arrive ConfigRequest")
            self.sendDataTPV(
                '{"typeRequest":'+str(TYPE_CONNECTED_REQUEST)+
                ',"stackA":' + str(self.paymentService.billWalletService.bv.stackA )+
                ',"stackB":'+str(self.paymentService.billWalletService.bv.stackB)+
                ',"quantityStackA":' + str(self.paymentService.billWalletService.bv.quantityStackA )+
                ',"quantityStackB":' + str(self.paymentService.billWalletService.bv.quantityStackB )+
                '}')
            return True
         
    def enrouteGetActualConfigRequest(self,request):
        if( isinstance(request,GetActualConfigRequest ) and self.routeInitialized ): 
            if(not self.paymentService.isPaying): 
                print("Arrive GetActualConfigRequest")

                self.paymentService.billWalletService.bv.inhibitAndGetCurrentBillCount()
                # TODO:
                # self.paymentService.coinWalletService.coinwallet.inhibitAndGetCurrentCoinCount()

                self.sendErrorTPV(
                    '{"typeRequest":'+str(TYPE_CONNECTED_REQUEST)+
                    ',"billwallet":{' +
                        '"stackA":' + str(self.paymentService.billWalletService.bv.stackA )+
                        ',"stackB":'+str(self.paymentService.billWalletService.bv.stackB)+ 
                        ',"quantityStackA":' + str(self.paymentService.billWalletService.bv.quantityStackA )+
                        ',"quantityStackB":' + str(self.paymentService.billWalletService.bv.quantityStackB )+
                        "}"
                    ',"coinwallet":{' +
                        '"tube_0_05":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_05 )+
                        '"tube_0_10":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_10 )+
                        '"tube_0_20":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_20 )+
                        '"tube_0_50":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_50 )+
                        '"tube_1_00":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_1_00 )+
                        '"tube_2_00":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_2_00 )+
                        "}"
                    '}')
                self.sendDataTPV(
                    '{"typeRequest":'+str(TYPE_CONNECTED_REQUEST)+
                    ',"billwallet":{' +
                        '"stackA":' + str(self.paymentService.billWalletService.bv.stackA )+
                        ',"stackB":'+str(self.paymentService.billWalletService.bv.stackB)+ 
                        ',"quantityStackA":' + str(self.paymentService.billWalletService.bv.quantityStackA )+
                        ',"quantityStackB":' + str(self.paymentService.billWalletService.bv.quantityStackB )+
                        "}"
                    ',"coinwallet":{' +
                        '"tube_0_05":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_05 )+
                        '"tube_0_10":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_10 )+
                        '"tube_0_20":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_20 )+
                        '"tube_0_50":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_50 )+
                        '"tube_1_00":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_1_00 )+
                        '"tube_2_00":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_2_00 )+
                        "}"
                    '}')
                return True
            else:
                self.sendErrorTPV("Error: No se puede configurar mientras se está pagando. Termine la orden pendiente.")
                return False
