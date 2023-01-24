from Model.TPVCommunication.Request.Request import *

class ConfigStackRequest(Request):
        def __init__(self, typeRequest,idOrder,stackA,stackB):
            print("init configrequest")
            self.stackA = stackA
            self.stackB = stackB
            super().__init__(typeRequest,idOrder)
            
