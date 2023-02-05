#!/usr/bin/env python3

import serial
import time
import logging
from Controller.BillWallet.CodesBillVal import *
from Controller.SerialCommunicator import *
from Controller.BillWallet.BillWalletController import *

###################################################
# CLASS BILLVAL
###################################################
class BillWalletService(SerialCommunicator):
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

    def __init__(self,cb, port,log_raw=False, threading=False):
        super().__init__(port)
        self.initializeSerial()
        self.cb = cb
        self.billwalletController = BillWalletController(self.com,self.cb)
    def start(self):
        self.billwalletController.run()
