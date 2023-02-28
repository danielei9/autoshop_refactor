from Model.TPVCommunication.Request.Request import *

class ConfigStackRequest(Request):
    def __init__(self, typeRequest,stackA,stackB,quantityStackA,quantityStackB):
        print("init configrequest")
        self.stackA = stackA
        self.stackB = stackB
        self.quantityStackA = quantityStackA
        self.quantityStackB = quantityStackB
        super().__init__(typeRequest)
            
