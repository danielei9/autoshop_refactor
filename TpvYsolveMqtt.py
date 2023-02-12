# inicializar Mqtt 
# subscribe mqtt
# esperar a obtener un request
# Procesar request
from Model.TPVCommunication.Mqtt.mqtt_credentials import *
# from Model.TPVCommunication.Request.Request import *
from Controller.MqttController import *

port = 1883
broker = '192.168.4.1'
username = "ysolve"
password = "y-solve2022"

#TODO:   quitar
broker = 'broker.hivemq.com'

class TpvYsolveMqtt():
    def __init__(self,adaptRequest):
        print("init")
        self.conn = None
        self.cb_adapt_request = adaptRequest
        self.initialize()

    def initialize(self):
        print("initialize TPV")
        self.credentials = MqttCredentials(broker,username,password,port)
        self.conn = MqttConnection(self.credentials)
        self.createLoopMqtt()

    def createLoopMqtt(self):
        self.conn.create_loop_mqtt_receive(self.cb_adapt_request)
        
    def sendError(self,error):
        print("Sending error to tpv: ", error)
        self.sendData('{"error":"' + str(error)+'"}')

    def sendData(self,data):
        try:
            # print("Sending to:" + self.credentials.topicSend)
            print("Sending to: payMachine/rx \n" , data)
            # self.clt.publish(topic +"/data",json.dumps(dataJson))
            self.conn.clt.publish("payMachine/rx" ,data)
            print("Sended!")
            
        except Exception as e :
            # TODO: Mostrar por pantalla el error
            print(e)
            raise e