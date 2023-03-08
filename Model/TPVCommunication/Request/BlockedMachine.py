from Model.TPVCommunication.Request.Request import *

class BlockedMachine(Request):
    def __init__(self, typeRequest, blocked):
        print("init GetActualConfigRequest")
        super().__init__(typeRequest)
        self.blocked = blocked

