from Model.TPVCommunication.Request.Request import *
class CancelRequest(Request):
        def __init__(self,idOrder, typeRequest, stackA, stackB):
            print("init cancel request")
            super().__init__(typeRequest,idOrder)
            self.stackA = stackA
            self.stackB = stackB
