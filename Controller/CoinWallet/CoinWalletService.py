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

    def __init__(self,cb, port,log_raw=False, threading=False):
        self.cb = cb
        self.port = port
        self.coinwallet:CoinWalletController = None

    def run(self):
        try:
            print("Running coinwallet service")
            self.coinwallet = CoinWalletController(self.port,self.cb)
            # self.bv.set_inhibit(0)
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