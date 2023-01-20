#!/usr/bin/env python3

import serial
import time
import logging
from Controller.BillWallet.CodesBillVal import *
from Controller.SerialCommunicator import *


###################################################
# CLASS BILLVAL
###################################################
class BillWalletController(SerialCommunicator):
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

    def __init__(self,cb, port,log_raw=False, threading=False):
        super().__init__(port)
        self.initializeSerial()
        self.cb = cb
        # Try to check and connect to dyn port USB 
        
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
        print("INITIALIZED BILLWALLET")

    def sendGetConfigStacksCommand(self):
        self.send_data(bytes([0xFC,0X07,0XF0,0X20,0X90,0x39,0X84]))
        
    def sendConfigCommand(self,stackA,stackB):
        # Currrency Selector (0x02)5€ (0x04)10€ (0x08)20€ (0x10)50€
        if(stackA == 5 and stackB == 10):
            self.send_data(bytes([0xFC,0X0D,0XF0,0X20,0XD0,0x02,0X00,0X01,0x04,0X00,0X02,0x19,0xE7]))
        if(stackA == 10 and stackB == 20):
            self.send_data(bytes([0xFC,0X0D,0XF0,0X20,0XD0,0x04,0X00,0X01,0x08,0X00,0X02,0x40,0x5A]))
        if(stackA == 20 and stackB == 50):
            self.send_data(bytes([0xFC,0X0D,0XF0,0X20,0XD0,0x08,0X00,0X01,0x10,0X00,0X02,0xE3,0x28]))
        if(stackA == 10 and stackB == 5):
            self.send_data(bytes([0xFC,0X0D,0XF0,0X20,0XD0,0x04,0X00,0X01,0x02,0X00,0X02,0x3A,0x29]))
        if(stackA == 20 and stackB == 10):
            self.send_data(bytes([0xFC,0X0D,0XF0,0X20,0XD0,0x08,0X00,0X01,0x04,0X00,0X02,0x17,0xCE]))
        if(stackA == 50 and stackB == 20):
            self.send_data(bytes([0xFC,0X0D,0XF0,0X20,0XD0,0X10,0X00,0X01,0X08,0X00,0X02,0x5C,0x08]))
        
        self.setStacksInOrden( stackA , stackB )


    def configMode(self,stackA,stackB):
        # print("configMode in Billval, reset,,")
        # self.send_data(bytes([0xFC,0x05,0x40,0x2B,0x15]))
        # time.sleep(30)
        print("sending inhibit configMode")
        self.send_data(bytes([0xFC,0x06,0xC3,0x01,0x8D,0xC7]))
        time.sleep(2)
        print("response: ",self.com.read_all())
        time.sleep(2)
        self.sendConfigCommand(stackA,stackB)
        time.sleep(2)
        print(self.com.readline().hex())
        time.sleep(2)
        print("Configured :) OK ")
        self.send_data(bytes([0xFC,0x06,0xC3,0x00,0x04,0xD6]))
        print(self.com.readline().hex())
        time.sleep(2)

        # 04  -- > convertStacksMachineToStacksEuro -- > 10€
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

    def setStacksInOrden(self, stackA,stackB):
            if(stackA > stackB):
                self.minBill = stackB
                self.maxBill = stackA
            else:
                self.minBill = stackA
                self.maxBill = stackB

            self.stackA = stackA
            self.stackB = stackB

    def getActualStacksConfig(self):
            print("sending get config Stacks")
            self.send_data(bytes([0xFC,0x06,0xC3,0x01,0x8D,0xC7]))
            time.sleep(.2)
            print("response: ",self.com.read_all())
            time.sleep(.2)
            self.sendGetConfigStacksCommand()
            time.sleep(.2)
            response = str(self.com.readline().hex())
            print()
            time.sleep(.2)
            # Volver a recogida de billetes, luz verde on bill
            self.send_data(bytes([0xFC,0x06,0xC3,0x00,0x04,0xD6]))
            print(self.com.readline().hex())
            time.sleep(.2)
            stackA = self.convertStacksMachineToStacksEuro(str(response[10:12]))
            stackB = self.convertStacksMachineToStacksEuro(str(response[14:16]))
            print("Actual config in stacks : ", stackA, "  " ,stackB)
            self.setStacksInOrden( stackA , stackB )

