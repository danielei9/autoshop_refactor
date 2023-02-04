#!/usr/bin/env python3

import serial
import time
import logging
from Controller.BillWallet.CodesBillVal import *
from Controller.SerialCommunicator import *
import Controller.BillWallet.BillWalletInit as BillWalletInit

###################################################
# CLASS BILLVAL
###################################################
class BillWalletController(SerialCommunicator):
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

    def __init__(self,cb, port,log_raw=False, threading=False):
        super().__init__(port)
        self.initializeSerial()
        self.cb = cb
    def start(self):
        BillWalletInit.main(self.com,self.cb)

