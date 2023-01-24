import json
class Request():
    def __init__(self, typeRequest,idOrder):
        print("init request")
        self.idOrder = idOrder
        self.typeRequest = typeRequest
        