# reset
# Set currency 

    def init(self):
        print("INITIALIZE")
        #       LOGGING DEBUG esto dará problemas, hay que ver como lo añadimos por que sirve para obtener el logg de la maquina de billetes
        if not logging.getLogger('').hasHandlers():
            logging.basicConfig(level=logging.DEBUG,
                                format="[%(asctime)s] %(levelname)s: %(message)s",
                                filename='debug_BillWallet.log',
                                filemode='w',
                                )
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
        print("power ON")
        self.power_on()
        print("power ON DONE ")
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
            self.set_inhibit(1)
        print("Get actual config ")
        
        # self.set_recycler_config(10,20)
        self.getActualStacksConfig()
    # RAW LOGGING
    def _raw(self, pre, msg):
        if self.raw:
            msg = ['0x%02x' % x for x in msg]
            log = open('raw.log', 'a')
            log.write('{} {}\r\n'.format(pre, msg))
            log.close()
####################################
#  UART STATES
####################################

#       BOX FULL
    async def _on_stacker_full(self, data):
        logging.error("Stacker full.")
#       Stacker OPEN
    async def _on_stacker_open(self, data):
        logging.warning("Stacker open.")
#       ACEPTANDO BILLETES Atascado
    async def _on_acceptor_jam(self, data):
        logging.error("Acceptor jam.")
#       Atasco donde guarda billetes
    async def _on_stacker_jam(self, data):
        logging.error("Stacker jam.")
#       Cuando el estado es pausa
    async def _on_pause(self, data):
        logging.warning(
            "BV paused. If there's a second bill being inserted, remove it.")
#       Intento de fraude de billetes
    async def _on_cheated(self, data):
        logging.warning("BV cheated.")
#
    async def _on_failure(self, data):
        fault = ord(data)
        if fault not in FAILURE_CODES:
            logging.error("Unknown failure: %02x" % fault)
        else:
            logging.error(FAILURE_CODES[fault])
#
    async def _on_comm_error(self, data):
        logging.warning("Communication error.")
        logging.debug("Details: %r" % ['0x%02x' % x for x in data])
#
    async def _on_invalid_command(self, data):
#
        logging.warning("Invalid command.")
#
    async def _on_paying(self, data):
        self.payDone = False
        logging.warning("Paying...")
#
    async def _on_pay_stay(self, data):
        logging.warning("Pay Stay.")
        (status,data) = self.req_status()
        print("_on_pay_stay: payStay Status: %02x" % status)
        self.sendAckPay()
#
    async def _on_pay_valid(self, data):
        (status,data) = self.req_status()
        logging.warning("_on_pay_valid: Pay Done. Status: %02x" % status)
        print("_on_pay_valid: Pay Done. Status: %02x" % status)
        self.sendAckPay()
#
    async def _on_idle(self, data):
        logging.info("BV idle.")
#
    async def _on_accepting(self, data):
        logging.info("BV accepting...")
#
    async def _on_escrow(self, data):
        """
        CUANDO RECIBE DINERO EL BILLETERO
        llama a esta función
        mediante la seleccion del billetero
        debe de enviar los billetes de un tipo a un sitio
        y los de otro al otro
        """
        escrow = data[0]
        if escrow not in self.bv_denoms:
            raise DenomError("No se que denom es: %x" % escrow)
        elif escrow == BARCODE_TKT:
            barcode = data[1:]
            logging.info("Barcode: %s" % barcode)
        else:
            logging.info("Denom: %s" % self.bv_denoms[escrow])
        self.escrow = escrow
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
        # while s_r not in ('1', '2', 'r'):
            # s_r = input("(1) Stack and acknowledge when bill passes stacker lever\n"
            #             "(2) Stack and acknowledge when bill is stored\n"
            #             "(R)eturn ").lower()
            
        s_r = '1'
        if int(self.bv_denoms[escrow]) == 10:
            print("Billete de 10 ")
        if int(self.bv_denoms[escrow]) == 20:
            print("Billete de 20 ")
        if int(self.bv_denoms[escrow]) == 5:
            print("Billete de 5 ")
        if int(self.bv_denoms[escrow]) == 50:
            print("Billete de 50 ")
        if s_r == '1':
            logging.info("Sending Stack-1 command...")
