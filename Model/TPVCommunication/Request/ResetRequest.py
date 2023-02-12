from Model.TPVCommunication.Request.Request import *

class ResetRequest(Request):
    def __init__(self, typeRequest):
        print("init configrequest")
        super().__init__(typeRequest)
            
