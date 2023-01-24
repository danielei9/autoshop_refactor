
ACK = 0x50
SYNC = 0xFC

## Setting commands ##
SET_DENOM = 0xC0
SET_SECURITY = 0xC1
SET_INHIBIT = 0xC3
SET_DIRECTION = 0xC4
SET_OPT_FUNC = 0xC5
SET_BAR_FUNC = 0xC6
SET_BAR_INHIBIT = 0xC7

## Setting status requests ##
GET_DENOM = 0x80
GET_SECURITY = 0x81
GET_INHIBIT = 0x83
GET_DIRECTION = 0x84
GET_OPT_FUNC = 0x85
GET_BAR_FUNC = 0x86
GET_BAR_INHIBIT = 0x87

GET_VERSION = 0x88
GET_BOOT_VERSION = 0x89

################################
### Controller -> Acceptor ###
################################

STATUS_REQ = 0x11
STATUS_REQ_EXTENSAO = bytearray([0xF0, 0x1A])

## Operation commands ##
RESET = 0x40
STACK_1 = 0x41
STACK_2 = 0x42
RETURN = 0x43
HOLD = 0x44
WAIT = 0x45

################################
### Acceptor -> Controller ###
################################

## Status ##
ENABLE = 0x11
IDLE = 0x11  # Alias for ENABLE
ACEPTING = 0x12
ESCROW = 0x13
STACKING = 0x14
VEND_VALID = 0x15
STACKED = 0x16
REJECTING = 0x17
RETURNING = 0x18
HOLDING = 0x19
DISABLE = 0x1A
INHIBIT = 0x1A  # Alias for DISABLE
INITIALIZE = 0x1B
NORM_STATUSES = tuple(range(0x11, 0x1C))
## Status extension ##
NORMAL = 0x10 #  + data 
PAYING = 0x20
PAY_STAY= 0x24
PAY_VALID= 0x23
 
## Power up status ##
POW_UP = 0x40
POW_UP_BIA = 0x41  # Power up with bill in acceptor
POW_UP_BIS = 0x42  # Power up with bill in stacker
POW_STATUSES = 0x40, 0x41, 0x42
PAYING_STATUSES = 0x23,0x24
## Error status ##
STACKER_FULL = 0x43
STACKER_OPEN = 0x44
ACCEPTOR_JAM = 0x45
STACKER_JAM = 0x46
PAUSE = 0x47
CHEATED = 0x48
FAILURE = 0x49
COMM_ERROR = 0x4A
INVALID_COMMAND = 0x4B
ERROR_STATUSES = tuple(range(0x43, 0x4C))
## Error status Extension##
RECYCLER_JAM = 0x40
DOOR_OPEN = 0x41
MOTOR_ERROR = 0x42
EEPROM_ERROR = 0x43
PAY_OUT_NOTE_ERROR = 0x44
RECYCLE_BOX_OPEN = 0x45
HARDWARE_ERROR = 0x4A

################################
### Data constants ###
################################

## Escrow ##
DENOM_1 = 0x61
DENOM_2 = 0x62
DENOM_3 = 0x63
DENOM_4 = 0x64
DENOM_5 = 0x65
DENOM_6 = 0x66
DENOM_7 = 0x67
DENOM_8 = 0x68
BARCODE_TKT = 0x6F

ESCROW_EU = {  # 2 and 8 are reserved
    DENOM_1: '5',
    DENOM_3: '10',
    DENOM_4: '20',
    DENOM_5: '50',
    DENOM_6: '100',
    DENOM_7: '200',
    BARCODE_TKT: 'TITO',
}

## Reject reasons ##
INSERTION_ERR = 0x71
MAG_ERR = 0x72
REMAIN_ACC_ERR = 0x73
COMP_ERR = 0X74
CONVEYING_ERR = 0x75
DENOM_ERR = 0x76
PHOTO_PTN1_ERR = 0x77
PHOTO_LVL_ERR = 0x78
INHIBIT_ERR = 0x79
OPERATION_ERR = 0x7B
REMAIN_STACK_ERR = 0x7C
LENGTH_ERR = 0x7D
PHOTO_PTN2_ERR = 0x7E
MULTI_ERR = 0x98
TKT_BACKSIDE_ERR = 0x9B

