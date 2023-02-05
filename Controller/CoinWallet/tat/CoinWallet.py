# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22
 
Example:


Todo:
    * Review some doc and 
    * Review Feature auto-select port


|--------coinWallet------|
|        __init__     setup()    
|                     reset()
|    __sendCommand    tubeStatus()
|                     poll()
|                     coinType()
|                     dispense()
|                     enableInsertCoins()
|                         |
|-------------------------|

"""
import os
from os.path import join
# MONEDERO idvendor  067b

def find_tty_usb(idVendor, idProduct):
    for dnbase in os.listdir('/sys/bus/usb/devices'):
        dn = join('/sys/bus/usb/devices', dnbase)
#         print(dn)
        if not os.path.exists(join(dn, 'idVendor')):
            continue
        idv = open(join(dn, 'idVendor')).read().strip()
#         print(idv)
        if idv != idVendor:
            continue
        idp = open(join(dn, 'idProduct')).read().strip()
#         print(idp)
        if idp != idProduct:
            continue
        for subdir in os.listdir(dn):
            if subdir.startswith(dnbase+':'):
                for subsubdir in os.listdir(join(dn, subdir)):
                    if subsubdir.startswith('ttyUSB'):
                        return join('/dev', subsubdir)

import re
import subprocess
def checkPorts():
    devices = []
    portBilletero = ""
    portMonedero = ""
    portDisplay = ""
    portLeds = ""
    
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")    
    df = str(df)
    df = df.replace("b'", '')
    for i in df.split("\\n"):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
#     print (devices)

    for device in devices:
        idUsb = str(device['id']).split(':')
        a = str(idUsb[0])
        b = str(idUsb[1])
        # print(device['id'])
    #     BILLETERO
    # Bus 001 Device 116: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
        if(device['id'] == "067b:2303"):
            portBilletero = find_tty_usb(a,b)
            print("BILLETERO: ",portBilletero,"\n")
    # Bus 001 Device 115: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
    #     MONEDERO
        if(device['id'] == "0403:6001"):
            portMonedero = find_tty_usb(a,b) 
            print("MONEDERO: ",portMonedero,"\n")
    # Bus 001 Device 019: ID 10c4:ea60 Cygnal Integrated Products, Inc. CP2102/CP2109 UART Bridge Controller [CP210x family]
    #     DISPLAY
        if(device['id'] == "10c4:ea60"):
            portDisplay = find_tty_usb(a,b)
            print("DISPLAY: ",portDisplay,"\n")
    # Bus 001 Device 020: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    #     LEDS
        if(device['id'] == "1a86:7523"):
            portLeds = find_tty_usb(a,b)
            print("DISPLAY: ",portLeds,"\n")
        
    return portBilletero,portMonedero,portDisplay,portLeds



import multiprocessing
import time
from BuchuSerial import BuchuSerial
# # # # # # # # # # # # # # # # # # # # # 
# NORMAL COMMANDS
# # # # # # # # # # # # # # # # # # # # #

# RECEIVING COINS

UN_EURO = '08 54'
DOS_EURO = '08 55'
ZERO_ZERO_FIVE = '08 50'
ZERO_TEN = '08 51'
ZERO_TWNTY = '08 52'
ZERO_FIVETY = '08 53'

"""
    #Send info about setup initi
    # Response 23 bytes z1-z23
    # z1 Changer Feature Level // Level3 = 0x03 // Level2 = 0x02 ...
    #  z2-z3 country code  for the Euro is 1978 (Z2 = 19 and Z3 = 78).
    # Z4 = Coin Scaling Factor - 1 byte 
    # Z5 = Decimal Places - 1 byte 
 Indicates the number of decimal places on a credit display. For example, this could be set to 02H in the USA.
    # Z6-Z7 Coin Type Routing - 2 bytes
    # Bit is set to indicate a coin type can be routed to the tube. Valid coin types are 0 to 15.
    # Z8 - Z23 = Coin Type Credit - 16 bytes 
    # Indicates the value of coin types 0 to 15. Values must be sent in ascending order. This number is the coin's monetary value
    #  divided by the coin scaling factor. Unused coin types are sent as 00H. Unsent coin types are assumed to be zero. It is not
    # necessary to send all coin types. Coin type credits sent as FFH are assumed to be vend tokens. That is, their value is assumed to worth one vend.
"""
SETUP = [0x09]
"""

    # This command is the vehicle that the VMC should use to tell the changer that it should return to its default operating mode
"""
RESET = [0x08]
"""
    # Z1 - Z2 = Tube Full Status - 2 bytes 
Indicates status of coin tube for coin types 0 to 15. 
A bit is set to indicate a full tube. For example, bit 7 = set would
    # indicate the tube for coin type 7 is ful
    # Z3 - Z18 = Tube Status - 16 bytes Indicates the greatest number of coins that the changer “knows” definitely are present in the coin tubes.
