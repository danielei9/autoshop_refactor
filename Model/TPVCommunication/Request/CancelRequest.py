from Model.TPVCommunication.Request.Request import *
class CancelRequest(Request):
        def __init__(self,idOrder, typeRequest, status):
            print("init cancel request")
            super().__init__(status,typeRequest)
            self.idOrder = idOrder
