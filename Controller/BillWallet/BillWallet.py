#!/usr/bin/env python3

import serial
import time
import logging
from  .CodesBillVal import *
from .BillWallterStates import *

class BillVal:
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""
    
    def __init__(self, com,cb, log_raw=False, threading=False):
        self.com = com
        self.cb = cb
        self.bv_status = None
        self.bv_version = None
        self.last_full_msg = None
        self.threading = threading
        self.lastMessage = None
        self.all_statuses = NORM_STATUSES + ERROR_STATUSES + POW_STATUSES
            
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
        }
        
        # TODO get this from version during powerup
        self.bv_denoms = ESCROW_USA
        
        self.bv_on = False
        
        # set up logging
        self.raw = log_raw
        
        if not logging.getLogger('').hasHandlers():
            logging.basicConfig(level=logging.DEBUG,
                                format="[%(asctime)s] %(levelname)s: %(message)s",
                                filename='debug.log',
                                filemode='w',
                                )
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
    
    createStates()

    def _raw(self, pre, msg):
        if self.raw:
            msg = ['0x%02x' % x for x in msg]
            log = open('raw.log', 'a')
            log.write('{} {}\r\n'.format(pre, msg))
            log.close()
  
    def send_command(self, command, data=b''):
        """Send a generic command to the bill validator"""
        
        length = 5 + len(data)  # SYNC, length, command, and 16-bit CRC
        message = bytes([SYNC, length, command]) + data
        message += get_crc(message)
        
        # log message
        self._raw('>', message)
        if(message != self.lastMessage):
            print("Sending " + str(message))
            self.lastMessage = message
        return self.com.write(message)
        
    def read_response(self):
        """Parse data from the bill validator. Returns a tuple (command, data)"""
        
        start = None
        while start == None:
            start = self.com.read(1)
            if len(start) == 0:
                # read timed out, return None
                return (None, b'')
            elif start == b'\x00':
                return (0x00, b'')
            elif ord(start) != SYNC and start:
                raise SyncError("Wrong start byte, got %s" % start)
            
        total_length = self.com.read()
        data_length = ord(total_length) - 5
        
        command = self.com.read()
        
        if data_length:
            data = self.com.read(data_length)
        else:
            data = b''
            
        crc = self.com.read(2)
        
        # log message
        full_msg = start + total_length + command + data
        self._raw('<', full_msg)
        
        # check our data
        # if get_crc(full_msg) != crc:
        #     raise CRCError("CRC mismatch")
        if(full_msg != self.last_full_msg):
            print("Received: " + str(full_msg))
            self.last_full_msg = full_msg
        return ord(command), data
        
    def power_on(self, *args, **kwargs):
        """Handle startup routines"""
        
        self.bv_on = True
        
        status = None
        while status is None or status == 0x00:
            status, data = self.req_status()
            if not self.bv_on:
                # in case polling thread needs to be terminated before power up
                self.init_status = None
                return
        
        self.init_status = status
            
        if status not in POW_STATUSES:
            logging.warning("Acceptor already powered up, status: %02x" % status)
            return self.init_status
        elif status == POW_UP:
            logging.info("Powering up...")
            logging.info("Getting version...")
            self.send_command(GET_VERSION)
            status, self.bv_version = self.read_response()
            logging.info("BV software version: %s" % self.bv_version.decode())
            
            while status != ACK:
                logging.debug("Sending reset command")
                self.send_command(RESET)
                status, data = self.read_response()
                
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)
        else:
            # Acceptor should either reject or stack bill
            while status != ACK:
                self.send_command(RESET)
                status, data = self.read_response()
                
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)
                    
        # typically call BillVal.poll() after this
        
        return self.init_status
    
    def initialize(self, denom=[0x82, 0], sec=[0, 0], dir=[0], opt_func=[0, 0], 
                   inhibit=[0], bar_func=[0x01, 0x12], bar_inhibit=[0]):
        """Initialize BV settings"""
        
        logging.debug("Setting denom inhibit: %r" % denom)
        denom = bytes(denom)
        self.send_command(SET_DENOM, denom)
        status, data = self.read_response()
        if (status, data) != (SET_DENOM, denom):
            logging.warning("Acceptor did not echo denom settings")
        
        logging.debug("Setting security: %r" % sec)
        sec = bytes(sec)
        self.send_command(SET_SECURITY, sec)
        status, data = self.read_response()
        if (status, data) != (SET_SECURITY, sec):
            logging.warning("Acceptor did not echo security settings")
            
        logging.debug("Setting direction inhibit: %r" % dir)
        dir = bytes(dir)
        self.send_command(SET_DIRECTION, dir)
        status, data = self.read_response()
        if (status, data) != (SET_DIRECTION, dir):
            logging.warning("Acceptor did not echo direction settings")
        
        logging.debug("Setting optional functions: %r" % opt_func)
        opt_func = bytes(opt_func)
        self.send_command(SET_OPT_FUNC, opt_func)
        status, data = self.read_response()
        if (status, data) != (SET_OPT_FUNC, opt_func):
            logging.warning("Acceptor did not echo option function settings")
            
        logging.debug("Setting inhibit: %r" % inhibit)
        inhibit = bytes(inhibit)
        self.send_command(SET_INHIBIT, inhibit)
        status, data = self.read_response()
        if (status, data) != (SET_INHIBIT, inhibit):
            logging.warning("Acceptor did not echo inhibit settings")
        
        logging.debug("Setting barcode functions: %r" % bar_func)
        bar_func = bytes(bar_func)
        self.send_command(SET_BAR_FUNC, bar_func)
        status, data = self.read_response()
        if (status, data) != (SET_BAR_FUNC, bar_func):
            logging.warning("Acceptor did not echo barcode settings")

        logging.debug("Setting barcode inhibit: %r" % bar_inhibit)
        bar_inhibit = bytes(bar_inhibit)
        self.send_command(SET_BAR_INHIBIT, bar_inhibit)
        status, data = self.read_response()
        if (status, data) != (SET_BAR_INHIBIT, bar_inhibit):
            logging.warning("Acceptor did not echo barcode inhibit settings")
            
        while self.req_status()[0] == INITIALIZE:
            # wait for initialization to finish
            time.sleep(0.2)
    
    def req_status(self):
        """Send status request to bill validator"""
        
        if not self.bv_on:
            # in case polling thread needs to be terminated before power up
            return None, b''
        
        if self.com.in_waiting:
            # discard any unused data
            logging.warning("Found unused data in buffer, %r" % self.com.read(self.com.in_waiting))
            
        self.send_command(STATUS_REQ)
        
        stat, data = self.read_response()
        if stat not in self.all_statuses + (0x00, None):
            logging.warning("Unknown status code received: %02x" % stat)
            logging.warning("Unknown status code received: data: %r" %  data)
        
        return stat, data
        
    def poll(self, interval=0.2):
        """Send a status request to the bill validator every `interval` seconds
        and fire event handlers. `interval` defaults to 200 ms, per ID-003 spec.
        
        Event handlers are only fired upon status changes. Event handlers can
        set `self.bv_status` to None to force event handler to fire on the next
        status request.
        """
        
        while True:
            poll_start = time.time()
            status, data = self.req_status()
            if (status, data) != self.bv_status:
                if status in self.bv_events:
                    self.bv_events[status](data)
            self.bv_status = (status, data)
            wait = interval - (time.time() - poll_start)
            if wait > 0.0:
                time.sleep(wait)
            
            
    def set_inhibit(self,inhibit):
        """
        Command to set the inhibit state
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting inhibit: %r" % inhibit)
        print("set_inhibit")
        inhibit = bytes(inhibit)
        time.sleep(.2)
        self.send_command(SET_INHIBIT, inhibit)
        time.sleep(.2)
        (status, data)  = self.bv_status 

        if (status, data) != (SET_INHIBIT, inhibit):
            logging.warning("Acceptor did not echo inhibit settings")
