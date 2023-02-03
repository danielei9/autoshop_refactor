import json
class Request():
    def __init__(self, typeRequest,status):
        print("init request")
        self.status = status
        self.typeRequest = typeRequest
        
