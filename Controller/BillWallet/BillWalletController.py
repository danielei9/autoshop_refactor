#!/usr/bin/env python3

from Controller.BillWallet.BillWallet import BillVal
import Controller.BillWallet.BillWallet as id003
import serial.tools.list_ports
import serial
import time
import logging
import asyncio
import threading


class BillWalletController ():
    def __init__(self,com,cb):
        self.bv:BillVal = None
        self.com = com
        self.cb = cb

    def run(self):
        try:
            self.bv = BillVal(self.com,self.cb)
            self.bv.power_on()
            if self.bv.init_status == id003.POW_UP:
                logging.info("BV powered up normally.")
            elif self.bv.init_status == id003.POW_UP_BIA:
                logging.info("BV powered up with bill in acceptor.")
            elif self.bv.init_status == id003.POW_UP_BIS:
                logging.info("BV powered up with bill in stacker.")
            self.bv.set_inhibit(0)
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