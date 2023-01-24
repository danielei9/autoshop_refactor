# Exceptions

class CRCError(Exception):
    """Computed CRC does not match given CRC"""
    pass

class SyncError(Exception):
    """Tried to read a message, but got wrong start byte"""
    pass

class PowerUpError(Exception):
    """Expected power up, but received wrong status"""
    pass

class AckError(Exception):
    """Acceptor did not acknowledge as expected"""
    pass

class DenomError(Exception):
    """Unknown denomination reported in escrow"""
    pass