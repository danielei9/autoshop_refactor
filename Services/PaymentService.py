from Controller.Display.DisplayController import *
from Controller.BillWallet.BillWalletService import *
from Controller.CoinWallet.CoinWalletController import *
from Controller.Leds.LedsController import *
from Controller.Printer.PrinterController import *
import asyncio
from Controller.UsbPortDetector import *
import threading

class PaymentService():
    
    def __init__(self):
        self.billWalletService:BillWalletService = None
        self.portBilletero = None
        self.portMonedero = None
        self.portDisplay = None
        self.portLeds = None
        UsbDetector = USBPortDetector()
        (self.portBilletero,self.portMonedero,self.portDisplay,self.portLeds) = UsbDetector.detect_ports()
        self.initializeControllers()
        self.totalAmount = 0
        self.priceClientShouldPay = 0

    def setErrorInDisplay(self,error):
        self.displayController.displayError(error)

    def initializeControllers(self):
        self.checkPorsConnected()
        # try:
        #     self.displayController = DisplayController(self.portDisplay)
        #     print("Display Initialized OK")
        # except:
        #     print("Please Connect Display")
        #     # TODO: Informar al tpv de que no estan conectados 
        #     time.sleep(5)
        #     pass
            # self.initializeControllers()
        try:
            self.billWalletService:BillWalletService = BillWalletService(self.manageTotalAmount, port=self.portBilletero)
            
            billwWalletPollThread = threading.Thread(target=self.billWalletService.run)
            billwWalletPollThread.start()

            print("BillWallet Initialized OK")
            
        except:
            print("Please Connect BillWallet ")
            # TODO: Informar al tpv de que no estan conectados 
            time.sleep(5)
        """# try:
        #     self.coinWalletController:CoinWalletController =  CoinWalletController()
        #     print("CoinWallet Initialized OK")
        # except:
        #     print("Please Connect CoinWallet ")
        #     # TODO: Informar al tpv de que no estan conectados 
        #     time.sleep(5)
        # #TODO: descomentar printer
        # try:
        #     self.printerController = PrinterController()
        #     print("Printer Initialized OK")
        # except:
        #     print("Please Connect Printer ")
        #     # TODO: Informar al tpv de que no estan conectados 
        #     time.sleep(5)
        # try:
        #     self.ledsController = LedsController(self.portLeds)
        #     print("Leds Initialized OK")

        # except:
        #     print("Please Connect Leds ")
        #     # TODO: Informar al tpv de que no estan conectados 
        #     time.sleep(5)"""

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
        print("manageTotalAmount : TotalAmount ", self.totalAmount ," cantidad ",cantidad )
        if self.totalAmount >= self.priceClientShouldPay:
            # self.inhibitCoins()
            print("PAGO COMPLETADO")
            self.paymentDone = True

    async def payChange(self, amount):
        print("PayCHange")
        changeBills = 0
        changeInCoins = 0
        minimumBill = self.billWalletService.bv.minbill
        print("Amount ",amount)
        print("self.priceClientShouldPay ",self.priceClientShouldPay)
        # self.displayController.printProgress(str(round(amount*1.00,2)) + "", round((amount/self.priceClientShouldPay) *100))
        if amount >= self.priceClientShouldPay:
            # self.__inhibitCoins()
            change = round(amount - self.priceClientShouldPay,2)
            changeInCoins = round(change % minimumBill ,2)

            # if(changeInCoins > 0):
            #     self.coinWalletController.enableInsertCoins()
            #     time.sleep(.1)
            #     await self.__coinBack( changeInCoins )
            #     change = change - changeInCoins

            if(change >= minimumBill):
                changeBills = round( change )
                toReturn = changeBills
                while( toReturn > 0 ):
                    print("**** TO RETURN ",toReturn)
                    time.sleep(.2)
                    # returnedToUser = await self.__billBack(changeBills)
                    # toReturn = toReturn - returnedToUser
                
            print("Amount: " + str( amount) +" Order: " + str(self.priceClientShouldPay) + " Change" + str(change) + " changeBills" + str(changeBills) + " changeInCoins" + str(changeInCoins) +" self.totalAmount: " + str( self.totalAmount)   )
            self.totalAmount = 0
            
            # self.billWalletService.init()
            # self.inhibitCoins()
            self.paymentDone = True

    def returnChangeToClient(self, amount):
        changeBills = 0
        changeInCoins = 0

        minimumBill = self.billWalletService.bv.minbill
        change = round(amount,2)
        changeInCoins = round(change % minimumBill ,2)
        
        # CAMBIO DE MONEDAS
            # # self.__inhibitCoins()
            # if(changeInCoins > 0):
            #         await self.__coinBack( changeInCoins )
            #         change = change - changeInCoins

        # CAMBIO DE BILLETES
        if( change >= minimumBill ):
            toReturn = round( change )
            # Mientras tengamos que devolver dinero...
            while( toReturn > 0 ):
                print("**** TO RETURN ",toReturn)
                time.sleep(.2)
                # Devolver Billetes
                # returnedToUser = await self.__billBack(changeBills)
                # Recalcular dinero a devolver
                # toReturn = toReturn - returnedToUser

        print("Cancelled ok Amount: " + str( amount) +" Order: " + str(self.priceClientShouldPay) + " Change" + str(change) + " changeBills" + str(changeBills) + " changeInCoins" + str(changeInCoins) +" self.totalAmount: " + str( self.totalAmount)   )
            
        # TODO: inhibir monedas
        # self.inhibitCoins()
        # self.paymentDone = True   

    def inhibitCoins(self):
        self.coinWalletController.disableInsertCoins()

    async def __coinBack(self, change):
        # coinWallet.enableInsertCoins()
        self.coinWalletController.cashBack(change)

    async def __billBack( self,changeBills ):
        print("Devolver: " + str(changeBills) + " €")
        payFromStack1 = False
        payFromStack2 = False

        if(changeBills >= self.billWalletService.maxBill):
            print("Pagar max billete %d" % self.billWalletService.maxBill)
            if(self.billWalletService.maxBill == self.billWalletService.stackA):
                payFromStack1 = True
                payFromStack2 = False
            if(self.billWalletService.maxBill == self.billWalletService.stackB):
                payFromStack1 = False
                payFromStack2 = True
        elif (changeBills >= self.billWalletService.minBill):
            print("PAY min billete %d" % self.billWalletService.minBill)
            
            if(self.billWalletService.minBill == self.billWalletService.stackA):
                payFromStack1 = True
                payFromStack2 = False
            if(self.billWalletService.minBill == self.billWalletService.stackB):
                payFromStack1 = False
                payFromStack2 = True
        else:
            print("ERROR: TO PAY  %d < minbill: %d" % self.billWalletService,self.billWalletService.minBill.minBill)
        while (self.billWalletService.status != IDLE):
            print("__billBack: Esperando estado IDLE, actual: %02x" % self.billWalletService.status)
            self.billWalletService.getStatus()
            time.sleep(.2)
        # time.sleep(.2)
        self.billWalletService.payout(payFromStack1,payFromStack2)
        if(payFromStack1 == True):
            return self.billWalletService.minBill
        if(payFromStack2 == True):
            return self.billWalletService.maxBill

    async def startMachinesPayment(self,priceClientShouldPay):
        print("startMachinesPayment")
        self.paymentDone = False
        self.priceClientShouldPay = priceClientShouldPay
        while self.paymentDone == False:
            print("waiting pay")
            time.sleep(5)
        while self.totalAmount > self.priceClientShouldPay :
            change = self.totalAmount - self.priceClientShouldPay
            self.returnChangeToClient(change)
      
        print("payment done from __startMachinesPayment")

    async def startMachinesConfig(self,stackA,stackB):
        self.billWalletService = BillWalletService(self.manageTotalAmount, port=self.portBilletero)
        # self.billWalletService.configMode(stackA,stackB)
        # self.coinWalletController = CoinWalletController(self.manageTotalAmount, port=self.portMonedero)
