#!/usr/bin/env python3

from Controller.BillWallet.BillWallet import BillVal
import Controller.BillWallet.BillWallet as id003
import serial.tools.list_ports
import serial
import time
import logging


def main(com,cb):
    # port = '/dev/ttyUSB0'  # JCM UAC device (USB serial adapter)

    bv = BillVal(com,cb)
    print("Please connect bill validator.")
    bv.power_on()

    if bv.init_status == id003.POW_UP:
        logging.info("BV powered up normally.")
    elif bv.init_status == id003.POW_UP_BIA:
        logging.info("BV powered up with bill in acceptor.")
    elif bv.init_status == id003.POW_UP_BIS:
        logging.info("BV powered up with bill in stacker.")
    bv.set_inhibit(0)
    time.sleep(5)
    bv.set_inhibit(1)
    time.sleep(5)
    bv.set_inhibit(0)
    bv.poll()


# if __name__ == '__main__':
#     main()