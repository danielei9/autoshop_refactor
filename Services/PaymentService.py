from Controller.Display.DisplayController import *
from Controller.CoinWallet.CoinWalletService import *
from Controller.Leds.LedsController import *
from Controller.Printer.PrinterController import *
import asyncio
from Controller.UsbPortDetector import *
import threading
from Controller.BillWallet.BillWalletService import *
from utils.RequestCodes import *

PRINTER = False
COINWALLET = True
BILLWALLET = True
DISPLAY = True
LEDS = True

PRINTER_ID = "Impresora"
COINWALLET_ID = "Monedero"
BILLWALLET_ID = "Billetero"
DISPLAY_ID = "Pantalla"
LEDS_ID = "Led"

class PaymentService():

    def __init__(self, sendErrorTPV, sendDataTPV):
        self.billWalletService: BillWalletService = None
        self.coinWalletService: CoinWalletService = None
        self.portBilletero = None
        self.portMonedero = None
        self.portDisplay = None
        self.portLeds = None
        self.UsbDetector = USBPortDetector()
        (self.portBilletero, self.portMonedero, self.portDisplay,
         self.portLeds) = self.UsbDetector.detect_ports()
        
        self.sendDataTPV = sendDataTPV
        self.sendErrorTPV = sendErrorTPV

        self.tpv = (self.sendDataTPV,self.sendErrorTPV)

        self.initializeControllers()
        self.isPaying = False
        self.totalAmount = 0
        self.priceClientShouldPay = 0
        self.payRequest: PayRequest = None
        self.actualCancelled = False
        self.change = 0.00
        while(self.billWalletService.stackA == None ):
            time.sleep(.5)

    def __initializeLedsController(self):
        if(LEDS):
            try:
                self.ledsController = LedsController(self.portLeds)
                time.sleep(.2)
                self.ledsController.setLedsPayingState(self.ledsController.configStatus)
                print("Leds Initialized OK")

            except Exception as e:
                print("Please Connect Leds ", e)
                self.setMachineErrorStatus(LEDS_ID)
                time.sleep(3)
                self.__initializeLedsController()

    def __initializeDisplayController(self):
        if(DISPLAY):
            try:
                self.displayController = DisplayController(self.portDisplay, self.tpv)
                self.displayController.setWelcomePage()

                print("Display Initialized OK")
            except Exception as e:
                print("Please Connect Display ", e)
                self.setMachineErrorStatus(DISPLAY_ID)
                time.sleep(3)
                self.__initializeDisplayController()

    def __initializeBillwalletController(self):
        if(BILLWALLET):
            try:
                self.billWalletService: BillWalletService = BillWalletService(
                    self.manageTotalAmount, port=self.portBilletero, sendErrorTpv=self.sendErrorTPV)

                billwWalletThread = threading.Thread(
                    target=self.billWalletService.run)
                billwWalletThread.start()

                print("BillWallet Initialized OK")

            except Exception as e:
                print("Please Connect BillWallet ", e)
                self.setMachineErrorStatus(BILLWALLET_ID)
                time.sleep(3)
                self.__initializeBillwalletController()

    def __initializeCoinwalletController(self):
        if(COINWALLET):
            try:
                self.coinWalletService: CoinWalletService = CoinWalletService(
                    self.manageTotalAmount, port=self.portMonedero)
                time.sleep(.4)
                coinWalletPollThread = threading.Thread(target=self.coinWalletService.run)
                coinWalletPollThread.start()
                print("CoinWallet Initialized OK")
            except Exception as e:
                print("Please Connect CoinWallet ", e)
                self.setMachineErrorStatus(COINWALLET_ID)
                time.sleep(3)
                self.__initializeCoinwalletController()

    def __initializePrinterController(self):
        if(PRINTER):
            try:
                self.printerController = PrinterController()
                print("Printer Initialized OK")
            except Exception as e:
                print("Please Connect printer ", e)
                self.setMachineErrorStatus(PRINTER_ID)
                time.sleep(3)
                self.__initializePrinterController()
    
    def setMachineErrorStatus(self,deviceID):
        self.sendErrorTPV(deviceID + " desconectado. Por favor revise la conexión.")
        self.__setErrorInDisplay(deviceID + " desconectado. Por favor revise la conexión.")
        
    def __setErrorInDisplay(self, error):
        if(DISPLAY):
            self.displayController.displayError(error)

    def __coinBack(self, change):
        print("coin back")
        self.coinWalletService.coinwallet.enableInsertCoins()
        time.sleep(.2)
        self.coinWalletService.coinwallet.cashBack(change)
        time.sleep(.2)
        self.coinWalletService.coinwallet.disableInsertCoins()
        time.sleep(.2)

    def __billBack(self, changeBills):
        print("Devolver: " + str(changeBills) + " €")
        payFromStack1 = False
        payFromStack2 = False

        maxBill = self.billWalletService.bv.maxBill
        minBill = self.billWalletService.bv.minBill


        if(changeBills >= maxBill):
            print("Pagar max billete ", maxBill)
            if(maxBill == self.billWalletService.bv.stackA):
                payFromStack1 = True
                payFromStack2 = False
            if(maxBill == self.billWalletService.bv.stackB):
                payFromStack1 = False
                payFromStack2 = True
        elif (changeBills >= minBill):
            print("PAY min billete ", minBill)

            if(minBill == self.billWalletService.bv.stackA):
                payFromStack1 = True
                payFromStack2 = False
            if(minBill == self.billWalletService.bv.stackB):
                payFromStack1 = False
                payFromStack2 = True
        else:
            print("ERROR: TO PAY " , changeBills , " menor que minbill: ",minBill,". Need to pay to finished: " + str(changeBills))
            # TODO: BORRASR
            payFromStack1 = True
            payFromStack2 = False
            self.sendErrorTPV("Failed to pay bills")
            
        (status, data) = self.billWalletService.bv.bv_status

        while (status != IDLE):
            print("__billBack: Esperando estado IDLE, actual: " , status)
            (status, data) = self.billWalletService.bv.bv_status
            time.sleep(.2)
            if(self.billWalletService.bv.pause_flag):
                (status, data) = self.billWalletService.bv.req_status()
        # time.sleep(.2)
        payoutDone = self.billWalletService.bv.payout(payFromStack1, payFromStack2)
        if(payoutDone == -1):
            self.sendErrorTPV("ERROR: Not bills available to pay. Need to pay to finished: " + str(changeBills))
        if(payFromStack1 == True):
            return minBill
        if(payFromStack2 == True):
            return maxBill
 
    def __initializePayment(self,payRequest:PayRequest):
        print("startMachinesPayment")
        self.sendAckRequest(STATUS_MACHINES_RECEIVED_REQUEST,payRequest.idOrder)
        self.setCancelledStatus(False)
        self.isPaying = True
        self.totalAmount = 0
        self.coinWalletService.coinwallet.enableInsertCoins()
        self.payRequest = payRequest
        self.billWalletService.bv.resumePollThread()
        self.paymentDone = False
        self.priceClientShouldPay = payRequest.price
        if(LEDS):
            self.ledsController.setLedsPayingState(self.ledsController.payStatus)

        if(DISPLAY):
            self.displayController.setOrderPage()
            self.displayController.display(self.payRequest)
        self.sendAckRequest(STATUS_MACHINES_ARE_PROCESSING_REQUEST,payRequest.idOrder)

    def initializeControllers(self):
        self.checkPortsConnected()
        self.__initializePrinterController()
        self.__initializeCoinwalletController()
        self.__initializeBillwalletController()
        self.__initializeDisplayController()
        self.__initializeLedsController()

    def checkPortsConnected(self):
        print("Finding Ports...")
        (self.portBilletero, self.portMonedero, self.portDisplay, self.portLeds) = self.UsbDetector.detect_ports()

        if(BILLWALLET):
            if(self.portBilletero == None):
                self.setMachineErrorStatus(BILLWALLET_ID)
                time.sleep(3)
                self.checkPortsConnected()

        if(COINWALLET):
            if(self.portMonedero == None):
                self.setMachineErrorStatus(COINWALLET_ID)
                time.sleep(3)
                self.checkPortsConnected()
       
        if(DISPLAY):
            if(self.portDisplay == None):
                self.sendErrorTPV(DISPLAY_ID)
                time.sleep(3)
                self.checkPortsConnected()
        if(LEDS):
            if(self.portLeds == None):
                self.sendErrorTPV(LEDS_ID)
                time.sleep(3)
                self.checkPortsConnected()

    def manageTotalAmount(self, cantidad):
        self.totalAmount = float(self.totalAmount) + float(cantidad)
        print("manageTotalAmount : TotalAmount ",
              self.totalAmount, " cantidad ", cantidad)
        # self.billWalletService.bv.resumePollThread()
    
        if(DISPLAY):
            try:
                self.displayController.printProgress(str(round(
                    self.totalAmount*1.00, 2)) + "", round((self.totalAmount/self.priceClientShouldPay) * 100))
            except ZeroDivisionError:
                print("DISPLAY: 100% Pagado")

    def checkIfUserPaymentComplete(self):
        print("self.totalAmount >= self.priceClientShouldPay  ", self.totalAmount, "  ",self.priceClientShouldPay  )
        if (self.totalAmount >= self.priceClientShouldPay):
                (statusBillWallet,dataBillWallet ) = self.billWalletService.bv.bv_status 
                while ( statusBillWallet != IDLE ):
                    (statusBillWallet,dataBillWallet ) = self.billWalletService.bv.bv_status 
                    time.sleep(.2)
                    print("BV : Waiting IDLE")
                self.setPaymentDone()

    def setPaymentDone(self):
            print("PAGO COMPLETADO")
            time.sleep(.2)
            self.billWalletService.bv.pausePollThread()
            self.coinWalletService.coinwallet.disableInsertCoins()
            self.displayController.setByePage()
            self.paymentDone = True

    def returnChangeToClient(self, amount):
        changeInBills = 0
        changeInCoins = 0
        minimumBill = self.billWalletService.bv.minBill
        
        change = round(amount, 2)
        self.change = change
        changeInCoins = round(change % minimumBill, 2)
        changeInBills = change - changeInCoins  
        
        if(changeInCoins == minimumBill):
            changeInBills += changeInCoins
            changeInCoins = 0
        
        # CAMBIO DE MONEDAS
        if(changeInCoins > 0 ):
                self.__coinBack( changeInCoins )

        # CAMBIO DE BILLETES
        print("MINIMO BILLETE",minimumBill)

        if(changeInBills >= minimumBill):
            toReturn = round(changeInBills)
            # Mientras tengamos que devolver dinero...
            while(toReturn > 0):
                print("**** TO RETURN ", toReturn)
                time.sleep(.2)
                if(self.billWalletService.bv.quantityStackA > 1 and self.billWalletService.bv.quantityStackB > 1 ):
                    # Devolver Billetes
                    returnedToUser = self.__billBack(toReturn)
                    toReturn = toReturn - returnedToUser
                else:
                    self.sendErrorTPV("")
                    time.sleep(2)
                    # self.actualCancelled = True
                # Recalcular dinero a devolver

        self.totalAmount = 0
        self.priceClientShouldPay = 0

        print(" Amount: " + str(amount) + " Order: " + str(self.priceClientShouldPay) + " Change" + str(change) +
              " changeInBills" + str(changeInBills) + " changeInCoins" + str(changeInCoins) + " totalAmount: " + str(self.totalAmount))
    
    def printTicket(self):
        self.printerController.prepareOrderToPrint(self.payRequest,self.change,self.totalAmount)
        try:
            if(self.actualCancelled == True):
                self.printerController.print("CANCELLED")

                return
            else:
                self.printerController.print("PAY")
        except:
            self.sendErrorTPV("Error: Printer is disconnected. Pls check connections and reset machine.")
            time.sleep(3)
            self.printTicket()
            pass
    
    def sendAckRequest(self, status, idOrder):
        self.sendDataTPV('{"status":' + str(status)+ ',"idOrder":'+str(idOrder)+'}')
   
    def setCancelledStatus(self,state):
        if(state):
            print("Order Cancelled")
        self.actualCancelled = state
        
    def startMachinesPayment(self, payRequest: PayRequest):
        self.__initializePayment(payRequest)
        # Esperando a pagar
        while self.paymentDone == False:
            print("waiting pay")
            self.checkIfUserPaymentComplete()
            time.sleep(1)
        self.sendAckRequest(STATUS_MACHINES_PAYING_REQUEST_FINISHED,payRequest.idOrder)

        if(PRINTER):   
            if(str(self.payRequest.idOrder) == str(-1)):
                print("CHARGE MACHINES")
                self.payRequest.price = self.totalAmount 
            self.sendAckRequest(STATUS_MACHINES_PRINTING_TICKET,payRequest.idOrder)
            self.change = self.totalAmount - self.priceClientShouldPay
            self.printTicket()

        if(self.actualCancelled == True ):
            if( payRequest.idOrder != -1 ):
                self.priceClientShouldPay = 0 

        # TODO:  Preguntando cuantos billetes hay 
       # self.billWalletService.bv.currentBillCountRequest()

        # Esperando a devolver en caso de tener que devolver
        if (self.billWalletService.bv.quantityStackA > 1 and self.billWalletService.bv.quantityStackB > 1) :
            # Puede pagar
            while self.totalAmount > self.priceClientShouldPay:
                print("waiting payOut")
                change = self.totalAmount - self.priceClientShouldPay
                self.returnChangeToClient(change)
                time.sleep(1)
        else:
            # No puede pagar
            while(self.actualCancelled != True):
                print("Waiting cancel request. No bills")
                self.sendErrorTPV("ERROR: Waiting cancel request. No bills available")
                time.sleep(3)
                pass
        # TODO:self.billWalletService.bv.currentBillCountRequest()

        self.sendDataTPV(
                        '{"typeRequest":'+str(TYPE_CONNECTED_REQUEST)+
                        ',"stackA":' + str(self.billWalletService.bv.stackA )+
                        ',"stackB":'+str(self.billWalletService.bv.stackB)+
                        ',"quantityStackA":' + str(self.billWalletService.bv.quantityStackA )+
                        ',"quantityStackB":' + str(self.billWalletService.bv.quantityStackB )+
                        '}')
        
        if(self.actualCancelled == True):
            self.billWalletService.bv.pausePollThread()

        if(LEDS):
            time.sleep(.2)
            self.ledsController.setLedsPayingState(self.ledsController.doneStatus)
        self.coinWalletService.coinwallet.disableInsertCoins()
        print("payment done from __startMachinesPayment")
        self.paymentDone = False
        time.sleep(3)
        self.sendAckRequest(STATUS_MACHINES_ORDER_FINISHED,payRequest.idOrder)

        self.displayController.setWelcomePage()
        self.actualProcessingRequest = None
        self.lastRequestArrived = None
        self.isPaying = False