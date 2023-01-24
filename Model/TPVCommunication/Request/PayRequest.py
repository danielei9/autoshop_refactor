from Model.TPVCommunication.Request.Request import *

class PayRequest(Request):
        def __init__(self, idOrder ,order,price ,status,date,typeRequest,shopName,address,phone):
            print("init PayRequest")
            self.order = order
            self.price = price
            self.status = status
            self.date = date
            self.shopName = shopName
            self.address = address
            self.phone = phone
            super().__init__(typeRequest,idOrder)
            