import json
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *

class RequestController():
    def __init__(self, payloadReceived):
        print("init requestController")
        self.rawPayload = payloadReceived
        self.requestAdapted = self.convertPayloadToRequest()
        
    def convertPayloadToRequest(self):
        jsonData = json.loads(self.rawPayload)
        # type = 0 => PayRequest 
        # type = 1 => ConfigRequest
        # type = 2 => CancelRequest
        if(jsonData['type'] == 0):
            return self.processPayRequest(jsonData)
        elif(jsonData['type'] == 1):
            return self.processConfigStackRequest(jsonData)
        elif(jsonData['type'] == 2):
            return self.processCancelRequest(jsonData)
        else:
            # TODO: Revisar y enviar to tpv error
            assert("Not valid Type")

    def processConfigStackRequest(self,jsonData):
        try:
            print("Config request converted")
            return ConfigStackRequest(jsonData["type"],jsonData["idOrder"],jsonData["stackA"],jsonData["stackB"])
        except:
            print("Error en conversion de la request de config de stacks")
            #TODO: Enviar datos de fallo por mqtt


    def processPayRequest(self,jsonData):
        try:
            print("Pay request converted")
            return (PayRequest(jsonData["idOrder"],jsonData["order"],jsonData["price"],jsonData["status"],jsonData["date"],jsonData["type"],jsonData["shopName"],jsonData["address"],jsonData["phone"]))
        except:
            print("Error en conversion de la request de Pay de stacks")
            #TODO: Enviar datos de fallo por mqtt

    def processCancelRequest(self,jsonData):
        try:
            # return (CancelRequest(jsonData["idOrder"],jsonData["order"],jsonData["price"],jsonData["status"],jsonData["date"],jsonData["type"],jsonData["shopName"],jsonData["address"],jsonData["phone"]))
            print("Cancel request converted")
            return (CancelRequest(jsonData["idOrder"],jsonData["type"]))
        except:
            print("Error en conversion de la request de Cancel de stacks")
            #TODO: Enviar datos de fallo por mqtt
