from escpos.printer import Usb
import json
from Model.TPVCommunication.Request.PayRequest import *

class PrinterController():

    def __init__(self):
        try:
            self.printer = Usb(0x10c5,0x0009,in_ep=0x81,out_ep=0x02)
            print("Printer is OK connected")
            self.type = ""

        except :
            print("Printer is not connected")

    def __printText(self):
        self.printer.set(width=7,height=7, align='center',bold=True ,double_height=True, double_width=True)
        self.printer.text(str(self.shopName) + '\n')
        self.printer.set(width=3, align='center',bold=True)
        self.printer.text('************************\n')
        self.printer.text(str(self.address) + '\n')
        self.printer.text(str(self.phone) + '\n')
        self.printer.text('************************\n')
        self.printer.set(align='right')
        self.printer.text("\n")
        self.printer.set(width=3 ,height=3, align='center',bold=True)
        self.printer.text("Fecha: "+ str(self.date) + "\n")
        self.printer.text("Ticket de compra nº " + str(self.idOrder))
        self.printer.text("\n")
        self.printer.text("\n")

        self.printer.set(width=5, align='left',bold=True)
        self.printer.text("{:>8}".format("Concepto"))
        self.printer.text("{:>22}".format("Precio"))

        self.printer.text("\n")
        if(str(self.idOrder) != "-1"):
            print("Printing: %s" % self.order)
            order_dict = json.loads(self.order)

            for key in order_dict:
                self.printer.set(width=3, align='left',bold=False)
                # self.printer.text(str(key)) # 36 de largo 
                self.printer.text("  {:>2}".format(str(key)))

                if(str(self.idOrder) != "-1"):
                    self.printer.set(width=3, align='right',bold=False)
                    self.printer.text("  {:>27}".format(str(order_dict[key])  + "   \n"))

                    # self.printer.text(str(order_dict[key]) + " \n") # 36 de largo 
                    print(str(key) + "   \n") # 36 de largo 
                    print("------------------------------ " + str(order_dict[key]) + " \n") # 36 de largo 
                    
            self.printer.set(width=5, align='right',bold=True)

        if(str(self.idOrder) != "-1"):
            self.printer.text("\n\nsubtotal: "+ str(round(self.price*0.79,2)) + "\n")
            self.printer.text("I.V.A (21%): "+ str(round(self.price*1.00*0.21,2)) + "\n")
            self.printer.text("\n")
            self.printer.text("TOTAL: "+ str(round(self.price*1.00,2)) + "   \n")
            self.printer.text("\n")
            self.printer.text("Pagado: "+ str(round(self.totalAmount*1.00,2)) + "   \n")
            self.printer.text("Cambio devuelto: "+ str(round(self.change*1.00,2)) + "   \n")
            self.printer.text("\n")

            self.printer.set(width=3 ,height=3, align='center',bold=True)
            if(self.type == "CANCELLED"):
                self.printer.text("ORDEN CANCELADA")
                return
            else:
                self.printer.text("Vuelva pronto ;)")
                pass
        else:
            self.printer.text("MAQUINA CARGADA: ")
            print("PRINTER CONTROLLER TOTAL : " , str(self.price))
            self.printer.text("\n\nTotal: "+ str(round(self.price,2)) + "\n")
            return



    def __printerCutPaper(self):
        self.printer.cut()
    
    def printerClose(self):
        self.printer.close()

    def __parseOrder(self,orderInJSONString):
        obj = json.loads(orderInJSONString) 
        return obj
        print(obj['id'])

    def prepareOrderToPrint(self,requestAdpated: PayRequest, change,totalAmount):
        self.idOrder = requestAdpated.idOrder
        if(self.idOrder != -1):
            self.order = str( requestAdpated.order).replace("\'","\"")
        self.price = requestAdpated.price
        self.status = requestAdpated.status
        self.date = requestAdpated.date
        self.shopName = requestAdpated.shopName
        self.address = requestAdpated.address
        self.phone = requestAdpated.phone
        self.change = change
        self.totalAmount = totalAmount

    def print(self,type):
        self.type = type
        self.__printText()
        self.__printerCutPaper()