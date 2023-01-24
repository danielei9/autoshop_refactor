class CoinWallet():
    def __init__(self):
        print("init coinwallet")
    
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
from .BuchuSerial import BuchuSerial
from infrastructure.common.USBDynamic.DinUsb import * 

class CoinWallet():
    statusDeactiveThread = False
    incommingCoin = ''
    status = ''
    data = ''