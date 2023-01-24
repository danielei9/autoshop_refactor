from getmac import get_mac_address
import random
import paho.mqtt.client as paho

class MqttCredentials:
    """ Get MQTT credentials """
    def __init__(self, broker, username, password, port):
        eth_mac = str(get_mac_address(interface="eth0")).replace(':',"")
        self.port = port
        self.broker = broker
        self.topic = "payMachine/" #+ eth_mac
        # From TPV to Machines
        self.topicSubscribed = self.topic + "/tx"
        # From Machines to TPV
        self.topicSend= self.topic + "/rx"
        self.client_id = str(eth_mac + str(random.randint(0,1000)))
        self.username = username
        self.password = password

        print("Config Mqtt: \n\tTopic: " + self.topic +
         "\n\tclient_id: " + self.client_id +
          "\n\tusername: " + self.username +
           "\n\tpassword: " + self.password +
            "\n\tbroker: " + self.broker +
             "\n\tport: " + str(self.port) + 
              "\n")
