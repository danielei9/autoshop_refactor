# # # # # # # # # # # # # # # # # # # # # 
# NORMAL COMMANDS
# # # # # # # # # # # # # # # # # # # # #

# RECEIVING COINS

UN_EURO = '08 54'
DOS_EURO = '08 55'
ZERO_ZERO_FIVE = '08 50'
ZERO_TEN = '08 51'
ZERO_TWNTY = '08 52'
ZERO_FIVETY = '08 53'

"""
    #Send info about setup initi
    # Response 23 bytes z1-z23
    # z1 Changer Feature Level // Level3 = 0x03 // Level2 = 0x02 ...
    #  z2-z3 country code  for the Euro is 1978 (Z2 = 19 and Z3 = 78).
    # Z4 = Coin Scaling Factor - 1 byte 
    # Z5 = Decimal Places - 1 byte 
 Indicates the number of decimal places on a credit display. For example, this could be set to 02H in the USA.
    # Z6-Z7 Coin Type Routing - 2 bytes
    # Bit is set to indicate a coin type can be routed to the tube. Valid coin types are 0 to 15.
    # Z8 - Z23 = Coin Type Credit - 16 bytes 
    # Indicates the value of coin types 0 to 15. Values must be sent in ascending order. This number is the coin's monetary value
    #  divided by the coin scaling factor. Unused coin types are sent as 00H. Unsent coin types are assumed to be zero. It is not
    # necessary to send all coin types. Coin type credits sent as FFH are assumed to be vend tokens. That is, their value is assumed to worth one vend.
"""
SETUP = [0x09]
"""

    # This command is the vehicle that the VMC should use to tell the changer that it should return to its default operating mode
"""
RESET = [0x08]
"""
    # Z1 - Z2 = Tube Full Status - 2 bytes 
Indicates status of coin tube for coin types 0 to 15. 
A bit is set to indicate a full tube. For example, bit 7 = set would
    # indicate the tube for coin type 7 is ful
    # Z3 - Z18 = Tube Status - 16 bytes Indicates the greatest number of coins that the changer “knows” definitely are present in the coin tubes.
"""
TUBE_STATUS = [0x0A]

DIAGNOSTIC_STATUS = [0x0F,0x05]
"""
    # Z1 - Z16 = Changer Activity - 16 bytes 
Indicates the changer activity. If there is nothing to report, the changer should send only an ACK. Otherwise, the only valid
    # responses 
"""
    
POLL =  [0x0B]
"""
# To enable desired coin acceptance and disable manual coin payout if desired
"""
COINTYPE = [0x0C]
DISPENSE =[0x0D]
EXPANSION_COMMAND = [0x0F]

# # # # # # # # # # # # # # # # # # # # # 
# #  EXPANSION LEVEL SUBCOMANDS
# # # # # # # # # # # # # # # # # # # # # 

IDENTIFICATION = [0x00]
PAYOUT = [0x02]
PAYOUT_STATUS = [0x03]
PAYOUT_VALUE_POLL = [0x04]
DIAGNOSTIC_STATUS = [0x05]