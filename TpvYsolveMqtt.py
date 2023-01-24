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
