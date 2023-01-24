import serial

class SerialCommunicator:
    def __init__(self, port, baudrate=9600, timeout=0.2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = False
        self.com = None
    
    def open_port(self):
        try:
            self.com = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.com.open()
            self.is_open = True
        except serial.SerialException as e:
            raise e
            
    def close_port(self):
        if self.is_open:
            self.com.close()
            self.is_open = False

    def send_data(self, data):
        if self.is_open:
            self.com.write(data)
    
    def receive_data(self):
        if self.is_open:
            return self.com.readline()

