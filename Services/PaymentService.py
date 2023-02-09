from Controller.Display.DisplayController import *
from Controller.CoinWallet.CoinWalletService import *
from Controller.Leds.LedsController import *
from Controller.Printer.PrinterController import *
import asyncio
from Controller.UsbPortDetector import *
import threading
from Controller.BillWallet.BillWalletService import *

PRINTER = False
COINWALLET = True
BILLWALLET = True
DISPLAY = False
LEDS = False


class PaymentService():

    def __init__(self):
        self.billWalletService: BillWalletService = None
        self.coinWalletService: CoinWalletService = None

        self.portBilletero = None
        self.portMonedero = None
        self.portDisplay = None
        self.portLeds = None
        UsbDetector = USBPortDetector()
        (self.portBilletero, self.portMonedero, self.portDisplay,
         self.portLeds) = UsbDetector.detect_ports()

        self.initializeControllers()

        self.totalAmount = 0
        self.priceClientShouldPay = 0
        self.payRequest: PayRequest = None

    def setErrorInDisplay(self, error):
        if(DISPLAY):
            self.displayController.displayError(error)

    def initializeControllers(self):
        self.checkPorsConnected()
        if(DISPLAY):
            try:
                self.displayController = DisplayController(self.portDisplay)
                print("Display Initialized OK")
            except:
                print("Please Connect Display")
                # TODO: Informar al tpv de que no estan conectados
                self.setErrorInDisplay("Please Connect Display")
                time.sleep(5)
                pass
                self.initializeControllers()
        if(BILLWALLET):
            try:
                self.billWalletService: BillWalletService = BillWalletService(
                    self.manageTotalAmount, port=self.portBilletero)

                billwWalletThread = threading.Thread(
                    target=self.billWalletService.run)
                billwWalletThread.start()

                print("BillWallet Initialized OK")

            except:
                print("Please Connect BillWallet ")
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(5)
        if(COINWALLET):
            try:
                print("MON: ", self.portMonedero)
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
        if(PRINTER):
            try:
                self.printerController = PrinterController()
                print("Printer Initialized OK")
            except:
                print("Please Connect Printer ")
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(5)
        if(LEDS):
            try:
                self.ledsController = LedsController(self.portLeds)
                # self.ledsController.setLedsPayingState(self.ledsController.configStatus)
                print("Leds Initialized OK")

            except:
                print("Please Connect Leds ")
                # TODO: Informar al tpv de que no estan conectados
                time.sleep(5)

    def checkPorsConnected(self):
        print("Trying to connect Ports")

        if(self.portBilletero == None):
            # TODO: Informar al tpv de que no estan conectados
            print("BillWallet NO connected")
        if(self.portMonedero == None):
            # TODO: Informar al tpv de que no estan conectados
            print("CoinWallet NO connected")
        if(self.portDisplay == None):
            # TODO: Informar al tpv de que no estan conectados
            print("Display NO connected")
        if(self.portLeds == None):
            # TODO: Informar al tpv de que no estan conectados
            print("Leds NO connected")

    def manageTotalAmount(self, cantidad):
        self.totalAmount = float(self.totalAmount) + float(cantidad)
        print("manageTotalAmount : TotalAmount ",
              self.totalAmount, " cantidad ", cantidad)
        self.billWalletService.bv.resumePollThread()
    
        if(DISPLAY):
            self.displayController.printProgress(str(round(
                self.totalAmount*1.00, 2)) + "", round((self.totalAmount/self.priceClientShouldPay) * 100))
       

    def checkIfPaymentComplete(self):
        if self.totalAmount >= self.priceClientShouldPay:
                (statusBillWallet,dataBillWallet ) = self.billWalletService.bv.bv_status 
                while ( statusBillWallet != IDLE ):
                    (statusBillWallet,dataBillWallet ) = self.billWalletService.bv.bv_status 
                    time.sleep(.2)
                    print("BV : Waiting IDLE")
                self.setPaymentDone()

    def setPaymentDone(self):
            print("PAGO COMPLETADO")
            self.paymentDone = True

    def returnChangeToClient(self, amount):
        changeBills = 0
        changeInCoins = 0
        minimumBill = self.billWalletService.bv.minBill
        
        change = round(amount, 2)
        changeInCoins = round(change % minimumBill, 2)
        changeInBills = changeInCoins - change 
        
        if(changeInCoins == minimumBill):
            changeInBills += changeInCoins
            changeInCoins = 0
        
        # CAMBIO DE MONEDAS
        if(changeInCoins > 0 ):
                self.__coinBack( changeInCoins )

        # CAMBIO DE BILLETES
        print("MINIMO BILLETE",minimumBill)
        if(changeBills >= minimumBill):
            toReturn = round(changeInBills)
            # Mientras tengamos que devolver dinero...
            while(toReturn > 0):
                print("**** TO RETURN ", toReturn)
                time.sleep(.2)
                # Devolver Billetes
                returnedToUser = self.__billBack(changeInBills)
                # Recalcular dinero a devolver
                toReturn = toReturn - returnedToUser

        print(" Amount: " + str(amount) + " Order: " + str(self.priceClientShouldPay) + " Change" + str(change) +
              " changeBills" + str(changeBills) + " changeInCoins" + str(changeInCoins) + " totalAmount: " + str(self.totalAmount))
        
        self.totalAmount = 0
        self.priceClientShouldPay = 0

        # TODO: inhibir monedas
        # self.inhibitCoins()
        # self.paymentDone = True
   

    def __coinBack(self, change):
        print("coin back")
        self.coinWalletService.coinwallet.enableInsertCoins()
        time.sleep(.2)
        self.coinWalletService.coinwallet.cashBack(change)

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
            
        (status, data) = self.billWalletService.bv.bv_status

        while (status != IDLE):
            print("__billBack: Esperando estado IDLE, actual: " , status)
            (status, data) = self.billWalletService.bv.bv_status
            time.sleep(.2)
        # time.sleep(.2)
        self.billWalletService.bv.payout(payFromStack1, payFromStack2)
        if(payFromStack1 == True):
            return minBill
        if(payFromStack2 == True):
            return maxBill

    def startMachinesPayment(self, payRequest: PayRequest):
        print("startMachinesPayment")
        self.coinWalletService.coinwallet.enableInsertCoins()
        # self.ledsController.setLedsPayingState(self.ledsController.payStatus)

        self.billWalletService.bv.resumePollThread()

        if(DISPLAY):
            self.displayController.display(self.payRequest)
        
        self.payRequest = payRequest
        self.paymentDone = False
        self.priceClientShouldPay = payRequest.price
        
        # Esperando a pagar
        while self.paymentDone == False:
            print("waiting pay")
            self.checkIfPaymentComplete()
            time.sleep(2)
        # Esperando a devolver en caso de tener que devolver
        while self.totalAmount > self.priceClientShouldPay:
            print("waiting payOut")
            change = self.totalAmount - self.priceClientShouldPay
            self.returnChangeToClient(change)
            time.sleep(5)
        # self.ledsController.setLedsPayingState(self.ledsController.doneStatus)

        print("payment done from __startMachinesPayment")

    def startMachinesConfig(self, stackA, stackB):
        self.billWalletService = BillWalletService(
            self.manageTotalAmount, port=self.portBilletero)
        # self.billWalletService.configMode(stackA,stackB)
