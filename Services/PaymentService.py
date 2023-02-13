from Controller.Display.DisplayController import *
from Controller.CoinWallet.CoinWalletService import *
from Controller.Leds.LedsController import *
from Controller.Printer.PrinterController import *
import asyncio
from Controller.UsbPortDetector import *
import threading
from Controller.BillWallet.BillWalletService import *
from utils.RequestCodes import *
PRINTER = True
COINWALLET = True
BILLWALLET = True
DISPLAY = True
LEDS = True


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

        self.totalAmount = 0
        self.priceClientShouldPay = 0
        self.payRequest: PayRequest = None
        self.actualCancelled = False
        while(self.billWalletService.stackA == None ):
            time.sleep(.5)


    def setErrorInDisplay(self, error):
        if(DISPLAY):
            self.displayController.displayError(error)

    def initializeControllers(self):
        self.checkPortsConnected()
        if(LEDS):
            try:
                self.ledsController = LedsController(self.portLeds)
                time.sleep(.2)
                self.ledsController.setLedsPayingState(self.ledsController.configStatus)
                print("Leds Initialized OK")

            except:
                print("Please Connect Leds ")
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(3)
                self.initializeControllers()
                self.sendErrorTPV("Some problems ocurred when init Leds")

        if(DISPLAY):
            try:
                self.displayController = DisplayController(self.portDisplay, self.tpv)
                print("Display Initialized OK")
            except:
                print("Please Connect Display")
                # TODO: Informar al tpv de que no estan conectados
                self.setErrorInDisplay("Please Connect Display")
                self.sendErrorTPV("Some problems ocurred when init Display")
                time.sleep(3)
                self.initializeControllers()
        if(BILLWALLET):
            try:
                self.billWalletService: BillWalletService = BillWalletService(
                    self.manageTotalAmount, port=self.portBilletero, sendErrorTpv=self.sendErrorTPV)

                billwWalletThread = threading.Thread(
                    target=self.billWalletService.run)
                billwWalletThread.start()

                print("BillWallet Initialized OK")

            except:
                print("Please Connect BillWallet ")
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(3)
                self.initializeControllers()
                self.sendErrorTPV("Some problems ocurred when init Billwallet")
        if(COINWALLET):
            try:
                # print("MON: ", self.portMonedero)
                self.coinWalletService: CoinWalletService = CoinWalletService(
                    self.manageTotalAmount, port=self.portMonedero)
                time.sleep(.4)
                coinWalletPollThread = threading.Thread(target=self.coinWalletService.run)
                coinWalletPollThread.start()
                print("CoinWallet Initialized OK")
            except Exception as e:
                print("Please Connect CoinWallet ", e)
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(3)
                self.initializeControllers()
                self.sendErrorTPV("Some problems ocurred when init CoinWallet")
        if(PRINTER):
            try:
                self.printerController = PrinterController()
                print("Printer Initialized OK")
            except:
                print("Please Connect Printer ")
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(3)
                self.initializeControllers()
                self.sendErrorTPV("Some problems ocurred when init Printer")
     
        
    def checkPortsConnected(self):
        print("Finding Ports...")
        (self.portBilletero, self.portMonedero, self.portDisplay, self.portLeds) = self.UsbDetector.detect_ports()

        if(BILLWALLET):
            if(self.portBilletero == None):
                self.sendErrorTPV("ERROR: BillWallet NO connected")
                time.sleep(3)
                self.checkPortsConnected()

        if(COINWALLET):
            if(self.portMonedero == None):
                self.sendErrorTPV("ERROR: CoinWallet NO connected")
                time.sleep(3)
                self.checkPortsConnected()
       
        if(DISPLAY):
            if(self.portDisplay == None):
                self.sendErrorTPV("ERROR: Display NO connected")
                time.sleep(3)
                self.checkPortsConnected()
        # TODO: Cuando obtenga un error crear una funcion aqui que envie al tpv y muestre color rojo con los leds que será pasada como referencia a los siguientes niveles
        if(LEDS):
            if(self.portLeds == None):
                self.sendErrorTPV("ERROR: Leds NO connected")
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

    def checkIfPaymentComplete(self):
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
            self.billWalletService.bv.pausePollThread()
            self.coinWalletService.coinwallet.disableInsertCoins()
            self.displayController.setByePage()
            self.paymentDone = True

    def returnChangeToClient(self, amount):
        changeInBills = 0
        changeInCoins = 0
        minimumBill = self.billWalletService.bv.minBill
        
        change = round(amount, 2)
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
                # Devolver Billetes
                returnedToUser = self.__billBack(toReturn)
                # Recalcular dinero a devolver
                toReturn = toReturn - returnedToUser
        
        self.totalAmount = 0
        self.priceClientShouldPay = 0

        print(" Amount: " + str(amount) + " Order: " + str(self.priceClientShouldPay) + " Change" + str(change) +
              " changeInBills" + str(changeInBills) + " changeInCoins" + str(changeInCoins) + " totalAmount: " + str(self.totalAmount))

        # TODO: inhibir monedas
        # self.inhibitCoins()
        # self.paymentDone = True
   

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
            print("ERROR: TO PAY " , changeBills , " menor que minbill: ",minBill)
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
            self.sendErrorTPV("Not bills available to pay")
        if(payFromStack1 == True):
            return minBill
        if(payFromStack2 == True):
            return maxBill
    def printTicket(self):
        self.printerController.prepareOrderToPrint(self.payRequest)
        try:
            if(self.actualCancelled == True):
                self.printerController.print("CANCELLED")
                return
            else:
                self.printerController.print("PAY")
        except:
            self.sendErrorTPV("Error: Printer is disconnected")
            time.sleep(3)
            self.printTicket()
            pass
    
    def sendAckRequest(self, status, idOrder):
        self.sendDataTPV('{"status":' + str(status)+ ',"idOrder":'+str(idOrder)+'}')

    def startMachinesPayment(self, payRequest: PayRequest):
        print("startMachinesPayment")
        self.sendAckRequest(STATUS_MACHINES_RECEIVED_REQUEST,payRequest.idOrder)
        self.actualCancelled = False
        self.totalAmount = 0
        self.coinWalletService.coinwallet.enableInsertCoins()
        if(LEDS):
            self.ledsController.setLedsPayingState(self.ledsController.payStatus)

        self.billWalletService.bv.resumePollThread()
        
        self.payRequest = payRequest
        self.paymentDone = False
        self.priceClientShouldPay = payRequest.price

        if(DISPLAY):
            self.displayController.setOrderPage()
            self.displayController.display(self.payRequest)
        self.sendAckRequest(STATUS_MACHINES_ARE_PROCESSING_REQUEST,payRequest.idOrder)
        
        # Esperando a pagar
        while self.paymentDone == False:
            print("waiting pay")
            self.checkIfPaymentComplete()
            time.sleep(1)
        self.sendAckRequest(STATUS_MACHINES_PAYING_REQUEST_FINISHED,payRequest.idOrder)

        if(PRINTER):
            if(str(self.payRequest.idOrder) == str(-1)):
                print("CHARGE MACHINEEEES")
                self.payRequest.price = self.totalAmount 
            self.sendAckRequest(STATUS_MACHINES_PRINTING_TICKET,payRequest.idOrder)
            self.printTicket()

        if(self.actualCancelled == True ):
            if( payRequest.idOrder != -1 ):
                self.priceClientShouldPay = 0 
        # Esperando a devolver en caso de tener que devolver
        while self.totalAmount > self.priceClientShouldPay:
            print("waiting payOut")
            change = self.totalAmount - self.priceClientShouldPay
            self.returnChangeToClient(change)
            time.sleep(1)
        if(self.actualCancelled == True):
            self.billWalletService.bv.pausePollThread()

        if(LEDS):
            time.sleep(.2)
            self.ledsController.setLedsPayingState(self.ledsController.doneStatus)
        self.coinWalletService.coinwallet.disableInsertCoins()
        print("payment done from __startMachinesPayment")
        self.paymentDone = False
        print("paymentDone",self.paymentDone)
        time.sleep(3)
        self.sendAckRequest(STATUS_MACHINES_ORDER_FINISHED,payRequest.idOrder)

        self.displayController.setWelcomePage()
        self.actualProcessingRequest = None
        self.lastRequestArrived = None


class LedsPortNotConnected(Exception):
    pass
class DisplayPortNotConnected(Exception):
    pass
class BillwalletPortNotConnected(Exception):
    pass
class CoinwalletPortNotConnected(Exception):
    pass
class PrinterPortNotConnected(Exception):
    pass