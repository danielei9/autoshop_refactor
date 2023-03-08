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
    incommingCoin = ''
    status = ''
    data = ''

    def __init__(self, cb,port,sendErrorTPV):
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
        self.sendErrorTPV = sendErrorTPV
        self.tubeFullState = []
        self.tubeQntyState = []
        self.tubeQnty_0_05 = 0
        self.tubeQnty_0_10 = 0
        self.tubeQnty_0_20 = 0
        self.tubeQnty_0_50 = 0
        self.tubeQnty_1_00 = 0
        self.tubeQnty_2_00 = 0
        self.enableReceivedMode = True
        print("Init Controller CoinWallet")
        self.cb = cb
        time.sleep(0.2)
        self.reset()
        time.sleep(0.2)
        self.setup()
        time.sleep(0.2)
        print(self.enableDisableChargeCoins())
        time.sleep(0.2)
        self.disableInsertCoins()
        time.sleep(0.4)
        self.tubeStatus()

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
    def __sendCommand(self,command):
        try:
            print("sendCommand: " , command)
            response = self.com.write(bytearray(command))
            return 1
        except:
            print("Error sending")
            pass

        return response
    def __sendCommandAndReceive(self,command):
        try:
            self.com.write(bytearray(command))
            # try to read if available
            startTimeOut = time.time()
            while (not self.com.in_waiting):
                print("waiting response...")
                endTimeOut = time.time()
                time.sleep(.2)
                # TimeOut
                if (endTimeOut - startTimeOut >= 2):  
                    return -1
            response = self.com.readline()
            # print(response)
            return response
        except:
            # TODO: Informar al usuario que no se ha podido enviar el comando 
            print("Error sending")
            pass
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
    def __getIfTubeIsFull(self, decimal_number):
        # Convierte el entero decimal en una cadena binaria de 8 bits
        binary_string = bin(decimal_number)[2:].zfill(8)
        for i in range(len(binary_string)):
            if binary_string[i] == "1":
                self.tubeFullState.append(1)
            else:
                self.tubeFullState.append(0)

        # Muestra los estados de las alarmas
        print(self.tubeFullState)

    def cashBack(self,moneyBack):
        print("Coin return : " + str(moneyBack))
        # MONEDERO OLD
        # countCoins = moneyBack / 0.05
        countCoins = moneyBack / 0.01
        while countCoins > 255:
            self.__sendCommand([0x0F, 0x02, 0xFF ])
            countCoins = countCoins - 255
            time.sleep(5)
        return self.__sendCommand([0x0F, 0x02, int(countCoins) ])
    def setup(self): 
        return self.__sendCommand(SETUP)
    
    def reset(self): 
        return self.__sendCommand(RESET)
    
    def enableDisableChargeCoins(self): 
        return self.__sendCommandAndReceive([0x0C,0xFF,0xFF])
    
    def tubeStatus(self):  
        try:
            self.com.readline()
            time.sleep(.1)
            self.__sendCommand([0x0A])
            time.sleep(.1)
            response = self.com.readline().split()
            int_array = [int(x, 16) for x in response]
            
            # print("lengtth ",len(response))
            if len(response)!= 19 :
                AssertionError("Error reading tube status")

            # print("TUBE STATUS: ",response)
            self.getTubesCount(int_array)
            
            self.countAvailableMoney()
            return 
        except Exception as e:
            print(e)
            self.tubeStatus()
            pass
    def getTubesCount(self,arrayResponse):
        
        tubeByte1 = arrayResponse[0]
        tubeByte2 = arrayResponse[1]
        self.checkIfTubeIsFull(tubeByte1,tubeByte2)

        self.tubeQnty_0_05 = arrayResponse[2]
        self.tubeQnty_0_10 = arrayResponse[3]
        self.tubeQnty_0_20 = arrayResponse[4]
        self.tubeQnty_0_50 = arrayResponse[5]
        self.tubeQnty_1_00 = arrayResponse[6]
        self.tubeQnty_2_00 = arrayResponse[7]

        print(" tubeQnty_0_05:  ",self.tubeQnty_0_05)
        print(" tubeQnty_0_10:  ",self.tubeQnty_0_10)
        print(" tubeQnty_0_20:  ",self.tubeQnty_0_20)
        print(" tubeQnty_0_50:  ",self.tubeQnty_0_50)
        print(" tubeQnty_1_00:  ",self.tubeQnty_1_00)
        print(" tubeQnty_2_00:  ",self.tubeQnty_2_00)
    def countAvailableMoney(self):
        self.availableMoneyInCoins = 0
        self.availableMoneyInCoins += self.tubeQnty_0_05 * 0.05
        self.availableMoneyInCoins += self.tubeQnty_0_10 * 0.10
        self.availableMoneyInCoins += self.tubeQnty_0_20 * 0.20
        self.availableMoneyInCoins += self.tubeQnty_0_50 * 0.50
        self.availableMoneyInCoins += self.tubeQnty_1_00 
        self.availableMoneyInCoins += self.tubeQnty_2_00 * 2
        self.availableMoneyInCoins = round(self.availableMoneyInCoins,2)

        self.checkAvailableMoney()

        print("availableMoneyInCoins: ",self.availableMoneyInCoins)

    def checkAvailableMoney(self):
        if(self.tubeQnty_0_05< 5):
            print("Warning: Hay pocas monedas de 0.05")
            self.sendErrorTPV("Warning: Hay pocas monedas de 0.05")
        if(self.tubeQnty_0_10< 5):
            print("Warning: Hay pocas monedas de 0.10")
            self.sendErrorTPV("Warning: Hay pocas monedas de 0.10")
        if(self.tubeQnty_0_20< 5):
            print("Warning: Hay pocas monedas de 0.20")
            self.sendErrorTPV("Warning: Hay pocas monedas de 0.20")
        if(self.tubeQnty_0_50< 5):
            print("Warning: Hay pocas monedas de 0.50")
            self.sendErrorTPV("Warning: Hay pocas monedas de 0.50")
        if(self.tubeQnty_1_00< 5):
            print("Warning: Hay pocas monedas de 1.00")
            self.sendErrorTPV("Warning: Hay pocas monedas de 1.00")
        if(self.tubeQnty_2_00< 5):
            print("Warning: Hay pocas monedas de 2.00")
            self.sendErrorTPV("Warning: Hay pocas monedas de 2.00")

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
        
    def coinType(self):  # 0x0C
        return self.__sendCommand([0x0C])
    
    def enableInsertCoins(self):
        print("enableInsert Coins")
        return self.__sendCommand([0x0C, 0xff, 0xff, 0xff, 0xff])
    
    def disableInsertCoins(self):
        print("disableInsert Coins")
        return self.__sendCommandAndReceive([0x0C, 0x00, 0x00, 0x00, 0x00])
    
    async def threadReceived(self):
        while True:
            if(self.enableReceivedMode):
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
    
    def checkIfTubeIsFull(self,byte1,byte2):
        self.tubeFullState = []
        self.__getIfTubeIsFull(byte1)
        self.__getIfTubeIsFull(byte2)
        for i in range(len(self.tubeFullState)):
            if self.tubeFullState[i] == 1:
                print ("FULL TUBE number: ", i)
                self.sendErrorTPV("ERROR: Revise el tubo numero " + str(i) + " esta lleno o atascado.")