REJECT_REASONS = {
    INSERTION_ERR: "Insertion error",
    MAG_ERR: "Magnetic sensor error",
    REMAIN_ACC_ERR: "Remaining bills in head error",
    COMP_ERR: "Compensation error",
    CONVEYING_ERR: "Conveying error",
    DENOM_ERR: "Error assessing denomination",
    PHOTO_PTN1_ERR: "Photo pattern 1 error",
    PHOTO_LVL_ERR: "Photo level error",
    INHIBIT_ERR: "Inhibited",
    OPERATION_ERR: "Operation error",
    REMAIN_STACK_ERR: "Remaining bills in stacker error",
    LENGTH_ERR: "Length error",
    PHOTO_PTN2_ERR: "Photo pattern 2 error",
    MULTI_ERR: "Multiple bills inserted",
    TKT_BACKSIDE_ERR: "Ticket inserted upside-down",
}

## Failure codes ##
STACK_MOTOR_FAULT = 0xA2
TRANS_SPEED_FAULT = 0xA5
TRANS_MOTOR_FAULT = 0xA6
CAN_NOT_RDY = 0xAB
HEAD_REMOVE = 0xAF
BOOT_ROM_FAULT = 0xB0
EXT_ROM_FAULT = 0xB1
ROM_FAULT = 0xB2
EXT_ROM_WRT_FAULT = 0xB3

FAILURE_CODES = {
    STACK_MOTOR_FAULT: "Stacker motor failure",
    TRANS_SPEED_FAULT: "Transport motor speed failure",
    TRANS_MOTOR_FAULT: "Transport motor failure",
    CAN_NOT_RDY: "Cash box not ready",
    HEAD_REMOVE: "Validator head removed",
    BOOT_ROM_FAULT: "Boot ROM failure",
    EXT_ROM_FAULT: "External ROM failure",
    ROM_FAULT: "ROM failure",
    EXT_ROM_WRT_FAULT: "External ROM write failure",
}

############################
### Bitfield constants ###
############################

## Denom inhibit (SET_DENOM) ##
# Two bytes, only first byte used
# 0 = enabled, 1 = disabled
DENOM_USA_1 = 1
DENOM_USA_RESERVED1 = 2
DENOM_USA_5 = 4
DENOM_USA_10 = 8
DENOM_USA_20 = 16
DENOM_USA_50 = 32
DENOM_USA_100 = 64
DENOM_USA_RESERVED2 = 128
DENOM_USA_DEFAULT = DENOM_USA_RESERVED1 | DENOM_USA_RESERVED2
DENOMS = {
    'denom1': 1,
    'denom2': 2,
    'denom3': 4,
    'denom4': 8,
    'denom5': 16,
    'denom6': 32,
    'denom7': 64,
    'denom8': 128,
}
DENOM_MAP = {
    'denom1': 0x61,
    'denom2': 0x62,
    'denom3': 0x63,
    'denom4': 0x64,
    'denom5': 0x65,
    'denom6': 0x66,
    'denom7': 0x67,
    'denom8': 0x68,
}

## Denom security (SET_SECURITY) ##
# Two bytes, only first byte used
# 0 = low security, 1 = high security
SECURITY_USA_1 = 1
SECURITY_USA_RESERVED1 = 2
SECURITY_USA_5 = 4
SECURITY_USA_10 = 8
SECURITY_USA_20 = 16
SECURITY_USA_50 = 32
SECURITY_USA_100 = 64
SECURITY_USA_RESERVED2 = 128
SECURITY_USA_DEFAULT = 0

## Direction inhibit (SET_DIRECTION) ##
# 0 = enabled, 1 = disabled
# When facing the obverse of the bill, A is on the left
DIR_FRONT_A = 1
DIR_FRONT_B = 2
DIR_BACK_A = 4
DIR_BACK_B = 8
DIR_DEFAULT = 0
DIRECTIONS = {
    'fa': 1,
    'fb': 2,
    'ba': 4,
    'bb': 8,
}

## Optional functions (SET_OPT_FUNC) ##
# 0 = disabled, 1 = enabled
OPT_POW_RECOV = 2  # power recovery
OPT_AUTO_RETRY = 4  # auto retry operation
OPT_24CHAR = 8  # accept 24-character barcodes
OPT_NEAR_FULL = 32  # nearly full stacker?
OPT_ENT_SENS = 64  # entrance sensor event
OPT_ENCRYPT = 128  # encryption
OPT_DEFAULT = 0
OPTIONS = {
    'power_recovery': 2,
    'auto_retry': 4,
    '24_char_barcode': 8,
    'near_full': 32,
    'entrance_event': 64,
    'encryption': 128,
}

## Barcode functions (SET_BAR_FUNC) ##
# first byte barcode type (only valid value is 0x01 = interleaved 2 of 5)
# second byte:
BAR_18_CHAR = 0x12
BAR_MULTI = 0xFF  # required if OPT_24CHAR is set?