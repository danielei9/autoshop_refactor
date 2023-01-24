import json
import serial,time
from infrastructure.common.USBDynamic.DinUsb import * 

class Display():
    def __init__(self):
        (portBilletero,portMonedero,portDisplay,portLeds) = checkPorts()
        try:
            print ( "display Port: ", portDisplay )
            self.com = serial.Serial(
                str(portDisplay),
                 9600,
                 serial.EIGHTBITS,
                 serial.PARITY_EVEN,
                 timeout=0.2)

            if self.com.isOpen() == True:
                self.com.close()
            time.sleep(.5)
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