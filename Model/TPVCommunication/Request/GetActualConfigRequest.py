from Model.TPVCommunication.Request.Request import *

class GetActualConfigRequest(Request):
    def __init__(self, typeRequest):
        print("init GetActualConfigRequest")
        super().__init__(typeRequest)
            
