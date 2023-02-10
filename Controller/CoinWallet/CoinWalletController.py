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
import multiprocessing
import time
from Controller.CoinWallet.CodesCoinWallet import *
from Controller.SerialCommunicator import *

class CoinWalletController(SerialCommunicator):
    statusDeactiveThread = False
    incommingCoin = ''
    status = ''
    data = ''
    # initialize the  connection to the com port
    """-------------------------- COINWALLET() ------------------------------"""
    """-------------------------- PRIVATE FUNCTIONS ------------------------------"""
    """-------------------------- Constructor ------------------------------"""
    def __init__(self, cb,port):
#         self.proc = multiprocessing.Process(target=self.threadReceived, args=())
#         self.proc.daemon = True
        super().__init__(port,parity=serial.PARITY_NONE)
        self.cw_events = {
            DOS_EURO: self.__onInserted2Euro,
            UN_EURO: self.__onInsertedEuro,
            ZERO_FIVETY: self.__onInserted50Cent,
            ZERO_TWNTY: self.__onInserted20Cent,
            ZERO_TEN: self.__onInserted10Cent,
            ZERO_ZERO_FIVE: self.__onInserted05Cent,
        }
        self.cb = cb
        self.data = ""
        self.status = ""
        self.initializeSerial()

        print("Init Controller CoinWallet")
        self.cb = cb
        time.sleep(0.2)
        self.reset()
        time.sleep(0.2)
        self.setup()
        time.sleep(0.2)
        print("***************IMOPRT")
        print(self.enableDisableChargeCoins())
        time.sleep(0.2)
        self.disableInsertCoins()
        # self.enableInsertCoins()
    """-------------------------- EVENTS ------------------------------"""
#     REVISAR LOS PARAMETROS DEL CALLBACK cb Ya Que no se usa la funcion cashbackroutine
    def __onInserted05Cent(self,data):
            print("0.05 euro")
            self.cb(0.05)
    def __onInserted10Cent(self,data):
            print("0.10 euro")
            self.cb(0.10)        
    def __onInserted20Cent(self,data):
            print("0.20 euro")
            self.cb(0.2)
    def __onInserted50Cent(self,data):
            print("0.50 euro")
            self.cb(0.5)
    def __onInsertedEuro(self,data):
            print("1 euro")
            self.cb(1)
    def __onInserted2Euro(self,data):
        print("2 euros")
        self.cb(2)
    # # # # # # # # # # # # # # # # # # # # # # 
    """--------------------------send command ------------------------------"""
    def __sendCommand(self,command):
        try:
            print("sendCommand: " , command)
            response = self.com.write(bytearray(command))
            return 1
        except:
            print("Error sending")
            pass

        return response
    """------------------ send command and receive --------------------------"""
    def __sendCommandAndReceive(self,command):
        try:# try to open
#             if not self.portConfig.isOpen():
#                 self.serialOpen()
            # try to send
            self.com.write(bytearray(command))
            # try to read if available
            count = 0
            startTimeOut = time.time()
            while (not self.com.in_waiting):
                print("waiting response...")
                endTimeOut = time.time()
                time.sleep(1)
                # TimeOut
                if (endTimeOut - startTimeOut >= 2):  
                    return -1
            response = self.com.readline()
            # print(response)
            return response
        except:
            print("Error sending")
            pass
            
    """---------------------------- ParseBytes ------------------------------"""
    def __parseBytes(self,received):
        status = str(received)[2:4]
        data = str(received)[5:(len(str(received))-5)]
        print("data : " ,data)
        print("Received : " ,str(received))
        self.status = status.split(" ")
        self.data = data.split(" ")
        self.incommingCoin = str(self.status[0] + " " + self.data[0])
        print("incomming coin  ", self.incommingCoin)
        if(self.incommingCoin  in self.cw_events):
            print("esta en el event")
            self.cw_events[self.incommingCoin ](data)
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
   
    """-------------------------- SETUP ------------------------------"""
    def setup(self): 
        return self.__sendCommand(SETUP)
    
    """-------------------------- Reset ------------------------------"""
    def reset(self): 
        return self.__sendCommand(RESET)
    
    def enableDisableChargeCoins(self): 
        return self.__sendCommandAndReceive([0x0C,0x00,0x00])
    
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
            print ("CoinWallet Respone: ",response)
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
    def startReceivingMode(self):
        """
            This function start the service
        """
        #self.proc = multiprocessing.Process(target= self.threadReceived, args=())
        self.enableInsertCoins()

#         self.proc.daemon = True
#         self.proc.start()
#         self.enableInsertCoins()
        return 0
 
    """-------------------------- startThreadReceived ------------------------------"""
    def threadReceived(self):
#         while not self.statusDeactiveThread:
        while True:
            if(self.com.in_waiting):    
                try:
                    received = self.com.readline()
                    print("received :: ", received )
                except serial.SerialException:
                    print('Port is not available')
                    return False
                except serial.portNotOpenError:
                    print('Attempting to use a port that is not open in read line')
                    return False
                except:
                    print("Not possible to read port")
                    return False

                # print("CoinWallet RX :: ", bytes(received))
                self.__parseBytes(received)
                print("cv status = " + str(self.status) + " data = " +str( self.data))
                self.data = str(self.data)
                self.status = str(self.status)