#!/usr/bin/env python3

import serial
import time
import logging
from CodesBillVal import *
import USBDynamic.DinUsb as dinUsb
"""Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

class BillWallet():

    def __init__(self,cb, log_raw=False, threading=False):
        self.cb = cb
        # Try to check and connect to dyn port USB 
        (portBilletero,portMonedero,portDisplay,portLeds) = checkPorts()

        self.com = serial.Serial(
            str(portBilletero),
            9600,
            serial.EIGHTBITS,
            serial.PARITY_EVEN, 
            timeout=0.05)

        self.status = 0x00
        self.data = 0x00
        self.bv_status = None
        self.bv_version = None
        self.threading = threading

        self.minBill = 10
        self.maxBill = 20
        self.stackA = self.minBill
        self.stackB = self.maxBill

        self.all_statuses = NORM_STATUSES + ERROR_STATUSES + POW_STATUSES + PAYING_STATUSES
#         se definen los eventos de la uart
        self.bv_events = {
            IDLE: self._on_idle,
            ACEPTING: self._on_accepting,
            ESCROW: self._on_escrow,
            STACKING: self._on_stacking,
            VEND_VALID: self._on_vend_valid,
            STACKED: self._on_stacked,
            REJECTING: self._on_rejecting,
            RETURNING: self._on_returning,
            HOLDING: self._on_holding,
            INHIBIT: self._on_inhibit,
            INITIALIZE: self._on_init,
            STACKER_FULL: self._on_stacker_full,
            STACKER_OPEN: self._on_stacker_open,
            ACCEPTOR_JAM: self._on_acceptor_jam,
            STACKER_JAM: self._on_stacker_jam,
            PAUSE: self._on_pause,
            CHEATED: self._on_cheated,
            FAILURE: self._on_failure,
            COMM_ERROR: self._on_comm_error,
            INVALID_COMMAND: self._on_invalid_command,
            PAYING: self._on_paying,
            PAY_STAY: self._on_pay_stay,
            PAY_VALID: self._on_pay_valid,
            INVALID_COMMAND:self._on_invalid_command
        }
        # Seleccion de Euros como Moneda
        self.bv_denoms = ESCROW_EU
        self.escrow = 0
        self.bv_on = False
        # set up logging
        self.raw = log_raw
