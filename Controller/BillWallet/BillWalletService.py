#!/usr/bin/env python3

import serial
import time
import logging
from Controller.BillWallet.CodesBillVal import *
from Controller.SerialCommunicator import *

from Controller.BillWallet.BillWallet import BillVal
import Controller.BillWallet.BillWallet as id003
import serial.tools.list_ports
import logging
import asyncio
import threading

###################################################
# CLASS BILLVAL
###################################################
class BillWalletService(SerialCommunicator):
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

    def __init__(self,cb, port,sendErrorTpv,log_raw=False, threading=False):
        super().__init__(port)
        self.initializeSerial()
        self.cb = cb
        self.bv:BillVal = None
        self.stackA = None
        self.stackB = None
        self.sendErrorTpv = sendErrorTpv

    def run(self):
        print("RUN  SERVICE pay billwallet...")
        try:
            self.bv = BillVal(self.com,self.cb,self.sendErrorTpv)
            self.bv.init()
            if self.bv.init_status == id003.POW_UP:
                logging.info("BV powered up normally.")
            elif self.bv.init_status == id003.POW_UP_BIA:
                logging.info("BV powered up with bill in acceptor.")
            elif self.bv.init_status == id003.POW_UP_BIS:
                logging.info("BV powered up with bill in stacker.")
            self.stackA = self.bv.stackA
            self.stackB = self.bv.stackB
            self.startPollingService()
            self.bv.pausePollThread()

        except Exception as e:
            print("ERROR: " + str(e))
            pass

    def startPollingService(self):
        try:
            pollThread = threading.Thread(target=self.startPollThread)
            pollThread.start()
        except Exception as e:
            print("ERROR: " + str(e))
            pollThread = threading.Thread(target=self.startPollThread)
            pollThread.start()
            pass

 


    def startPollThread(self):
        print("startPollThread")
        asyncio.run( self.bv.poll())   
    