from Controller.SerialCommunicator import *
import serial

class LedsController(SerialCommunicator):

    def __init__(self, port):
        super().__init__(port,115200)
        # self.doneStatus = "RED_"
        # self.doneStatus = "CYAN_"
        self.doneStatus = "GREEN_"
        self.offStatus = "OFF_" 
        self.configStatus = "BLUE_"
        self.payStatus = "GRPARP_"

    def setLedsPayingState(self,state):
        print("SETTING LEDS MODE TO ", (str(state)).encode("utf-8"))
        time.sleep(.2)
        self.com.write((str(state)).encode("utf-8"))