#             self.accepting_denom = self.bv_denoms[escrow]
            status = None
            while status != ACK:
                self.send_command(STACK_1, b'')
                status, data = self.read_response()
            logging.debug("Received ACK")
            self.bv_status = None
        elif s_r == '2':
            logging.info("Sending Stack-2 command...")
#             self.accepting_denom = self.bv_denoms[escrow]
            status = None
            while status != ACK:
                self.send_command(STACK_2, b'')
                status, data = self.read_response()
            logging.debug("Received ACK")
            self.bv_status = None
        elif s_r == 'r':
            logging.info("BV to return...")
            status = None
            while status != ACK:
                self.send_command(RETURN, b'')
                status, data = self.read_response()
            logging.debug("Received ACK")
            self.bv_status = None
# ----------------------------------------------------------------
    async def _on_stacking(self, data):
        logging.info("BV stacking...")
#
    async def _on_vend_valid(self, data):
        # logging.info("Vend valid for %s." % self.accepting_denom)
        self.send_command(ACK, b'')
        time.sleep(0.25)
        print("self.cb(self.bv_denoms[self.escrow])")
        await self.cb(self.bv_denoms[self.escrow])
#         
    async def _on_stacked(self, data):
        logging.info("Stacked.")
#
    async def _on_rejecting(self, data):
        reason = ord(data)
        if reason in REJECT_REASONS:
            logging.warning("BV rejecting, reason: %s" %
                            REJECT_REASONS[reason])
        else:
            logging.warning("BV rejecting, unknown reason: %02x" % reason)
#
    async def _on_returning(self, data):
        logging.info("BV Returning...")
#
    async def _on_holding(self, data):
        logging.info("Holding...")
#
    async def _on_inhibit(self, data):
        logging.warning("BV inhibited.")
        print("RESET BV AND INITIALIZE")
        # input("Press enter to reset and initialize BV.")
        status = None
        while status != ACK:
            logging.debug("Sending reset command")
            self.send_command(RESET, b'')
            status, data = self.read_response()
            time.sleep(0.2)
        logging.debug("Received ACK")
        if self.req_status()[0] == INITIALIZE:
            logging.info("Initializing bill validator...")
            self.initialize()
        self.bv_status = None
#
    async def _on_init(self, data):
        logging.warning("BV waiting for initialization")
        # input("Press enter to reinitialize the BV.")
        print("REINITIALIZE BV")

        self.initialize()

###################################################
# Send default command
#       HEAD => SYNC(FC) LENGTH [command] [data] CRC1 CRC2
###################################################
 
    def send_command(self, command, data=b''):
        """Send a generic command to the bill validator"""
        print("sendCommand")

        length = 5 + len(data)  # SYNC, length, command, and 16-bit CRC
        message = bytes([SYNC, length, command]) + data
        message += self.get_crc(message)
        print(message)

        # log message
        self._raw('>', message)

        return self.send_data(message)
