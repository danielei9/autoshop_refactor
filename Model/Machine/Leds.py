import serial

class Leds():

    def __init__(self):
        # self.doneStatus = "RED_"
        # self.doneStatus = "CYAN_"
        self.doneStatus = "GREEN_"
        self.offStatus = "OFF_" 
        self.configStatus = "BLUE_"
        self.payStatus = "GRPARP_"
        try:
            print ( "Leds Port: ", portLeds )
            self.com = serial.Serial(
                str(portLeds),
                115200,
                serial.EIGHTBITS,
                serial.PARITY_EVEN,
                timeout=0.2)
                
            if self.com.isOpen() == False:
                self.com.open()

            self.com.flushInput()
            self.com.flushOutput()
        except serial.SerialException as e:
            print(e)
            if e.error == 13:
                raise e
            pass
        except OSError:
            pass

    def setLedsPayingState(self,state):
        #print("SETTING LEDS MODE TO ", (str(state)).encode())
        self.com.write((str(state)).encode())