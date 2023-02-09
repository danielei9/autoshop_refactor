#!/usr/bin/env python3

import serial
import time
import logging
from  .CodesBillVal import *

class BillVal:
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""
    
    def __init__(self, com,cb, log_raw=False, threading=False):
        self.com = com  
        self.cb = cb
        self.bv_status = (0x00,0x00)
        self.bv_version = None
        self.last_full_msg = None
        self.threading = threading
        self.lastMessage = None
        self.all_statuses = NORM_STATUSES + ERROR_STATUSES + POW_STATUSES + PAYING_STATUSES
        self.pause_flag = False
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
            INVALID_COMMAND: self._on_invalid_command,
            PAY_VALID: self._on_pay_valid,
            PAY_STAY:self._on_pay_stay,
            PAY_OUT_NOTE_ERROR:self._on_note_error
        }
        
        # TODO get this from version during powerup
        self.bv_denoms = ESCROW_USA
        
        self.bv_on = False
        
        # set up logging
        self.raw = log_raw
        
        self.minBill = 5
        self.maxBill = 10

        if not logging.getLogger('').hasHandlers():
            logging.basicConfig(level=logging.DEBUG,
                                format=" BillWallet [%(asctime)s] %(levelname)s: %(message)s",
                                filename='debug.log',
                                filemode='w',
                                )
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter("BillWallet %(levelname)s: %(message)s")
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)

    def pausePollThread(self):
        print("BV: PAUSE POLL")
        self.pause_flag = True

    def resumePollThread(self):
        print("BV: RESUME POLL")
        time.sleep(.2)
        self.pause_flag = False

    def init(self):
        print("INITIALIZE")
        #       LOGGING DEBUG esto dará problemas, hay que ver como lo añadimos por que sirve para obtener el logg de la maquina de billetes
        self.power_on()
        if self.init_status == POW_UP:
            logging.info("BV powered up normally. POW_UP")
        
        elif self.init_status == POW_UP_BIA:
            logging.info("BV powered up with bill in acceptor. POW_UP_BIA")
        
        elif self.init_status == POW_UP_BIS:
            logging.info("BV powered up with bill in stacker. POW_UP_BIS")

        if self.init_status == IDLE:
            print("Status IDLE")

        (status,data) = self.req_status()
  
        if  (status == INHIBIT):
            print("Setting to INHIBIT/DISABLE (enable setting buchubills)")

        if (status == IDLE):
            self.set_inhibited()
        
        try:
            self.getActualStacksConfig()
            self.set_recycler_config(self.stackA,self.stackB)
        except Exception as e:
            print("Error getting stacks config: ", e)
            time.sleep(2)
            self.getActualStacksConfig()
            self.set_recycler_config(self.stackA,self.stackB)

    def process_stack_config(self,stack):
        if stack == 0:
            return 0x00
        if stack == 5:
            return 0x02
        if stack == 10:
            return 0x04
        if stack == 20:
            return 0x08
        if stack == 50:
            return 0x10
        if stack == 100:
            return 0x20

    def set_recycler_config(self, stack1,stack2):
        """
            Stack1 === 0,5,10,20,50,100
            Stack2 === 0,5,10,20,50,100
        """
        print("set_recycler_config")
        confByteStack1 = self.process_stack_config(stack1)
        confByteStack2 = self.process_stack_config(stack2)
        status = ""
        self.com.flushInput()
        self.com.flushOutput()
        time.sleep(0.2)
        message = bytes([0xFC ,0x0D, 0xF0, 0x20, 0xD0, 0x08, 0x00, 0x01, 0x04,0x00,0x02])
        message += get_crc(message)

        self.com.write(message)
        time.sleep(0.2)
        print("Finish set_recycler_config ")
        status, data = self.read_response()
        print("status: %02x" % status)
        return

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
        time.sleep(.2)
        start = None
        while start == None:
            start = self.com.read(1)
            if len(start) == 0:
                # read timed out, return None
                return (None, b'')
            elif start == b'\x00':
                return (0x00, b'')
            elif ord(start) != SYNC and start:
                print("ERROR:")
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
            print("BV Received: " + str(full_msg))
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
        print("ACTUAL STATUS power_on: " , str(status))
                # Si se vuelva iniciar pero ya estaba encendida e inhibida    
        # if status == INHIBIT:
        #     self.set_inhibited()
        #     logging.warning(
        #         "Acceptor already powered up,but inhibited status: %02x" % status)
        #     return
        
        if status not in POW_STATUSES:
            logging.warning("Acceptor already powered up, status: %02x" % status)
            print("ACTUAL STATUS power_on if: " , str(status))
            return self.init_status
        elif status == POW_UP:
            logging.info("Powering up...")
            logging.info("Getting version...")
            self.send_command(GET_VERSION)
            status, self.bv_version = self.read_response()
            logging.info("BV software version: %s" % self.bv_version.decode())
            print("ACTUAL STATUS power_on elif: " , str(status))
            
            while status != ACK:
                logging.debug("Sending reset command")
                self.send_command(RESET)
                status, data = self.read_response()
                
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)
        else:
            # Acceptor should either reject or stack bill
            print("ACTUAL STATUS power_on else: " , str(status))

            while status != ACK:
                self.send_command(RESET)
                status, data = self.read_response()
                
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)
                    
        return self.init_status
    
    def initialize(self, denom=[0x82, 0], sec=[0, 0], dir=[0], opt_func=[0, 0], 
                   inhibit=[0], bar_func=[0x01, 0x12], bar_inhibit=[0]):
        """Initialize BV settings"""
        
        logging.debug("Setting denom inhibit: %r" % denom)
        denom = bytes(denom)
        self.send_command(SET_DENOM, denom)
        status, data = self.read_response()
        while (status, data) != (SET_DENOM, denom):
            logging.warning("Acceptor did not echo denom settings")
            time.sleep(2)
        
        logging.debug("Setting security: %r" % sec)
        sec = bytes(sec)
        self.send_command(SET_SECURITY, sec)
        status, data = self.read_response()
        while (status, data) != (SET_SECURITY, sec):
            logging.warning("Acceptor did not echo security settings")
            time.sleep(2)
            
        logging.debug("Setting direction inhibit: %r" % dir)
        dir = bytes(dir)
        self.send_command(SET_DIRECTION, dir)
        status, data = self.read_response()
        while (status, data) != (SET_DIRECTION, dir):
            logging.warning("Acceptor did not echo direction settings")
            time.sleep(2)

        logging.debug("Setting optional functions: %r" % opt_func)
        opt_func = bytes(opt_func)
        self.send_command(SET_OPT_FUNC, opt_func)
        status, data = self.read_response()
        while (status, data) != (SET_OPT_FUNC, opt_func):
            logging.warning("Acceptor did not echo option function settings")
            time.sleep(2)
            
        logging.debug("Setting inhibit: %r" % inhibit)
        inhibit = bytes(inhibit)
        self.send_command(SET_INHIBIT, inhibit)
        status, data = self.read_response()
        while (status, data) != (SET_INHIBIT, inhibit):
            logging.warning("Acceptor did not echo inhibit settings")
            time.sleep(2)

        logging.debug("Setting barcode functions: %r" % bar_func)
        bar_func = bytes(bar_func)
        self.send_command(SET_BAR_FUNC, bar_func)
        status, data = self.read_response()
        while (status, data) != (SET_BAR_FUNC, bar_func):
            logging.warning("Acceptor did not echo barcode settings")
            time.sleep(2)

        logging.debug("Setting barcode inhibit: %r" % bar_inhibit)
        bar_inhibit = bytes(bar_inhibit)
        self.send_command(SET_BAR_INHIBIT, bar_inhibit)
        status, data = self.read_response()
        while (status, data) != (SET_BAR_INHIBIT, bar_inhibit):
            logging.warning("Acceptor did not echo barcode inhibit settings")
            time.sleep(1)
            
        while self.req_status()[0] == INITIALIZE:
            # wait for initialization to finish
            time.sleep(0.2)

        print("INITIALIZED BV")
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
        
    def poll(self, interval=0.5):
        """Send a status request to the bill validator every `interval` seconds
        and fire event handlers. `interval` defaults to 200 ms, per ID-003 spec.
        
        Event handlers are only fired upon status changes. Event handlers can
        set `self.bv_status` to None to force event handler to fire on the next
        status request.
        """
        
        while True:
            while self.pause_flag:
                time.sleep(0.1)
            poll_start = time.time()
            status, data = self.req_status()
            if (status, data) != self.bv_status:
                if status in self.bv_events:
                    self.bv_events[status](data)
            self.bv_status = (status, data)
            wait = interval - (time.time() - poll_start)
            if wait > 0.0:
                time.sleep(wait)

    def set_inhibited(self):
        """
        Command to set the inhibit state
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        self.pausePollThread() 
        inhibit = 0x01
        logging.debug("Setting inhibit: %r" % inhibit)
        inhibit = bytes(inhibit)
        self.send_command(SET_INHIBIT, inhibit)
        status, data = self.read_response()
        while (status, data) != (SET_INHIBIT, inhibit):
            print(status, " data: " ,data)
            logging.warning("Acceptor did not echo inhibit settings")
            time.sleep(2)
            self.set_inhibited()
    
    def set_not_inhibited(self):
        """
        Command to set the inhibit state
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        # self.pausePollThread()
        print("sending NOT inhibit")
        
        self.pausePollThread() 
        inhibit = 0x00
        logging.debug("Setting inhibit: %r" % inhibit)
        inhibit = bytes(inhibit)
        self.send_command(SET_INHIBIT, inhibit)
        status, data = self.read_response()
        while (status) != (SET_INHIBIT):
            print(str(status), " data: " ,str(data))
            print("Should be " ,str(SET_INHIBIT), " inhibit: " ,str(inhibit))
            logging.warning("Acceptor did not echo inhibit settings")
            time.sleep(2)
            self.set_inhibited()
        # self.resumePollThread()

    def getActualStacksConfig(self):
        print("get Actual Stacks Config ")
        # self.set_inhibited()
        time.sleep(.2)
        print("BV Setting inhibit...")
        self.com.write(bytes([0xFC,0X06,0XC3,0X01,0X8D,0xC7]))
        time.sleep(.2)
        response = str(self.com.readline().hex())
        print("BV Response : ",response)
        time.sleep(.2)
        print("BV Getting config ...")
        self.com.write(bytes([0xFC,0X07,0XF0,0X20,0X90,0x39,0X84]))
        time.sleep(.1)
        response = str(self.com.readline().hex())
        self.stackA = self.convertStacksMachineToStacksEuro(str(response[10:12]))
        self.stackB = self.convertStacksMachineToStacksEuro(str(response[14:16]))
        print("BV Response : ",response)
        time.sleep(.2)
        # Volver a recogida de billetes, luz verde on bill
        print("BV Encender leds IDLE ...")
        self.com.write(bytes([0xFC,0x06,0xC3,0x00,0x04,0xD6]))
        response = str(self.com.readline().hex())
        print("BV Response : ",response)
        time.sleep(.2)
        print("Actual config in stacks : ", self.stackA, "  " ,self.stackB)
        self.setStacksInOrden( self.stackA , self.stackB )

    def setStacksInOrden(self, stackA,stackB):
            if(stackA > stackB):
                self.minBill = stackB
                self.maxBill = stackA
            else:
                self.minBill = stackA
                self.maxBill = stackB

            self.stackA = stackA
            self.stackB = stackB 
            
    def convertStacksMachineToStacksEuro(self, stack):
        if(stack == "00"):
            return 0
        if(stack == "02"):
            return 5
        if(stack == "04"):
            return 10
        if(stack == "08"):
            return 20
        if(stack == "10"):
            return 50

    def payout(self,payFromStack1,payFromStack2):
        print("Corutina de devolución:")
        self.pausePollThread()
        print("BV Setting inhibit...")
        self.com.write(bytes([0xFC,0X06,0XC3,0X01,0X8D,0xC7]))
        status,data = self.read_response()
        print("BV STATUS: ",status)
        time.sleep(.2)

        self.sendPayCommand(payFromStack1,payFromStack2)
        print("SENDED PAYOUT")
        status,data = self.read_response()
        print("*should be [FC 05 50 AA 05]")
        print("BV STATUS: ",status)
        time.sleep(.2)
        
        # Request status
        self.com.write(bytes([0xFC,0X05,0X11,0X27,0X56]))
        status,data = self.read_response()
        print("Should be  Pay Stay [FC 05 24 09 30]")
        print("BV STATUS: ",status)
        time.sleep(.2)

        # ACK 
        self.com.write(bytes([0xFC,0X05,0X50,0XAA,0X05]))
        status,data = self.read_response()
        print("Should be  []")
        print("BV STATUS: ",status)
        time.sleep(.2)

        try:
            time.sleep(.1)
            response = str(self.com.readline().hex())
            print(response)
        except:
            print("Error parsing response")
            pass

        while True:
           self.resumePollThread()
           (status,data) = self.bv_status
           time.sleep(.3)
           print("payout():Status: " , status)
           if status == PAY_VALID:
                self.pausePollThread()
                break
    
    def sendPayCommand(self,payFromStack1,payFromStack2):
        
        #payout():Status: 1a 
        if(payFromStack1):
            print("sendPayCommand to Stack1")
            return self.com.write(bytes([0xFC ,0x09, 0xF0, 0x20, 0x4A, 0x01, 0x01, 0x10, 0x6E]))
        if(payFromStack2):
            print("sendPayCommand to Stack2")
            return self.com.write(bytes([0xFC ,0x09, 0xF0, 0x20, 0x4A, 0x01, 0x02, 0x8B, 0x5C]))

    def _on_stacker_full(self, data):
        logging.error("Stacker full.")
    def _on_stacker_open(self, data):
        logging.warning("Stacker open.")
    def _on_acceptor_jam(self, data):
        logging.error("Acceptor jam.")
    def _on_stacker_jam(self, data):
        logging.error("Stacker jam.")
    def _on_pause(self, data):
        logging.warning("BV paused. If there's a second bill being inserted, remove it.")
    def _on_cheated(self, data):
        logging.warning("BV cheated.")
    def _on_failure(self, data):
        fault = ord(data)
        if fault not in FAILURE_CODES:
            logging.error("Unknown failure: %02x" % fault)
        else:
            logging.error(FAILURE_CODES[fault])
    def _on_comm_error(self, data):
        logging.warning("Communication error.")
        logging.debug("Details: %r" % ['0x%02x' % x for x in data])
    def _on_invalid_command(self, data):
        logging.warning("Invalid command.")
    def _on_pay_valid(self, data):
        logging.info(" BV: PAY VALID")
        self.com.write(bytes([0xFC,0X05,0X50,0XAA,0X05]))
        status,data = self.read_response()
        print("Should be  []")
        print("BV STATUS: ",status)
    def _on_note_error(self, data):
        logging.error(" BV: note error")
    def _on_pay_stay(self, data):
        logging.info(" BV: Pay stay")
    def _on_idle(self, data):
        logging.info("BV idle.")
    def _on_accepting(self, data):
        logging.info("BV accepting...")
    def _on_escrow(self, data):
        escrow = data[0]
        if escrow not in self.bv_denoms:
            raise DenomError("Unknown Bill code: %x" % escrow)
        elif escrow == BARCODE_TKT:
            barcode = data[1:]
            logging.info("Barcode: %s" % barcode)
        else:
            self.cb(self.bv_denoms[escrow])
            logging.info("Denom: %s" % self.bv_denoms[escrow])
            
        s_r = '1'
        # "(1) Stack and acknowledge when bill passes stacker lever\n"
        # "(2) Stack and acknowledge when bill is stored\n"
        if s_r == '1':
            logging.info("Sending Stack-1 command...")
            self.accepting_denom = self.bv_denoms[escrow]
            status = None
            while status != ACK:
                self.send_command(STACK_1, b'')
                status, data = self.read_response()
            logging.debug("Received ACK")
            self.bv_status = (0x00,0x00)
        elif s_r == '2':
            logging.info("Sending Stack-2 command...")
            self.accepting_denom = self.bv_denoms[escrow]
            status = None
            while status != ACK:
                self.send_command(STACK_2, b'')
                status, data = self.read_response()
            logging.debug("Received ACK")
            self.bv_status =  (0x00,0x00)
        elif s_r == 'r':
            logging.info("Telling BV to return...")
            status = None
            while status != ACK:
                self.send_command(RETURN, b'')
                status, data = self.read_response()
            logging.debug("Received ACK")
            self.bv_status =  (0x00,0x00)     
    def _on_stacking(self, data):
        logging.info("BV stacking...")
    def _on_vend_valid(self, data):
        # logging.info("Vend valid for %s." % self.accepting_denom)
        self.send_command(ACK, b'')
        self.accepting_denom = None
    def _on_stacked(self, data):
        logging.info("Stacked.")
    def _on_rejecting(self, data):
        reason = ord(data)
        if reason in REJECT_REASONS:
            logging.warning("BV rejecting, reason: %s" % REJECT_REASONS[reason])
        else:
            logging.warning("BV rejecting, unknown reason: %02x" % reason)
    def _on_returning(self, data):
        logging.info("BV Returning...")
    def _on_holding(self, data):
        logging.info("Holding...")
    def _on_inhibit(self, data):
        logging.warning("BV inhibited.")
        # input("Press enter to reset and initialize BV.")
        status = None
        (status, data) = self.bv_status

        while status != ACK: 
            logging.debug("Sending reset command")
            self.send_command(RESET, b'')
            status, data = self.read_response()
            time.sleep(0.2)
        logging.debug("Received ACK")
        if self.req_status()[0] == INITIALIZE:
            logging.info("Initializing bill validator...")
            self.initialize()
    def _on_init(self, data):
        logging.warning("BV waiting for initialization")
        # input("Press enter to reinitialize the BV.")
        self.initialize()