###################################################
# Send expansion command
#       HEAD => SYNC(FC) LENGTH [command] [data] CRC1 CRC2
#       FC 09 F0 20 4A 01 02 8B 5C PAYOUT COMMAND
###################################################
    def sendRawCommand(self):
        print("sendRawCommand")
        return self.send_data(bytes([0xFC ,0x09, 0xF0, 0x20, 0x4A, 0x01, 0x02, 0x8B, 0x5C]))
    def sendPayCommand(self,payFromStack1,payFromStack2):
        
        # TODO: WARNING: Found unused data in buffer, b'\xfc\x05\x1a\xf4\xe8'
        #payout():Status: 1a 

        print("sendPayCommand")
        if(payFromStack1):
            print("sendPayCommand to Stack1")
            return self.send_data(bytes([0xFC ,0x09, 0xF0, 0x20, 0x4A, 0x01, 0x01, 0x10, 0x6E]))
        if(payFromStack2):
            print("sendPayCommand to Stack2")
            return self.send_data(bytes([0xFC ,0x09, 0xF0, 0x20, 0x4A, 0x01, 0x02, 0x8B, 0x5C]))
    def sendAckPay(self):
        print("sendingACK Confirmed Pay")
        time.sleep(0.2)
        res = self.send_data(bytes([0xFC ,0x05, 0x50, 0xAA, 0x05]))
        time.sleep(0.2)
        self.set_inhibit(1)
        return res       
    def send_expansion_command(self, command, data=b''):
        """Send a expansion command to the bill validator"""
        commandA = 0xF0
        length = 6 + len(data)  # SYNC, length, command, and 16-bit CRC
        message = bytes([SYNC, length, commandA,command]) + bytes(data)
        message += get_crc(message)
# [FC 0D F0 20 D0 04 00 01 08 00 02 40 5A
        # log message
        self._raw('>', message)

        return self.send_data(message)
###################################################
# Read default command
###################################################
    def read_response(self):
        """Parse data del billetero. Devuelve una tuple (command, data)"""

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
        if get_crc(full_msg) != crc:
            pass
            #raise CRCError("CRC mismatch") (TODO:fallo con crc a veces revisar)

        return ord(command), data
###################################################
#  POWER ON FASE 1 
###################################################
    def power_on(self, *args, **kwargs):
        """Handle startup routines"""
        # Activamos el estado de ON
        self.bv_on = True
        # Limpiamos estado
        status = None
        # Esperamos nuevo estado cuando envia POW_STATUSES
        # Siguiente estado POW_STATUSES
        while status is None or status == 0x00:
            status, data = self.req_status()
            print("While")
            if not self.bv_on:
                # En caso de polling forzamos PowerUP
                self.init_status = None
                return
        print("LLEGAS 1")
        # update estado
        self.init_status = status
        # Si se vuelva iniciar pero ya estaba encendida e inhibida    
        if status == INHIBIT:
            self.set_inhibit(1)
            logging.warning(
                "Acceptor already powered up,but inhibited status: %02x" % status)
            return
        # #Ya esta ready to fight 
        print("LLEGAS 1a")
        if status not in POW_STATUSES:
            logging.warning(
                "Acceptor already powered up, status: %02x" % status)
            return self.init_status

        # Estado POW_UP para inicializar
        elif status == POW_UP:
            print("LLEGAS 2")
            logging.info("Powering up...")
            logging.info("Getting version...")
            self.send_command(GET_VERSION)
            status, self.bv_version = self.read_response()
            logging.info("BV software version: %s" % self.bv_version.decode())
            # Estado POW_UP para inicializar
            # Enviando 40H RESET 
            self.reset()
            while status != ACK:
                logging.debug("Sending reset command")
                self.send_command(RESET)
                status, data = self.read_response()
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)
        else:
            # Esta en Reject  o Stack Mode
            while status != ACK:
                self.send_command(RESET)
                status, data = self.read_response()
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)
        
        #  BillVal.poll() 
        print("LLEGAS 3")
        
        return self.init_status
    def initialize(self, denom=[0x82, 0], sec=[0, 0], dir=[0], opt_func=[0, 0],
                   inhibit=[0], bar_func=[0x01, 0x12], bar_inhibit=[0]):
        
        """Initialize BV settings"""   
        self.set_denom(denom)
        self.set_security(sec)
        self.set_direction(dir)
        self.set_optional_func(opt_func)
        self.set_inhibit(inhibit)
        self.set_barcode_inhibit(bar_inhibit)
        self.set_barcode_function(bar_func)
        while self.req_status()[0] == INITIALIZE:
            # wait for initialization to finish
            time.sleep(0.2)
    def getStatus(self):
        self.status, self.data = self.req_status()
        return (self.status, self.data)
