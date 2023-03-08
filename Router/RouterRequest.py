from Model.TPVCommunication.Request.Request import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Model.TPVCommunication.Request.ConnectedRequest import *
from Model.TPVCommunication.Request.ResetRequest import *
from Model.TPVCommunication.Request.GetActualConfigRequest import *
from Model.TPVCommunication.Request.BlockedMachine import *
from Services.PaymentService import * 
from TpvYsolveMqtt import *
from utils.RequestCodes import *

class Router():
    def __init__(self,actualProcessingRequest, lastRequestArrived, tpvComm:TpvYsolveMqtt):
        self.routeInitialized = False
        self.actualProcessingRequest = actualProcessingRequest
        self.lastRequestArrived = lastRequestArrived
        self.paymentService:PaymentService = None
        self.tpv:TpvYsolveMqtt = tpvComm
        self.sendErrorTPV = self.tpv.sendError
        self.sendDataTPV = self.tpv.sendData
        self.autoCancelRequest = self.tpv.sendAutoCancelRequest
        self.setMqttListenerPaused = None
        self.initializePaymentService()
        self.shouldCountMoney = False
        
    def initializePaymentService(self):
        self.paymentService = PaymentService(self.sendErrorTPV,self.sendDataTPV, self.autoCancelRequest)
    
    def setActualProcessingRequest(self,request):
        self.actualProcessingRequest= request
    def setlastRequestArrived(self,request):
        self.lastRequestArrived = request
    def setErrorPayingInDisplay(self,error):
        self.paymentService.setErrorInDisplay(error)

    def countMoneyAvailable(self):
        self.paymentService.coinWalletService.coinwallet.enableReceivedMode = False
        time.sleep(.1)
        self.paymentService.coinWalletService.coinwallet.tubeStatus()
        self.paymentService.billWalletService.bv.inhibitAndGetCurrentBillCount()
        self.shouldCountMoney = False
        time.sleep(.1)
        self.paymentService.coinWalletService.coinwallet.enableReceivedMode = True

    def routeRequest(self, setMqttListenerPaused):
        while self.paymentService.machineBlockedPayments :
            time.sleep(.2)
        self.setMqttListenerPaused = setMqttListenerPaused
        self.paymentService.displayController.setWelcomePage()
        self.routeInitialized = True
        self.setMqttListenerPaused(False)
        if(self.shouldCountMoney):
            self.countMoneyAvailable()
        self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.doneStatus)
        self.sendDataTPV('{"success":"Maquina disponible para recibir pedidos"}')

        while True:
            self.actualProcessingRequest = self.lastRequestArrived

            # Procesar pago
            if( isinstance(self.actualProcessingRequest,PayRequest ) ):
                self.tpv.actualProcessingRequest = self.actualProcessingRequest
                if(self.actualProcessingRequest.idOrder == -1):
                    self.sendDataTPV('{"success":"Rellenando monedero"}')
                else:
                    self.sendDataTPV('{"success":"Pedido recibido"}')

                print("Arrive PayRequest: " + str(self.actualProcessingRequest.price) + " €")
                self.paymentService.startMachinesPayment(self.actualProcessingRequest)
                self.paymentService.paymentDone = True
                self.actualProcessingRequest = None
                self.lastRequestArrived = None
                self.shouldCountMoney = True
                return True

    # Cancelar 
    def enrouteCancelRequest(self,request):
        if( isinstance(request,CancelRequest ) and self.routeInitialized): 
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.cancelStatus)
            if(request.idOrder != -1):
                self.sendDataTPV('{"success":"Cancelando..."}')
            time.sleep(1)
            print("Arrive paymentDone")
            # poner el precio de la orden a 0 así realizará la cancelación
            self.actualProcessingRequest = None
            self.lastRequestArrived = None
            self.paymentService.paymentDone = True
            self.paymentService.setCancelledStatus(True)
            self.paymentService.sendAckRequest(STATUS_MACHINES_ORDER_CANCELLED_OK,request.idOrder)
            time.sleep(1)
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.doneStatus)
            self.paymentService.displayController.setWelcomePage()
            if(request.idOrder == -1):
                self.sendDataTPV('{"success":"Rellenado de monedero completado"}')
            else:
                self.sendDataTPV('{"success":"Cancelado completado"}')
            return True
    
    # Request de configuracion 
    def enrouteConfigRequest(self,request):
        if( isinstance(request,ConfigStackRequest ) and self.routeInitialized ):
            if(self.paymentService.isPaying):
                self.sendErrorTPV("Error: No se puede configurar mientras un pedido pendiente. Termine la orden pendiente.")
                return False
            self.sendDataTPV('{"success":"Configurando billetero"}')
            
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.configStatus)

            print("Arrive ConfigRequest")
            self.paymentService.billWalletService.bv.configMode(request.stackA, request.stackB,request.quantityStackA,request.quantityStackB)
            self.paymentService.ledsController.setLedsPayingState(self.paymentService.ledsController.doneStatus)
            self.sendDataTPV('{"success":"Billetero configurado completado"}')
            time.sleep(.2)
            self.paymentService.unlockPaymentMachine()

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
            self.sendDataTPV('{"success":"Conectado"}')
            print("Arrive ConfigRequest")
            self.sendDataTPV(
                '{"typeRequest":'+str(TYPE_CONNECTED_REQUEST)+ ',"blocked":' + str(int(self.paymentService.machineBlockedPayments))+
                '}')
            return True
         
    def enrouteGetActualConfigRequest(self,request):
        if( isinstance(request,GetActualConfigRequest ) and self.routeInitialized ): 
            if(not self.paymentService.isPaying):
                print("Arrive GetActualConfigRequest")
                self.sendDataTPV(
                    '{"typeRequest":'+str(TYPE_GET_ACTUAL_CONFIG_REQUEST)+
                    ',"billwallet":{' +
                        '"availableMoney":' + str(self.paymentService.billWalletService.bv.availableMoneyInBills)+
                        ',"stackA":' + str(self.paymentService.billWalletService.bv.stackA )+
                        ',"stackB":'+str(self.paymentService.billWalletService.bv.stackB)+ 
                        ',"quantityStackA":' + str(self.paymentService.billWalletService.bv.quantityStackA )+
                        ',"quantityStackB":' + str(self.paymentService.billWalletService.bv.quantityStackB )+
                        "}"
                    ',"coinwallet":{' +
                        '"availableMoney":' + str(self.paymentService.coinWalletService.coinwallet.availableMoneyInCoins)+
                        ',"tube_0_05":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_05 )+
                        ',"tube_0_10":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_10 )+
                        ',"tube_0_20":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_20 )+
                        ',"tube_0_50":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_0_50 )+
                        ',"tube_1_00":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_1_00 )+
                        ',"tube_2_00":' + str(self.paymentService.coinWalletService.coinwallet.tubeQnty_2_00 )+
                        '}' +
                    '}')
                return True
            else:
                self.sendErrorTPV("Error: No se puede configurar mientras se está pagando. Termine la orden pendiente.")
                return False

    def enrouteBlockedMachine(self,request):
        if( isinstance(request,BlockedMachine ) and self.routeInitialized ): 
            if(not self.paymentService.isPaying):
                print("Arrive BlockedMachine")
                self.paymentService.billWalletService.bv.currentBillCountRequest()
                self.paymentService.coinWalletService.coinwallet.tubeStatus()
                self.paymentService.unlockPaymentMachine()

                return True
            else:
                self.sendErrorTPV("Error: No se puede configurar mientras se está pagando. Termine la orden pendiente.")
                return False
    