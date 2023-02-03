from Controller.Display.DisplayController import *
from Controller.BillWallet.BillWalletController import *
from Controller.CoinWallet.CoinWalletController import *
from Controller.Leds.LedsController import *
from Controller.Printer.PrinterController import *
import asyncio
from Controller.UsbPortDetector import *

class PaymentService():
    def __init__(self):
        self.portBilletero = None
        self.portMonedero = None
        self.portDisplay = None
        self.portLeds = None
        UsbDetector = USBPortDetector()
        (self.portBilletero,self.portMonedero,self.portDisplay,self.portLeds) = UsbDetector.detect_ports()
        self.initializeControllers()

    def setErrorInDisplay(self,error):
        self.displayController.displayError(error)

    def initializeControllers(self):
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
        # try:
        #     self.displayController = DisplayController(self.portDisplay)
        # except:
        #     print("Please Connect REQUIRED Display")
        #     # TODO: Informar al tpv de que no estan conectados 
        #     time.sleep(5)
        #     pass
            # self.initializeControllers()
        try:
            self.billWalletController:BillWalletController = None # BillWalletController(self.manageTotalAmount)
            print("BillWallet Initialized OK")
        except:
            print("Please Connect BillWallet Display")
            # TODO: Informar al tpv de que no estan conectados 
            time.sleep(5)
        try:
            self.coinWalletController:CoinWalletController = None # CoinWalletController()
            print("CoinWallet Initialized OK")
        except:
            print("Please Connect CoinWallet Display")
            # TODO: Informar al tpv de que no estan conectados 
            time.sleep(5)
        #TODO: descomentar printer
        # try:
        #     self.printerController = PrinterController()
        # except:
        #     print("Please Connect Printer Display")
        #     # TODO: Informar al tpv de que no estan conectados 
        #     time.sleep(5)
        try:
            self.ledsController = LedsController(self.portLeds)
            print("Leds Initialized OK")

        except:
            print("Please Connect Leds Display")
            # TODO: Informar al tpv de que no estan conectados 
            time.sleep(5)
        
    async def manageTotalAmount(self, cantidad):
        print("manageTotalAmount : cantidad", cantidad)
        self.totalAmount = float(self.totalAmount) + float(cantidad)
        # print("manageTotalAmount : TotalAmount ", self.totalAmount)
        if self.totalAmount >= self.order:
            self.inhibitCoins()
        await self.payChange(self.totalAmount)

    async def payChange(self, amount):
        changeBills = 0
        changeInCoins = 0
        minimumBill = self.billWalletController.minBill

        self.displayController.printProgress(str(round(amount*1.00,2)) + "", round((amount/self.order) *100))
        if amount >= self.order:
            # self.__inhibitCoins()
            change = round(amount - self.order,2)
            changeInCoins = round(change % minimumBill ,2)

            if(changeInCoins > 0):
                self.coinWalletController.enableInsertCoins()
                time.sleep(.1)
                await self.__coinBack( changeInCoins )
                change = change - changeInCoins

            if(change >= minimumBill):
                changeBills = round( change )
                toReturn = changeBills
                while( toReturn > 0 ):
                    print("**** TO RETURN ",toReturn)
                    time.sleep(.2)
                    returnedToUser = await self.__billBack(changeBills)
                    toReturn = toReturn - returnedToUser
                
            print("Amount: " + str( amount) +" Order: " + str(self.order) + " Change" + str(change) + " changeBills" + str(changeBills) + " changeInCoins" + str(changeInCoins) +" self.totalAmount: " + str( self.totalAmount)   )
            self.totalAmount = 0
            
            self.billWalletController.init()
            self.inhibitCoins()
            self.paymentDone = True

    async def backMoneyCancelledOrder(self, amount):
        changeBills = 0
        changeInCoins = 0
        minimumBill = self.billWalletController.minBill
        # TODO: enviar cambio de estado display
        if(str(self.idOrder) != "-1"):      
            print("backmoney")
            change = round(amount,2)
            changeInCoins = round(change % minimumBill ,2)
            # self.__inhibitCoins()
            if(changeInCoins > 0):
                    await self.__coinBack( changeInCoins )
                    change = change - changeInCoins

            if(change >= minimumBill):
                    changeBills = round( change )
                    toReturn = changeBills
                    while( toReturn > 0 ):
                        print("**** TO RETURN ",toReturn)
                        time.sleep(.2)
                        returnedToUser = await self.__billBack(changeBills)
                        toReturn = toReturn - returnedToUser
                
            print("Cancelled ok Amount: " + str( amount) +" Order: " + str(self.order) + " Change" + str(change) + " changeBills" + str(changeBills) + " changeInCoins" + str(changeInCoins) +" self.totalAmount: " + str( self.totalAmount)   )
        self.totalAmount = 0
            
        self.billWalletController.init()
        # TODO: inhibir monedas
        self.inhibitCoins()
        self.paymentDone = True   

    def inhibitCoins(self):
        self.coinWalletController.disableInsertCoins()
   
    async def __coinBack(self, change):
        # coinWallet.enableInsertCoins()
        self.coinWalletController.cashBack(change)
        
    async def __billBack( self,changeBills ):
        print("Devolver: " + str(changeBills) + " €")
        payFromStack1 = False
        payFromStack2 = False

        if(changeBills >= self.billWalletController.maxBill):
            print("Pagar max billete %d" % self.billWalletController.maxBill)
            if(self.billWalletController.maxBill == self.billWalletController.stackA):
                payFromStack1 = True
                payFromStack2 = False
            if(self.billWalletController.maxBill == self.billWalletController.stackB):
                payFromStack1 = False
                payFromStack2 = True
        elif (changeBills >= self.billWalletController.minBill):
            print("PAY min billete %d" % self.billWalletController.minBill)
            
            if(self.billWalletController.minBill == self.billWalletController.stackA):
                payFromStack1 = True
                payFromStack2 = False
            if(self.billWalletController.minBill == self.billWalletController.stackB):
                payFromStack1 = False
                payFromStack2 = True
        else:
            print("ERROR: TO PAY  %d < minbill: %d" % self.billWalletController,self.billWalletController.minBill.minBill)
        while (self.billWalletController.status != IDLE):
            print("__billBack: Esperando estado IDLE, actual: %02x" % self.billWalletController.status)
            self.billWalletController.getStatus()
            time.sleep(.2)
        # time.sleep(.2)
        self.billWalletController.payout(payFromStack1,payFromStack2)
        if(payFromStack1 == True):
            return self.billWalletController.minBill
        if(payFromStack2 == True):
            return self.billWalletController.maxBill

    async def startMachinesPayment(self):
        print("startMachinesPayment")
        self.paymentDone = False
        self.billWalletController = BillWalletController(self.manageTotalAmount, port=self.portBilletero)
        # self.billWalletController.init()
        print("BillWalletController OK ")

        self.coinWalletController = CoinWalletController(self.manageTotalAmount, port=self.portMonedero)
        print("CoinWalletController OK ")
        while self.paymentDone == False:
            # if(str(mensaje) == '1'):
            print("detected cancelled 2")
            await self.backMoneyCancelledOrder(self.totalAmount)
            self.paymentDone = True
      
            await asyncio.wait_for(self.coinWalletController.threadReceived(), timeout=0.2)
            await asyncio.wait_for(self.billWalletController.poll(), timeout=0.2)
        print("payment done from __startMachinesPayment")
    
    async def startMachinesConfig(self,stackA,stackB):
        self.billWalletController = BillWalletController(self.manageTotalAmount, port=self.portBilletero)
        self.billWalletController.configMode(stackA,stackB)
        self.coinWalletController = CoinWalletController(self.manageTotalAmount, port=self.portMonedero)
    