###################################################
#  POLL FASE 2 Recoleccion de billetes 
###################################################
    async def poll(self, interval=0.2):
        """Send a status request to the bill validator every `interval` seconds
        and fire event handlers. `interval` defaults to 200 ms

        Event handlers are only fired upon status changes. Event handlers can
        set `self.bv_status` to None to force event handler to fire on the next
        status request.
        """
        while True:
            poll_start = time.time()
            status, data = self.req_status()
            if (status, data) != self.bv_status:
                if status in self.bv_events:
                    await self.bv_events[status](data)
            self.bv_status = (status, data)
            self.status = status
            self.data = data
            if(status):
                print("POLL STATUS: ",status,"DATA: ",data )
            wait = interval - (time.time() - poll_start)
            # if (status != IDLE):
            #     print("POLL : Status: %02x" % status)
            if wait > 0.0:
                time.sleep(wait)
###################################################
#  PAYOUT FASE 3 Pago de billetes 
###################################################
    def payout(self,payFromStack1,payFromStack2):
        print("Corutina de devolución:")
        time.sleep(.3)
        # self.set_inhibit(0)
        (status,data) = self.req_status()
        while status != INHIBIT:
            (status,data) = self.req_status()
            self.set_inhibit(0)
            time.sleep(.3)
        # self.set_recycler_config(10,20)
        time.sleep(.3)
        self.sendPayCommand(payFromStack1,payFromStack2)
        while True:
                (status,data) = self.req_status()
                time.sleep(.3)
                print("payout():Status: %02x " % status)
                if status == PAY_VALID:
                    break
                if status == INHIBIT:
                    self.power_on()
                if status == ENABLE:
                    self.payout(payFromStack1,payFromStack2)
        self.sendAckPay()
        return 0
    def getBills(self):
        time.sleep(0.2)
        print("Setting to getBills")
        while (status != INHIBIT): 
            self.set_inhibit(1)
            (status,data) = self.req_status()
    
    # TODO: DELETE
    def settingsCurrencyRecycler(self):
        print("settingsCurrencyRecycler")
        (status,data) = self.req_status()
        while (status != INHIBIT):
            self.send_command(0xF0,0x20,0xD0,0x04,0x00,0x01,0x08,0x00,0x02) 
            time.sleep(0.2)
            (status,data) = self.req_status()
        print("settingsCurrencyRecycler DONE")