"""
TUBE_STATUS = [0x0A]

DIAGNOSTIC_STATUS = [0x0F,0x05]
"""
    # Z1 - Z16 = Changer Activity - 16 bytes 
Indicates the changer activity. If there is nothing to report, the changer should send only an ACK. Otherwise, the only valid
    # responses 
"""
    
POLL =  [0x0B]
"""
# To enable desired coin acceptance and disable manual coin payout if desired
"""
COINTYPE = [0x0C]
DISPENSE =[0x0D]
EXPANSION_COMMAND = [0x0F]

# # # # # # # # # # # # # # # # # # # # # 
# #  EXPANSION LEVEL SUBCOMANDS
# # # # # # # # # # # # # # # # # # # # # 

IDENTIFICATION = [0x00]
PAYOUT = [0x02]
PAYOUT_STATUS = [0x03]
PAYOUT_VALUE_POLL = [0x04]
DIAGNOSTIC_STATUS = [0x05]

class CoinWallet():
    statusDeactiveThread = False
    incommingCoin = ''
    status = ''
    data = ''
    # initialize the  connection to the com port
    """-------------------------- COINWALLET() ------------------------------"""
    """-------------------------- PRIVATE FUNCTIONS ------------------------------"""
    """-------------------------- Constructor ------------------------------"""
    def __init__(self, cb):
#         self.proc = multiprocessing.Process(target=self.threadReceived, args=())
#         self.proc.daemon = True
        (portBilletero,portMonedero,portDisplay,portLeds) = checkPorts()
        self.conn = BuchuSerial(str(portMonedero))
        print("Connected Monedero")
        self.cw_events = {
            DOS_EURO: self.__onInserted2Euro,
            UN_EURO: self.__onInsertedEuro,
            ZERO_FIVETY: self.__onInserted50Cent,
            ZERO_TWNTY: self.__onInserted20Cent,
            ZERO_TEN: self.__onInserted10Cent,
            ZERO_ZERO_FIVE: self.__onInserted05Cent,
        }
        self.cb = cb
        self.enableInsertCoins()
    """-------------------------- EVENTS ------------------------------"""
#     REVISAR LOS PARAMETROS DEL CALLBACK cb Ya Que no se usa la funcion cashbackroutine
    async def __onInserted05Cent(self,data):
        if(self.data[0] == '50'  ):
            print("0.05 euro")
            await self.cb(0.05)
            
    async def __onInserted10Cent(self,data):
        if(self.data[0] == '51'  ):
            print("0.10 euro")
            await self.cb(0.10)
            
    async def __onInserted20Cent(self,data):
        if(self.data[0] == '52'  ):
            print("0.20 euro")
            await self.cb(0.2)
    async def __onInserted50Cent(self,data):
        if(self.data[0] == '53'  ):
            print("0.50 euro")
            await self.cb(0.5)
    async def __onInsertedEuro(self,data):
        if(self.data[0] == '54'):
            print("1 euro")
            await self.cb(1)
    async def __onInserted2Euro(self,data):
        if(self.data[0] == '55'  ):
            print("2 euros")
            await self.cb(2)

    # # # # # # # # # # # # # # # # # # # # # # 
   
    """--------------------------send command ------------------------------"""
    def __sendCommand(self,command):
        response = self.conn.serialSend(bytearray(command))
        return response
    """------------------ send command and receive --------------------------"""
    def __sendCommandAndReceive(self,command):
        response = self.conn.serialSendAndReceive(bytearray(command))
        return response
    """---------------------------- ParseBytes ------------------------------"""
    async def __parseBytes(self,received):
        status = str(received)[2:4]
        data = str(received)[5:(len(str(received))-5)]
        self.status = status.split(" ")
        self.data = data.split(" ")
        print("received")
        print(received)
        self.incommingCoin = str(self.status[0] + " " + self.data[0])
        if(self.incommingCoin  in self.cw_events):
            await self.cw_events[self.incommingCoin ](data)
        return
        
    
    """--------------------------fullTube------------------------------"""
    def __fullTube(self,tube):
        print("FULL TUBE Number " + str(tube))
        
    """--------------------------cashBack------------------------------"""
    def cashBack(self,moneyBack):
        """
            CashBack(R) Esta función sirve
            para devolver el dinero indicado por parámetros
        """
        print("CoinWallet.cashback:  DEVOLVER" + str(moneyBack))
        countCoins = moneyBack / 0.05
        return self.__sendCommand([0x0F, 0x02, int(countCoins) ])
    """-------------------------- PUBLIC FUNCTIONS ------------------------------"""
    
    """-------------------------- startThreadReceived ------------------------------"""
    async def threadReceived(self):
#         while not self.statusDeactiveThread:
        #while True:
            if(self.conn.serialAvailable()):
                received = self.conn.serialReadLine()
                print("received :: ", received)
                await self.__parseBytes(received)
                print("cv status = " + str(self.status) + " data = " + str(self.data))
                self.data = str(self.data)
                self.status = str(self.status)
            return
    """-------------------------- SETUP ------------------------------"""
    def setup(self): 
        return self.__sendCommand(SETUP)
    
    """-------------------------- Reset ------------------------------"""
    def reset(self): 
        return self.__sendCommand(RESET)
    
    """-------------------------- tubeStatus ------------------------------"""
    def tubeStatus(self):  
        """
        VMC Command Code Changer Response Data
        TUBE STATUS 0AH 18 bytes: Z1 - Z18
        Z1 - Z2 = Tube Full Status - 2 bytes
        Indicates status of coin tube for coin types 0 to 15.
        b15 b14 b13 b12 b11 b10 b9 b8 | b7 b6 b5 b4 b3 b2 b1 b0
         Z1 Z2
        A bit is set to indicate a full tube. For example, bit 7 = set would
        indicate the tube for coin type 7 is full.
        Z3 - Z18 = Tube Status - 16 bytes
        Indicates the greatest number of coins that the changer “knows”
        definitely are present in the coin tubes. A bytes position in the
        16 byte string indicates the number of coins in a tube for a 
        Multi-Drop Bus / Internal Communication Protocol
        MDB/ICP Version 4.3 July, 2019 5•6
        particular coin type. For example, the first byte sent indicates
        the number of coins in a tube for coin type 0. Unsent bytes are
        assumed to be zero. For tube counts greater than 255, counts
        should remain at 255. 
        """
        return self.__sendCommandAndReceive([0x0A])

        
    """-------------------------- poll ------------------------------"""
    """ NOT IN USE SUST BY THREAD """
    def poll(self):  # 0x0B
        interval = 0.2
        while True:
            poll_start = time.time()
            response = self.__sendCommand([0x0B])
            print (response)
            self.cw_events[self.status](self.data)
            wait = interval - (time.time() - poll_start)
            if wait > 0.0:
                time.sleep(wait)
        
    """-------------------------- EnableInsertCoins ------------------------------"""
    def coinType(self):  # 0x0C
        """
        Y1 - Y2 = Coin Enable - 2 bytes
        b15 b14 b13 b12 b11 b10 b9 b8 | b7 b6 b5 b4 b3 b2 b1 b0
        Y1 Y2
        A bit is set to indicate a coin type is accepted. For example, bit 6 is set to
        indicate coin type 6, bit 15 is set to indicate coin type 15, and so on. To
        disable the changer, disable all coin types by sending a data block containing
        0000H. All coins are automatically disabled upon reset.
        Y3 - Y4 = Manual Dispense Enable - 2 bytes
        b15 b14 b13 b12 b11 b10 b9 b8 | b7 b6 b5 b4 b3 b2 b1 b0
        Y3 Y4
        A bit is set to indicate dispense enable. For example, bit 2 is set to enable
        dispensing of coin type 2. This command enables/disables manual
        dispensing using optional inventory switches. All manual dispensing switches
        are automatically enabled upon reset. 
        """
        return self.__sendCommand([0x0C])
    
    """-------------------------- Dispense ------------------------------"""
    """  NOT IN USE """
    def dispense(self): # 0D
        return self.__sendCommand([0x0D,0x05])
    
    """-------------------------- EnableInsertCoins ------------------------------"""
    def enableInsertCoins(self):
        """
            This function enable the possibility
            of insert all kind of coins
        """
        print("enableInsert Coins")
        return self.__sendCommand([0x0C, 0xff, 0xff, 0xff, 0xff])
    """-------------------------- EnableInsertCoins ------------------------------"""
    def disableInsertCoins(self):
        """
            This function disable the possibility
            of insert all kind of coins
        """
        print("disableInsert Coins")
        return self.__sendCommand([0x0C, 0x00, 0x00, 0x00, 0x00])


    """--------------------------cashBack------------------------------"""
    def cashBackRoutine(self,moneyBack):
        """
            CashBack(R) Esta función sirve
            para devolver el dinero indicado por parámetros
            realizando la rutina completa
        """
        self.reset()
        time.sleep(0.5)
        self.setup()
        time.sleep(0.5)
        self.enableInsertCoins()
        time.sleep(0.5)
        self.tubeStatus()
        time.sleep(0.5)
        return self.cashBack(round(moneyBack,2))
    """--------------------------startReceivingMode------------------------------"""
    async def startReceivingMode(self):
        """
            This function start the service
        """
        #self.proc = multiprocessing.Process(target= self.threadReceived, args=())
        self.enableInsertCoins()

#         self.proc.daemon = True
#         self.proc.start()
#         self.enableInsertCoins()
        return 0
    """--------------------------stopReceivingMode------------------------------"""
    def stopReceivingMode(self):
        """
            This function stop the service
        """
        # self.proc.join()
#         self.proc.close()
#         self.statusDeactiveThread = True
