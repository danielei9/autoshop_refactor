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
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

    def __init__(self,cb, port,log_raw=False, threading=False):
        self.cb = cb
        self.coinwallet:CoinWalletController = None

    def run(self):
        try:
            self.coinwallet = CoinWalletController(self.com,self.cb)
            # self.bv.set_inhibit(0)
            pollThread = threading.Thread(target=self.startPollThread)
            pollThread.start()

        except Exception as e:
            print("ERROR: " + str(e))
            pollThread = threading.Thread(target=self.startPollThread)
            pollThread.start()
            pass

    def startPollThread(self):
        print("startPollThread")
        asyncio.run( self.coinwallet.threadReceived())   