###################################################
# BUCHHELPER
###################################################
    def req_status(self):
        """Send status request to bill validator"""

        # if not self.bv_on:
        #     # in case polling thread needs to be terminated before power up
        #     print("Not UP Billwallet")
        #     return None, b''

        if self.com.in_waiting:
            # discard any unused data
            logging.warning("Found unused data in buffer, %r" %
                            self.com.read(self.com.in_waiting))

        self.send_command(STATUS_REQ)

        stat, data = self.read_response()
        print("Estado Billetero: " +str(stat)," data ",str(data) )
        #  TODO: Habilitar el debug de errores POLL
        if stat not in self.all_statuses + (0x00, None):
            logging.warning(
                "Unknown status code received: %02x, data: %r" , stat, data)

        return stat, data
    
    def set_denom(self,denom):
        """
        Command to set the receiving of each bill denomintation
            ->:param bytes denom: [0x82, 0] default
            :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting denom inhibit: %r" % denom)
        denom = bytes(denom)
        self.send_command(SET_DENOM, denom)
        status, data = self.read_response()
        if (status, data) != (SET_DENOM, denom):
            logging.warning("Acceptor did not echo denom settings")
        
    def set_security(self,sec):
        """
        Command to set the security config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting security: %r" % sec)
        sec = bytes(sec)
        self.send_command(SET_SECURITY, sec)
        status, data = self.read_response()
        if (status, data) != (SET_SECURITY, sec):
            logging.warning("Acceptor did not echo security settings")
     
    def set_direction(self,dir):
        """
        Command to set the direction config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting direction inhibit: %r" % dir)
        dir = bytes(dir)
        self.send_command(SET_DIRECTION, dir)
        status, data = self.read_response()
        if (status, data) != (SET_DIRECTION, dir):
            logging.warning("Acceptor did not echo direction settings")
    
    def set_optional_func(self,opt_func):
        """
        Command to set the optional function config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting optional functions: %r" % opt_func)
        opt_func = bytes(opt_func)
        self.send_command(SET_OPT_FUNC, opt_func)
        status, data = self.read_response()
        if (status, data) != (SET_OPT_FUNC, opt_func):
            logging.warning("Acceptor did not echo option function settings")

    def set_inhibit(self,inhibit):
        """
        Command to set the inhibit state
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting inhibit: %r" % inhibit)
        print("set_inhibit")
        inhibit = bytes(inhibit)
        self.send_command(SET_INHIBIT, inhibit)
        status, data = self.read_response()
        if (status, data) != (SET_INHIBIT, inhibit):
            logging.warning("Acceptor did not echo inhibit settings")

    def set_barcode_function(self,bar_func):
        """
        Command to set the bar code config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting barcode functions: %r" % bar_func)
        bar_func = bytes(bar_func)
        self.send_command(SET_BAR_FUNC, bar_func)
        status, data = self.read_response()
        if (status, data) != (SET_BAR_FUNC, bar_func):
            logging.warning("Acceptor did not echo barcode settings")

    def set_barcode_inhibit(self,bar_inhibit):
        """
        Command to set the bar code config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting barcode inhibit: %r" % bar_inhibit)
        bar_inhibit = bytes(bar_inhibit)
        self.send_command(SET_BAR_INHIBIT, bar_inhibit)
        status, data = self.read_response()
        if (status, data) != (SET_BAR_INHIBIT, bar_inhibit):
            logging.warning("Acceptor did not echo barcode inhibit settings")

    def rc_status_request(self,data):
        """
        Command to set the bar code config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("RC request status (extension) ")
        RC_STATUS_REQUEST = bytes(0xF0,0x1A)
        self.send_command(RC_STATUS_REQUEST, bytes(data))
        status, data = self.read_response()
        if (status, data) != (0xF0, data):
            logging.warning("Acceptor did not echo status request (extension)")

    def reset(self):
        status = None
        while status != ACK:
            print("Sending buchu reset command")
            self.send_command(RESET)
            status, data = self.read_response()
            if self.req_status()[0] == RESET:
                print('BUCHU DONE')
        # self.set_recycler_config(self.minBill,self.maxBill)

   
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

        self.send_data(message)
        time.sleep(0.2)
        print("Finish set_recycler_config ")
        status, data = self.read_response()
        print("status: %02x" % status)
        return


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
        
        
#      TEST 
    def buchu_set_recycler_config(self, data=bytes([0x02, 0x00, 0x01, 0x08, 0x00, 0x02])):
        status = None
        while status != ACK:
            print("Sending buchu_set_recycler_config")
            length = 8 + len(data)  # SYNC, length, command, and 16-bit CRC
            message = bytes([SYNC, length, 240, 32, 208]) + data
            message += get_crc(message)
            self._raw('>', message)
            self.send_data(message)
            status, data = self.read_response()
            if self.req_status()[0] == SET_INHIBIT:
                print('BUCHU DONE SET_INHIBIT')

    def get_crc(self,message):
        """Get CRC value for a given bytes object using CRC-CCITT Kermit"""

        TABLE = [
            0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF,
            0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
            0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E,
            0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
            0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD,
            0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
            0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C,
            0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
            0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB,
            0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
            0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A,
            0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
            0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9,
            0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
            0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738,
            0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
            0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7,
            0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
            0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036,
            0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
            0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5,
            0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
            0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134,
            0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
            0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3,
            0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
            0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232,
            0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
            0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1,
            0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
            0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330,
            0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78
        ]

        crc = 0x0000
        for byte in message:
            crc = (crc >> 8) ^ TABLE[(crc ^ byte) & 0xff]

        # convert to bytes
        crc = '%04x' % crc
        crc = [int(crc[-2:], 16), int(crc[:-2], 16)]

        return bytes(crc)
