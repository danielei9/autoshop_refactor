# inicializar Mqtt 
# subscribe mqtt
# esperar a obtener un request
# Procesar request
from Model.TPVCommunication.Mqtt.mqtt_credentials import *
# from Model.TPVCommunication.Request.Request import *
from Controller.MqttController import *
from utils.RequestCodes import *
port = 1883
broker = '192.168.4.1'
username = "ysolve"
password = "y-solve2022"

# broker = 'broker.hivemq.com'

class TpvYsolveMqtt():
    def __init__(self,adaptRequest):
        print("init")
        self.conn = None
        self.cb_adapt_request = adaptRequest
        self.initialize()
        self.actualProcessingRequest = None

    def initialize(self):
        print("initialize TPV")
        self.credentials = MqttCredentials(broker,username,password,port)
        self.conn = MqttConnection(self.credentials)
        self.createLoopMqtt()

    def setMqttListenerPaused(self,status):
        print("SET MQTT LISTENER TO ", status)
        self.conn.isPaused = status

    def createLoopMqtt(self):
        self.conn.create_loop_mqtt_receive(self.cb_adapt_request)
        
    def sendError(self,error):
        print("Sending error to tpv: ", error)
        self.sendData('{"error":"' + str(error)+'"}')

    def sendData(self,data):
        try:
            # print("Sending to:" + self.credentials.topicSend)
            print("Sending to: ", str(self.credentials.topicSend) , data)
            # self.clt.publish(topic +"/data",json.dumps(dataJson))
            self.conn.clt.publish(str(self.credentials.topicSend)  ,data)
            print("Sended!")
            
        except Exception as e :
            print(e)

    def sendAutoCancelRequest(self):
        print("sendAutoCancelRequest ")
        print(self.actualProcessingRequest.idOrder)
        if(self.actualProcessingRequest != None):
            self.conn.clt.publish(str(self.credentials.topicSubscribed) , '{"idOrder":'+str(self.actualProcessingRequest.idOrder)+',"typeRequest":'+str(TYPE_CANCELLED_REQUEST)+'}')
