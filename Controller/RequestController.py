import json
from Model.TPVCommunication.Request.ConfigStackRequest import *
from Model.TPVCommunication.Request.PayRequest import *
from Model.TPVCommunication.Request.CancelRequest import *
from Model.TPVCommunication.Request.ConnectedRequest import *
from Model.TPVCommunication.Request.ResetRequest import *
from Model.TPVCommunication.Request.GetActualConfigRequest import *
from Model.TPVCommunication.Request.BlockedMachine import *
from utils.RequestCodes import *


class RequestController():
    def __init__(self, payloadReceived, sendErrorTpv):
        print("init requestController")
        self.rawPayload = payloadReceived
        self.requestAdapted = self.convertPayloadToRequest()
        self.sendErrorTpv = sendErrorTpv

    def convertPayloadToRequest(self):
        jsonData = json.loads(self.rawPayload)
        if(jsonData['typeRequest'] == TYPE_PAY_REQUEST):
            return self.processPayRequest(jsonData)
        elif(jsonData['typeRequest'] == TYPE_CONFIG_REQUEST):
            return self.processConfigStackRequest(jsonData)
        elif(jsonData['typeRequest'] == TYPE_CANCELLED_REQUEST):
            return self.processCancelRequest(jsonData)
        elif(jsonData['typeRequest'] == TYPE_CONNECTED_REQUEST):
            return self.processConnectedRequest(jsonData)
        elif(jsonData['typeRequest'] == TYPE_RESET_REQUEST):
            return self.processResetRequest(jsonData)
        elif(jsonData['typeRequest'] == TYPE_GET_ACTUAL_CONFIG_REQUEST):
            return self.processGetActualConfigRequest(jsonData)
        elif(jsonData['typeRequest'] == TYPE_BLOCKED_MACHINE):
            return self.processBlockedMachine(jsonData)
        else:
            self.sendErrorTpv("Error en conversion de la request")
            
    def processConfigStackRequest(self,jsonData):
        try:
            print("Config request converted")
            return ConfigStackRequest(jsonData["typeRequest"],jsonData["stackA"],jsonData["stackB"],jsonData["quantityStackA"],jsonData["quantityStackB"])
        except:
            print("Error en conversion de la request de config de stacks")
            self.sendErrorTpv("Error en conversion de la request de config de stacks")

    def processGetActualConfigRequest(self,jsonData):
        try:
            print("Config request converted")
            return GetActualConfigRequest(jsonData["typeRequest"])
        except:
            print("Error en conversion de la request de get actual configuracion")
            self.sendErrorTpv("Error en conversion de la request de obtener configuración actual")

    def processResetRequest(self,jsonData):
        try:
            print("RESET request converted")
            return ResetRequest(jsonData["typeRequest"])
        except:
            print("Error en conversion de la request de reset")
            self.sendErrorTpv("Error en conversion de la request de reset")

    def processConnectedRequest(self,jsonData):
        try:
            print("Connect request converted")
            return ConnectedRequest(jsonData["typeRequest"],jsonData["connected"])
        except:
            print("Error en conversion de la request de Connected")
            self.sendErrorTpv("Error en conversion de la request de Connected")

    def processPayRequest(self,jsonData):
        try:
            print("Pay request converted")
            return (PayRequest(jsonData["idOrder"],jsonData["order"],jsonData["price"],jsonData["status"],jsonData["date"],jsonData["typeRequest"],jsonData["shopName"],jsonData["address"],jsonData["phone"]))
        except:
            print("Error en conversion de la request de Pay de stacks")
            self.sendErrorTpv("Error en conversion de la request de pago")

    def processCancelRequest(self,jsonData):
        try:
            print("Cancel request converted")
            return (CancelRequest(jsonData["idOrder"],jsonData["typeRequest"]))
        except:
            print("Error en conversion de la request de Cancel de stacks")
            self.sendErrorTpv("Error en conversion de la request de cancelación")

    def processBlockedMachine(self,jsonData):
        try:
            print("Blocked machine received")
            return (BlockedMachine(jsonData["typeRequest"],jsonData["blocked"]))
        except:
            print("Error en conversion de la request de Bloqueo de maquina")
            self.sendErrorTpv("Error en conversion de request Bloqueo de maquina")
