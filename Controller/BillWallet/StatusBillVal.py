import logging
from .CodesBillVal import *
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
        self.bv_status = None
    elif s_r == '2':
        logging.info("Sending Stack-2 command...")
        self.accepting_denom = self.bv_denoms[escrow]
        status = None
        while status != ACK:
            self.send_command(STACK_2, b'')
            status, data = self.read_response()
        logging.debug("Received ACK")
        self.bv_status = None
    elif s_r == 'r':
        logging.info("Telling BV to return...")
        status = None
        while status != ACK:
            self.send_command(RETURN, b'')
            status, data = self.read_response()
        logging.debug("Received ACK")
        self.bv_status = None
                

def _on_stacking(self, data):
    logging.info("BV stacking...")

def _on_vend_valid(self, data):
    logging.info("Vend valid for %s." % self.accepting_denom)
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

def _on_init(self, data):
    logging.warning("BV waiting for initialization")
    input("Press enter to reinitialize the BV.")
    self.initialize()
