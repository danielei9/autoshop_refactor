#!/usr/bin/env python3

import serial
import time
import logging
from Controller.CoinWallet.CodesCoinWallet import *
from Controller.SerialCommunicator import *

from Controller.CoinWallet.CoinWalletController import *
import serial.tools.list_ports
import logging
import asyncio
import threading

###################################################
# CLASS BILLVAL
###################################################
class CoinWalletService():

    def __init__(self,cb, port,sendErrorTPV, log_raw=False, threading=False):
        self.cb = cb
        self.port = port
        self.sendErrorTPV = sendErrorTPV
        self.coinwallet:CoinWalletController = None

    def run(self):
        try:
            print("Running coinwallet service")
            self.coinwallet = CoinWalletController(self.cb,self.port,self.sendErrorTPV)
            time.sleep(.2)
            pollThread = threading.Thread(target=self.startRxThread)
            pollThread.start()

        except Exception as e:
            print("ERROR: " + str(e))
            pollThread = threading.Thread(target=self.startRxThread)
            pollThread.start()
            pass

    def startRxThread(self):
        print("startPollThread")
        asyncio.run( self.coinwallet.threadReceived())   