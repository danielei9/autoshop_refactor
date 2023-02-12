from Model.TPVCommunication.Request.Request import *

class ConfigStackRequest(Request):
        def __init__(self, typeRequest,idOrder,stackA,stackB):
            print("init configrequest")
            self.stackA = stackA
            self.stackB = stackB
            self.idOrder = idOrder
            super().__init__(0,typeRequest)
            
