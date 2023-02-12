from Model.TPVCommunication.Request.Request import *

class ConnectedRequest(Request):
    def __init__(self, typeRequest,connected):
        print("init ConnectedRequest")
        self.connected = connected
        super().__init__(typeRequest)
            
