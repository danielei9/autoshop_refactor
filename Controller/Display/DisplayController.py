# import modelDisplay
import time
from Controller.SerialCommunicator import *
from Controller.Display.CodesDisplay import *
from Model.TPVCommunication.Request.PayRequest import *

class DisplayController(SerialCommunicator):
    def __init__(self,port,tpv):
        try:
            super().__init__(port)
            self.initialize()
            self.sendData, self.sendError = tpv
        except:
            assert Exception("Error with DisplayController in port: " + str(port))
            time.sleep(3)
            self.__init__(port)
            
    def initialize(self):
        self.open_port()

    def clear_display(self):
        self.send_data('CLEAR')

    def close(self):
        self.clear_display()
        self.close_port()

    def printProgress(self, textBar, progressBar):
        if(progressBar >= 100):
            progressBar = 100
        self.printInDisplay(ID_NEXTION_PROCESS_BAR_NUM, str(progressBar))
        self.printInDisplay(ID_NEXTION_ORDER_PERCENTAGE, str(textBar))

    def printInDisplay(self, id, data):
        time.sleep(.2)
        print(id, " ", data)
        try:
            if(id == ID_NEXTION_PROCESS_BAR_NUM):
                self.com.write((id+".val=" + data ).encode())
            else:
                self.com.write((id+".txt=\"" + data + "\"").encode('unicode_escape'))
            self.com.write(b"\xFF\xFF\xFF")
        except:
            self.sendError("Error Sending To Display")

    def setWelcomePage(self):
        time.sleep(.2)
        try:
            self.com.write(b"\x70\x61\x67\x65\x20\x31\xFF\xFF\xFF")
        except:
            self.sendError("Error change page in Display")
    def setOrderPage(self):
        time.sleep(.2)
        try:
            self.com.write(b"\x70\x61\x67\x65\x20\x30\xFF\xFF\xFF")
        except:
            self.sendError("Error change page in Display")
    def setByePage(self):
        time.sleep(.2)
        try:
            self.com.write(b"\x70\x61\x67\x65\x20\x32\xFF\xFF\xFF")
        except:
            self.sendError("Error change page in Display")

    def adaptRequestToDisplay(self,obj:PayRequest,p = 0):
        print(obj)
        try:
            percent = p
            itemList = ""
            itemPriceList = ""
            idOrder = obj.idOrder
            priceTotal = obj.price
            print(priceTotal)
            ticketQr = ""
            for itemName in obj.order:
                itemList += (itemName + NEXTION_LINE_CHANGE )
                ticketQr += (itemName + "   " + obj.order[str(itemName)] + NEXTION_LINE_CHANGE )
                # itemPriceList += (itemName + NEXTION_LINE_CHANGE )
                itemPriceList += ( obj.order[str(itemName)] + NEXTION_LINE_CHANGE)
                if(str(idOrder) == "-1"):
                    ticketQr = ("0" + NEXTION_LINE_CHANGE )
                    priceTotal = 0
                    itemPriceList = ( "0.00" + NEXTION_LINE_CHANGE)

            print(itemList)
            return (ticketQr,itemList,itemPriceList,priceTotal,percent)
        except:
            self.sendError("Error to display order")
 
    def putDataToDisplay(self,ticketQr,itemList,itemPriceList,priceTotal,percent):
        print(itemPriceList)
        self.printInDisplay(ID_NEXTION_QR, ticketQr)
        self.printInDisplay(ID_NEXTION_ORDER_TEXT,str(itemList))
        self.printInDisplay(ID_NEXTION_ORDER_PRICES_TEXT,itemPriceList)
        self.printInDisplay(ID_NEXTION_TOTAL_PRICE_TEXT, str(round(priceTotal*1.00,2)))
        self.printInDisplay(ID_NEXTION_ORDER_PERCENTAGE,str(percent) +"%")
        self.printInDisplay(ID_NEXTION_PROCESS_BAR_NUM, str(percent))
    
    def display(self,request:PayRequest):
        time.sleep(.2)
        print("request displayController : ", request)
        (ticketQr,itemList,itemPriceList,priceTotal,percent) = self.adaptRequestToDisplay(request)
        self.putDataToDisplay(ticketQr,itemList,itemPriceList,priceTotal,percent) 

    def displayError(self,error):
        print("Display Error setted")
        self.printInDisplay(ID_NEXTION_ORDER_TEXT,str(error))
